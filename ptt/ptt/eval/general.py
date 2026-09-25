"""General-capability retention: run lm-eval-harness on the *live* model (W_eff materialised).

Call before the stream and after it with identical `tasks`, `num_fewshot`, `limit`, and seed.
Requires `pip install lm-eval>=0.4.5`.
"""
from typing import Dict, List


def eval_general(model, tokenizer, tasks: List[str] = ("hellaswag", "arc_easy"), num_fewshot: int = 0,
                 limit: int = 500, batch_size: int = 8, device: str = "cuda") -> Dict[str, float]:
    import lm_eval
    from lm_eval.models.huggingface import HFLM
    lm = HFLM(pretrained=model, tokenizer=tokenizer, batch_size=batch_size, device=device)
    res = lm_eval.simple_evaluate(model=lm, tasks=list(tasks), num_fewshot=num_fewshot, limit=limit,
                                  random_seed=0, numpy_random_seed=0, torch_random_seed=0, fewshot_random_seed=0)
    out = {}
    for t, r in res["results"].items():
        for k in ("acc_norm,none", "acc,none"):
            if k in r:
                out[t] = float(r[k]); break
        # record both scoring rules to separate real capability shifts from length-normalization drift
        if "acc,none" in r:
            out[f"{t}__acc"] = float(r["acc,none"])
        if "acc_norm,none" in r:
            out[f"{t}__acc_norm"] = float(r["acc_norm,none"])
    return out
