#!/usr/bin/env python3
"""
Sample 50 from C_ids (the 525) for hand-labeling. Stratified by cited_by_count so the
label set spans the decline range, not just the deadest tail. Agent samples + fetches
metadata; HUMAN assigns foreclosure labels (truth layer, non-delegable).

  python sample_label_set.py --cids ./corpus_out/C_ids.json --n 50 --out ./corpus_out
"""
import argparse, json, sys, time, traceback, urllib.request, urllib.parse
from pathlib import Path
import numpy as np

OPENALEX = "https://api.openalex.org/works"

def log(m): print(f"[sample] {m}", flush=True)
def get_json(url, tries=3):
    last=None
    for i in range(tries):
        try:
            req=urllib.request.Request(url, headers={"User-Agent":"orphan-gate/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read().decode())
        except Exception as e: last=str(e); time.sleep(2**i)
    raise RuntimeError(f"GET failed {tries}x: {url} :: {last}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cids", required=True)
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="./corpus_out")
    a=ap.parse_args()
    out=Path(a.out); out.mkdir(parents=True, exist_ok=True)
    try:
        ids=json.loads(Path(a.cids).read_text())
        if len(ids) < a.n: raise RuntimeError(f"Only {len(ids)} IDs; need {a.n}. Halt.")

        meta=[]
        for i in range(0, len(ids), 50):
            batch="|".join(x.split("/")[-1] for x in ids[i:i+50])
            q=urllib.parse.urlencode({"filter":f"ids.openalex:{batch}","per-page":50,
                                      "select":"id,title,publication_year,cited_by_count,doi"})
            meta.extend(get_json(f"{OPENALEX}?{q}").get("results",[]))
        rng=np.random.default_rng(a.seed)
        meta.sort(key=lambda w: w.get("cited_by_count",0))
        terciles=np.array_split(meta, 3)
        per=a.n//3; rem=a.n%3
        picks=[]
        for idx_t,t in enumerate(terciles):
            extra=1 if idx_t<rem else 0
            n_take=min(per+extra, len(t))
            j=rng.choice(len(t), size=n_take, replace=False)
            picks.extend(t[int(jj)] for jj in j)
        picks=picks[:a.n]

        rows=[{"openalex_id":w["id"],"title":w.get("title"),"year":w.get("publication_year"),
               "cited_by_count":w.get("cited_by_count"),"doi":w.get("doi"),
               "label_foreclosure_reason":"", "label_barrier_dissolved":"",
               "label_mace_verifiable":""} for w in picks]
        (out/"label_set.json").write_text(json.dumps(rows, indent=2))
        log(f"wrote {len(rows)} to label_set.json — HUMAN fills the three label_* fields.")
    except Exception:
        (out/"SAMPLE_ERROR.txt").write_text(traceback.format_exc()); sys.exit(2)

if __name__=="__main__":
    main()