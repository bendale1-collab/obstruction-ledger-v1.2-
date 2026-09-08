#!/usr/bin/env python3
"""Diagnostic characterization of F-4 failure (not a scored test)."""
import sys, numpy as np
sys.path.insert(0, '/Users/brukendale/ol-run/obstruction-ledger-v1.2/engine')
from f1 import RealizationPair
from scipy import linalg

rp = RealizationPair(N=1024, L=20.0)
FLOOR = -0.497
DELTA = 5e-4

L_clean = rp._build_operator(a=0.0, odd_basis=True)
eig_clean = linalg.eigvals(L_clean)
re_clean = eig_clean.real

in_zone_mask = (re_clean > FLOOR) & (re_clean < -DELTA)
print(f"Total clean eig: {len(eig_clean)}")
print(f"In-zone (FLOOR, -5e-4) count: {int(in_zone_mask.sum())}")

zone_eigs = eig_clean[in_zone_mask]
order = np.argsort(-zone_eigs.real)
print("\nTop 12 in-zone eigenvalues (Re, Im):")
for z in zone_eigs[order][:12]:
    print(f"  Re={z.real:+.6f}  Im={z.imag:+.4f}")

below_floor = eig_clean[re_clean < FLOOR]
print(f"\nBelow FLOOR: n={len(below_floor)}, mean Re={below_floor.real.mean():.6f}")

for target, name in [(0.0, '0'), (1.0, '1')]:
    dist = np.abs(eig_clean - target)
    idx = np.argmin(dist)
    print(f"Nearest to {name}: Re={eig_clean[idx].real:.6f} Im={eig_clean[idx].imag:.4f} dist={dist[idx]:.6f}")

# Compare naive vs clean: are the SAME eigenvalues appearing?
L_naive = rp._build_operator(a=0.0, odd_basis=False)
eig_naive = linalg.eigvals(L_naive)
re_naive = eig_naive.real
nz_naive = int(((re_naive > FLOOR) & (re_naive < -DELTA)).sum())
print(f"\nNaive in-zone count: {nz_naive}")
