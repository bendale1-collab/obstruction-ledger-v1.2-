#!/usr/bin/env python3
"""
K0 Checker v3 — C3/C6/R1.
C3: quoted strings in report must substring-match corpus (manifest + all reports).
C6: threshold retro-fitting detection (Option X with threshold, rejected).
R1: controls mentioned in report must carry pass/fail verdict.
"""
import json, re, sys; from pathlib import Path

def load_manifest(path):
    m = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            parts = line.split(None, 1)
            if len(parts) == 2: m[parts[1]] = parts[0]
    return m

def build_corpus(manifest, extra_dirs=None):
    """Build set of all text from manifest files + extra directories."""
    texts = set()
    base = Path.cwd()
    for src_rel in manifest:
        for p in [base / src_rel, base.parent / src_rel]:
            if p.exists():
                texts.add(p.read_text(errors='replace').lower())
                break
    if extra_dirs:
        for d in extra_dirs:
            dp = Path(d) if Path(d).is_absolute() else base / d
            if dp.exists():
                for f in dp.glob('*.md'):
                    try:
                        texts.add(f.read_text(errors='replace').lower())
                    except: pass
    return texts

def check_c3(text, corpus):
    """Return list of quoted strings NOT found in corpus."""
    qkeys = set()
    for m in re.finditer(r'"([^"]{12,})"', text):
        c = m.group(1).strip().lower()
        c = re.sub(r'\s+', ' ', c)
        if len(c) >= 15: qkeys.add(c)
    for m in re.finditer(r'^>\s*(.*)', text, re.MULTILINE):
        c = m.group(1).strip().lower()
        c = c.replace('**', '').replace('*', '').strip()
        c = re.sub(r'\s+', ' ', c)
        if len(c) >= 25: qkeys.add(c)
    failures = []
    for q in sorted(qkeys):
        found = any(q in t for t in corpus)
        if not found:
            failures.append(q[:120])
    return {"total": len(qkeys), "matched": len(qkeys)-len(failures), "unmatched": failures}

def check_c6(text):
    """Detect threshold retro-fitting."""
    findings = []
    if 'retro-fitting' in text.lower() or 'retrofit' in text.lower():
        findings.append("retro-fitting detected")
    blocks = re.findall(r'(Option|Alternative|Proposal)\s*\(?\s*([A-Za-z])\s*\)?\s*:\s*(.*?)(?=\n\s*(?:Option|\n\n|$))', text, re.IGNORECASE|re.DOTALL)
    for _, letter, block in blocks:
        bl = block.lower()
        if 'rejected' in bl or 'refused' in bl:
            nums = re.findall(r'[±±]?\s*(\d+\.?\d*(?:e[±]?\d+)?)', block)
            vals = [float(n) for n in nums if 1e-6 < float(n) < 100]
            if vals:
                findings.append(f"REJECTED:{letter}:thresholds={vals}")
    return findings

def check_r1(text, registry_controls):
    """Check controls mentioned in text carry pass/fail."""
    text_lower = text.lower()
    missing_ctrl = []
    verdict_kw = ['pass', 'fail', '✅', '❌', 'correct', 'incorrect', 'present', 'absent',
                  'green', 'red', 'met', 'not met', 'yes', 'no', 'verified', 'ok', 'true', 'false']
    
    for ctrl in registry_controls:
        name = ctrl.get('name', '')
        cid = ctrl.get('id', '').lower()
        # Build search terms from the control
        search_terms = set()
        for t in [name, cid]:
            if not t or t == 'none': continue
            for part in t.replace('-', ' ').replace('_', ' ').lower().split():
                if len(part) > 3: search_terms.add(part)
        if not search_terms: continue
        
        # Is the control mentioned anywhere in the text?
        mentioned = False
        found_verdict = False
        for term in search_terms:
            idx = text_lower.find(term)
            if idx >= 0:
                mentioned = True
                # Check for verdict near this occurrence
                ctx = text_lower[max(0,idx-100):idx+200]
                if any(kw in ctx for kw in verdict_kw):
                    found_verdict = True
                    break
        if mentioned and not found_verdict:
            missing_ctrl.append(cid or name)
    
    return {"registry_count": len(registry_controls),
            "matched": len(registry_controls)-len(missing_ctrl),
            "controls_without_verdict": missing_ctrl}

def load_registry(registry_dir):
    import yaml
    controls = []
    p = Path(registry_dir)
    if p.exists():
        for f in sorted(p.glob('*.yaml')):
            try:
                d = yaml.safe_load(f.read_text())
                if d: controls.append(d)
            except: pass
    return controls

def check_one(path, corpus, registry_controls):
    text = Path(path).read_text(errors='replace')
    c3 = check_c3(text, corpus)
    c6 = check_c6(text)
    r1 = check_r1(text, registry_controls)
    return {"file": str(path), "checks": {"C3": c3, "C6": c6, "R1": r1}}

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', default='MANIFEST.sha256')
    parser.add_argument('--registry-dir', default='registry')
    parser.add_argument('--extra-corpus-dirs', action='append', default=[])
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    
    manifest = load_manifest(args.manifest)
    corpus = build_corpus(manifest, args.extra_corpus_dirs)
    registry = load_registry(args.registry_dir)
    
    results = []
    for fp in args.files:
        results.append(check_one(fp, corpus, registry))
    print(json.dumps(results, indent=2))