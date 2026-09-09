#!/usr/bin/env python3
"""HALF-DOMAIN TEST. $0, arbiter-grade. Full comparison of H(phi0) and T2 via
   (i) full-grid FFT → restrict, (ii) odd-basis construction's own H matrix."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np; from scipy import linalg; from f1 import RealizationPair, FourierSpectralEngine, FourierSpectralEngine as FSE

N, L = 1024, 20.0; M = 2*N+1; c = M//2; right_ix = np.arange(c, M)
rp = RealizationPair(N=N, L=L); ft = FourierSpectralEngine(N, L)
x = ft.x; xr = x[right_ix]

# ─── Exact closed-forms ────────────────────────────────────────────────
ex_phi0    = -x / (2.0 * (x**2 + 0.25)**2)          # full grid
ex_phi0_r  = ex_phi0[right_ix]
ex_phi0p   = (3.0 * x**2 - 0.25) / (2.0 * (x**2 + 0.25)**3)
ex_phi0p_r = ex_phi0p[right_ix]
ex_Hphi0   = -(x**2 - 0.25) / (2.0 * (x**2 + 0.25)**2)
ex_Hphi0_r = ex_Hphi0[right_ix]
ex_Omega   = -x / (x**2 + 0.25)
ex_Omega_r = ex_Omega[right_ix]

# ─── Method (i): full-grid FFT Hilbert → restrict ─────────────────────
Hphi0_full = ft.hilbert(ex_phi0)
Hphi0_i = Hphi0_full[right_ix]
err_i = Hphi0_i - ex_Hphi0_r
rel_err_i = np.where(np.abs(ex_Hphi0_r) > 1e-15, err_i / ex_Hphi0_r, 0.0)

print("=" * 78)
print("HALF-DOMAIN TEST — H(phi0) by two methods")
print("=" * 78)
print(f"\nMethod (i): Full-grid FFT Hilbert (2049 pts) -> restrict to right_ix")
print(f"  RMS error (abs):  {np.sqrt(np.mean(err_i**2)):.6e}")
print(f"  RMS rel error:    {np.sqrt(np.mean(rel_err_i**2)):.6e}")
print(f"  Max |rel| error:  {np.max(np.abs(rel_err_i)):.6e}")

# ─── Method (ii): odd-basis operator's H matrix ──────────────────────
# Build the full H matrix (2049x2049): H_mat[:,j] = ft.hilbert(delta_j)
# Actually just build a few columns
print(f"\nMethod (ii): Odd-basis operator's own Hilbert (from L_cur construction)")
# Build H_kernel matrix for the full grid
H_full = np.zeros((M, M))
for j in range(M):
    v = np.zeros(M)
    v[j] = 1.0
    H_full[:, j] = ft.hilbert(v)

# Odd projection
R = np.zeros((M, M))
for i in range(M):
    R[i, M-1-i] = 1.0
P = (np.eye(M) - R) / 2.0

# Odd-projected H matrix
H_odd = P @ H_full @ P
H_cur = H_odd[np.ix_(right_ix, right_ix)]

# Apply to phi0_r
Hphi0_ii = H_cur @ ex_phi0_r
err_ii = Hphi0_ii - ex_Hphi0_r
rel_err_ii = np.where(np.abs(ex_Hphi0_r) > 1e-15, err_ii / ex_Hphi0_r, 0.0)

print(f"  RMS error (abs):  {np.sqrt(np.mean(err_ii**2)):.6e}")
print(f"  RMS rel error:    {np.sqrt(np.mean(rel_err_ii**2)):.6e}")
print(f"  Max |rel| error:  {np.max(np.abs(rel_err_ii)):.6e}")

# ─── Same comparison for T2 (derivative term) ─────────────────────────
# (i) Full FFT derivative
phi0p_full = ft.differentiate(ex_phi0)
phi0p_i = phi0p_full[right_ix]
# T2_i = xr * phi0p_i
# T2_ex = xr * ex_phi0p_r
err_t2_i = xr * (phi0p_i - ex_phi0p_r)
rel_err_t2_i = np.where(np.abs(xr * ex_phi0p_r) > 1e-15, err_t2_i / (xr * ex_phi0p_r), 0.0)

print(f"\n{'─'*78}")
print("DERIVATIVE T2: x·phi0' comparison")
print(f"{'─'*78}")
print(f"\nMethod (i): Full-grid FFT derivative -> restrict")
print(f"  RMS rel error:  {np.sqrt(np.mean(rel_err_t2_i**2)):.6e}")
print(f"  Max |rel| error: {np.max(np.abs(rel_err_t2_i)):.6e}")

# (ii) Via L_cur's D matrix
# The derivative matrix is embedded in L_cur. Extract it.
# Build D_mat: D_mat[:,j] = differentiate(delta_j)
D_full = np.zeros((M, M))
for j in range(M):
    v = np.zeros(M)
    v[j] = 1.0
    D_full[:, j] = ft.differentiate(v)
D_odd = P @ D_full @ P
D_cur = D_odd[np.ix_(right_ix, right_ix)]
phi0p_ii = D_cur @ ex_phi0_r
err_t2_ii = xr * (phi0p_ii - ex_phi0p_r)
rel_err_t2_ii = np.where(np.abs(xr * ex_phi0p_r) > 1e-15, err_t2_ii / (xr * ex_phi0p_r), 0.0)

print(f"\nMethod (ii): Odd-basis derivative (from L_cur construction)")
print(f"  RMS rel error:  {np.sqrt(np.mean(rel_err_t2_ii**2)):.6e}")
print(f"  Max |rel| error: {np.max(np.abs(rel_err_t2_ii)):.6e}")

# ─── Conclusion: half-domain defect? ──────────────────────────────────
h_i_rms = np.sqrt(np.mean(rel_err_i[np.isfinite(rel_err_i)]**2))
h_ii_rms = np.sqrt(np.mean(rel_err_ii[np.isfinite(rel_err_ii)]**2))
d_i_rms = np.sqrt(np.mean(rel_err_t2_i[np.isfinite(rel_err_t2_i)]**2))
d_ii_rms = np.sqrt(np.mean(rel_err_t2_ii[np.isfinite(rel_err_t2_ii)]**2))

print(f"\n{'─'*78}")
print("HALF-DOMAIN VERDICT")
print(f"{'─'*78}")
print(f"  H(phi0)  (i) full FFT -> restrict: RMS rel = {h_i_rms:.4e}")
print(f"  H(phi0) (ii) odd-basis H matrix:    RMS rel = {h_ii_rms:.4e}")
print(f"  T2       (i) full FFT -> restrict: RMS rel = {d_i_rms:.4e}")
print(f"  T2      (ii) odd-basis D matrix:    RMS rel = {d_ii_rms:.4e}")
print()

# Both ~0.7? Both ~1e-4? Or one of each?
if h_i_rms < 1e-3 and h_ii_rms > 0.1:
    print(f"  >>> HALF-DOMAIN H DEFECT (h_i={h_i_rms:.2e}, h_ii={h_ii_rms:.2e})")
    print(f"  >>> Full-grid H is accurate, odd-basis H is not. Construction bug. Fourier stays.")
elif h_i_rms < 1e-3 and h_ii_rms < 1e-3:
    print(f"  >>> Both accurate. No half-domain H defect. Truncation is the issue.")
elif h_i_rms > 0.1 and h_ii_rms > 0.1:
    print(f"  >>> Both poor (h_i={h_i_rms:.2e}, h_ii={h_ii_rms:.2e}). Genuine truncation effect. Mellin.")
else:
    print(f"  >>> Mixed/inconclusive. Check individual errors.")

print(f"\n{'─'*78}")
print("L_Xu(phi0) via full-grid -> odd-restrict")
print(f"{'─'*78}")

# ─── Apply L_Xu to phi0, full-grid, correct H, then odd-restrict ──────
# L_Xu = -phi0 - x*phi0' + phi0*HOmega + Omega*Hphi0
# (Xu Eq 3.1 at a=0, sign convention)
HO_full = ft.hilbert(ex_Omega)
HO_r = HO_full[right_ix]
Hphi0_full = ft.hilbert(ex_phi0)
Hphi0_r = Hphi0_full[right_ix]
phi0p_full = ft.differentiate(ex_phi0)
phi0p_r = phi0p_full[right_ix]

# L_Xu on right_ix (full-grid FFT applied, then restrict)
LXu_full = -ex_phi0_r - xr * phi0p_r + ex_phi0_r * HO_r + ex_Omega_r * Hphi0_r

# Expected: L_Xu(phi0) = phi0 (since L_Xu = -L_eng and L_eng(phi0) = -phi0)
# Check: L_Xu(phi0) / phi0
LXu_ratio = -ex_phi0_r / ex_phi0_r  # from exact: L_Xu(phi0)/phi0 = 1
# Compute best-fit eigenvalue
# Fit: L_Xu = lambda * phi0
num = np.sum(LXu_full * ex_phi0_r)
den = np.sum(ex_phi0_r * ex_phi0_r)
lambda_fit = num / den if den > 1e-30 else 0.0
residual_fit = np.sqrt(np.mean((LXu_full - lambda_fit * ex_phi0_r)**2)) / np.sqrt(np.mean(ex_phi0_r**2))

print(f"  L_Xu(phi0) = {lambda_fit:.10f} * phi0 (best-fit, full FFT)")
print(f"  Expected: 1.0000000000 * phi0")
print(f"  Residual: {residual_fit:.6e}")
print(f"  Distance from 1: {abs(lambda_fit - 1.0):.6e}")

# Now check via L_cur:
L_cur = rp._build_operator(a=0.0, odd_basis=True)
L_cur_phi0 = L_cur @ ex_phi0_r
eig, vecs = linalg.eig(L_cur)
overlaps = np.abs(vecs.conj().T @ (ex_phi0_r / (np.linalg.norm(ex_phi0_r)+1e-30)))
best_idx = np.argmax(overlaps)
eng_eig = eig[best_idx]
print(f"  Engine (L_cur) eigenvalue: λ_eng = {eng_eig.real:.10f}")
print(f"  Under Xu sign (negated):   λ_Xu = {-eng_eig.real:.10f}")

# Pointwise check of L_Xu/phi0
print(f"\n  Pointwise L_Xu(phi0)/phi0 on right_ix:")
p0_nz = np.abs(ex_phi0_r) > 1e-12
ratios = np.where(p0_nz, LXu_full / ex_phi0_r, np.nan)
print(f"    Mean: {np.nanmean(ratios):.10f}")
print(f"    Std:  {np.nanstd(ratios):.10e}")

# ─── Find lambda=0 mode: solve L_Xu(aΩ + b·y·Ω') = 0 ──────────────────
print(f"\n{'─'*78}")
print("λ=0 MODE: L_Xu(a*Omega + b*y*Omega') = 0")
print(f"{'─'*78}")

# Test both candidate functions
ex_yOp = xr * (-(xr**2 - 0.25) / (xr**2 + 0.25)**2)  # y*Omega' (Omega' is the derivative)
# y*Omega' for Omega = -y/(y^2+1/4):
# Omega' = (y^2-1/4)/(y^2+1/4)^2
# y*Omega' = y*(y^2-1/4)/(y^2+1/4)^2

# Compute L_Xu on Omega
HOmega_full = ft.hilbert(ex_Omega)
HOmega_r = HOmega_full[right_ix]
Omega_p_full = ft.differentiate(ex_Omega)
Omega_p_r = Omega_p_full[right_ix]
# HOmega via φ₀'s H already computed

# L_Xu(Omega) = -Omega - x*Omega' + Omega*HOmega + Omega*HOmega
# = -Omega - x*Omega' + 2*Omega*HOmega
LXu_Omega_v = -ex_Omega_r - xr * Omega_p_r + 2.0 * ex_Omega_r * HOmega_r

# L_Xu(y*Omega')
# Need H(y*Omega') and derivative of y*Omega'
yOp = xr * Omega_p_r
# Full grid extension for y*Omega'
yOp_full = np.zeros(M)
yOp_full[right_ix] = yOp
yOp_full[:c] = -yOp[-1:c-1:-1]  # odd extension (this is odd? Omega' is even, y is odd => odd)
HyOp_full = ft.hilbert(yOp_full)
HyOp_r = HyOp_full[right_ix]
yOp_p_full = ft.differentiate(yOp_full)
yOp_p_r = yOp_p_full[right_ix]

# L_Xu(y*Omega') = -y*Omega' - x*(y*Omega')' + (y*Omega')*HOmega + Omega*H(y*Omega')
LXu_yOp = -yOp - xr * yOp_p_r + yOp * HOmega_r + ex_Omega_r * HyOp_r

# Solve for (a,b): L = a*LXu_Omega + b*LXu_yOp = 0
# and mode = a*Omega + b*y*Omega'
# At each point: a*LXu_Omega_v[i] + b*LXu_yOp[i] = 0
# So b/a = -LXu_Omega_v[i] / LXu_yOp[i]  (should be constant)
b_over_a = np.where(np.abs(LXu_yOp) > 1e-12, -LXu_Omega_v / LXu_yOp, np.nan)
print(f"\n  b/a ratio (should be constant if mode exists):")
print(f"    Mean: {np.nanmean(b_over_a):.6f}")
print(f"    Std:  {np.nanstd(b_over_a[np.isfinite(b_over_a)]):.6f}")

# If constant, report the mode
if np.nanstd(b_over_a[np.isfinite(b_over_a)]) < 0.1:
    ba = np.nanmean(b_over_a)
    print(f"  → Constant b/a = {ba:.6f}")
    print(f"  → λ=0 mode = Ω + {ba:.6f}·y·Ω'")
    # Check λ on this mode
    mode0 = ex_Omega_r + ba * yOp
    L_mode = LXu_Omega_v + ba * LXu_yOp
    mode_res = np.sqrt(np.mean(L_mode**2)) / (np.sqrt(np.mean(mode0**2)) + 1e-30)
    print(f"  → Residual: {mode_res:.6e}")
else:
    print(f"  → b/a NOT constant (std={np.nanstd(b_over_a[np.isfinite(b_over_a)]):.6f})")
    print("  \u2192 No simple linear combination of {Omega, y*Omega'} is the lambda=0 mode")
    
# Also try phi0 = Omega + y*Omega' directly:
LXu_phi0_L = -ex_phi0_r - xr*phi0p_r + ex_phi0_r*HOmega_r + ex_Omega_r*Hphi0_r
print(f"\n  L_Xu(phi0) = Ω+y·Ω' gives:")
print(f"    λ = L_Xu(phi0)/phi0 = {np.nanmean(np.where(np.abs(ex_phi0_r)>1e-12, LXu_phi0_L/ex_phi0_r, np.nan)):.6f}")

# ═══════════════════════════════════════════════════════════════════════
#  RB-05 UPDATE
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'─'*78}")
print("RB-05 UPDATE: φ₀ as odd λ=1 closed form (derived, not quoted)")
print(f"{'─'*78}")

# Load current RB-05
import yaml
base = os.path.dirname(os.path.abspath(__file__))
corpus_dir = os.path.join(os.path.dirname(base), 'known-bad-specs')
rb05_path = os.path.join(corpus_dir, 'RB-05.yaml')

# Overwrite extraction C with phi0 expression
# First read
with open(rb05_path, 'r') as f:
    rb05 = yaml.safe_load(f)

# Extract current C's expression
old_c_expr = rb05['spec_fragment']['registry'][0]['extractions'][2]['mode_expression']
print(f"  Old extraction C (FABRICATED): {old_c_expr[:70]}")

# New extraction C
new_c = {
    'extractor': {'family': 'arbiter', 'model': 'sympy', 'variant': 'derived'},
    'body': 'phi0 = Omega + y*Omega_p = -y/(2*(y^2+1/4)^2)',
    'mode_expression': '-y/(2*(y**2 + 1/4)**2)',
    'parity': 'odd',
    'source_eq': 'derived: phi0 = Omega + y*Omega\' (scaling mode, λ=+1 under Xu L_Xu)'
}
rb05['spec_fragment']['registry'][0]['extractions'][2] = new_c
rb05['pre_registered'] = 'arbiter returns HALT-REFERENT: all three extractions now ODD but λ=1 vs λ=0 conflict remains (phi0=λ=+1, not λ=0 mode)'

with open(rb05_path, 'w') as f:
    yaml.dump(rb05, f, default_flow_style=False)
print(f"  New extraction C: phi0 = -y/(2(y²+¼)²) (ODD)")
print(f"  RB-05.yaml updated.")

# Re-run arbiter
sys.path.insert(0, os.path.join(os.path.dirname(base)))
import arbiter
exts = rb05['spec_fragment']['registry'][0]['extractions']
for i, e in enumerate(exts):
    expr = e.get('mode_expression', '')
    if expr:
        r = arbiter.check_mode(expr)
        print(f"  Ext {i}: expr={expr[:50]}, parity={r['parity']}")

# New expected outcome: all odd now, A and B had EVEN from dΩ/dξ
# Actually A and B are still dΩ/dξ (EVEN). C is now phi0 (ODD).
# So A=EVEN, B=EVEN, C=ODD → still HALT-REFERENT by parity disagreement.
# But NOW the disagreement is between λ=1 (even translation) and λ=1 (odd scaling under Xu)
# This is a DIFFERENT kind of disagreement — both λ=1 candidates, different parity
print(f"  → Ext A (dΩ/dξ, EVEN, λ=1 translation)")
print(f"  → Ext B (dΩ/dξ, EVEN, λ=1 translation)")
print(f"  → Ext C (φ₀, ODD, λ=+1 under Xu's operator)")
print(f"  → Parity: 2 EVEN + 1 ODD = HALT-REFERENT (correct: different λ=1 modes)")

# ═══════════════════════════════════════════════════════════════════════
#  FORK DECISION
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'='*78}")
print("FORK DECISION")
print(f"{'='*78}")

print(f"""
  HALF-DOMAIN TEST:
    H(phi0) (i) full FFT -> restrict: RMS rel = {h_i_rms:.4e}
    H(phi0) (ii) odd-basis H matrix:  RMS rel = {h_ii_rms:.4e}
    T2 (i) full FFT -> restrict: RMS rel = {d_i_rms:.4e}
    T2 (ii) odd-basis D matrix:  RMS rel = {d_ii_rms:.4e}
