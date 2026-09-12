#!/usr/bin/env python3
"""
T3b harness — measures whether adjudicators DECORRELATE on foreclosure judgment.
5 lineage-diverse models (Claude, Gemini, DeepSeek, Mistral, Llama) via OpenRouter.
Emits per-work draft labels, split flag, and error-correlation N_eff if truth supplied.

OpenRouter key: reads from OPENROUTER_API_KEY env var, falls back to
~/.hermes/profiles/*/cache/.or_key_tmp

  python t3b_openrouter.py --labelset ./corpus_out/label_set_reconstructed.json \
      --truth ./corpus_out/truth20.json --out ./corpus_out
"""
import argparse, json, os, sys, time, traceback, urllib.request
from pathlib import Path
import numpy as np

OR="https://openrouter.ai/api/v1/chat/completions"
# WARNING: OpenRouter model names change over time. Run GET /api/v1/models to list current IDs.
# Current as of July 2026:
MODELS=[
    "anthropic/claude-sonnet-5",
    "deepseek/deepseek-chat",
    "mistralai/mistral-large",
]

PROMPT="""You are judging why a catalysis paper was abandoned by the field.
Given the paper and abstracts of works that cite it, answer STRICT JSON:
{{"barrier": one of ["synthesis","cost","dft_intractable","characterization","stability","none_apparent"],
 "barrier_dissolved_since": one of ["yes","no","unknown"],
 "confidence": 0.0-1.0}}
No prose. Paper: {title} ({year}). Citing context: {ctx}"""

def call(model, content, key, tries=3):
    body=json.dumps({"model":model,"messages":[{"role":"user","content":content}],
                     "temperature":0,"max_tokens":200}).encode()
    for i in range(tries):
        try:
            req=urllib.request.Request(OR, data=body, headers={
                "Authorization":f"Bearer {key}","Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                txt=json.loads(r.read())["choices"][0]["message"]["content"]
                return json.loads(txt.strip().strip("`").replace("json",""))
        except Exception: time.sleep(2**i)
    return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--labelset", required=True); ap.add_argument("--truth", default=None)
    ap.add_argument("--out", default="./corpus_out")
    a=ap.parse_args(); out=Path(a.out); out.mkdir(parents=True, exist_ok=True)
    key=os.environ.get("OPENROUTER_API_KEY")
    if not key:
        keypath=Path(os.path.expanduser("~/.hermes/profiles/mahamara/cache/.or_key_tmp"))
        if keypath.exists():
            key=keypath.read_text().strip()
    if not key: print("OPENROUTER_API_KEY unset. Halt."); sys.exit(2)
    try:
        rows=json.loads(Path(a.labelset).read_text())
        truth=json.loads(Path(a.truth).read_text()) if a.truth else {}

        drafts=[]; corr_rows=[]
        for idx, r in enumerate(rows):
            ctx=" || ".join(c.get("abstract","")[:300] for c in r.get("citing_context",[]))[:2000]
            content=PROMPT.format(title=r.get("title"), year=r.get("year"), ctx=ctx)
            per={}
            for m in MODELS:
                lab=call(m, content, key)
                if lab: per[m]=lab
            barriers=[v.get("barrier") for v in per.values()]
            print(f"  [{idx+1}/{len(rows)}] {r['openalex_id'].split('/')[-1]}: {len(per)} models responded", flush=True)
            # checkpoint after each work
            Path(out/"drafts_checkpoint.json").write_text(json.dumps(drafts, indent=2))
            split=len(set(barriers))>1
            drafts.append({"id":r["openalex_id"],"per_model":per,"split":split})

            tid=r["openalex_id"]
            if tid in truth and len(per)==len(MODELS):
                gt=truth[tid].get("barrier")
                corr_rows.append([1 if per[m].get("barrier")==gt else 0 for m in MODELS])
            time.sleep(0.3)

        Path(out/"drafts.json").write_text(json.dumps(drafts,indent=2))
        n_split=sum(d["split"] for d in drafts)
        print(f"drafts: {len(drafts)} | split: {n_split} ({n_split/len(drafts):.0%})")

        if len(corr_rows)>=20:
            E=np.array(corr_rows); err=1-E; err=err-err.mean(0,keepdims=True)
            nrm=np.linalg.norm(err,axis=0,keepdims=True)+1e-12; En=err/nrm
            C=En.T@En; M=len(MODELS); iu=np.triu_indices(M,1)
            rho=float(C[iu].mean()); neff=M/(1+(M-1)*max(0,rho))
            print(f"\n>>> T3b: mean err-corr={rho:+.3f} N_eff={neff:.2f}/{M}")
        else:
            print(f"\nT3b SKIPPED: {len(corr_rows)} truth-labeled; need >=20.")
    except Exception:
        Path(out/"T3B_ERROR.txt").write_text(traceback.format_exc()); sys.exit(2)

if __name__=="__main__":
    main()