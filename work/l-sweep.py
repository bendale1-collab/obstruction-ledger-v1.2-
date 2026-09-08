#!/usr/bin/env python3
"""
L-SWEEP DIAGNOSTIC — origin-H2 operator at N=1024, L ∈ {10, 20, 40, 80}.
Track 20 residual strip modes by eigenvector continuity.
Pre-registered split: |dRe/dlogL| > 1e-2 => L-dependent (essential spectrum artifact).
$0 compute. No engine edits.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np
from scipy import linalg
from f1 import RealizationPair

P0_THRESH = -0.5 + 1e-3
L_VALUES = [10, 20, 40, 80]
N = 1024

print("L-SWEEP DIAGNOSTIC — origin-H2, N=1024")
print("Pre-registered split: |dRe/dlogL| > 1e-2 => L-dependent")
print()

# Build at each L, get eigenvectors
all_data = {}
for L in L_VALUES:
    rp = RealizationPair(N=N, L=L)
    L_mat = rp._build_operator(a=0.0, odd_basis=True)
    eigvals, eigvecs = linalg.eig(L_mat)
    
    # Filter |eig| < 10
    filt = np.abs(eigvals) < 10.0
    eig_f = eigvals[filt]
    vecs_f = eigvecs[:, filt]
    
    # Get strip modes (P0 zone)
    re = eig_f.real
    mask = (re > P0_THRESH) & (np.abs(eig_f) > 1e-2) & (np.abs(eig_f - 1.0) > 1e-2)
    strip = eig_f[mask]
    strip_vecs = vecs_f[:, mask]
    
    all_data[L] = {'eig_f': eig_f, 'vecs_f': vecs_f, 'strip': strip, 'strip_vecs': strip_vecs,
                   'n_strip': len(strip)}
    print(f"  L={L}: {len(strip)} strip modes")

L20_data = all_data[20]
L20_strip = L20_data['strip']
L20_strip_vecs = L20_data['strip_vecs']

# Track each L=20 strip mode across L values by nearest eigenvalue + overlap
tracking = []
for k in range(min(20, len(L20_strip))):
    z_ref = L20_strip[k]
    v_ref = L20_strip_vecs[:, k]
    v_ref = v_ref / np.linalg.norm(v_ref)
    
    rec = {'idx': k, 'ref_L20_eig': complex(z_ref)}
    
    for L in L_VALUES:
        d = all_data[L]
        dists = np.abs(d['eig_f'] - z_ref)
        nearest_idx = int(np.argmin(dists))
        nearest_eig = complex(d['eig_f'][nearest_idx])
        nearest_vec = d['vecs_f'][:, nearest_idx]
        nearest_vec = nearest_vec / np.linalg.norm(nearest_vec)
        overlap = float(abs(np.vdot(v_ref.conj(), nearest_vec)))
        
        dist_to_strip = float(np.min(np.abs(d['strip'] - z_ref))) if len(d['strip']) > 0 else float('inf')
        
        rec[L] = {'nearest_eig': nearest_eig, 'dist': float(dists[nearest_idx]),
                  'overlap': overlap, 'strip_dist': dist_to_strip}
    
    tracking.append(rec)

# Print tracking table
print(f"\n{'='*100}")
print("MODE TRACKING BY EIGENVECTOR OVERLAP")
print(f"{'='*100}")
print(f"{'k':>3s} L=20 Re      Im        | ", end='')
for L in L_VALUES:
    print(f"L={L} Re      Im      |Ov|  ", end='')
print()
print("-" * 100)
for rec in tracking:
    print(f"{rec['idx']:>3d} {rec['ref_L20_eig'].real:>+8.6f} {rec['ref_L20_eig'].imag:>+8.4f} | ", end='')
    for L in L_VALUES:
        if L == 20:
            continue
        d = rec[L]
        print(f" {d['nearest_eig'].real:>+8.6f} {d['nearest_eig'].imag:>+8.4f} {d['overlap']:>5.3f}  ", end='')
    print()

# Compute dRe/dlogL
print(f"\n{'='*80}")
print("dRe/dlogL ANALYSIS")
print(f"{'='*80}")
print(f"{'k':>3s} {'Re(L=10)':>10s} {'Re(L=20)':>10s} {'Re(L=40)':>10s} {'Re(L=80)':>10s} {'dRe/dlogL':>12s} {'L-dep?':>8s} {'dIm/dlogL':>12s} {'Verdict':>16s}")

n_dep = 0; n_indep = 0
for rec in tracking:
    Ls = sorted(rec.keys() - {'idx', 'ref_L20_eig'})
    # Collect Re and logL
    logL_vals = [np.log(L) for L in sorted(L_VALUES)]
    re_vals = [rec[L]['nearest_eig'].real for L in sorted(L_VALUES)]
    im_vals = [rec[L]['nearest_eig'].imag for L in sorted(L_VALUES)]
    
    # Linear fit: Re = a*logL + b
    A = np.vstack([logL_vals, np.ones_like(logL_vals)]).T
    coeff_re = np.linalg.lstsq(A, re_vals, rcond=None)[0][0]
    coeff_im = np.linalg.lstsq(A, im_vals, rcond=None)[0][0]
    
    dep = abs(coeff_re) > 1e-2
    if dep:
        n_dep += 1
        verdict = "L-DEP (ess.spec)"
    else:
        n_indep += 1
        verdict = "L-INDEP (point)"
    
    print(f"{rec['idx']:>3d} {re_vals[0]:>+10.6f} {re_vals[1]:>+10.6f} {re_vals[2]:>+10.6f} {re_vals[3]:>+10.6f} {coeff_re:>+12.6f} {'YES' if dep else 'NO':>8s} {coeff_im:>+12.6f} {verdict:>16s}")

print(f"\nClassification: L-dependent={n_dep}, L-independent={n_indep}, total={n_dep+n_indep}")

out = {
    'method': 'origin-H2 at N=1024, L-sweep {10,20,40,80}',
    'split_threshold': '|dRe/dlogL| > 1e-2 => L-dependent',
    'classification': {'L_dependent': n_dep, 'L_independent': n_indep},
}
with open('work/l-sweep-results.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nResults saved to work/l-sweep-results.json")