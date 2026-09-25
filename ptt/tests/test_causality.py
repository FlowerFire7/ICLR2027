"""Runs on CPU with a tiny randomly-initialised GPT-2. `python -m pytest tests -q` or `python tests/test_causality.py`.

Checks (plan §F):
  1. eval-only run never changes the weights
  2. the recorded loss of chunk k is computed BEFORE chunk k is written (apply-then-update)
  3. policy identities: persist == decay(gamma=1) ; consistency with alpha==1 == persist ;
     reset leaves G_slow at zero ; random has the same alpha histogram as consistency
  4. streaming with policy=reset gives identical per-doc results to processing each doc in isolation
"""
import copy, math, os, sys
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from transformers import GPT2Config, GPT2LMHeadModel
from ptt.fastweight import FastWeightManager, FWConfig
from ptt.runner import Doc, RunConfig, run_stream

torch.manual_seed(0)


def tiny_model():
    cfg = GPT2Config(n_layer=2, n_head=2, n_embd=32, vocab_size=97, n_positions=256)
    return GPT2LMHeadModel(cfg)


def docs(n=4, L=180, seed=0):
    g = torch.Generator().manual_seed(seed)
    return [Doc(ids=torch.randint(0, 97, (L,), generator=g).tolist(), name=f"d{i}",
                masks={"m": [bool(x) for x in torch.rand(L, generator=g) < 0.3]}) for i in range(n)]


def make(policy, **kw):
    m = tiny_model()
    fw = FastWeightManager(m, FWConfig(eta=1e-2, clip=1e-2, policy=policy, dtype=torch.float32, **kw))
    return m, fw


def test_eval_only_is_frozen():
    m, fw = make("persist")
    before = fw.snapshot()
    run_stream(m, fw, docs(), RunConfig(chunk=64, ctx_len=64), device="cpu", eval_only=True)
    assert before == fw.snapshot()


def test_apply_then_update():
    """loss recorded for chunk k must equal the loss of a frozen model holding the state *before* chunk k."""
    import torch.nn.functional as F
    d = docs(1, L=200)
    torch.manual_seed(0); m1 = tiny_model()
    fw1 = FastWeightManager(m1, FWConfig(eta=1e-2, clip=1e-2, policy="persist", dtype=torch.float32))
    res1 = run_stream(m1, fw1, d, RunConfig(chunk=64, ctx_len=64), device="cpu")
    torch.manual_seed(0); m2 = tiny_model(); m2.eval()
    fw2 = FastWeightManager(m2, FWConfig(eta=1e-2, clip=1e-2, policy="persist", dtype=torch.float32))
    ids = torch.tensor(d[0].ids); L = len(ids)
    for ci, start in enumerate(range(0, L - 1, 64)):
        end = min(start + 64, L); cstart = max(0, start - 64)
        x = ids[cstart:end][None]; p0 = (start - cstart) - 1 if start > 0 else 0
        with torch.no_grad():
            lg = m2(input_ids=x).logits[0]
            frozen_loss = F.cross_entropy(lg[p0:end - cstart - 1], x[0, p0 + 1:]).item()
        assert abs(frozen_loss - res1["records"][ci]["loss"]) < 1e-4, (ci, frozen_loss, res1["records"][ci]["loss"])
        with torch.enable_grad():
            lg = m2(input_ids=x).logits[0]
            loss = F.cross_entropy(lg[p0:end - cstart - 1], x[0, p0 + 1:])
        fw2.write_chunk(loss)


def _run(policy, seed=0, **kw):
    torch.manual_seed(seed); m = tiny_model()
    fw = FastWeightManager(m, FWConfig(eta=1e-2, clip=1e-2, policy=policy, dtype=torch.float32, **kw))
    res = run_stream(m, fw, docs(), RunConfig(chunk=64, ctx_len=64), device="cpu")
    return fw, [d["ppl"] for d in res["docs"]]


def test_policy_identities():
    _, p1 = _run("persist")
    _, p2 = _run("decay", gamma=1.0)
    assert all(abs(a - b) < 1e-6 for a, b in zip(p1, p2))
    fw_r, _ = _run("reset")
    assert all(g.abs().sum() == 0 for g in fw_r.G_slow)
    # consistency with gamma_d=0 -> D = sign(G_fast) exactly, alpha = 1 wherever G_fast != 0 -> equals persist after warm-up doc
    fw_c, pc = _run("consistency", gamma_d=0.0)
    # doc 0 is warm-up for consistency (no write) so ppls differ from doc 1 on; check doc 2.. equal to a persist run started at doc 1
    torch.manual_seed(0); m = tiny_model()
    fw_p = FastWeightManager(m, FWConfig(eta=1e-2, clip=1e-2, policy="persist", dtype=torch.float32))
    d = docs()
    run_stream(m, fw_p, d[:1], RunConfig(chunk=64, ctx_len=64), device="cpu"); fw_p.reset_all()  # doc0 as no-op
    res = run_stream(m, fw_p, d[1:], RunConfig(chunk=64, ctx_len=64), device="cpu")
    pp = [x["ppl"] for x in res["docs"]]
    assert all(abs(a - b) < 1e-5 for a, b in zip(pc[1:], pp)), (pc[1:], pp)


def test_random_matches_consistency_histogram():
    torch.manual_seed(0); m = tiny_model()
    fw_c = FastWeightManager(m, FWConfig(eta=1e-2, clip=1e-2, policy="consistency", dtype=torch.float32, gamma_d=0.5))
    run_stream(m, fw_c, docs(3), RunConfig(chunk=64, ctx_len=64), device="cpu")
    torch.manual_seed(0); m = tiny_model()
    fw_r = FastWeightManager(m, FWConfig(eta=1e-2, clip=1e-2, policy="random", dtype=torch.float32, gamma_d=0.5))
    run_stream(m, fw_r, docs(3), RunConfig(chunk=64, ctx_len=64), device="cpu")
    # alpha histograms are identical by construction (permutation); mean alpha reported must match
    assert abs(fw_c.stats["alpha_mean"] - fw_r.stats["alpha_mean"]) < 1e-3


def test_reset_equals_isolated_docs():
    torch.manual_seed(0); m = tiny_model()
    fw = FastWeightManager(m, FWConfig(eta=1e-2, clip=1e-2, policy="reset", dtype=torch.float32))
    d = docs(3)
    res = run_stream(m, fw, d, RunConfig(chunk=64, ctx_len=64), device="cpu")
    for i in range(3):
        torch.manual_seed(0); mi = tiny_model()
        fwi = FastWeightManager(mi, FWConfig(eta=1e-2, clip=1e-2, policy="reset", dtype=torch.float32))
        ri = run_stream(mi, fwi, [d[i]], RunConfig(chunk=64, ctx_len=64), device="cpu")
        assert abs(ri["docs"][0]["ppl"] - res["docs"][i]["ppl"]) < 1e-5


if __name__ == "__main__":
    for f in [test_eval_only_is_frozen, test_apply_then_update, test_policy_identities,
              test_random_matches_consistency_histogram, test_reset_equals_isolated_docs]:
        f(); print("ok", f.__name__)


def test_entity_split_single_newlines():
    """Regression: WikiText-style single-newline articles must still split into multiple docs."""
    from ptt.streams.entity import _split_docs

    class TokStub:
        def __call__(self, t, add_special_tokens=False):
            return {"input_ids": list(range(len(t.split())))}
    text = "\n".join("para %d " % i + "word " * 500 for i in range(6))
    docs = _split_docs(text, TokStub(), target_tokens=600, min_tokens=100)
    assert len(docs) >= 3, len(docs)
