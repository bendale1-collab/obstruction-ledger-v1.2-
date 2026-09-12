#!/usr/bin/env python3
"""Re-run H-K1-2 only: rebuild the identical fixture directory (7d4aad7 vs 51c2234)
and capture the FULL k1_2.py JSON output without truncation."""

import json, subprocess, sys
from pathlib import Path

REPO = Path("/Users/brukendale/ol-run/obstruction-ledger-v1.2")
K1A = REPO / "work" / "k1a"
FIXTURE = REPO / "work" / "k1a-holdout-H-K1-2-fixture"
OUT = REPO / "work" / "k1a-holdout-H-K1-2-full-2026-09-12.json"

def git_show(commit, path):
    r = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=REPO,
                       capture_output=True, text=True, timeout=30)
    return r.stdout if r.returncode == 0 else None

# Rebuild identical fixture: same construction as original H-K1-2 run
manifest_2 = git_show("7d4aad7", "MANIFEST.sha256")
assert manifest_2 is not None, "MANIFEST.sha256 not found at 7d4aad7"

seal_d = FIXTURE / "seal"
head_d = FIXTURE / "head"
seal_d.mkdir(parents=True, exist_ok=True)
head_d.mkdir(parents=True, exist_ok=True)

paths = []
for line in manifest_2.splitlines():
    line = line.strip()
    if line and not line.startswith("#"):
        parts = line.split(None, 1)
        if len(parts) >= 2:
            paths.append(parts[1])

(FIXTURE / "MANIFEST").write_text("\n".join(paths))

for p in paths:
    sc = git_show("7d4aad7", p)
    hc = git_show("51c2234", p)
    if sc is not None:
        f = seal_d / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(sc)
    if hc is not None:
        f = head_d / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(hc)

(head_d / "ledger").mkdir(exist_ok=True)
for lf in (REPO / "ledger").glob("*"):
    if lf.is_file():
        (head_d / "ledger" / lf.name).write_text(lf.read_text())

# Run k1_2.py, capture full stdout
r = subprocess.run([sys.executable, str(K1A / "k1_2.py"), str(FIXTURE)],
                   capture_output=True, text=True, timeout=60)

raw_stdout = r.stdout
Path(OUT).write_text(raw_stdout)

print(f"Written: {OUT}")
print(f"Exit code: {r.returncode}")
print(f"Bytes written: {len(raw_stdout)}")

try:
    data = json.loads(raw_stdout)
    print(f"Total entries: {len(data)}")
    not_same = [d for d in data if d.get("status") != "SAME"]
    print(f"status != SAME: {len(not_same)}")
    for d in not_same:
        print(f"  {json.dumps(d)}")
except Exception as e:
    print(f"JSON parse error: {e}")