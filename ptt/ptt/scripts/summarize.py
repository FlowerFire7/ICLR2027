#!/usr/bin/env python
"""Summarise results/*.json into one table and (optionally) a per-repo curve.

  python scripts/summarize.py results/*.json
"""
import glob, json, sys
import numpy as np

rows = []
for f in sys.argv[1:] or sorted(glob.glob("results/*.json")):
    r = json.load(open(f)); c = r["config"]; s = r["summary"]
    D = r["docs"]
    # cross-file accuracy restricted to files with index >= 2 (first files of a repo have few xfile targets)
    late = [d for d in D if d.get("file_idx", 0) >= 2 and d.get("xfile_n", 0) > 0]
    xl = (sum(d["xfile_acc"] * d["xfile_n"] for d in late) / sum(d["xfile_n"] for d in late)) if late else float("nan")
    gb, ga = r.get("general_before"), r.get("general_after")
    dgen = (sum(ga.values()) / len(ga) - sum(gb.values()) / len(gb)) if (gb and ga) else float("nan")
    rt = r.get("retest_summary") or {}
    bwt = (rt["xfile_acc_end"] - rt["xfile_acc_stream"]) if rt.get("xfile_acc_end") is not None else float("nan")
    rows.append((c["policy"], c["eta"], c.get("gamma_eff"), s["xfile_acc"], s.get("xfile_ppl", float("nan")), s["xfile_n"],
                 s.get("xrep_acc"), s["local_acc"], s["geo_mean_doc_ppl"], dgen, bwt,
                 D[-1].get("b_g_slow_norm", 0.0), r.get("peak_mem_gb", 0), r["wall_s"] / 60, f))

rows.sort(key=lambda x: (x[0], x[1]))
hdr = (f"{'policy':12s} {'eta':>8s} {'gamma':>6s} {'xfile':>7s} {'xfilePPL':>9s} {'n':>6s} {'xrep':>7s} {'local':>7s} "
       f"{'docPPL':>8s} {'dGen':>7s} {'BWT_x':>7s} {'|Gslow|':>8s} {'GB':>5s} {'min':>6s}")
print(hdr); print("-" * len(hdr))
for p, e, g, xa, xp, xn, ra, la, ppl, dgen, bwt, gn, mem, mins, f in rows:
    print(f"{p:12s} {e:8.1e} {g if g is not None else 0:6.3f} {xa if xa else 0:7.3f} {xp if xp else 0:9.2f} {xn:6d} "
          f"{ra if ra else 0:7.3f} {la if la else 0:7.3f} {ppl:8.2f} {dgen:+7.3f} {bwt:+7.3f} {gn:8.3f} {mem:5.1f} {mins:6.1f}")