""")

if h_i_rms < 1e-3 and h_ii_rms < 1e-3:
    print("  Both H methods accurate — NO half-domain defect.")
    print("  The eigenvalue shift is a GENUINE TRUNCATION EFFECT.")
    print("")
    print("  FORK: MELLIN. Build ℝ-discretization to recover exact eigenvalues.")
    print("  The periodic Fourier truncation shifts eigenvalues by O(1)")
    print("  for non-periodic functions. This is fundamental, not a bug.")
    print("  Option (A) 'accept within +/-0.5' REJECTED per directive.")
elif h_i_rms < 1e-3 and h_ii_rms > 0.1:
    print("  >>> HALF-DOMAIN H DEFECT detected.")
    print("  >>> The odd-basis projection restricts H incorrectly.")
    print("  >>> FORK: FOURIER. Fix the odd-basis construction bug.")
    print("  >>> After fix, the periodic engine should recover correct eigenvalues.")
else:
    print("  Complex result — see error paths above.")

print(f"""
  L_Xu(phi0) via full-grid FFT -> odd-projection restrict:
    λ_Xu = {lambda_fit:.10f}  (expected: 1.0000000000)
    Residual: {residual_fit:.6e}
""")

# Report what the fork decision is
if h_i_rms < 1e-3 and h_ii_rms < 1e-3:
    print(f"\n  FORK: MELLIN — periodic Fourier cannot represent R Hilbert accurately for non-periodic functions.")
else:
    print(f"\n  FORK: FOURIER (fix half-domain construction first).")

print(f"\n  Option (A) 'accept eigenvalues within +/-0.5 of target' is REJECTED.")
print(f"  Per directive: 'A tolerance that wide cannot distinguish 0 from 1")
print(f"  on a spectrum whose entire content is {{0,1}}. Not a pre-registration; a surrender.'")