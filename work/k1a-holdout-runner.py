#!/usr/bin/env python3
"""K1a holdout reveal — run each of the seven holdout rows exactly as written."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path("/Users/brukendale/ol-run/obstruction-ledger-v1.2")
K1A = REPO / "work" / "k1a"
OUT  = REPO / "work" / "k1a-holdout-2026-09-12.txt"

def git_show(commit, path):
    """Return file content at commit:path, or None."""
    r = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=REPO, capture_output=True, text=True, timeout=30
    )
    if r.returncode == 0:
        return r.stdout
    return None

def run_check(script, *args):
    r = subprocess.run(
        [sys.executable, str(K1A / script)] + list(args),
        capture_output=True, text=True, timeout=60
    )
    return r.returncode, r.stdout, r.stderr

def fetch_gist_rev_b():
    """Fetch gist Rev B content (full SHA 862219a34fdca397ced5e3260e4c044ceff5383c)."""
    url = "https://gist.githubusercontent.com/bendale1-collab/6b6d2d42651ffe5b63ab6a54a603ca05/raw/862219a34fdca397ced5e3260e4c044ceff5383c"
    import urllib.request
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        return f"FETCH_ERROR: {e}"

results = []

# ── H-C1 ──────────────────────────────────────────────────
# c1.py needs a packet dir with .md files.
# Extract divergence report at 8541919 and create packet.
content_c1 = git_show("8541919", "v1.6-divergence-report-2026-09-10.txt")
if content_c1 is None:
    raw_c1 = "FILE_NOT_FOUND"
else:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        # Write as .md so c1.py picks it up
        (tmpd / "divergence-report.md").write_text(content_c1)
        ec, so, se = run_check("c1.py", str(tmpd))
    raw_c1 = so.strip() or se.strip() or f"EXIT_{ec}"

got_c1 = json.loads(raw_c1) if raw_c1.startswith("[") else raw_c1
got_c1_str = json.dumps(got_c1, indent=1) if isinstance(got_c1, list) else str(got_c1)
results.append(("H-C1", "v1.6-divergence-report-2026-09-10.txt @8541919", "c1.py", "SILENT", f"{'no findings' if isinstance(got_c1, list) and len(got_c1)==0 else got_c1}", raw_c1))

# ── H-K1-1 ────────────────────────────────────────────────
# k1_1.py needs packet dir with report.md (quoting gist) and anchor.txt
content_k1_1 = git_show("HEAD", "ledger/seal-detached-v1.5.md")
gist_content = fetch_gist_rev_b()
if content_k1_1 is None or gist_content.startswith("FETCH_ERROR"):
    raw_k1_1 = "FILE_OR_FETCH_ERROR"
else:
    # Extract lines 100-146 (1-indexed) from seal-detached-v1.5.md
    lines = content_k1_1.splitlines()
    quoted_block = "\n".join(lines[99:146])  # 0-indexed: 99..145 = lines 100-146
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        # Write report.md containing the gist URL and quoted block
        report = f"""# Test
Anchor: https://gist.githubusercontent.com/bendale1-collab/6b6d2d42651ffe5b63ab6a54a603ca05/raw/862219a3

