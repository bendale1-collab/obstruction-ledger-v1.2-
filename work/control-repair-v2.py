#!/usr/bin/env python3
"""
Control Repair v2 — odd λ=1 mode test.
The odd λ=1 closed form is NOT available from Xu 2607.19762 — 
Theorem 2 states its existence, Eq 3.7 gives only the EVEN translation mode.
Scan for candidate odd functions overlapping with the eigenspace.
$0 compute.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np
from scipy import linalg
from f1 import RealizationPair, FourierSpectralEngine

N=1024; L=20.0; M=2*N+1; center=M//2
right_ix = np.arange(center, M)
rp = RealizationPair(N=N, L=L)
ft = FourierSpectralEngine(N, L)
x = ft.x; xr = x[right_ix]

L_cur = rp._build_operator(a=0.0, odd_basis=True)
eig, vec_all = linalg.eig(L_cur)

# Search: what eigenvectors have eigenvalue near 1?
e_f = eig[np.abs(eig) < 10.0]
v_f = vec_all[:, np.abs(eig) < 10.0]

idx_sort = np.argsort(np.abs(e_f - 1.0))
print("Eigenvectors closest to λ=1 on odd-basis operator:")
print(f"{'idx':>3s} {'λ Re':>12s} {'λ Im':>12s} {'|λ-1|':>10s} {'m_in':>8s} {'m_out':>8s} {'parity':>8s}")
for i in idx_sort[:15]:
    lam = e_f[i]
    v = v_f[:, i]
    vn = v / (np.linalg.norm(v)+1e-30)
    mi = float(np.sum(np.abs(vn[np.abs(xr) < 1.0])**2))
    mo = float(np.sum(np.abs(vn[np.abs(xr) > L/2])**2))
    # Parity: extend to full grid and check
    v_full = np.zeros(M, dtype=np.complex128)
    v_full[right_ix] = vn
    v_full[:center] = -vn[-1:center-1:-1] if center > 0 else v_full[:center]
    odd_err = float(np.linalg.norm(v_full + v_full[::-1]) / (np.linalg.norm(v_full)+1e-30) if M > 0 else 0)
    print(f"{i:>3d} {lam.real:12.6f} {lam.imag:12.6f} {abs(lam-1.0):10.4f} {mi:8.4f} {mo:8.4f} {'ODD' if odd_err < 1e-10 else 'even':>8s}")