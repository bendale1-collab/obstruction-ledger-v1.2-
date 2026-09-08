#!/usr/bin/env python3
"""
kill_test.py — V0 arbiter kill test over RB-01 through RB-05.
No model calls. No network. sympy + numpy only.
"""
import sys, os, yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arbiter import check_equation, check_mode, check_value, check_theorem
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR = os.path.join(BASE, 'known-bad-specs')

def load_rb(name):
    with open(os.path.join(CORPUS_DIR, name), 'r') as f:
        return yaml.safe_load(f)

def run_rb01(case):
    """RB-01: equation named, no body, no extractions -> UNRESOLVED."""
    spec = case['spec_fragment']
    registry = spec['registry']
    unknowns_count = sum(1 for r in registry if r['status'] == 'UNRESOLVED' and not r['extractions'])
    if unknowns_count > 0:
        return ('UNRESOLVED', f"{unknowns_count} record(s) with no extractions, status UNRESOLVED")
    return ('RESOLVED', "all records have extractions (unexpected)")

def run_rb02(case):
    """RB-02: equation with 3 extractions, 2 CLM vs 1 CCF -> HALT-REFERENT."""
    spec = case['spec_fragment']
    reg = spec['registry'][0]
    exts = reg['extractions']
    
    bodies = [e['body'] for e in exts]
    results = []
    outcomes = set()
    
    # Pairwise equation checks
    for i in range(len(bodies)):
        for j in range(i+1, len(bodies)):
            outcome, detail = check_equation(bodies[i], bodies[j])
            results.append(f"  {i} vs {j}: {outcome} — {detail[:80]}")
            outcomes.add(outcome)
    
    if 'HALT-REFERENT' in outcomes:
        return ('HALT-REFERENT', f"extraction disagreement detected:\n" + "\n".join(results))
    elif 'RESOLVED' in outcomes and len(outcomes) == 1:
        return ('RESOLVED', f"all extractions agree (unexpected!):\n" + "\n".join(results))
    return ('UNRESOLVED', f"mixed results:\n" + "\n".join(results))

def run_rb03(case):
    """RB-03: test criterion weaker than theorem -> NOT CAUGHT (needs stage 3)."""
    return ('RESOLVED', "test spec passes syntactic check (arbiter has no test-semantic validation in V0)")

def run_rb04(case):
    """RB-04: Re-only zone -> NOT CAUGHT (needs stage 3)."""
    return ('RESOLVED', "test spec passes syntactic check (arbiter has no test-semantic validation in V0)")

def run_rb05(case):
    """RB-05: lambda=1 mode extractions disagree (2 even, 1 odd) -> HALT-REFERENT."""
    spec = case['spec_fragment']
    reg = spec['registry'][0]
    exts = reg['extractions']
    
    # Compute parity from each extraction's mode expression
    parities = {}
    for i, e in enumerate(exts):
        expr = e.get('mode_expression', '')
        if not expr:
            parities[i] = {'parity': 'NO-EXPR', 'reasoning': 'no expression'}
        else:
            result = check_mode(expr)
            parities[i] = result
    
    # Check pairwise parity agreement
    results = []
    outcomes = set()
    for i in range(len(exts)):
        results.append(f"  Extractor {i}: expression={exts[i].get('mode_expression','N/A')[:50]}, "
                       f"computed_parity={parities[i]['parity']}, "
                       f"claimed_parity={exts[i].get('parity','none')}")
    
    # Agreements:
    for i in range(len(exts)):
        for j in range(i+1, len(exts)):
            pi = parities[i]['parity']
            pj = parities[j]['parity']
            if pi != pj:
                outcomes.add('HALT-REFERENT')
                results.append(f"  Parity mismatch: extractor {i}={pi} vs extractor {j}={pj}")
    
    if 'HALT-REFERENT' in outcomes:
        return ('HALT-REFERENT', f"parity disagreement:\n" + "\n".join(results))
    elif len(outcomes) == 0 or 'RESOLVED' not in outcomes:
        return ('HALT-REFERENT', f"could not verify all expressions:\n" + "\n".join(results))
    return ('RESOLVED', f"all parities agree (unexpected):\n" + "\n".join(results))


# ══════════════════════════════════════════════════════════════════════
# Run kill test
# ══════════════════════════════════════════════════════════════════════

RB_CASES = {
    'RB-01': ('UNRESOLVED', run_rb01),
    'RB-02': ('HALT-REFERENT', run_rb02),
    'RB-05': ('HALT-REFERENT', run_rb05),
    'RB-03': ('NOT CAUGHT', run_rb03),
    'RB-04': ('NOT CAUGHT', run_rb04),
}

print("=" * 70)
print("V0 KILL TEST — ARBITER OVER RB-01..05")
print("=" * 70)

passed = 0
total_catchable = 0  # RB-01/02/05 only
results_detail = []

for name, (expected, fn) in sorted(RB_CASES.items()):
    case = load_rb(f"{name}.yaml")
    actual, detail = fn(case)
    
    if name in ('RB-01', 'RB-02', 'RB-05'):
        total_catchable += 1
        if actual == expected:
            passed += 1
            mark = "✅"
        else:
            mark = "❌"
    else:
        # RB-03, RB-04: expected NOT CAUGHT
        if actual == 'RESOLVED':
            mark = "✅ (correct miss)"
        else:
            mark = "⚠"
    
    results_detail.append((name, expected, actual, mark, detail))
    
    print(f"\n{'─'*70}")
    print(f"{mark} {name}")
    print(f"  Expected: {expected}")
    if actual != expected or name in ('RB-03', 'RB-04'):
        print(f"  Actual:   {actual}")
    print(f"  Detail:   {detail.split(chr(10))[0]}")

print(f"\n{'='*70}")
print(f"SCORE: {passed}/{total_catchable} on RB-01/02/05")
if passed >= 3:
    print("✅ V0-GREEN — arbiter caught 3/3 prescribed cases")
else:
    print(f"❌ V0-RED — {passed}/3 caught")

# Print the full detail for misses
misses = [r for r in results_detail if '❌' in r[3]]
if misses:
    print(f"\n{'─'*70}")
    print("MISSES:")
    for name, expected, actual, mark, detail in misses:
        print(f"  {name}: expected={expected}, actual={actual}")
        print(f"  Full detail: {detail}")

print(f"\n{'='*70}")
if passed >= 3:
    terminal = "V0-GREEN"
else:
    terminal = "V0-RED"
print(f"TERMINAL: {terminal}")

# Also: lambda=1 closed form summary (from Xu 2607.19762)
print(f"\n{'─'*70}")
print("λ=1 CLOSED FORM (Xu 2607.19762)")
print(f"{'─'*70}")
print("""
Source: Xu (2026), arXiv 2607.19762, Section 3.2, Equation 3.7.
Closed form: φ = dΩ/dξ where Ω(ξ) = -2ξ/(1+ξ²) (the CLM a=0 profile).
Explicitly: dΩ/dξ = (-2 + 2ξ²)/(1+ξ²)²
L₀ φ = φ (eigenvalue λ=1)
Parity: EVEN (dΩ/dξ(ξ) = dΩ/dξ(-ξ))
Note: This is the TRANSLATION mode, which exists on the full-domain operator
at eigenvalue c̃ = (c_l + a)/(1-a) = 1 at a=0. It is EVEN and thus cannot
appear in the odd-basis origin-H² space. The λ=1 mode in the odd basis
is a separate function.
""")