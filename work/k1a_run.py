#!/usr/bin/env python3
"""K1a harness. Reads each fixture dir's index.md, runs the check with its real
CLI, compares to the expected column. Properties: draws from PROPERTIES
strategies, renders each case, invokes the check, asserts no finding.
Emits one JSON file and one markdown table. Never edits anything.
Author: Claude (fixture author for c1/k1-1/k1-2; no check code authored).
"""
import json, re, subprocess, sys, tempfile, importlib.util, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
CHECKS = sorted((ROOT/"work/k1a").glob("*.py"))
DIRMAP = {"c1":"c1","k1_1":"k1-1","k1_2":"k1-2","k1_3":"k1-3","k1_4":"k1-4","k1_5":"k1-5","k1_6":"k1-6"}
UNTESTABLE = {"k1_3":"ledger/k1a-k1-3-fixture-defect.md: single files, check needs before/after",
              "k1_6":"sealed fixtures are .txt; check scope is .yaml/.yml/.json (section 2)"}
PY = sys.executable

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    try: out = json.loads(r.stdout) if r.stdout.strip() else []
    except json.JSONDecodeError: out = [{"error":"non-json","stdout":r.stdout[:200],"stderr":r.stderr[:200]}]
    return out, r.returncode

def findings_of(stem, out):
    if not isinstance(out, list): return ["non-list"]
    if any(isinstance(o,dict) and "error" in o for o in out): return ["ERROR"]
    if stem=="k1_5": return [o for o in out if not (isinstance(o,dict) and set(o)=={"_summary"})]
    if stem=="k1_1": return [o for o in out if isinstance(o,dict) and o.get("verdict")=="MISMATCH"]
    if stem=="k1_2": return [o for o in out if isinstance(o,dict) and o.get("status")=="FINDING"]
    return out

def parse_index(d):
    rows=[]
    for line in (d/"index.md").read_text().splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("|--"): continue
        cells=[c.strip() for c in line.strip("|").split("|")]
        if len(cells)<2 or cells[0] in ("case","file"): continue
        case, exp = cells[0], cells[1]
        if not (case.startswith("p-") or case.startswith("n-") or case.startswith("pos-") or case.startswith("neg-")): continue
        rows.append((case, exp))
    return rows

def norm(exp):
    e=exp.upper()
    if e.startswith("FINDING") or e.startswith("MISMATCH") or e.startswith("FAIL"): return "FIRE"
    return "QUIET"

def locate(d, case):
    hits=[p for p in d.rglob(case+"*") if p.name.startswith(case)]
    hits=[h for h in hits if h.is_dir() or h.suffix in (".md",".txt",".sha256","")]
    return hits[0] if hits else None

def invoke(stem, check, fx):
    if stem=="c1" and Path(fx).is_file():
        # C1 (Agent A) reads a packet directory of *.md; sealed fixtures are single files. Glue only.
        with tempfile.TemporaryDirectory() as td:
            import shutil; shutil.copy(fx, Path(td)/"packet.md"); return run([PY,str(check),td])
    if stem in ("c1","k1_1","k1_2","k1_4","k1_5","k1_6"): return run([PY,str(check),str(fx)])
    raise RuntimeError(stem)

results=[]
for check in CHECKS:
    stem=check.stem; d=ROOT/"injections-k1a"/DIRMAP[stem]
    for case,exp in parse_index(d):
        want=norm(exp)
        if stem in UNTESTABLE:
            results.append(dict(check=stem,case=case,expected=exp,got="UNTESTABLE-FIXTURE-DEFECT",verdict="UNTESTABLE",note=UNTESTABLE[stem])); continue
        fx=locate(d,case)
        if stem=="k1_5" and fx is not None and fx.is_file():
            toks=[l.split()[0] for l in fx.read_text().splitlines() if l.strip() and not l.startswith("#")]
            if toks and not all(re.fullmatch(r"[0-9a-fA-F]+",t) for t in toks):
                results.append(dict(check=stem,case=case,expected=exp,got="UNTESTABLE-FIXTURE-DEFECT",verdict="UNTESTABLE",note="non-hex placeholder in sha256sum-format manifest; check regex requires hex (section 2 sha256sum format)")); continue
        if fx is None:
            results.append(dict(check=stem,case=case,expected=exp,got="FIXTURE-NOT-FOUND",verdict="ERROR")); continue
        out,rc=invoke(stem,check,fx)
        f=findings_of(stem,out)
        if f==["ERROR"] or f==["non-list"]:
            results.append(dict(check=stem,case=case,expected=exp,got="ERROR",verdict="ERROR",raw=out[:3],exit=rc)); continue
        got="FIRE" if f else "QUIET"
        results.append(dict(check=stem,case=case,expected=exp,got=got,verdict="PASS" if got==want else "FAIL",n_findings=len(f),exit=rc))

