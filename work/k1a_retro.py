#!/usr/bin/env python3
"""K1a retrodiction runner. Runs the sealed rows R1-R14 (checker-k1-prereg.md §3)
and RA-1..RA-5 (checker-k1a-prereg.md §3.3) against real commits in this repo.
Expected outcomes are copied from the sealed documents; nothing is decided here.
Emits JSON + a table. Adjudication is the founder's.
Author: Claude. Fixture author for c1/k1-1/k1-2; no check code authored.
"""
import json, re, subprocess, sys, tempfile, shutil, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
K = ROOT/"work/k1a"
PY = sys.executable
rows = []

def sh(cmd, cwd=ROOT, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=120, **kw)

def check(name, *args):
    r = sh([PY, str(K/name), *[str(a) for a in args]])
    try: out = json.loads(r.stdout) if r.stdout.strip() else []
    except json.JSONDecodeError: out = [{"error":"non-json","stdout":r.stdout[:300],"stderr":r.stderr[:300]}]
    return out, r.returncode

def export(commit, paths, dest):
    """Materialize paths at a commit into dest. Returns list of written paths."""
    written=[]
    for p in paths:
        r = sh(["git","show",f"{commit}:{p}"])
        if r.returncode: continue
        t = dest/p; t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(r.stdout); written.append(p)
    return written

def manifest_paths(commit):
    r = sh(["git","show",f"{commit}:MANIFEST.sha256"])
    return [l.split(None,1)[1].strip() for l in r.stdout.splitlines() if l.strip()]

def row(rid, target, chk, expected, got, note=""):
    rows.append(dict(row=rid, target=target, check=chk, expected=expected, got=got, note=note))

# ---------- K1-1 rows ----------
with tempfile.TemporaryDirectory() as td:
    d = Path(td)/"r1"; d.mkdir()
    # R1: the Hermes composed anchor block. Anchor = the verbatim gist text recorded
    # in ledger/seal-detached-v1.5.md at 78d961b; report = the condensed rendering.
    ok = export("78d961b", ["ledger/seal-detached-v1.5.md"], d)
    out, rc = check("k1_1.py", d)
    row("R1","ledger/seal-detached-v1.5.md @78d961b (composed-vs-verbatim)","K1-1",
        "MISMATCH x2 blocks (v1.5, v1.6)", json.dumps(out)[:400], f"exported={ok} rc={rc}")
with tempfile.TemporaryDirectory() as td:
    d = Path(td)/"r2"; d.mkdir()
    ok = export("78d961b", ["ledger/seal-detached-v1.5.md"], d)
    out, rc = check("k1_1.py", d)
    row("R2","seal-detached verbatim correction @78d961b","K1-1","MATCH", json.dumps(out)[:400], f"rc={rc}")

# ---------- K1-2 rows (git mode over the real manifest) ----------
for rid, base, head, exp in [
    ("R3","7d4aad7","fe8a1e9","leg-a-closed DIFFERS/EDIT, UNDECLARED"),
    ("R4","7d4aad7","a8e11c8","17 SAME; seal-detached DIFFERS/APPEND declared; leg-a-closed DIFFERS/RENUMBER declared")]:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td); (d/"seal").mkdir(); (d/"head").mkdir()
        mp = manifest_paths(base)
        export(base, mp, d/"seal")
        export(head, mp + [p for p in manifest_paths(head) if p not in mp], d/"head")
        # ledger entries at head, for declaration lookup
        lr = sh(["git","ls-tree","-r","--name-only",head,"ledger/"])
        export(head, [p for p in lr.stdout.split() if p.endswith(".md")], d/"head")
        (d/"MANIFEST").write_text("\n".join(mp)+"\n")
        out, rc = check("k1_2.py", d)
        findings=[o for o in out if isinstance(o,dict) and o.get("status")=="FINDING"]
        same=[o for o in out if isinstance(o,dict) and o.get("status")=="SAME"]
        diff=[o for o in out if isinstance(o,dict) and o.get("status")=="DIFFERS"]
        row(rid, f"{base} vs {head} ({len(mp)} manifest paths)","K1-2",exp,
            f"SAME={len(same)} DIFFERS={len(diff)} FINDING={len(findings)}",
            json.dumps([{k:o.get(k) for k in ('path','status','nature','declaring_entries')} for o in out if isinstance(o,dict) and o.get('status')!='SAME'])[:600])

