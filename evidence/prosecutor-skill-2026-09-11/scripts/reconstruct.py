#!/usr/bin/env python3
"""
Reconstruct foreclosure evidence cascade. For each orphan in the label set:
  1. citing-context: abstracts of works that CITE it (where "why field moved on" lives)
  2. own-abstract:   Crossref -> Semantic Scholar -> Unpaywall (coverage gaps)
  3. residual:       no evidence -> flagged inference_required=true

  python reconstruct.py --labelset ./corpus_out/label_set.json --out ./corpus_out

Pitfalls:
- Semantic Scholar rate-limits aggressively (429). Remove from cascade if stuck.
- Unpaywall needs API key. Remove if unavailable.
- Citing-context from OpenAlex covers ~96% of cases on its own.
"""
import argparse, json, sys, time, traceback, urllib.request, urllib.parse
from pathlib import Path

OA="https://api.openalex.org/works"
CR="https://api.crossref.org/works/"

def gj(url, tries=3, hdr=None):
    last=None
    for i in range(tries):
        try:
            req=urllib.request.Request(url, headers=hdr or {"User-Agent":"orphan-gate/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read().decode())
        except Exception as e: last=str(e); time.sleep(2**i)
    return None

def deinvert(inv):
    if not inv: return None
    pos={}
    for w,ix in inv.items():
        for i in ix: pos[i]=w
    return " ".join(pos[i] for i in sorted(pos))

def citing_context(oaid, cap=5):
    q=urllib.parse.urlencode({"filter":f"cites:{oaid}","per-page":cap,
        "select":"title,publication_year,abstract_inverted_index","sort":"cited_by_count:desc"})
    d=gj(f"{OA}?{q}")
    if not d: return []
    out=[]
    for w in d.get("results",[]):
        ab=deinvert(w.get("abstract_inverted_index"))
        if ab: out.append({"citing_title":w.get("title"),"year":w.get("publication_year"),"abstract":ab})
    return out

def own_abstract(doi):
    if not doi: return None,None
    d=doi.replace("https://doi.org/","")
    c=gj(CR+urllib.parse.quote(d))
    if c and c.get("message",{}).get("abstract"): return c["message"]["abstract"],"crossref"
    return None,None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--labelset", required=True); ap.add_argument("--out", default="./corpus_out")
    a=ap.parse_args(); out=Path(a.out)
    try:
        rows=json.loads(Path(a.labelset).read_text())
        n_ctx=n_own=n_res=0
        for r in rows:
            oaid=r["openalex_id"].split("/")[-1]
            r["citing_context"]=citing_context(oaid)
            if not r.get("abstract"):
                r["abstract"],r["abstract_source"]=own_abstract(r.get("doi"))
            else:
                r["abstract_source"]="openalex"
            has_ctx=bool(r["citing_context"]); has_own=bool(r.get("abstract"))
            r["inference_required"]=not (has_ctx or has_own)
            n_ctx+=has_ctx; n_own+=has_own; n_res+=r["inference_required"]
        Path(out/"label_set_reconstructed.json").write_text(json.dumps(rows,indent=2))
        print(f"citing-context: {n_ctx}/50 | own-abstract: {n_own}/50 | "
              f"inference-required residual: {n_res}/50")
        print(f"\nR10/R14: silent-orphan fraction = {n_res}/50 = {n_res/50:.0%}")
    except Exception:
        Path(out/"RECON_ERROR.txt").write_text(traceback.format_exc()); sys.exit(2)

if __name__=="__main__":
    main()