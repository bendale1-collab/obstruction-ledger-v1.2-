#!/usr/bin/env python3
"""
Lambda=1 and Lambda=0 residual test on Xu closed-form eigenfunctions.
Current odd-basis and Defect-A-modified operator, L=20, N=1024.
$0 compute. No engine edits.
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

ft = FourierSpectralEngine(N, L)
xi = ft.x
Omega = -xi / (xi**2 + 0.25)
Op = ft.differentiate(Omega)
HO = ft.hilbert(Omega)
U = ft.integrate(HO)

def apply_L(v):
    vp = ft.differentiate(v)
    Hv = ft.hilbert(v)
    Uv = ft.integrate(Hv)
    return (1.0 * v + 1.0 * xi * vp - HO * v - Hv * Omega)

eps = 1e-5
L_full = np.zeros((M, M))
for j in range(M):
    v = np.zeros(M)
    v[j] = eps
    L_full[:, j] = apply_L(v) / eps

# Operators
rp = RealizationPair(N=N, L=L)
L_current = rp._build_operator(a=0.0, odd_basis=True)

R = np.zeros((M, M))
for i in range(M):
    R[i, M - 1 - i] = 1.0
P_odd = (np.eye(M) - R) / 2.0
L_odd_full = P_odd @ L_full @ P_odd
L_proj = L_odd_full[np.ix_(right_ix, right_ix)]

# Xu closed-form eigenfunctions
# phi_1 = dOmega/dxi for Omega = -2*xi/(1+xi^2) (the correct CLM profile)
# phi_0 = y*Omega' + Omega = -4*y/(1+y^2)^2
phi_1 = (-2 + 2*xi**2) / (1 + xi**2)**2
phi_0 = -4 * xi / (1 + xi**2)**2
phi_1_right = phi_1[right_ix]
phi_0_right = phi_0[right_ix]

# Compute residuals
def report(Lmat, phi, label):
    Lv = Lmat @ phi
    r = float(np.linalg.norm(Lv - phi) / (np.linalg.norm(phi) + 1e-30))
    abs_diff = np.abs(Lv - phi) + 1e-30
    abs_diff /= np.sum(abs_diff)
    xr = xi[right_ix]
    fo = float(np.sum(abs_diff[np.abs(xr) < 1.0]))
    fb = float(np.sum(abs_diff[np.abs(xr) > L/2]))
    return {'residual': r, 'frac_origin': fo, 'frac_boundary': fb}

r1_cur = report(L_current, phi_1_right, "")
r1_proj = report(L_proj, phi_1_right, "")
r0_cur = report(L_current, phi_0_right, "")
r0_proj = report(L_proj, phi_0_right, "")

print("LAMBDA=1 AND LAMBDA=0 RESIDUAL TEST")
print("="*70)
print(f"phi_1(xi) = (-2+2xi^2)/(1+xi^2)^2  (Xu Eq 3.7)")
print(f"phi_0(xi) = -4xi/(1+xi^2)^2        (Xu Sec 3.2)")
print()

print(f"Operator                     | λ   | ||Lv-v||/||v|| | near origin | near boundary")
print(f"-----------------------------|-----|---------------|-------------|--------------")
print(f"Current odd-basis            | λ=1 | {r1_cur['residual']:.4e}       | {r1_cur['frac_origin']:.4f}       | {r1_cur['frac_boundary']:.4f}")
print(f"Defect-A (symmetry proj)     | λ=1 | {r1_proj['residual']:.4e}       | {r1_proj['frac_origin']:.4f}       | {r1_proj['frac_boundary']:.4f}")
print(f"Current odd-basis            | λ=0 | {r0_cur['residual']:.4e}       | {r0_cur['frac_origin']:.4f}       | {r0_cur['frac_boundary']:.4f}")
print(f"Defect-A (symmetry proj)     | λ=0 | {r0_proj['residual']:.4e}       | {r0_proj['frac_origin']:.4f}       | {r0_proj['frac_boundary']:.4f}")

# Full naive for reference
Lv1_full = L_full @ phi_1
r1_full = float(np.linalg.norm(Lv1_full - phi_1) / np.linalg.norm(phi_1))
Lv0_full = L_full @ phi_0
r0_full = float(np.linalg.norm(Lv0_full - phi_0) / np.linalg.norm(phi_0))
print(f"Full naive (full domain)      | λ=1 | {r1_full:.4e}       |  ---      |  ---")
print(f"Full naive (full domain)      | λ=0 | {r0_full:.4e}       |  ---      |  ---")

# Full naive spatial distribution
ab1 = np.abs(Lv1_full - phi_1) + 1e-30
ab1 /= np.sum(ab1)
print(f"Full naive λ=1 |Lv-v| origin: {np.sum(ab1[np.abs(xi)<1.0]):.4f}  boundary: {np.sum(ab1[np.abs(xi)>L/2]):.4f}")

# Essential cluster controls
print(f"\n{'='*70}")
print("MISSING ESSENTIAL-CLUSTER CONTROLS (re-requested)")
print("="*70)

ev, vv = linalg.eig(L_current)
ev_f = ev[np.abs(ev) < 10.0]
vv_f = vv[:, np.abs(ev) < 10.0]
xr = xi[right_ix]

print(f"Current: {len(ev_f)} modes (|eig|<10)")
print(f"  |Im|>5:     {(np.abs(ev_f.imag) > 5).sum()} modes")
print(f"  |Im|>3:     {(np.abs(ev_f.imag) > 3).sum()} modes")
print(f"  |Im|>2:     {(np.abs(ev_f.imag) > 2).sum()} modes")
print(f"  20 strip:   {(ev_f.real > -0.499).sum()} modes (P0 zone)")

# Mass fractions for essential-spectrum-band modes (near Re = -0.5, various Im)
for re_min, re_max in [(-0.52, -0.49), (-0.49, -0.45), (-0.45, -0.35), (-0.35, -0.2), (-0.2, 0.0)]:
    idx = np.where((ev_f.real > re_min) & (ev_f.real < re_max))[0]
    if len(idx) == 0: 
        continue
    mins_in = []; mins_out = []
    for ix in idx[:min(5, len(idx))]:
        vn = vv_f[:, ix]
        vn = vn / (np.linalg.norm(vn) + 1e-30)
        mins_in.append(float(np.sum(np.abs(vn[np.abs(xr) < 1.0])**2)))
        mins_out.append(float(np.sum(np.abs(vn[np.abs(xr) > L/2])**2)))
    print(f"  Re∈[{re_min:.3f},{re_max:.3f}] n={len(idx):>3d}: m_in={np.mean(mins_in):.4f} m_out={np.mean(mins_out):.4f}")

print(f"\nResults saved.")