# ---------- properties ----------
def render_c1(text, td): p=td/"case.md"; p.write_text(text); return td
def render_k11(pair, td):
    a,r=pair; (td/"anchor.txt").write_bytes(a); (td/"report.md").write_text(r); return td
def render_k12(spec, td):
    for p,c in spec["seal"].items(): (td/"seal"/p).parent.mkdir(parents=True,exist_ok=True); (td/"seal"/p).write_text(c)
    for p,c in spec["head"].items(): (td/"head"/p).parent.mkdir(parents=True,exist_ok=True); (td/"head"/p).write_text(c)
    for p,c in spec["ledger"].items(): (td/"head"/p).parent.mkdir(parents=True,exist_ok=True); (td/"head"/p).write_text(c)
    (td/"MANIFEST").write_text("\n".join(spec["MANIFEST"])+"\n"); return td
RENDER={"c1":render_c1,"k1_1":render_k11,"k1_2":render_k12}

prop_results=[]
from hypothesis import given, settings, HealthCheck
for check in CHECKS:
    stem=check.stem; pf=ROOT/"injections-k1a"/DIRMAP[stem]/"properties.py"
    if not pf.exists():
        prop_results.append(dict(check=stem,property="(none)",verdict="NO-PROPERTIES-FILE")); continue
    spec=importlib.util.spec_from_file_location("props_"+stem,pf); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    if not hasattr(m,"PROPERTIES"):
        prop_results.append(dict(check=stem,property="(module)",verdict="VACUOUS-PROPERTY",note="properties.py defines no PROPERTIES strategies and never invokes the check; its own tests assert facts about generated strings")); continue
    if stem in UNTESTABLE or stem not in RENDER:
        prop_results.append(dict(check=stem,property="(module)",verdict="UNTESTABLE")); continue
    for name,strat in m.PROPERTIES.items():
        viol=[]; n=[0]
        @settings(max_examples=getattr(m,"MIN_EXAMPLES",200), suppress_health_check=list(HealthCheck), deadline=None)
        @given(strat)
        def t(x):
            n[0]+=1
            with tempfile.TemporaryDirectory() as td:
                fx=RENDER[stem](x, Path(td)); out,rc=invoke(stem,check,fx)
                f=findings_of(stem,out)
                if f: viol.append({"input":str(x)[:300],"findings":f[:2]})
        try: t()
        except Exception as e: viol.append({"harness_error":repr(e)[:300]})
        prop_results.append(dict(check=stem,property=name,examples=n[0],violations=len(viol),verdict="PASS" if not viol else "FAIL",sample=viol[:3]))

fired={r["check"] for r in results if r.get("got")=="FIRE"}
for p in prop_results:
    if p["verdict"]=="PASS" and p["check"] not in fired: p["verdict"]="PASS-VACUOUS"; p["note"]="check produced no finding on any positive; property cannot discriminate"
out={"head":subprocess.run(["git","rev-parse","HEAD"],capture_output=True,text=True,cwd=ROOT).stdout.strip(),
     "python":sys.version.split()[0],"injections":results,"properties":prop_results}
Path(sys.argv[1] if len(sys.argv)>1 else "work/k1a-run-output.json").write_text(json.dumps(out,indent=1))
# summary table
lines=["check | case | expected | got | verdict"]
for r in results: lines.append(f"{r['check']} | {r['case']} | {r['expected']} | {r['got']} | {r['verdict']}")
lines.append(""); lines.append("check | property | examples | violations | verdict")
for p in prop_results: lines.append(f"{p['check']} | {p['property']} | {p.get('examples','-')} | {p.get('violations','-')} | {p['verdict']}")
print("\n".join(lines))
