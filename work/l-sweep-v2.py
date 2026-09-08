#!/usr/bin/env python3
"""
L-SWEEP v2 — fixed-resolution rerun.
Pre-registered before running:
  Grid spacing dx = 2L/(2N+1) held constant at the L=20, N=1024 value.
  Sweep L in {10, 20, 40, 80} with N in {512, 1024, 2048, 4096}.
  Track the 20 modes by eigenvector continuity (origin-H2) and naive.

Expected if essential-spectrum artifact:
  dRe/dlogL < 0 (modes converge toward -1/2 as L grows), |dIm| bounded.
Expected if resolution confound explains v1's positive sign:
  v1 sign flips or magnitude collapses under fixed dx.

Also report: same sweep on the naive (max-L2) realization, 4 same points.
$0 compute. No engine edits.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np
from scipy import linalg
from f1 import RealizationPair

P0_THRESH = -0.5 + 1e-3
# Pre-registered L-N pairs: fixed dx = 40/2049 ≈ 0.01952
SWEEP = [(10, 512), (20, 1024), (40, 2048), (80, 4096)]

ref_dx = 2 * 20.0 / (2 * 1024 + 1)

print("L-SWEEP v2 — FIXED RESOLUTION")
print(f"Reference: L=20, N=1024, dx = {ref_dx:.6f}")
print(f"Sweep points: L ∈ {[p[0] for p in SWEEP]}, N ∈ {[p[1] for p in SWEEP]}")
print(f"Pre-registered: |dRe/dlogL| > 1e-2 threshold applies to both realizations")
print()

# Build at each (L,N) for both realizations
all_h2 = {}
all_naive = {}

for L, N in SWEEP:
    dx = 2 * L / (2 * N + 1)
    
    # origin-H2
    rp = RealizationPair(N=N, L=L)
    L_h2 = rp._build_operator(a=0.0, odd_basis=True)
    e_h2, v_h2 = linalg.eig(L_h2)
    filt_h2 = np.abs(e_h2) < 10.0
    e_h2_f = e_h2[filt_h2]
    v_h2_f = v_h2[:, filt_h2]
    re_h2 = e_h2_f.real
    mask_h2 = (re_h2 > P0_THRESH) & (np.abs(e_h2_f) > 1e-2) & (np.abs(e_h2_f - 1.0) > 1e-2)
    strip_h2 = e_h2_f[mask_h2]
    strip_h2_vecs = v_h2_f[:, mask_h2]
    
    # naive (max-L2)
    L_naive = rp._build_operator(a=0.0, odd_basis=False)
    e_naive, v_naive = linalg.eig(L_naive)
    filt_naive = np.abs(e_naive) < 10.0
    e_naive_f = e_naive[filt_naive]
    v_naive_f = v_naive[:, filt_naive]
    re_naive = e_naive_f.real
    mask_naive = (re_naive > P0_THRESH) & (np.abs(e_naive_f) > 1e-2) & (np.abs(e_naive_f - 1.0) > 1e-2)
    strip_naive = e_naive_f[mask_naive]
    strip_naive_vecs = v_naive_f[:, mask_naive]
    
    all_h2[L] = {'eig': e_h2_f, 'vecs': v_h2_f, 'strip': strip_h2, 'strip_vecs': strip_h2_vecs,
                 'n_strip': len(strip_h2)}
    all_naive[L] = {'eig': e_naive_f, 'vecs': v_naive_f, 'strip': strip_naive, 'strip_vecs': strip_naive_vecs,
                    'n_strip': len(strip_naive)}
    
    print(f"L={L:>3d} N={N:>4d} dx={dx:.6f}  H2 strip={len(strip_h2):>3d}  Naive strip={len(strip_naive):>3d}")

# ── Track origin-H2 modes ──
L20_h2 = all_h2[20]
ref_strip = L20_h2['strip']
ref_strip_vecs = L20_h2['strip_vecs']

print(f"\n{'='*110}")
print("ORIGIN-H2 TRACKING | dRe/dlogL ANALYSIS (fixed dx)")
print(f"{'='*110}")
print(f"{'k':>3s} | Re(10)   Re(20)   Re(40)   Re(80)   | dRe/dlogL    L-dep?   | Im(10)   Im(80)")

h2_tracking = []
for k in range(len(ref_strip)):
    z_ref = ref_strip[k]
    
    rec = {'k': k, 'ref': complex(z_ref)}
    logL_vals = []; re_vals = []; im_vals = []
    
    for L, N in SWEEP:
        d = all_h2[L]
        dists = np.abs(d['eig'] - z_ref)
        ni = int(np.argmin(dists))
        ne = complex(d['eig'][ni])
        
        rec[L] = {'eig': ne, 'dist': float(dists[ni])}
        logL_vals.append(np.log(L))
        re_vals.append(ne.real)
        im_vals.append(ne.imag)
    
    # dRe/dlogL
    A = np.vstack([logL_vals, np.ones_like(logL_vals)]).T
    coeff_re = np.linalg.lstsq(A, re_vals, rcond=None)[0][0]
    coeff_im = np.linalg.lstsq(A, im_vals, rcond=None)[0][0]
    dep = abs(coeff_re) > 1e-2
    
    h2_tracking.append({'k': k, 'ref_eig': str(z_ref), 'dRe_dlogL': float(coeff_re),
                        'dIm_dlogL': float(coeff_im), 'L_dependent': bool(dep),
                        'tracking': {L: {'eig': str(rec[L]['eig'])} for L,_ in SWEEP}})
    
    print(f"{k:>3d} | {re_vals[0]:>+8.6f} {re_vals[1]:>+8.6f} {re_vals[2]:>+8.6f} {re_vals[3]:>+8.6f} | {coeff_re:>+11.6f} {'YES' if dep else 'NO':>8s} | {im_vals[0]:>+6.3f} {im_vals[3]:>+6.3f}")

# Classification
n_h2_dep = sum(1 for t in h2_tracking if t['L_dependent'])
n_h2_indep = len(h2_tracking) - n_h2_dep
print(f"\nH2: L-dependent={n_h2_dep}, L-independent={n_h2_indep}")

# ── Track naive modes ──
L20_naive = all_naive[20]
ref_naive_strip = L20_naive['strip']

# Track each naive strip mode
naive_tracking = []
naive_records = []

for k in range(min(len(ref_naive_strip), 50)):
    z_ref = ref_naive_strip[k]
    rec = {'k': k, 'ref_eig': str(complex(z_ref))}
    logL_vals = []; re_vals = []; im_vals = []
    
    for L, N in SWEEP:
        d = all_naive[L]
        dists = np.abs(d['eig'] - z_ref)
        ni = int(np.argmin(dists))
        ne = complex(d['eig'][ni])
        rec[L] = {'eig': str(ne), 'dist': float(dists[ni])}
        logL_vals.append(np.log(L))
        re_vals.append(ne.real)
        im_vals.append(ne.imag)
    
    A = np.vstack([logL_vals, np.ones_like(logL_vals)]).T
    coeff_re = np.linalg.lstsq(A, re_vals, rcond=None)[0][0]
    coeff_im = np.linalg.lstsq(A, im_vals, rcond=None)[0][0]
    dep = abs(coeff_re) > 1e-2
    naive_records.append({'k': k, 'dRe_dlogL': float(coeff_re), 'dIm_dlogL': float(coeff_im), 'L_dependent': bool(dep)})

print(f"\n{'='*110}")
print("NAIVE (max-L2) TRACKING | dRe/dlogL ANALYSIS (fixed dx)")
print(f"{'='*110}")
print(f"{'k':>3s} | Re(10)   Re(20)   Re(40)   Re(80)   | dRe/dlogL    L-dep?   | Im(10)   Im(80)   | Strip type")

# Separate strip types:
# - negative-Re modes (the ones that also appear in H2 -> essential spectrum artifacts)
# - positive-Re modes (the true strip of the wrong realization)

n_naive_dep = 0; n_naive_indep = 0
for k in range(min(len(ref_naive_strip), 50)):
    z_ref = ref_naive_strip[k]
    logL_vals = []; re_vals = []; im_vals = []
    
    for L, N in SWEEP:
        d = all_naive[L]
        dists = np.abs(d['eig'] - z_ref)
        ni = int(np.argmin(dists))
        ne = complex(d['eig'][ni])
        logL_vals.append(np.log(L))
        re_vals.append(ne.real)
        im_vals.append(ne.imag)
    
    A = np.vstack([logL_vals, np.ones_like(logL_vals)]).T
    coeff_re = np.linalg.lstsq(A, re_vals, rcond=None)[0][0]
    coeff_im = np.linalg.lstsq(A, im_vals, rcond=None)[0][0]
    dep = abs(coeff_re) > 1e-2
    
    if dep: n_naive_dep += 1
    else: n_naive_indep += 1
    
    # Check if this is positive-Re or negative-Re
    re_at_20 = z_ref.real
    strip_type = "positive-Re" if re_at_20 > 0 else "negative-Re"
    
    print(f"{k:>3d} | {re_vals[0]:>+8.6f} {re_vals[1]:>+8.6f} {re_vals[2]:>+8.6f} {re_vals[3]:>+8.6f} | {coeff_re:>+11.6f} {'YES' if dep else 'NO':>8s} | {im_vals[0]:>+6.3f} {im_vals[3]:>+6.3f} | {strip_type}")

print(f"\nNaive: L-dependent={n_naive_dep}, L-independent={n_naive_indep}")

# ── Final classification ──
print(f"\n{'='*80}")
print("CLASSIFICATION")
print(f"{'='*80}")

# Check all origin-H2 modes
h2_all_dep = n_h2_dep == len(h2_tracking)
# Check sign of dRe/dlogL for all origin-H2 modes
h2_sign = np.mean([t['dRe_dlogL'] for t in h2_tracking])
h2_sign_neg = all(t['dRe_dlogL'] < 0 for t in h2_tracking)

print(f"Origin-H2: {n_h2_dep}/{len(h2_tracking)} modes L-dependent")
print(f"  Mean dRe/dlogL: {h2_sign:.4f}")
print(f"  All negative? {h2_sign_neg}")

# Check positive-Re naive modes vs negative-Re naive modes
naive_pos = [r for r in naive_records if all_naive[20]['strip'][r['k']].real > 0]
naive_neg = [r for r in naive_records if all_naive[20]['strip'][r['k']].real <= 0]
print(f"Naive positive-Re: {len(naive_pos)} modes")
if len(naive_pos) > 0:
    pos_sign = np.mean([r['dRe_dlogL'] for r in naive_pos])
    print(f"  Mean dRe/dlogL: {pos_sign:.4f}")
print(f"Naive negative-Re: {len(naive_neg)} modes")
if len(naive_neg) > 0:
    neg_sign = np.mean([r['dRe_dlogL'] for r in naive_neg])
    print(f"  Mean dRe/dlogL: {neg_sign:.4f}")

# Discriminator: do positive-Re naive modes behave differently from negative-Re (and H2)
if h2_sign_neg:
    print(f"\nTERMINAL: SWEEP-CONVERGENT — dRe/dlogL negative at fixed dx.")
    print(f"  Essential spectrum artifact CONFIRMED. v1's positive sign was resolution confound.")
    term = "SWEEP-CONVERGENT"
elif abs(h2_sign) < 1e-2:
    print(f"\nTERMINAL: SWEEP-CONFOUNDED — dRe/dlogL near zero at fixed dx.")
    print(f"  v1's positive sign was resolution confound. No growth, no shrink.")
    term = "SWEEP-CONFOUNDED"
else:
    print(f"\nTERMINAL: DISCRETIZATION-NONCONVERGENT — dRe/dlogL still positive at fixed dx.")
    print(f"  Fourier discretization on [-L,L] does not approach origin-H2 operator as L grows.")
    print(f"  ESCALATE TO FOUNDER before any F-4 v2 proposal.")
    term = "DISCRETIZATION-NONCONVERGENT"

# Save results
out = {
    'method': 'L-sweep v2 fixed dx, L∈{10,20,40,80} N∈{512,1024,2048,4096}',
    'ref_dx': ref_dx,
    'terminal': term,
    'origin_H2': {
        'n_L_dependent': n_h2_dep,
        'n_total': len(h2_tracking),
        'mean_dRe_dlogL': float(h2_sign),
        'all_negative': h2_sign_neg,
        'mode_details': h2_tracking,
    },
    'naive': {
        'n_positive_re_modes': len(naive_pos),
        'n_negative_re_modes': len(naive_neg),
    },
    'discriminator': {
        'positive_re_mean_dRe_dlogL': float(np.mean([r['dRe_dlogL'] for r in naive_pos])) if len(naive_pos) > 0 else 'N/A',
        'negative_re_mean_dRe_dlogL': float(np.mean([r['dRe_dlogL'] for r in naive_neg])) if len(naive_neg) > 0 else 'N/A',
    }
}
with open('work/l-sweep-v2-results.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nResults saved to work/l-sweep-v2-results.json")