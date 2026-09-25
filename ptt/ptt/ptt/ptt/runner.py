"""Chunk-wise apply-then-update over a stream of documents.

For each document (list of token ids, plus optional per-token metadata masks):
  for each chunk of size C:
      ctx  = last `ctx_len` tokens of the document seen so far (never crosses documents)
      x    = ctx + chunk
      1) forward with grad on x; compute NTP loss ONLY on chunk positions
      2) record prequential metrics from these logits  (fast weights NOT yet updated on this chunk)
      3) fw.write_chunk(loss)  -> updates G_fast, materializes W_eff
  fw.end_document()

Metric masks are evaluated at position t predicting token t+1, i.e. logits at t are compared with
ids[t+1]. A mask over target tokens is therefore shifted by one to the left internally (see §F.2).
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import torch
import torch.nn.functional as F

from .fastweight import FastWeightManager


@dataclass
class Doc:
    ids: List[int]
    name: str = ""
    # optional boolean masks over *target tokens* (same length as ids); True = evaluate this token
    masks: Dict[str, List[bool]] = field(default_factory=dict)
    meta: Dict = field(default_factory=dict)


@dataclass
class RunConfig:
    chunk: int = 1024
    ctx_len: int = 1024
    max_docs: Optional[int] = None
    log_every: int = 1


def _acc_and_nll(logits: torch.Tensor, targets: torch.Tensor, mask: torch.Tensor):
    """logits [T,V] for positions predicting targets [T]; mask [T] bool."""
    if mask.sum() == 0:
        return 0.0, 0.0, 0
    lp = F.log_softmax(logits.float(), dim=-1)
    nll = -lp.gather(-1, targets[:, None]).squeeze(-1)
    pred = logits.argmax(-1)
    correct = (pred == targets) & mask
    return correct.sum().item(), nll[mask].sum().item(), int(mask.sum().item())


def run_stream(model, fw: FastWeightManager, docs: List[Doc], rcfg: RunConfig, device="cuda",
               eval_only: bool = False) -> Dict:
    """Returns a dict with per-chunk records and per-document summaries."""
    model.eval()  # no dropout; grads still flow to selected params
    if hasattr(fw, "_collect"):
        fw._collect = not eval_only
    records = []
    doc_summaries = []
    t0 = time.time()
    n_docs = len(docs) if rcfg.max_docs is None else min(len(docs), rcfg.max_docs)

    for di in range(n_docs):
        doc = docs[di]
        ids = torch.tensor(doc.ids, dtype=torch.long)
        L = len(doc.ids)
        mask_t = {k: torch.tensor(v, dtype=torch.bool) for k, v in doc.masks.items()}
        doc_tot = {"nll": 0.0, "n": 0}
        doc_mask_tot = {k: [0, 0.0, 0] for k in mask_t}  # correct, nll, count
        first_loss = None

        for ci, start in enumerate(range(0, L - 1, rcfg.chunk)):
            end = min(start + rcfg.chunk, L)          # chunk = ids[start:end]
            cstart = max(0, start - rcfg.ctx_len)     # context prefix from same doc only
            x = ids[cstart:end].to(device)[None]      # [1, T]
            # positions inside x that predict chunk tokens: predict ids[t+1] for t in [start-1 .. end-2]
            # (the first chunk token is predicted from the last context token, if any)
            p0 = (start - cstart) - 1 if start > 0 else 0
            with torch.set_grad_enabled(not eval_only):
                out = model(input_ids=x, use_cache=False)
                logits = out.logits[0]                # [T, V]
                pred_logits = logits[p0:end - cstart - 1]          # predicts x[p0+1 : ]
                targets = x[0, p0 + 1:]
                loss = F.cross_entropy(pred_logits.float(), targets)

            # ---- prequential metrics on this chunk (before any write) ----
            with torch.no_grad():
                nll_sum = loss.item() * targets.numel()
                doc_tot["nll"] += nll_sum; doc_tot["n"] += targets.numel()
                tgt_abs = torch.arange(cstart + p0 + 1, end)       # absolute indices of targets
                rec = {"doc": di, "chunk": ci, "n": targets.numel(), "loss": loss.item()}
                for k, m in mask_t.items():
                    mm = m[tgt_abs].to(device)
                    c, nl, n = _acc_and_nll(pred_logits, targets, mm)
                    rec[f"{k}_correct"] = c; rec[f"{k}_nll"] = nl; rec[f"{k}_n"] = n
                    doc_mask_tot[k][0] += c; doc_mask_tot[k][1] += nl; doc_mask_tot[k][2] += n
                records.append(rec)
            if first_loss is None:
                first_loss = loss.item()

            # ---- write (apply-then-update) ----
            if not eval_only:
                fw.write_chunk(loss)
            del out, logits, loss

        fw.note_first_chunk_loss(first_loss if first_loss is not None else 0.0)
        bstats = fw.end_document() if not eval_only else {}
        summ = {"doc": di, "name": doc.name, "tokens": L,
                "ppl": math.exp(doc_tot["nll"] / max(1, doc_tot["n"])),
                "g_fast_norm_at_end": None, **{f"b_{k}": v for k, v in bstats.items()}, **doc.meta}
        for k, (c, nl, n) in doc_mask_tot.items():
            summ[f"{k}_acc"] = (c / n) if n else None
            summ[f"{k}_ppl"] = math.exp(nl / n) if n else None
            summ[f"{k}_n"] = n
        doc_summaries.append(summ)
        if (di + 1) % rcfg.log_every == 0:
            extra = " ".join(f"{k}_acc={summ[k+'_acc']:.3f}(n={summ[k+'_n']})" for k in mask_t if summ[k + "_acc"] is not None)
            print(f"[doc {di+1}/{n_docs}] {doc.name[:40]:40s} ppl={summ['ppl']:.2f} {extra} "
                  f"gslow={bstats.get('g_slow_norm', 0):.3f} t={time.time()-t0:.0f}s", flush=True)

    return {"records": records, "docs": doc_summaries}