# ---------- K1-3 rows ----------
def k13(rid, path, before, after, exp):
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); b=d/"before.md"; a=d/"after.md"
        rb=sh(["git","show",f"{before}:{path}"]); ra=sh(["git","show",f"{after}:{path}"])
        if rb.returncode or ra.returncode:
            row(rid,f"{path} {before}->{after}","K1-3",exp,"PATH-ABSENT"); return
        b.write_text(rb.stdout); a.write_text(ra.stdout)
        out,rc=check("k1_3.py", b, a, before, after)
        f=[o for o in out if isinstance(o,dict) and "error" not in o]
        row(rid,f"{path} {before}->{after}","K1-3",exp,
            ("FINDING x%d"%len(f)) if f else "SILENT", json.dumps(out)[:400])
k13("R5","leg-a-closed-2026-09-09.md","7d4aad7","fe8a1e9","FINDING (section 7 inserted)")
k13("R6","leg-a-closed-2026-09-09.md","fe8a1e9","78d961b","FINDING (3/4 inserted, 3-5 renumbered)")
mp7 = [p for p in manifest_paths("7d4aad7") if p != "leg-a-closed-2026-09-09.md"]
r7=[]
for p in mp7:
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); b=d/"b"; a=d/"a"
        rb=sh(["git","show",f"7d4aad7:{p}"]); ra=sh(["git","show",f"a8e11c8:{p}"])
        if rb.returncode or ra.returncode: r7.append((p,"ABSENT")); continue
        b.write_text(rb.stdout); a.write_text(ra.stdout)
        out,rc=check("k1_3.py", b, a, "7d4aad7","a8e11c8")
        f=[o for o in out if isinstance(o,dict) and "error" not in o]
        r7.append((p, "FINDING x%d"%len(f) if f else "SILENT"))
row("R7","18 other sealed files 7d4aad7->a8e11c8","K1-3","18 x SILENT",
    f"SILENT={sum(1 for _,v in r7 if v=='SILENT')} FINDING={sum(1 for _,v in r7 if v.startswith('FINDING'))} ABSENT={sum(1 for _,v in r7 if v=='ABSENT')}",
    json.dumps([x for x in r7 if x[1]!='SILENT'])[:600])

# ---------- K1-4 rows ----------
def k14(rid, commit, paths, exp):
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); w=export(commit, paths, d)
        if not w: row(rid,f"{paths} @{commit}","K1-4",exp,"PATH-ABSENT"); return
        out,rc=check("k1_4.py", *[d/p for p in w])
        f=[o for o in out if isinstance(o,dict) and "error" not in o]
        row(rid,f"{paths} @{commit}","K1-4",exp,
            ("FINDING x%d"%len(f)) if f else "SILENT", json.dumps(out)[:500])
for c in ["5f49023","9123787","e7b2261"]:
    k14(f"R8@{c}", c, ["SEAL-PACKET.md","leg-a-closed-2026-09-09.md"],
        "FINDING at locked coordinates only (31-char variant)")
k14("R8b","0c32940",["v1.6-publication-confirmation-2026-09-10.txt"],"FINDING x1 (10-char anchor ref)")
k14("R8c","0c32940",["gist-id-audit-2026-09-10.txt","work/r8-grep-2026-09-10.txt"],"SILENT (QUOTED header)")
k14("R9","6b70539",["anchors/ANCHORS.md"],"SILENT")

