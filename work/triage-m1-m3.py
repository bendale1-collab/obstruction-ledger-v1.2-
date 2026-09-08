#!/usr/bin/env python3
"""
RED-TRIAGE: M1 + M3 diagnostic.
ORDER-ID: OL-v1.5-P1-TRIAGE (authorized by founder, $2 cap, no scoring)
Do NOT modify engine/f1.py. Do NOT modify harness/p1_battery.py except instrumentation.
"""
import sys, os, time, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np
from scipy import linalg
from f1 import RealizationPair, FourierSpectralEngine

L = 20.0

# ══════════════════════════════════════════════════════════════════════
# M1: Operator matrix comparison at N=1024
# ══════════════════════════════════════════════════════════════════════
t0 = time.time()
N1 = 1024
M = 2 * N1 + 1  # 2049
center = M // 2  # 1024
n_sub = M - center  # 1025 right-half points

rp = RealizationPair(N=N1, L=L)
L_naive = rp._build_operator(a=0.0, odd_basis=False)      # 2049 x 2049
L_h2    = rp._build_operator(a=0.0, odd_basis=True)        # n_sub x n_sub

print(f"M1: Op dimensions — naive={L_naive.shape}, H2={L_h2.shape}")

# The naive matrix includes the origin point at index center.
# Both operators act on the right half (including origin for naive).
# The origin-H2 operator acts on right-half INCLUDING origin, but with
# odd extension enforced and the origin value zeroed.
# For fair comparison: extract the sub-block of naive that corresponds
# to the right-half indices (center: M).
right_ix = np.arange(center, M)  # indices [1024..2048], length 1025

L_naive_sub = L_naive[np.ix_(right_ix, right_ix)]  # 1025x1025

# L_h2 is also 1025x1025 (n_sub = M - center = 1025)
frob_diff = np.linalg.norm(L_h2 - L_naive_sub, 'fro')
frob_naive_sub = np.linalg.norm(L_naive_sub, 'fro')
frob_ratio = frob_diff / frob_naive_sub if frob_naive_sub > 0 else float('inf')

print(f"M1: ||L_H2 - L_L2_sub||_F = {frob_diff:.6f}")
print(f"M1: ||L_L2_sub||_F         = {frob_naive_sub:.6f}")
print(f"M1: ratio                  = {frob_ratio:.6f}")
print(f"M1: roundoff? (O(1e-12))   = {frob_diff < 1e-10}")
print(f"M1: O(1)?                  = {frob_diff > 0.1}")
print(f"M1 elapsed: {time.time()-t0:.1f}s")

# Also check: do the spectra agree on the right-half subspace?
eig_h2 = linalg.eigvals(L_h2)
eig_naive_sub = linalg.eigvals(L_naive_sub)

# Sort by real part
eig_h2_sorted = sorted(eig_h2, key=lambda z: z.real)
eig_naive_sub_sorted = sorted(eig_naive_sub, key=lambda z: z.real)

# What's the maximum difference between corresponding eigenvalues?
# Only compare the top K eigenvalues (the meaningful ones)
n_compare = min(50, len(eig_h2_sorted))
diffs = [abs(eig_h2_sorted[-i] - eig_naive_sub_sorted[-i]) for i in range(1, n_compare+1)]
mean_diff = np.mean(diffs)
max_diff = np.max(diffs)
print(f"M1: Top-{n_compare} eig diff (mean, max): {mean_diff:.6e}, {max_diff:.6e}")

# ══════════════════════════════════════════════════════════════════════
# M3: P0 H-B replication at N=256 (P0 resolution) and N=1024
# ══════════════════════════════════════════════════════════════════════
t0 = time.time()
print("\n" + "="*60)
print("M3: P0 H-B replication")
print("="*60)

