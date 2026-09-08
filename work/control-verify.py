#!/usr/bin/env python3
"""Verify Φ₀ is an exact eigenvector of L_cur at λ=-0.470182."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np
from scipy import linalg
from f1 import RealizationPair, FourierSpectralEngine

N=1024; L=20.0; M=2*N+1; center=M//2
right_ix = np.arange(center, M)
rp = RealizationPair(N=N, L=L)
x = rp.ft.x

L_cur = rp._build_operator(a=0.0, odd_basis=True)
eig, vec = linalg.eig(L_cur)
phi0_r = (-x / (2*(x**2+0.25)**2))[right_ix]

Lv = L_cur @ phi0_r
# Find best-fit λ
lam_fit = float(np.vdot(Lv, phi0_r).real / (np.vdot(phi0_r, phi0_r)+1e-30))
resid = float(np.linalg.norm(Lv - lam_fit*phi0_r) / np.linalg.norm(phi0_r))

phi1_even_r = ((x**2-0.25)/(x**2+0.25)**2)[right_ix]
Lv1 = L_cur @ phi1_even_r
lam1_fit = float(np.vdot(Lv1, phi1_even_r).real / (np.vdot(phi1_even_r, phi1_even_r)+1e-30))
resid1 = float(np.linalg.norm(Lv1 - lam1_fit*phi1_even_r) / np.linalg.norm(phi1_even_r))

print(f"φ₀ best-fit λ = {lam_fit:.6f}, residual = {resid:.6e}")
print(f"φ₁ (even) best-fit λ = {lam1_fit:.6f}, residual = {resid1:.6e}")
print()
print(f"Engine λ=0 eigenvector: λ = {eig[np.argmin(np.abs(eig))]:.10f}")
print(f"Engine nearest to λ=1:  λ = {eig[np.argmin(np.abs(eig-1.0))].real:.6f}")
print(f"  (dist = {abs(np.min(np.abs(eig-1.0))):.2e})")
print(f"φ₁ even projection onto engine eigenspace (top 3):")
ovs = [(j, abs(np.vdot(phi1_even_r/(np.linalg.norm(phi1_even_r)+1e-30).conj(), vec[:,j]/(np.linalg.norm(vec[:,j])+1e-30)))) for j in range(len(eig))]
for j,ov in sorted(ovs, key=lambda x: -x[1])[:3]:
    print(f"  λ = {eig[j].real:.6f}{eig[j].imag:+.6f}j  overlap = {ov:.6f}")