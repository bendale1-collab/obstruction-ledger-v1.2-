#!/usr/bin/env python3
"""
Defect A fix diagnostic — compare current odd-basis construction with
symmetry-projection approach. No engine edits to f1.py done yet —
this is the diagnostic to determine the correct fix.
$0 compute. No engine mods.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np
from scipy import linalg
from f1 import RealizationPair, FourierSpectralEngine

N = 1024; L = 20.0
M = 2*N + 1
center = M // 2
right_ix = np.arange(center, M)
n_sub = len(right_ix)

ft = FourierSpectralEngine(N, L)
x = ft.x
Omega = -x / (x**2 + 0.25)
Op = ft.differentiate(Omega)
HO = ft.hilbert(Omega)
U = ft.integrate(HO)

def apply_L(v):
    vp = ft.differentiate(v)
    Hv = ft.hilbert(v)
    Uv = ft.integrate(Hv)
    return (1.0 * v + 1.0 * x * vp
            - HO * v - Hv * Omega)

# Build full naive operator
eps = 1e-5
L_full = np.zeros((M, M))
for j in range(M):
    v = np.zeros(M)
    v[j] = eps
    L_full[:, j] = apply_L(v) / eps

# 1) CURRENT odd-basis construction (right half + odd extension + zero center)
L_current = np.zeros((n_sub, n_sub))
def apply_L_odd_current(v_sub):
    v_full = np.zeros(M)
    v_full[right_ix] = v_sub
    for i_r, ix in enumerate(right_ix):
        j = M - 1 - ix
        if j < center:
            v_full[j] = -v_sub[i_r]
    idx0 = np.argmin(np.abs(x))
    v_full[idx0] = 0.0
    Lv = apply_L(v_full)
    return Lv[right_ix]

for j in range(n_sub):
    v = np.zeros(n_sub)
    v[j] = eps
    L_current[:, j] = apply_L_odd_current(v) / eps

eig_current = linalg.eigvals(L_current)

# 2) SYMMETRY PROJECTION approach
R = np.zeros((M, M))
for i in range(M):
    R[i, M - 1 - i] = 1.0
P = (np.eye(M) - R) / 2.0
L_odd_proj = P @ L_full @ P  # Full M×M projected operator

# Restrict to right half
L_proj = L_odd_proj[np.ix_(right_ix, right_ix)]
eig_proj = linalg.eigvals(L_proj)

# 3) COMPARE eigenvalues
print("=" * 80)
print("DEFECT A DIAGNOSTIC — Odd-basis operator comparison")
print("=" * 80)

# Filter |eig| < 10
filt_cur = np.abs(eig_current) < 10.0
filt_proj = np.abs(eig_proj) < 10.0
ec = eig_current[filt_cur]
ep = eig_proj[filt_proj]

print(f"\nCurrent: {len(ec)} eigenvalues (|eig|<10)")
print(f"Projected: {len(ep)} eigenvalues (|eig|<10)")

# Nearest to 1
n1_cur = ec[np.argmin(np.abs(ec - 1.0))]
n1_proj = ep[np.argmin(np.abs(ep - 1.0))]
print(f"\nNearest to λ=1:")
print(f"  Current:  {n1_cur.real:.6f}{n1_cur.imag:+.6f}j  (dist={abs(n1_cur - 1.0):.6e})")
print(f"  Projected: {n1_proj.real:.6f}{n1_proj.imag:+.6f}j  (dist={abs(n1_proj - 1.0):.6e})")

# Nearest to 0
n0_cur = ec[np.argmin(np.abs(ec))]
n0_proj = ep[np.argmin(np.abs(ep))]
print(f"\nNearest to λ=0:")
print(f"  Current:  {n0_cur.real:.6f}{n0_cur.imag:+.6f}j  (dist={abs(n0_cur):.6e})")
print(f"  Projected: {n0_proj.real:.6f}{n0_proj.imag:+.6f}j  (dist={abs(n0_proj):.6e})")

# Frobenius norm difference between matrices
frob_diff = np.linalg.norm(L_proj - L_current, 'fro')
frob_norm_cur = np.linalg.norm(L_current, 'fro')
print(f"\nMatrix comparison:")
print(f"  ||L_proj - L_current||_F = {frob_diff:.6f}")
print(f"  ||L_current||_F = {frob_norm_cur:.6f}")
print(f"  Ratio = {frob_diff/frob_norm_cur:.6f}")

# Full-domain naive nearest to 1
L_full_eig = linalg.eigvals(L_full)
L_full_eig_f = L_full_eig[np.abs(L_full_eig) < 10.0]
n1_full = L_full_eig_f[np.argmin(np.abs(L_full_eig_f - 1.0))]
print(f"\nFull naive nearest λ=1: {n1_full.real:.6f}{n1_full.imag:+.6f}j  (dist={abs(n1_full - 1.0):.6e})")

# Check: does the FULL operator have ANY eigenvalue near 1?
within_5e4 = np.sum(np.abs(L_full_eig_f - 1.0) < 5e-4)
within_1e2 = np.sum(np.abs(L_full_eig_f - 1.0) < 0.1)
print(f"  Full naive: {within_5e4} eigenvalues within 5e-4 of 1, {within_1e2} within 0.1 of 1")

# Also check the unprojected P @ L_full @ P restricted — does λ=1 appear?
# The odd subspace should have λ=1 if it exists in the continuous operator
print(f"\nFull projected operator eigenvalues near λ=1:")
ep_within_1 = ep[np.abs(ep - 1.0) < 0.3]
for z in sorted(ep_within_1, key=lambda z: abs(z-1.0)):
    print(f"  λ = {z.real:.6f}{z.imag:+.6f}j  (dist={abs(z - 1.0):.6e})")

print(f"\nCurrent operator eigenvalues near λ=1:")
ec_within_1 = ec[np.abs(ec - 1.0) < 0.3]
for z in sorted(ec_within_1, key=lambda z: abs(z-1.0)):
    print(f"  λ = {z.real:.6f}{z.imag:+.6f}j  (dist={abs(z - 1.0):.6e})")