#!/usr/bin/env python3
"""Residual by cite tercile — does inference-required concentrate in the dead stratum?
R14 test. Also counts citing-context that plausibly states a foreclosure reason."""
import json
from pathlib import Path
import numpy as np

REASON_HINTS=("instab","degrad","poison","cost","expensive","difficult","not reproduc",
    "could not","limited","hinder","barrier","challeng","overpotential","dissolution",
    "leach","poor stability","scal","synthesi")

rows=json.loads(Path("./corpus_out/label_set_reconstructed.json").read_text())
cc=[r.get("cited_by_count",0) for r in rows]
terc=np.array_split(np.argsort(cc),3)
names=["LOW(dead)","MID","HIGH"]
for name,idx in zip(names,terc):
    grp=[rows[i] for i in idx]
    n=len(grp)
    inf=sum(r.get("inference_required") for r in grp)
    reason=0
    for r in grp:
        txt=" ".join(c.get("abstract","").lower() for c in r.get("citing_context",[]))
        if any(h in txt for h in REASON_HINTS): reason+=1
    print(f"{name:10} n={n:2} inference-required={inf}/{n} citing-states-reason={reason}/{n}")
print("\nR14 holds if inference-required concentrates in LOW stratum.")