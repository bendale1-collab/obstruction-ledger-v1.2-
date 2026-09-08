#!/usr/bin/env python3
"""
F-5 DIAGNOSTIC — resolvent-norm distribution on two strip populations:
  1) 20 residual origin-H2 strip modes (the ones F-4 could not eliminate)
  2) 22 positive-Re eliminated naive strip modes (absent in origin-H2)
Sealed engine. No modifications. $0 compute.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np
from scipy import linalg
from f1 import RealizationPair, FourierSpectralEngine

L = 20.0; FLOOR = -0.497; DELTA = 5e-4; P0_THRESH = -0.5 + 1e-3

def strip_modes_by_zone(eig, lo, hi, excl=1e-2):
    """Return eigenvalues in Re in (lo, hi), excluding {0,1} within excl."""
    re = eig.real
    mask = (re > lo) & (re < hi)
    ok = mask & (np.abs(eig) > excl) & (np.abs(eig - 1.0) > excl)
    return eig[ok]

def resolvent_metric(L_mat, z, eps=1e-3):
    """eps * ||(z - eps - L)^-1|| via smallest singular value."""
    n = L_mat.shape[0]
    B = (z - eps) * np.eye(n) - L_mat
    s = linalg.svdvals(B)
    sigma_min = s[-1]
    if sigma_min < 1e-300:
        return float('inf')
    return float(eps / sigma_min)

# Build operators at N=1024
rp = RealizationPair(N=1024, L=L)
L_naive = rp._build_operator(a=0.0, odd_basis=False)
L_h2    = rp._build_operator(a=0.0, odd_basis=True)

eig_n = linalg.eigvals(L_naive)
eig_h = linalg.eigvals(L_h2)

# Filtered sets (P0 zone, |eig| < 10)
eig_nf = eig_n[np.abs(eig_n) < 10.0]
eig_hf = eig_h[np.abs(eig_h) < 10.0]

# Population 1: 20 residual origin-H2 strip modes
r20 = strip_modes_by_zone(eig_hf, P0_THRESH, np.inf)
print(f"Population 1: {len(r20)} residual origin-H2 strip modes")
print(f"  Re range: [{r20.real.min():+.6f}, {r20.real.max():+.6f}]")

# Population 2: eliminated positive-Re naive modes (in naive but NOT in origin-H2)
n42 = strip_modes_by_zone(eig_nf, P0_THRESH, np.inf)
e22 = np.array([z for z in n42 if np.min(np.abs(z - r20)) > 1e-10])
print(f"Population 2: {len(e22)} eliminated naive positive-Re strip modes")
print(f"  Re range: [{e22.real.min():+.6f}, {e22.real.max():+.6f}]")

# Compute resolvent norms
EPS = 1e-3
THRESH = 1e2  # per pre-reg F-5 threshold

def compute_resolvent_distribution(eig_set, L_mat, label):
    results = []
    for z in eig_set:
        rn = resolvent_metric(L_mat, z, EPS)
        results.append({'eig_real': round(float(z.real), 6),
                        'eig_imag': round(float(z.imag), 6),
                        'resolvent_norm': round(rn, 4)})
    
    norms = np.array([r['resolvent_norm'] for r in results])
    n_trusted = int(np.sum(norms <= THRESH))
    n_untrusted = int(np.sum(norms > THRESH))
    
    print(f"\n{label}:")
    print(f"  N={len(results)}, ε={EPS}, threshold={THRESH}")
    print(f"  Resolvent norm stats: min={norms.min():.2f}, max={norms.max():.2e}, median={np.median(norms):.2f}")
    print(f"  Trusted (≤{THRESH}): {n_trusted}/{len(results)}")
    print(f"  Untrusted (>{THRESH}): {n_untrusted}/{len(results)}")
    
    # Show worst cases
    worst = sorted(results, key=lambda r: -r['resolvent_norm'])[:5]
    for w in worst:
        print(f"    Re={w['eig_real']:.6f} Im={w['eig_imag']:.4f}  ε·||(z-ε-L)^-1||={w['resolvent_norm']:.2e}")
    
    return results

# Population 1: use origin-H2 operator (the space they live in)
r1 = compute_resolvent_distribution(r20, L_h2, "Population 1: 20 residual H2 strip modes (on L_h2)")

# Same population, but evaluated on naive operator for comparison
r1b = compute_resolvent_distribution(r20, L_naive, "Population 1: same 20 modes, evaluated on L_naive")

# Population 2: eliminated modes, on naive operator (their native space)
r2 = compute_resolvent_distribution(e22, L_naive, "Population 2: 22 eliminated naive positive-Re strip modes (on L_naive)")

# Population 2 on origin-H2 (are they BAD artifacts or genuine spectrum?)
r2b = compute_resolvent_distribution(e22, L_h2, "Population 2: same 22 eliminated modes, evaluated on L_h2")

out = {
    'epsilon': EPS,
    'threshold': THRESH,
    'p1_residual_h2_modes': {'n': len(r20), 'results': r1},
    'p1b_residual_h2_on_naive': {'results': r1b},
    'p2_eliminated_positive_re': {'n': len(e22), 'results': r2},
    'p2b_eliminated_on_h2': {'results': r2b},
}
with open('work/f5-diagnostic-results.json', 'w') as f:
    json.dump(out, f, indent=2)

print(f"\nResults saved to work/f5-diagnostic-results.json")