# ---------- C1 rows ----------
def c1row(rid, commit, path, exp):
    r=sh(["git","show",f"{commit}:{path}"])
    if r.returncode: row(rid,f"{path} @{commit}","C1",exp,"PATH-ABSENT"); return
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); (d/"packet.md").write_text(r.stdout)
        out,rc=check("c1.py", d)
        f=[o for o in out if isinstance(o,dict) and "error" not in o]
        row(rid,f"{path} @{commit}","C1",exp,("FINDING x%d"%len(f)) if f else "SILENT", json.dumps(out)[:500])
# R10/R11 targets: search history for the A1/A5 reconciliation and K0 H2 packets
def find_path(pat):
    r=sh(["git","log","--all","--pretty=format:","--name-only","--diff-filter=A"])
    hits=[l.strip() for l in r.stdout.splitlines()
          if l.strip() and "/" in l and "." in l.rsplit("/",1)[1] and re.search(pat,l,re.I)]
    return hits[0] if hits else None
# Targets fixed by name from history, not pattern-matched at runtime:
# the A1/A5 reconciliation packet and the K0 H2 report. Both are .md/.py in work/.
p10="work/red-close-reconciliation.py"
p11="work/h2-report.md"
c1row("R10", "a8e11c8", p10, "FINDING (distance reported as eigenvalue)") if p10 else row("R10","(A1/A5 reconciliation packet)","C1","FINDING","TARGET-NOT-FOUND","no path in history matches a1/a5|reconcil")
c1row("R11", "a8e11c8", p11, "SILENT (bet; adjudication branch)") if p11 else row("R11","(K0 H2 report)","C1","SILENT","TARGET-NOT-FOUND","no path in history matches h2 report")

# ---------- K1-5 / K1-6 rows ----------
def k15(rid, commit, path, exp):
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); w=export(commit,[path],d)
        if not w: row(rid,f"{path} @{commit}","K1-5",exp,"PATH-ABSENT"); return
        out,rc=check("k1_5.py", d/path)
        summ=[o for o in out if isinstance(o,dict) and "_summary" in o]
        f=[o for o in out if isinstance(o,dict) and "_summary" not in o and "error" not in o]
        row(rid,f"{path} @{commit}","K1-5",exp,
            ("FINDING x%d"%len(f)) if f else "SILENT",
            json.dumps({"summary":summ,"findings":f})[:500])
k15("R12","7d4aad7","MANIFEST.sha256","FINDING x1: 53ca0569 at misidentification pair; 19 lines / 18 distinct")
k15("R14","51c2234","K1-MANIFEST.sha256","SILENT")
with tempfile.TemporaryDirectory() as td:
    d=Path(td); mp=manifest_paths("7d4aad7"); export("7d4aad7", mp, d)
    (d/"MANIFEST.sha256").write_text(sh(["git","show","7d4aad7:MANIFEST.sha256"]).stdout)
    out,rc=check("k1_6.py", d/"MANIFEST.sha256", d)
    fails=[o for o in out if isinstance(o,dict) and o.get("status")=="FAIL"]
    parses=[o for o in out if isinstance(o,dict) and o.get("status")=="PARSE"]
    row("R13","5 .yaml manifest paths @7d4aad7","K1-6",
        "FAIL x4 (chebyshev, conv-flag, fourier-diff, misidentification); PARSE x1 (C1-exclusion-list)",
        f"FAIL x{len(fails)}, PARSE x{len(parses)}",
        json.dumps([{"path":o.get("path"),"status":o.get("status")} for o in out])[:600])

