#!/usr/bin/env python
"""Fetch a larger, less-famous set of Python repos via the GitHub search API (no token needed, ~10 req/min).
Targets mid-popularity repos (100-1500 stars) created recently, which are both less likely to be memorised
and, together with identifier obfuscation, give a clean cross-file recall test.

  python scripts/fetch_repos.py --n 50 --out repos50
"""
import argparse, json, os, subprocess, time, urllib.parse, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=50)
ap.add_argument("--out", default="repos50")
ap.add_argument("--min_stars", type=int, default=100)
ap.add_argument("--max_stars", type=int, default=1500)
ap.add_argument("--created_after", default="2025-06-01")
ap.add_argument("--max_kb", type=int, default=20000)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
got, page = 0, 1
while got < args.n and page <= 10:
    q = f"language:python stars:{args.min_stars}..{args.max_stars} created:>{args.created_after} size:<{args.max_kb} license:mit"
    url = "https://api.github.com/search/repositories?q=" + urllib.parse.quote(q) + f"&sort=stars&order=desc&per_page=30&page={page}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "ptt"})
    items = json.load(urllib.request.urlopen(req))["items"]
    for it in items:
        if got >= args.n: break
        name = it["full_name"].replace("/", "__")
        dst = os.path.join(args.out, name)
        if os.path.isdir(dst): got += 1; continue
        r = subprocess.run(["git", "clone", "--depth", "1", "-q", it["clone_url"], dst])
        if r.returncode == 0: got += 1; print(got, it["full_name"], it["stargazers_count"], flush=True)
    page += 1; time.sleep(7)
print("done", got)
