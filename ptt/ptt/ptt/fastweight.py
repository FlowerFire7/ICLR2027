"""Persistent test-time training on MLP down-projections.

Design (see plan v2, §3):
  W_eff = W_base + G_slow + G_fast
  * G_fast : written every chunk by a clipped gradient step on the NTP loss of that chunk
  * G_slow : written only at document boundaries by a persistence policy
  * D      : cross-document direction EMA used by the consistency policy
  * F      : within-document EMA of grad^2 used by the fisher policy

Apply-then-update is enforced by the caller (`stream_runner`): the chunk is first scored
with the current W_eff (prequential evaluation), and only afterwards written into G_fast.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import torch
import torch.nn as nn


@dataclass
class FWConfig:
    eta: float = 1e-3          # inner-loop step size on the NTP gradient
    clip: float = 1e-3         # element-wise clip of a single write
    policy: str = "reset"      # reset | persist | decay | consistency | fisher | surprise | random
    gamma: float = 1.0         # decay of G_slow at each boundary (policy-dependent default)
    gamma_d: float = 0.9       # direction-EMA decay (consistency)
    fisher_beta: float = 0.99  # EMA for grad^2 (fisher)
    surprise_tau: float = 1.0  # temperature for surprise gate
    g_slow_max: Optional[float] = None  # optional Frobenius cap per layer
    alpha_norm: bool = False   # normalise gate to mean 1 at each boundary -> same write budget as persist
    project_k: int = 0         # >0: project writes orthogonal to the top-k activation subspace of PAST sessions (GPM-style)
    project_energy: float = 0.95  # or keep as many directions as needed for this fraction of energy (<= project_k)
    layer_subset: Optional[List[int]] = None  # None = all layers
    dtype: torch.dtype = torch.bfloat16
    seed: int = 0


def _find_down_projs(model: nn.Module) -> List[nn.Module]:
    """Return MLP down-projection modules for Qwen/Llama (down_proj) or GPT-2 (mlp.c_proj)."""
    mods = []
    for name, m in model.named_modules():
        if name.endswith("mlp.down_proj") or name.endswith("mlp.c_proj"):
            mods.append(m)
    if not mods:
        raise RuntimeError("No MLP down-projection modules found (expected *.mlp.down_proj or *.mlp.c_proj)")
    return mods


class FastWeightManager:
    """Owns the fast-weight state for every selected down-projection layer."""

    def __init__(self, model: nn.Module, cfg: FWConfig):
        self.model = model
        self.cfg = cfg
        self.gen = torch.Generator(device="cpu").manual_seed(cfg.seed)
        self._gen_dev = None

        all_mods = _find_down_projs(model)
        idx = cfg.layer_subset if cfg.layer_subset is not None else list(range(len(all_mods)))
        self.layers: List[nn.Module] = [all_mods[i] for i in idx]
        self.layer_idx = idx

        # freeze everything, then enable grad only on the selected down-proj weights
        for p in model.parameters():
            p.requires_grad_(False)
        self.params: List[nn.Parameter] = []
        for m in self.layers:
            m.weight.requires_grad_(True)
            self.params.append(m.weight)

        dev = self.params[0].device
        self.W_base = [p.detach().clone().to(cfg.dtype) for p in self.params]
        self.G_fast = [torch.zeros_like(w) for w in self.W_base]
        self.G_slow = [torch.zeros_like(w) for w in self.W_base]
        self.D = [torch.zeros_like(w) for w in self.W_base] if cfg.policy == "consistency" else None
        self.F = [torch.zeros_like(w) for w in self.W_base] if cfg.policy == "fisher" else None
        # random policy needs a reference sparsity pattern; we derive it from an internal direction EMA
        self.D_ref = [torch.zeros_like(w) for w in self.W_base] if cfg.policy == "random" else None

        # GPM-style projection state
        self.in_axis = [1 if isinstance(m, nn.Linear) else 0 for m in self.layers]  # weight axis that multiplies the input
        self.cov = [None] * len(self.layers)   # running d_ff x d_ff activation covariance of the current session
        self.U = [None] * len(self.layers)     # d_ff x k orthonormal basis of past sessions' activations
        self._hooks = []
        if cfg.project_k > 0:
            for i, m in enumerate(self.layers):
                self._hooks.append(m.register_forward_hook(self._make_cov_hook(i)))
        self._collect = True
        self.doc_count = 0
        self.loss_running: Optional[float] = None  # running mean of first-chunk loss (surprise)
        self.last_doc_first_loss: Optional[float] = None
        self.stats: Dict[str, float] = {}

    def _make_cov_hook(self, i):
        def hook(mod, inp, out):
            if not self._collect:
                return
            x = inp[0].detach().float().reshape(-1, inp[0].shape[-1])   # [T, d_ff]
            c = x.T @ x
            self.cov[i] = c if self.cov[i] is None else self.cov[i] + c
        return hook

    @torch.no_grad()
    def _project(self, i: int, delta: torch.Tensor) -> torch.Tensor:
        U = self.U[i]
        if U is None:
            return delta
        if self.in_axis[i] == 1:      # nn.Linear: delta [out, in]
            return delta - (delta.float() @ U) @ U.T
        return delta - U @ (U.T @ delta.float())   # Conv1D: delta [in, out]

    @torch.no_grad()
    def end_session(self):
        """Session (e.g. repo) boundary: fold this session's activation covariance into the protected basis."""
        cfg = self.cfg
        if cfg.project_k > 0:
            for i in range(len(self.layers)):
                if self.cov[i] is None:
                    continue
                C = self.cov[i]
                if self.U[i] is not None:  # remove already-protected part (as in GPM)
                    U = self.U[i]
                    C = C - U @ (U.T @ C) - (C @ U) @ U.T + U @ (U.T @ C @ U) @ U.T
                evals, evecs = torch.linalg.eigh(C)
                evals, evecs = evals.flip(0), evecs.flip(1)
                tot = evals.clamp_min(0).sum() + 1e-12
                k = int((evals.clamp_min(0).cumsum(0) / tot < cfg.project_energy).sum().item()) + 1
                k = min(k, cfg.project_k)
                Unew = evecs[:, :k]
                self.U[i] = Unew if self.U[i] is None else torch.linalg.qr(torch.cat([self.U[i], Unew], 1))[0]
                if self.U[i].shape[1] > cfg.project_k * 8:   # hard cap on basis size
                    self.U[i] = self.U[i][:, : cfg.project_k * 8]
                self.cov[i] = None
        if cfg.policy == "session":
            for gs in self.G_slow:
                gs.zero_()
            self.materialize()

    def basis_size(self) -> float:
        return sum(0 if u is None else u.shape[1] for u in self.U) / len(self.U)

    def _maybe_norm(self, alpha: torch.Tensor) -> torch.Tensor:
        if self.cfg.alpha_norm:
            m = alpha.float().mean().clamp_min(1e-8)
            alpha = (alpha.float() / m).clamp_max(4.0).to(alpha.dtype)  # cap to avoid huge single writes
        return alpha

    # ------------------------------------------------------------------ apply
    @torch.no_grad()
    def materialize(self):
        """Write W_eff = W_base + G_slow + G_fast into the live parameters."""
        for p, wb, gs, gf in zip(self.params, self.W_base, self.G_slow, self.G_fast):
            p.data.copy_((wb + gs + gf).to(p.dtype))

    # ----------------------------------------------------------------- update
    def write_chunk(self, loss: torch.Tensor):
        """One inner-loop write into G_fast from the NTP loss of the *current* chunk.

        Must be called AFTER the chunk has been scored for evaluation (apply-then-update).
        """
        grads = torch.autograd.grad(loss, self.params, allow_unused=False)
        with torch.no_grad():
            for i, g in enumerate(grads):
                g = g.to(self.cfg.dtype)
                delta = (-self.cfg.eta * g).clamp_(-self.cfg.clip, self.cfg.clip)
                if self.cfg.project_k > 0:
                    delta = self._project(i, delta).to(self.cfg.dtype)
                self.G_fast[i].add_(delta)
                if self.F is not None:
                    self.F[i].mul_(self.cfg.fisher_beta).add_((1 - self.cfg.fisher_beta) * g.float().pow(2).to(self.cfg.dtype))
        self.materialize()

    # --------------------------------------------------------------- boundary
    @torch.no_grad()
    def end_document(self):
        """Apply the persistence policy at a document boundary, then reset G_fast."""
        cfg = self.cfg
        pol = cfg.policy
        self.doc_count += 1
        alpha_mean = 0.0

        if pol == "reset":
            pass  # G_slow untouched (stays zero)
        elif pol in ("persist", "session"):
            for gs, gf in zip(self.G_slow, self.G_fast):
                gs.add_(gf)
        elif pol == "decay":
            for gs, gf in zip(self.G_slow, self.G_fast):
                gs.mul_(cfg.gamma).add_(gf)
        elif pol == "consistency":
            tot = 0.0
            for gs, gf, d in zip(self.G_slow, self.G_fast, self.D):
                d.mul_(cfg.gamma_d).add_((1 - cfg.gamma_d) * torch.sign(gf))
                if self.doc_count > 1:  # first document: only update D (zero-write warm-up)
                    alpha = self._maybe_norm(d.abs())
                    gs.mul_(cfg.gamma).add_(alpha * gf)
                    tot += alpha.float().mean().item()
            alpha_mean = tot / len(self.G_slow)
        elif pol == "fisher":
            tot = 0.0
            for gs, gf, f in zip(self.G_slow, self.G_fast, self.F):
                # importance-gated: alpha = 1/(1 + F/median(F)); median-relative so the gate actually varies
                fr = f.float()
                med = fr.median() + 1e-20
                alpha = (1.0 / (1.0 + fr / med)).to(cfg.dtype)
                alpha = self._maybe_norm(alpha)
                gs.mul_(cfg.gamma).add_(alpha * gf)
                tot += alpha.float().mean().item()
                f.zero_()
            alpha_mean = tot / len(self.G_slow)
        elif pol == "surprise":
            # scalar gate from how surprising this document was relative to the running mean
            s = self.last_doc_first_loss if self.last_doc_first_loss is not None else 0.0
            if self.loss_running is None:
                self.loss_running = s
            z = (s - self.loss_running) / cfg.surprise_tau
            alpha_s = float(torch.sigmoid(torch.tensor(z)))
            self.loss_running = 0.9 * self.loss_running + 0.1 * s
            for gs, gf in zip(self.G_slow, self.G_fast):
                gs.mul_(cfg.gamma).add_(alpha_s * gf)
            alpha_mean = alpha_s
        elif pol == "random":
            tot = 0.0
            for gs, gf, d in zip(self.G_slow, self.G_fast, self.D_ref):
                d.mul_(cfg.gamma_d).add_((1 - cfg.gamma_d) * torch.sign(gf))
                if self.doc_count > 1:
                    # same histogram as the consistency gate, randomly permuted -> control condition
                    flat = d.abs().flatten()
                    if self._gen_dev is None or self._gen_dev.device != flat.device:
                        self._gen_dev = torch.Generator(device=flat.device)
                        self._gen_dev.manual_seed(self.cfg.seed + 7919)
                    # GPU-side permutation via argsort of random keys (CPU randperm on 1e7 elements was ~100x slower)
                    perm = torch.argsort(torch.rand(flat.numel(), device=flat.device, generator=self._gen_dev))
                    alpha = self._maybe_norm(flat[perm].view_as(d))
                    gs.mul_(cfg.gamma).add_(alpha * gf)
                    tot += alpha.float().mean().item()
            alpha_mean = tot / len(self.G_slow)
        else:
            raise ValueError(f"unknown policy {pol}")

        if cfg.g_slow_max is not None:
            for gs in self.G_slow:
                n = gs.float().norm()
                if n > cfg.g_slow_max:
                    gs.mul_(cfg.g_slow_max / n)

        for gf in self.G_fast:
            gf.zero_()
        self.materialize()

        self.stats = {
            "doc": self.doc_count,
            "alpha_mean": alpha_mean,
            "g_slow_norm": sum(g.float().norm().item() for g in self.G_slow) / len(self.G_slow),
        }
        return self.stats

    # --------------------------------------------------------------- helpers
    def note_first_chunk_loss(self, loss_value: float):
        self.last_doc_first_loss = loss_value

    @torch.no_grad()
    def g_fast_norm(self) -> float:
        return sum(g.float().norm().item() for g in self.G_fast) / len(self.G_fast)

    @torch.no_grad()
    def snapshot(self) -> List[torch.Tensor]:
        """Cheap fingerprint of the live effective weights (for causality tests)."""
        return [p.detach().float().sum().item() for p in self.params]

    @torch.no_grad()
    def reset_all(self):
        for gf, gs in zip(self.G_fast, self.G_slow):
            gf.zero_(); gs.zero_()
        self.materialize()