# ---------- RA rows (gates retrodicting K1's RED causes) ----------
def ra_smoke(rid, commit, exp):
    with tempfile.TemporaryDirectory() as td:
        d=Path(td)
        r=sh(["git","ls-tree","-r","--name-only",commit,"work/k1/"])
        pys=[p for p in r.stdout.split() if p.endswith(".py") and "/k1/" in p]
        export(commit, pys, d)
        # py3.9 via uv (the K1 failure interpreter); falls back to reporting NO-PY39
        res=[]
        for p in pys:
            code=f"import importlib.util,sys;s=importlib.util.spec_from_file_location('m',r'{d/p}');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)"
            try:
                rr=subprocess.run(["uv","run","--python","3.9","python","-c",code],
                                  capture_output=True,text=True,timeout=120,cwd=str(ROOT))
            except FileNotFoundError:
                res.append((p,"NO-PY39")); continue
            if rr.returncode!=0 and ("No interpreter" in rr.stderr or "not found" in rr.stderr.lower() and "python" in rr.stderr.lower() and "TypeError" not in rr.stderr):
                res.append((p,"NO-PY39")); continue
            res.append((p,"IMPORT-OK" if rr.returncode==0 else "IMPORT-FAIL"))
        row(rid, f"work/k1/*.py @{commit} under py3.9","G0 smoke",exp,
            f"OK={sum(1 for _,v in res if v=='IMPORT-OK')} FAIL={sum(1 for _,v in res if v=='IMPORT-FAIL')} NOPY39={sum(1 for _,v in res if v=='NO-PY39')}",
            json.dumps(res)[:500])
ra_smoke("RA-1","b21abb0","IMPORT-FAIL x2 (k1_1, k1_2)")
ra_smoke("RA-2","d00f75f","IMPORT-OK x5, IMPORT-FAIL x2")
with tempfile.TemporaryDirectory() as td:
    d=Path(td); r=sh(["git","ls-tree","-r","--name-only","d00f75f","work/k1/"])
    pys=[p for p in r.stdout.split() if p.endswith(".py")]
    export("d00f75f", pys, d)
    rr=sh(["uvx","ruff","check","--select","FA,UP","--target-version","py39",str(d/"work/k1")], cwd=ROOT)
    fa=[l for l in rr.stdout.splitlines() if "FA102" in l or "k1_1.py:44" in l or "k1_2.py:26" in l]
    row("RA-3","work/k1/ @d00f75f","G1 ruff FA102","FINDING at k1_1.py:44 and k1_2.py:26",
        f"FA102 lines={len(fa)}", ("\n".join(fa))[:500] or rr.stdout[:400])
r=sh(["git","show","d00f75f:work/k1-test.py"])
calls=sorted(set(re.findall(r"run_check\('([a-z0-9_]+)\.py'", r.stdout)))
row("RA-4","work/k1-test.py @d00f75f","G2 collect-only","3 of 7 checks — harness defect reproduced",
    f"checks invoked={len(calls)}", json.dumps(calls))
with tempfile.TemporaryDirectory() as td:
    d=Path(td); w=export("a094184",["injections/c1/neg-01.md"],d)
    if w:
        pk=d/"pk"; pk.mkdir(); shutil.copy(d/"injections/c1/neg-01.md", pk/"neg-01.md")
        out,rc=check("c1.py", pk)
        f=[o for o in out if isinstance(o,dict) and "error" not in o]
        row("RA-5","injections/c1/neg-01 @a094184 (K1 set, unedited)","C1",
            "FINDING — contamination reproduced on the sealed fixture",
            ("FINDING x%d"%len(f)) if f else "SILENT", json.dumps(out)[:400])
    else:
        row("RA-5","injections/c1/neg-01 @a094184","C1","FINDING","PATH-ABSENT")

out={"head":sh(["git","rev-parse","HEAD"]).stdout.strip(),"python":sys.version.split()[0],"rows":rows}
Path(sys.argv[1] if len(sys.argv)>1 else "work/k1a-retro.json").write_text(json.dumps(out,indent=1))
print("row | check | expected | got")
for r in rows: print(f"{r['row']} | {r['check']} | {r['expected'][:60]} | {r['got'][:80]}")
