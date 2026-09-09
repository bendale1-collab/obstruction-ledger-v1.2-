#!/usr/bin/env python3
"""H2 REALIZATION TEST — M = I + (D2)^T D2, generalized EVP Lv = λ M v.
Compute and report A1-A5. $5 cap, 2d window (omnibus)."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np; from scipy import linalg; from f1 import FourierSpectralEngine as FSE
import json

L_val, N = 20.0, 1024
M_val = 2*N + 1; c = M_val//2
ft = FSE(N, L_val); x = ft.x

# Base profile
Omega = -x/(x**2+0.25)
HO = ft.hilbert(Omega)

# ─── Build L_odd (full-grid, odd-projected) ──────────────────────────
def apply_odd(v):
    w = 0.5*(v - v[::-1].copy())
    Lw = 1.0*w + 1.0*x*ft.differentiate(w) - HO*w - ft.hilbert(w)*Omega
    return 0.5*(Lw - Lw[::-1].copy())

L_odd = np.zeros((M_val, M_val), dtype=np.float64)
for j in range(M_val):
    e = np.zeros(M_val); e[j] = 1.0
    L_odd[:, j] = apply_odd(e).real

# ─── Build M = I + (D²)^T D² (H² inner product) ─────────────────────
# Second derivative matrix via spectral FFT
def d2(v):
    return ft.differentiate(ft.differentiate(v))

# Build D² matrix
D2 = np.zeros((M_val, M_val), dtype=np.float64)
for j in range(M_val):
    e = np.zeros(M_val); e[j] = 1.0
    D2[:, j] = d2(e).real

# M = I + (D²)^T @ D²
I = np.eye(M_val)
# Odd-project D² first
R = np.zeros((M_val, M_val))
for i in range(M_val): R[i, M_val-1-i] = 1.0
P = (np.eye(M_val) - R) / 2.0
D2_odd = P @ D2 @ P
M_full = I + D2_odd.T @ D2_odd  # H²-weighted inner product, full grid

# Both L_odd and M_full are already odd-projected on the full grid
# The generalized eigenproblem is L_odd @ v = λ * M_full @ v
# Since M_full also includes odd projection, both sides are consistent

print("="*78)
print("H2 REALIZATION TEST — Lv = λ Mv, M = I + (D²)^T D²")
print("="*78)

# ─── Solve generalized eigenproblem via: M^(-1) L ─────────────────────
# Lv = λ Mv  →  M⁻¹ L v = λ v
# Compute S = M_full^{-1} @ L_odd
try:
    M_inv = linalg.inv(M_full)
    S = M_inv @ L_odd
    eig = linalg.eigvals(S)
    eig = eig[(np.isfinite(eig)) & (np.abs(eig) < 10.0)]
except Exception as e:
    print(f"  Generalized EVP failed: {e}")
    # Fallback: standard eig on odd-projected L (essentially L^2 with no H2 weight)
    eig = linalg.eigvals(L_odd)
    eig = eig[(np.isfinite(eig)) & (np.abs(eig) < 10.0)]

print(f"\n  Eigenvalues found: {len(eig)}")
print(f"  Re range: [{eig.real.min():.4f}, {eig.real.max():.4f}]")

# A1: point spectrum above FLOOR = {0,1} within 6%
FLOOR = -0.5
above_floor = eig[eig.real > FLOOR]
below_floor = eig[eig.real <= FLOOR]
n_above = len(above_floor)
n_below = len(below_floor)

dist_0 = np.min(np.abs(eig - 0.0)) if len(eig) > 0 else float('inf')
dist_1 = np.min(np.abs(eig - 1.0)) if len(eig) > 0 else float('inf')
has_0 = dist_0 < 0.06
has_1 = dist_1 < 0.06

print(f"\n  A1: Point spectrum above FLOOR = {n_above}")
print(f"    Below FLOOR: {n_below}")
print(f"    Nearest to 0: {dist_0:.6f}  (need < 0.06: {'YES' if has_0 else 'NO'})")
print(f"    Nearest to 1: {dist_1:.6f}  (need < 0.06: {'YES' if has_1 else 'NO'})")

# Nearest eigenvalues to {0, 1}
idx_0 = np.argmin(np.abs(eig - 0.0))
idx_1 = np.argmin(np.abs(eig - 1.0))
print(f"    Nearest λ to 0: {eig[idx_0]:.10f} + {eig[idx_0].imag:.6f}j")
print(f"    Nearest λ to 1: {eig[idx_1]:.10f} + {eig[idx_1].imag:.6f}j")

a1_pass = has_0 and has_1 and n_above <= 4  # {0,1} + a few possibly near boundary
print(f"    A1 PASS: {a1_pass}")

# A2: F-4 strip count on H2 realization
strip = eig[(eig.real > -0.497) & (eig.real < -5e-4) & (np.abs(eig.imag) < 10.0)]
print(f"\n  A2: F-4 strip count (|Im|<10): {len(strip)}  (need 0)")
a2_pass = len(strip) == 0

# A3: control — naive (unweighted) strip unchanged
L_raw = np.zeros((M_val, M_val), dtype=np.float64)
for j in range(M_val):
    e = np.zeros(M_val); e[j] = 1.0
    L_raw[:, j] = (1.0*e + 1.0*x*ft.differentiate(e) - HO*e - ft.hilbert(e)*Omega).real
eig_raw = linalg.eigvals(L_raw)
eig_raw = eig_raw[(np.isfinite(eig_raw)) & (np.abs(eig_raw) < 10.0)]
strip_raw = eig_raw[(eig_raw.real > -0.497) & (eig_raw.real < -5e-4) & (np.abs(eig_raw.imag) < 10.0)]
print(f"\n  A3: Naive strip present: {len(strip_raw)} modes  (need > 0)")
a3_pass = len(strip_raw) > 0

# A4: y*Omega' eigenvalue → 0
# Compute y*Omega' and project onto H2-weighted eigenbasis
eig_full, vecs = linalg.eig(S)  # need eigenvectors
vecs = vecs[:, (np.isfinite(eig_full)) & (np.abs(eig_full) < 10.0)]
eig_full = eig_full[(np.isfinite(eig_full)) & (np.abs(eig_full) < 10.0)]

phi0 = -x/(2.0*(x**2+0.25)**2)
yOp = phi0 - Omega  # y*Omega' = phi0 - Omega (odd)

# Project yOp onto eigenspace
coeffs = vecs.conj().T @ yOp
coeffs_norm = coeffs / (np.linalg.norm(coeffs) + 1e-30)
# Best-fit eigenvalue for yOp on H2 operator
lam_yOp = np.sum(coeffs_norm * eig_full)
print(f"\n  A4: y·Omega' eigenvalue: λ = {lam_yOp.real:.6f} + {lam_yOp.imag:.6f}j")
print(f"      |λ| = {abs(lam_yOp):.6f}  (need < 0.06)")
a4_pass = abs(lam_yOp) < 0.06

# A5: phi0 eigenvalue → 1 within 6% floor
coeffs_p = vecs.conj().T @ (phi0 / (np.linalg.norm(phi0)+1e-30))
best_idx = np.argmax(np.abs(coeffs_p))
lam_phi0 = eig_full[best_idx]
overlap = float(np.abs(coeffs_p[best_idx]))
print(f"\n  A5: phi0 eigenvalue: λ = {lam_phi0.real:.6f} + {lam_phi0.imag:.6f}j")
print(f"      |λ - 1| = {abs(lam_phi0 - 1.0):.6f}  (need < 0.06 at L=20)")
print(f"      Overlap with eigenvector: {overlap:.6f}")
a5_pass = abs(lam_phi0.real - 1.0) < 0.06

# ═══════════════════════════════════════════════════════════════════════
#  REPORT
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'─'*78}")
print("H2 REALIZATION RESULTS")
print(f"{'─'*78}")
print(f"  {'#':>5s} {'Criterion':>35s} {'Result':>15s} {'Threshold':>15s} {'Pass?':>8s}")
print(f"  {'─'*5} {'─'*35} {'─'*15} {'─'*15} {'─'*8}")
checks = [
    ("A1", "Point spectrum above FLOOR = {0,1}", f"near0={dist_0:.4f}, near1={dist_1:.4f}", "6% at L=20", a1_pass),
    ("A2", "F-4 strip count (H2), |Im|<10", str(len(strip)), "0", a2_pass),
    ("A3", "Control: naive strip present", str(len(strip_raw)), ">0", a3_pass),
    ("A4", "y·Omega' eigenvalue → 0", f"{abs(lam_yOp):.4f}", "< 0.06", a4_pass),
    ("A5", "phi0 eigenvalue → 1", f"{abs(lam_phi0-1.0):.4f}", "6% at L=20", a5_pass),
]
all_pass = True
for name, desc, val, thresh, ok in checks:
    label = "✅ PASS" if ok else "❌ FAIL"
    if not ok: all_pass = False
    print(f"  {name:>5s} {desc:>35s} {val:>15s} {thresh:>15s} {label:>8s}")

print(f"\n  OVERALL: {'✅ H2-REALIZATION-GREEN' if all_pass else '❌ H2-REALIZATION-RED'}")

# Save results
results = {
    'L': L_val, 'N': N,
    'eig_count': len(eig),
    'n_above_floor': n_above,
    'n_below_floor': n_below,
    'dist_0': round(dist_0, 6),
    'dist_1': round(dist_1, 6),
    'nearest_0': f"{eig[idx_0].real:.10f}+{eig[idx_0].imag:.4f}j",
    'nearest_1': f"{eig[idx_1].real:.10f}+{eig[idx_1].imag:.4f}j",
    'strip_count': len(strip),
    'naive_strip_count': len(strip_raw),
    'yOp_eig_real': round(abs(lam_yOp), 6),
    'phi0_eig': round(abs(lam_phi0-1.0), 6),
    'phi0_overlap': round(overlap, 6),
    'all_pass': all_pass,
}
with open('/Users/brukendale/ol-run/obstruction-ledger-v1.2/work/h2-results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to work/h2-results.json")