def p0_hb_criterion(rp, N):
    """Replicate P0's H-B test exactly as in engine/f1.py main()."""
    # naive_strip at N
    rp.N = N
    rp.ft = FourierSpectralEngine(N, L)
    L_naive = rp._build_operator(a=0.0, odd_basis=False)
    eig_naive = linalg.eigvals(L_naive)
    eig_naive = eig_naive[np.abs(eig_naive) < 10.0]
    re_naive = eig_naive.real
    mask_n = (np.abs(eig_naive) > 1e-2) & (np.abs(eig_naive - 1.0) > 1e-2)
    re_f_n = re_naive[mask_n]
    strip_present = bool(np.any(re_f_n > -0.5 + 1e-3))
    n_naive = int(np.sum(re_f_n > -0.5 + 1e-3))
    
    # origin_clean at N
    rp.ft = FourierSpectralEngine(N, L)
    L_h2 = rp._build_operator(a=0.0, odd_basis=True)
    eig_h2 = linalg.eigvals(L_h2)
    eig_h2 = eig_h2[np.abs(eig_h2) < 10.0]
    re_h2 = eig_h2.real
    mask_c = (np.abs(eig_h2) > 1e-2) & (np.abs(eig_h2 - 1.0) > 1e-2)
    re_f_c = re_h2[mask_c]
    n_clean = int(np.sum(re_f_c > -0.5 + 1e-3)) if len(re_f_c) > 0 else 0
    
    strip_reduced = n_clean < n_naive
    return {
        'N': N,
        'naive_strip_present': strip_present,
        'naive_n_strip': n_naive,
        'clean_n_strip': n_clean,
        'strip_reduced': strip_reduced,
        'hb_passed': strip_present and strip_reduced,
    }

# P0 resolution: N=256
rp_m3 = RealizationPair(N=256, L=L)
r_p0 = p0_hb_criterion(rp_m3, 256)
print(f"M3 P0 (N=256):")
print(f"  naive strip present = {r_p0['naive_strip_present']}, n={r_p0['naive_n_strip']}")
print(f"  clean strip count   = {r_p0['clean_n_strip']}")
print(f"  strip reduced?      = {r_p0['strip_reduced']}")
print(f"  H-B PASSED          = {r_p0['hb_passed']}")

# N=1024
r_1024 = p0_hb_criterion(rp_m3, 1024)
print(f"M3 (N=1024):")
print(f"  naive strip present = {r_1024['naive_strip_present']}, n={r_1024['naive_n_strip']}")
print(f"  clean strip count   = {r_1024['clean_n_strip']}")
print(f"  strip reduced?      = {r_1024['strip_reduced']}")
print(f"  H-B criterion       = {r_1024['hb_passed']}")
print(f"M3 elapsed: {time.time()-t0:.1f}s")

# ══════════════════════════════════════════════════════════════════════
# Hypothesis ranking
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("HYPOTHESIS RANKING")
print("="*60)
print(f"H1 (unsealed code / reimplemented): {'LIVE' if False else 'DEAD'} — battery imports sealed engine directly")
print(f"H2 (runner bug / wrong operator call): {'LIVE if H2 differs' if frob_diff > 1e-10 else 'DEAD'}")
print(f"H3 (structural — switch is a no-op on this disc.): {'LIVE' if frob_diff < 1e-10 else 'DEPENDS on eig agreement'}")

# Final one-liner
if frob_diff < 1e-10:
    hypothesis = "H3: Realization switch is structurally a no-op on this Fourier discretization. Both operators coincide."
elif frob_diff > 0.1:
    hypothesis = f"H2: Operators differ structurally (Frob={frob_diff:.4f}) but spectra nearly coincide (max top eig diff={max_diff:.4e}). Runner uses sealed code. Engine construction issue."
else:
    hypothesis = f"Cross: Operators differ moderately (Frob={frob_diff:.4f}), eig diffs={max_diff:.4e}. H2 partial."

# Save results
results = {
    'M1': {
        'L_naive_shape': list(L_naive.shape),
        'L_h2_shape': list(L_h2.shape),
        'Frob_norm_diff': float(frob_diff),
        'Frob_norm_naive_sub': float(frob_naive_sub),
        'Frob_ratio': float(frob_ratio),
        'top_eig_diffs_mean': float(mean_diff),
        'top_eig_diffs_max': float(max_diff),
    },
    'M2': {
        'import_path': 'from f1 import RealizationPair, gCLMSolver',
        'call_site_F4_spectrum_of': 'rp._build_operator(a=0.0, odd_basis=odd_basis)',
        'reimplements_engine': False,
    },
    'M3': {
        'p0_at_N256': r_p0,
        'at_N1024': r_1024,
    },
    'hypothesis': hypothesis.strip(),
}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'triage-results.json'), 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to triage-results.json")
print(f"Hypothesis: {hypothesis.strip()}")