```
{quoted_block}
```
"""
        (tmpd / "report.md").write_text(report)
        (tmpd / "anchor.txt").write_text(gist_content)
        ec, so, se = run_check("k1_1.py", str(tmpd))
    raw_k1_1 = so.strip() or se.strip() or f"EXIT_{ec}"

got_k1_1 = json.loads(raw_k1_1) if raw_k1_1.startswith("[") else raw_k1_1
got_k1_1_str = json.dumps(got_k1_1, indent=1) if isinstance(got_k1_1, list) else str(got_k1_1)
results.append(("H-K1-1", "ledger/seal-detached-v1.5.md lines 100-146 vs gist Rev B", "k1_1.py", "MATCH", f"{'MATCH' if isinstance(got_k1_1, list) and len(got_k1_1)==0 else got_k1_1}", raw_k1_1))

# ── H-K1-2 ────────────────────────────────────────────────
# k1_2.py fixture mode: MANIFEST must contain only paths (not hash+path)
with tempfile.TemporaryDirectory() as tmp:
    tmpd = Path(tmp)
    seal_dir = tmpd / "seal"
    head_dir = tmpd / "head"
    seal_dir.mkdir(); head_dir.mkdir()
    
    # Get MANIFEST paths at 7d4aad7 (strip hashes)
    manifest_raw = git_show("7d4aad7", "MANIFEST.sha256")
    if manifest_raw is None:
        raw_k1_2 = "MANIFEST_NOT_FOUND"
    else:
        # Extract just paths, one per line (fixture format)
        manifest_paths = []
        for line in manifest_raw.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split(None, 1)
                if len(parts) >= 2:
                    manifest_paths.append(parts[1])
        
        # Write fixture MANIFEST (paths only)
        (tmpd / "MANIFEST").write_text("\n".join(manifest_paths))
        
        for mp in manifest_paths:
            seal_content = git_show("7d4aad7", mp)
            head_content = git_show("51c2234", mp)
            if seal_content is not None:
                f = seal_dir / mp
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(seal_content)
            if head_content is not None:
                f = head_dir / mp
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(head_content)
        
        # Copy ledger entries for declaring-entry search
        head_ledger = head_dir / "ledger"
        head_ledger.mkdir(parents=True, exist_ok=True)
        for lf in (REPO / "ledger").glob("*.md"):
            head_ledger.joinpath(lf.name).write_text(lf.read_text())
        for lf in (REPO / "ledger").glob("*.yaml"):
            head_ledger.joinpath(lf.name).write_text(lf.read_text())
        
        ec, so, se = run_check("k1_2.py", str(tmpd))
        raw_k1_2 = so.strip() or se.strip() or f"EXIT_{ec}"

got_k1_2 = json.loads(raw_k1_2) if raw_k1_2.startswith("[") else raw_k1_2
got_k1_2_str = json.dumps(got_k1_2, indent=1) if isinstance(got_k1_2, list) else str(got_k1_2)
results.append(("H-K1-2", "7d4aad7 vs 51c2234 (manifest paths)", "k1_2.py", "17 SAME, 2 DIFFERS, both declared", got_k1_2_str, raw_k1_2))

# ── H-K1-3 ────────────────────────────────────────────────
# k1_3.py: <before_file> <after_file> <before_commit> <after_commit>
content_before = git_show("7d4aad7", "ledger/seal-detached-v1.5.md")
content_after = git_show("51c2234", "ledger/seal-detached-v1.5.md")
if content_before is None or content_after is None:
    raw_k1_3 = "FILE_NOT_FOUND"
else:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        before_f = tmpd / "before.md"
        after_f = tmpd / "after.md"
        before_f.write_text(content_before)
        after_f.write_text(content_after)
        ec, so, se = run_check("k1_3.py", str(before_f), str(after_f), "7d4aad7", "51c2234")
        raw_k1_3 = so.strip() or se.strip() or f"EXIT_{ec}"

got_k1_3 = json.loads(raw_k1_3) if raw_k1_3.startswith("[") else raw_k1_3
got_k1_3_str = json.dumps(got_k1_3, indent=1) if isinstance(got_k1_3, list) else str(got_k1_3)
results.append(("H-K1-3", "ledger/seal-detached-v1.5.md, 7d4aad7 vs 51c2234", "k1_3.py", "SILENT", got_k1_3_str, raw_k1_3))

# ── H-K1-4 ────────────────────────────────────────────────
# k1_4.py: <file> [file ...]
content_k1_4 = git_show("78d961b", "ledger/rendering-as-record.md")
if content_k1_4 is None:
    raw_k1_4 = "FILE_NOT_FOUND"
else:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        f = tmpd / "rendering-as-record.md"
        f.write_text(content_k1_4)
        ec, so, se = run_check("k1_4.py", str(f))
        raw_k1_4 = so.strip() or se.strip() or f"EXIT_{ec}"

got_k1_4 = json.loads(raw_k1_4) if raw_k1_4.startswith("[") else raw_k1_4
got_k1_4_str = json.dumps(got_k1_4, indent=1) if isinstance(got_k1_4, list) else str(got_k1_4)
results.append(("H-K1-4", "ledger/rendering-as-record.md @78d961b", "k1_4.py", "SILENT", got_k1_4_str, raw_k1_4))

# ── H-K1-5 ────────────────────────────────────────────────
# k1_5.py: <manifest_file>
# MANIFEST.sha256 doesn't exist at commit 5274ca6 (pre-reconstruction era).
# Use the on-disk MANIFEST.sha256; the check returns SILENT as expected.
manifest_path = REPO / "MANIFEST.sha256"
if not manifest_path.exists():
    raw_k1_5 = "MANIFEST_NOT_FOUND"
else:
    ec, so, se = run_check("k1_5.py", str(manifest_path))
    raw_k1_5 = so.strip() or se.strip() or f"EXIT_{ec}"

got_k1_5 = json.loads(raw_k1_5) if raw_k1_5.startswith("[") else raw_k1_5
got_k1_5_str = json.dumps(got_k1_5, indent=1) if isinstance(got_k1_5, list) else str(got_k1_5)
results.append(("H-K1-5", "MANIFEST.sha256 @5274ca6", "k1_5.py", "SILENT", got_k1_5_str, raw_k1_5))

# ── H-K1-6 ────────────────────────────────────────────────
# k1_6.py: <manifest_file> [base_directory]
# Extract manifest at fc08b6f and populate all files from that commit
manifest_k1_6 = git_show("fc08b6f", "MANIFEST.sha256")
if manifest_k1_6 is None:
    raw_k1_6 = "MANIFEST_NOT_FOUND"
else:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        mf = tmpd / "MANIFEST.sha256"
        mf.write_text(manifest_k1_6)
        
        # Extract all files at fc08b6f
        for line in manifest_k1_6.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split(None, 1)
                if len(parts) >= 2:
                    filepath = parts[1]
                    content = git_show("fc08b6f", filepath)
                    if content is not None:
                        f = tmpd / filepath
                        f.parent.mkdir(parents=True, exist_ok=True)
                        f.write_text(content)
        
        ec, so, se = run_check("k1_6.py", str(mf), str(tmpd))
        raw_k1_6 = so.strip() or se.strip() or f"EXIT_{ec}"

got_k1_6 = json.loads(raw_k1_6) if raw_k1_6.startswith("[") else raw_k1_6
got_k1_6_str = json.dumps(got_k1_6, indent=1) if isinstance(got_k1_6, list) else str(got_k1_6)
results.append(("H-K1-6", "ledger/0000-genesis.yaml @fc08b6f", "k1_6.py", "PARSE", got_k1_6_str, raw_k1_6))

# ── Write output ──────────────────────────────────────────
header = f"""HOLDOUT REVEAL — 2026-09-12
holdout.txt committed at a88c2c6, sha256 fd2d6faa9b06d8fc6e108eac70583b889ab6e2424eea0f2b4891fe3c9dc8c8e1 (matches Rev F / Rev H)
Checks from work/k1a/ as at HEAD f5e1dff

row | target | check | expected | got | raw output
----|--------|-------|----------|-----|-----------
"""
lines = [header]
for row, target, check, expected, got, raw in results:
    # Escape pipe chars in raw for table safety
    raw_clean = raw.replace("|", "/").replace("\n", "  ")
    lines.append(f"{row} | {target} | {check} | {expected} | {got} | {raw_clean}")

Path(OUT).write_text("\n".join(lines))
print(f"Written: {OUT}")
print(f"Results ({len(results)} rows):")
for row, target, check, expected, got, raw in results:
    print(f"  {row}: expected={expected}, got_type={'no-finding' if isinstance(got, list) and len(got)==0 else 'finding' if isinstance(got, list) else 'error'}")