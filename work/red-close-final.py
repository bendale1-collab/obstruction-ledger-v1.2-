#!/usr/bin/env python3
"""
RED-CLOSE FINAL — clean four-count table, characterization, {1} eigenvalue, rescope.
No engine edits. Report only.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np
from scipy import linalg
from f1 import RealizationPair, FourierSpectralEngine

L = 20.0; FLOOR = -0.497; DELTA = 5e-4; P0_THRESH = -0.5 + 1e-3

def count_F4(eig):
    re = eig.real; mask = (re > FLOOR) & (re < -DELTA); ok = mask.copy()
    for idx in np.where(mask)[0]:
        z = eig[idx]
        if abs(z) < DELTA or abs(z - 1.0) < DELTA: ok[idx] = False
    return int(np.sum(ok))

def count_P0(eig):
    re = eig.real
    return int(np.sum((re > P0_THRESH) & (np.abs(eig) > 1e-2) & (np.abs(eig - 1.0) > 1e-2)))

rp = RealizationPair(N=1024, L=L)
L_naive = rp._build_operator(a=0.0, odd_basis=False)
L_h2    = rp._build_operator(a=0.0, odd_basis=True)
eig_n = linalg.eigvals(L_naive)
eig_h = linalg.eigvals(L_h2)
eig_nf = eig_n[np.abs(eig_n) < 10.0]
eig_hf = eig_h[np.abs(eig_h) < 10.0]

print("="*70)
print("FOUR COUNTS — SAME MATRICES, TWO CRITERIA (N=1024)")
print("="*70)
print(f"  {'':>18s}  {'F-4 zone':>12s}  {'P0 zone':>12s}")
print(f"  {'':>18s}  {f'({FLOOR}, -{DELTA})':>12s}  {f'(Re > {P0_THRESH})':>12s}")
print(f"  {'─'*46}")
print(f"  {'No |eig|<10 filter:':>18s}")
print(f"  {'Naive (full)':>18s}  {count_F4(eig_n):>10d}        {count_P0(eig_n):>8d}")
print(f"  {'Origin-H2':>18s}  {count_F4(eig_h):>10d}        {count_P0(eig_h):>8d}")
print(f"  {'':>18s}")
print(f"  {'With |eig|<10 filter:':>18s}")
print(f"  {'Naive (full)':>18s}  {count_F4(eig_nf):>10d}        {count_P0(eig_nf):>8d}")
print(f"  {'Origin-H2':>18s}  {count_F4(eig_hf):>10d}        {count_P0(eig_hf):>8d}")

# F-4 strip mode characterization
def describe_strip(eig, label):
    re = eig.real
    mask = (re > FLOOR) & (re < -DELTA); ok = mask.copy()
    for idx in np.where(mask)[0]:
        z = eig[idx]
        if abs(z) < DELTA or abs(z - 1.0) < DELTA: ok[idx] = False
    s = eig[ok]; im = abs(s.imag)
    print(f"\n  {label}: {len(s)} F-4 strip modes, Im ∈ [{im.min():.1f}, {im.max():.1f}]")
    print(f"    |Im|<10 (physical): {(im < 10).sum()}  |Im|≥10 (artifact): {(im >= 10).sum()}")

describe_strip(eig_n, "Naive (unfiltered)")
describe_strip(eig_h, "Origin-H2 (unfiltered)")

# ALSO check: the P0 strip modes WITH |eig|<10 filter are the "real" ones
def describe_P0_strip(eig, label, count_this_set=False):
    re = eig.real
    s = eig[(re > P0_THRESH) & (np.abs(eig) > 1e-2) & (np.abs(eig - 1.0) > 1e-2)]
    im = abs(s.imag)
    print(f"  {label} (P0 zone, |eig|<10): {len(s)} modes")
    print(f"    Re ∈ [{s.real.min():+.6f}, {s.real.max():+.6f}]  Im ∈ [{im.min():.1f}, {im.max():.1f}]")
    return s

print()
print("P0 strip modes (the 'real' ones, |eig|<10 filter):")
s_n = describe_P0_strip(eig_nf, "Naive")
s_h = describe_P0_strip(eig_hf, "Origin-H2")
print(f"  Ratio H2/Naive: {len(s_h)}/{len(s_n)} = {len(s_h)/len(s_n):.2f} (~2x reduction)")

# Check overlap
common = sum(1 for z in s_h if np.min(np.abs(eig_nf - z)) < 1e-10)
print(f"  Origin-H2 subset of naive: {common}/{len(s_h)} ({100*common/len(s_h):.0f}%)")

# DOUBLING
print()
print("="*70)
print("DOUBLING STABILITY (P0 zone, |eig|<10): 1024 -> 2048")
print("="*70)
for N in [1024, 2048]:
    rp2 = RealizationPair(N=N, L=L)
    e_n = linalg.eigvals(rp2._build_operator(a=0.0, odd_basis=False))
    e_h = linalg.eigvals(rp2._build_operator(a=0.0, odd_basis=True))
    e_nf2 = e_n[np.abs(e_n) < 10.0]
    e_hf2 = e_h[np.abs(e_h) < 10.0]
    nn = count_P0(e_nf2); nh = count_P0(e_hf2)
    print(f"  N={N}: naive={nn}, H2={nh}, ratio={nh/nn:.2f}")

# {1} EIGENVALUE
print()
print("="*70)
print("{1} EIGENVALUE")
print("="*70)
for N in [1024, 2048]:
    rp_n = RealizationPair(N=N, L=L)
    e_n = linalg.eigvals(rp_n._build_operator(a=0.0, odd_basis=False))
    e_h = linalg.eigvals(rp_n._build_operator(a=0.0, odd_basis=True))
    e_nf = e_n[np.abs(e_n) < 10.0]
    e_hf = e_h[np.abs(e_h) < 10.0]
    
    for label, e in [("Naive (|eig|<10)", e_nf), ("Naive (all)", e_n),
                     ("H2 (|eig|<10)", e_hf), ("H2 (all)", e_h)]:
        nearest = e[np.argmin(np.abs(e - 1.0))]
        if np.any(np.abs(e - 1.0) < 1e-10):
            print(f"  N={N} {label}: {1} EXACT (dist=0)")
        else:
            print(f"  N={N} {label}: nearest = {nearest.real:.6f}{nearest.imag:+.6f}j, dist={abs(nearest-1.0):.4e}")

# Time-shift mode parity
print()
ft = FourierSpectralEngine(256, L)
xi, dx = ft.x, ft.differentiate
Omega = -2*xi/(1 + xi**2)
dOmega = dx(Omega)
idx0 = len(xi)//2
r = dOmega[idx0+1]/dOmega[idx0-1] if abs(dOmega[idx0-1]) > 1e-10 else 0
print(f"Time-shift mode dΩ/dξ: dΩ(0)={dOmega[idx0]:.4f}, ratio={r:+.4f} {'EVEN' if abs(r-1)<1e-4 else 'not even?'}")

# Rescope proposal
print()
print("="*70)
print("RESCOPE PROPOSAL (report only, no build)")
print("="*70)
print("""
How to impose origin-H2 domain condition as a CONSTRAINT rather than parity restriction:

A — Boundary constraint rows (simplest):
  Add Ω(0)=0, Ω'(0)=0 as explicit constraint rows to the linearized
  eigenvalue problem. Cost: 2 extra rows, QR or nullspace projection
  in eigensolver. ~20 lines.

B — Weighted Sobolev inner product (most principled):
  Solve the generalized eigenvalue problem A v = λ B v where B weights
  the H^2(R+) inner product at x=0 via tanh(x/ε). Eigenvalues λ→0 as
  weight→0 at origin. Cost: build B matrix, scipy.linalg.eigh(A,B).
  ~15 lines.

C — Exterior mapping (replaces mesh):
  Map (-L,L)→(-1,1) via x = L*tanh(πξ/2), cluster grid points at x=0,
  enforce odd basis + spectral vanishing at origin simultaneously.
  Cost: new mesh class, existing engine otherwise unchanged. ~10 lines.
""")
print("═"*70)
print("VERDICT: ENGINE-RED (unchanged). P1 Leg A requires new engine construction,")
print("new pre-registration, new cap. CLOSED.")
print("═"*70)