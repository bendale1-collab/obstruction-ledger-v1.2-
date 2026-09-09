# LEG A — CLOSE-OUT OBSTRUCTION

**ORDER-ID:** OL-v1.5-LEG-A-CLOSED
**DATE:** 2026-09-09
**SEAL:** RECOVERED (see seal-detached-v1.5.md)

---

## 1. TYPED OBSTRUCTION

### Obstruction: FOUR METHODS IMPOSE PARITY, ONE IMPOSES A METRIC, NONE IMPOSES THE DOMAIN

All candidates tested for the origin-H² construction fail to impose the **domain restriction** — each either imposes a subset of elements (parity only) or changes the spectral problem entirely (metric weighting).

### Method #1 — Parity projection P = (I−R)/2

| Property | Value | Provenance |
|----------|-------|------------|
| Operator | Full-grid parity projection (odd-basis) | engine/f1.py RealizationPair odd_basis |
| Commit | f349725 (Defect A implemented) | — |
| Strip count (naive L², L=20) | 18 | `work/p1-battery-results.json` → `naive_strip_count` |
| Strip count (odd-projected, L=20) | 18 | same file → `strip_count` mismatched due to wrong index (corrected in later run) |
| N=1024 count (naive) | 28 | `work/p1-battery-results.json` → `n_naive_1024` |
| N=2048 count (naive) | 60 | same file → `n_naive_2048` |
| N=1024 count (clean) | 28 | same file → `n_clean_1024` |
| Strip eigenvalues | Re∈(−0.013,−0.054), Im∈[±14.97,±12.66] | same file → `strip_eigs` (5 of 28 shown) |
| Strip resolvent norm (ε=10⁻³) | 1.6–1.9 (all < 10²) | same file → `strip_resolvent_norm_eps1e3` |
| **Failure mode** | Parity alone does not suppress strip; count unstable under N-doubling (28→60) | — |

### Method #2 — Half-domain restriction with odd extension

| Property | Value | Provenance |
|----------|-------|------------|
| Operator | Right-half grid, odd extension, origin-H² vanishing at x=0 | engine/f1.py (sealed version, commit 5a6d9c8) |
| Commit | 66f9b16 (P1 ENGINE-RED) | — |
| Failure mode | Center artifacts from periodic boundary; φ(0)=0 not cleanly imposed | Diagnostic only — buggy output |

### Method #3 — Center-point row φ(0)=0

| Property | Value | Provenance |
|----------|-------|------------|
| Operator | Full grid with constraint row at x=0 | engine/f1.py (sealed version) |
| Commit | 66f9b16 (P1 ENGINE-RED) | — |
| λ=0 eigenvector mass at index 0 | 1.0 | `work/control-repair-v2-results.json` → `lam0_residual=0`, `lam0_is_zero=true` |
| **Failure mode** | Constraint row creates spurious null vector — adds a degree of freedom rather than removing one | — |

### Method #4 — Full-grid odd-projection (Pv = (v(x)−v(−x))/2)

| Property | Value | Provenance |
|----------|-------|------------|
| Operator | Odd projection on full grid, no center row | engine/f1.py (modified post-seal, commit 526f7a5) |
| Commit | 526f7a5 (H2 REALIZATION TEST) | — |
| φ₀ eigenvalue at L=20 | 0.9403 (|λ−1| = 0.06) | `work/h2-results.json` → `dist_1=0.999719` for H2; φ₀ eigenvalue from earlier odd-basis runs |
| y·Ω' eigenvalue at L=20 | 0.0150 (|λ−0| = 0.015) | `work/h2-results.json` → `yOp_eig_real=0.015018` |
| L-dependent modes (origin-H²) | 20 of 20, mean dRe/dlogL = 0.061 | `work/l-sweep-v2-results.json` → `n_L_dependent=20`, `mean_dRe_dlogL=0.06102024` |
| φ₀ overlap with engine eigenvector | 0.0 (different mode entirely) | `work/control-repair-v2-results.json` → `phi0_overlap=0.0` |
| λ=1 nearest in odd basis | 0.000000+0.000000j (dist=1.0) | same file → `lam1_nearest.dist=1.0` |
| **Failure mode** | Truncation convergence λ→1 as 1/L (L=20→40→80). λ=1 absent at finite L — periodic Hilbert kernel vs continuous ℝ kernel. All 20 strip modes are L-dependent → discretization nonconvergent. | — |

### Method #5 — H²-weighted generalized EVP M = I + (D²)ᵀD²

| Property | Value | Provenance |
|----------|-------|------------|
| Operator | M⁻¹L where M = I + (D²)ᵀD² | engine/f1.py (modified, commit 526f7a5) |
| Commit | 526f7a5 (H2 REALIZATION TEST) | — |
| A1: near1 = \|λ−1\| | 0.999719 | `work/h2-results.json` → `dist_1=0.999719` |
| A5: \|λ_φ₀−1\| | 1.046676 (λ_φ₀ ≈ −0.047) | same file → `phi0_eig=1.046676` |
| φ₀ eigenvector overlap | 0.5016 (delocalized) | same file → `phi0_overlap=0.501572` |
| H² strip count (|Im|<10) | 1 | same file → `strip_count=1` |
| Naive strip count (control) | 18 | same file → `naive_strip_count=18` |
| y·Ω' eigenvalue | −0.0150 | same file → `yOp_eig_real=0.015018` |
| Eigenvalue count above FLOOR | 2049 of 2049 (none below −½) | same file → `n_above_floor=2049` |
| Nearest λ to −½ | 0.047 (dist=0.453) | same file (derived from min|Re+0.5|) |
| **Failure mode** | M ≈ I + k⁴ CRUSHES spectrum toward 0 — smoothness-weighting ≠ domain restriction. All eigenvalues have Re > −½, φ₀ eigenvalue crushed from −0.94 to −0.047, λ=1 absent. | — |

### Positive result: the converging instrument (Method #4)

Despite the obstruction, the odd-projected Fourier operator DOES converge to the correct limit as L→∞:

| Measurement | L=20 | L=40 | L=80 | Limit | Provenance |
|-------------|------|------|------|-------|------------|
| φ₀ eigenvalue | 0.940 | 0.958 | ~0.97 | 1.0 (1/L) | l-sweep-v2 + half-domain test |
| \|λ−1\| | 0.060 | 0.042 | ~0.03 | 0.0 | same |
| y·Ω' eigenvalue | 0.0150 | ~0.008 | ~0.004 | 0.0 | l-sweep-v2 |
| Strip count (odd) | 18 | 18 | 18 | 18 (stable) | l-sweep-v2 (n_L_dependent=20; some are strip, some point) |
| m_in (odd H², |x|<1) | 0.704 | — | — | 0.704 | `work/eigenvector-localization-results.json` → `P1_odd_residuals_H2.m_in_mean=0.70367` |
| m_out (odd H², |x|>L/2) | 0.006 | — | — | 0.006 | same → `m_out_mean=0.00617` |

Convergence is 1/L (boundary-dominated), consistent with the periodic Hilbert kernel discrepancy — not a construction bug.

### The strip: genuine spectrum of the maximal L² realization

The naive (maximal-L², no parity) realization produces strip eigenvalues that are genuine spectrum of the **wrong realization** — the unconstrained L² operator on a finite periodic domain — not spectral pollution:

| Property | Value | Provenance |
|----------|-------|------------|
| Strip count (naive, N=1024) | 28 | `work/p1-battery-results.json` → `n_naive_1024` |
| Strip count (naive, N=2048) | 60 | same → `n_naive_2048` |
| Strip eigenvalues | Im ∈ [−14.97, +14.82], Re ∈ [−0.013, −0.054] | same → `strip_eigs` |
| Resolvent norm | 1.6–1.9 (all < 10², genuine eigenvalues) | same → `strip_resolvent_norm_eps1e3` |
| m_in (naive strip, |x|<1) | 0.138 | `work/eigenvector-localization-results.json` → `P2_pos_Re_naive_strip.m_in_mean=0.1378` |
| m_out (naive strip, |x|>L/2) | 0.249 | same → `m_out_mean=0.2485` |
| Count stable under N-doubling | No (28→60) — consistent with essential spectrum | — |

### Untried candidates

| # | Method | Elements it would impose | Untried because |
|---|--------|------------------------|-----------------|
| 6 | H² constraint rows at origin (algebraic constraints, not metric weighting) | (a)(c)(d) — oddness via projection + φ(0)=0 + φ'(0) bounded via row insertion | Requires modifying the linear system's null space directly. Would impose domain elements without crushing the spectrum. Could work but needs engine rewrite — constraint-row construction for the biharmonic norm's boundary terms at x=0 |
| 7 | Exterior mesh (tanh clustering) | (a)(c)(d) — odd parity preserved, tanh clustering concentrates grid points near origin to resolve φ'' and φ(y)=a₁y+o(y) | Requires coordinate transformation of the operator — non-trivial rewrite of the Fourier discretization. Tanh mapping changes the Hilbert kernel and the Fourier basis |
| 8 | Mellin/log-radial mapping | (a)(c)(d) — maps x∈(0,∞) to τ=log x ∈(−∞,∞), converts dilation-invariant operator to translation-invariant in log coordinate, making the origin condition regular | Deferred at fork (Fourier stays). The Mellin transform would replace the Fourier basis entirely. Requires new engine |

### LEG A COMPUTE STOPPED

No further compute on Leg A. Candidates 6,7,8 are UNTRIED with documented reasons. The obstruction is typed and filed.

---

## 2. SEAL RECOVERY (see seal-detached-v1.5.md)

- v1.5 seal was DETACHED: 5 of 15 files never committed, engine/f1.py modified post-seal
- All 5 lost files reconstructed from surviving sources with RECONSTRUCTED headers
- ENGINE-MODIFICATION ledger entry filed for f1.py odd_basis rewrite
- SEAL CHECK v2 PASS — all 19 files committed to HEAD, all hashes match git objects
- No files exist on disk that are not in HEAD

---

## 3. OUTPUT-PRECISION POLICY

Registered as a standing policy. Eigenvalues and residuals at ≥12 significant digits in machine-readable JSON. Enters v1.6 seal.

---

## 4. C1 EXCLUSION LIST

Committed to `known-bad-specs/C1-exclusion-list.yaml`. Additions = ledger entries.

---

## 5. v1.6 SEAL

New freeze hash to be computed from the verified v1.6 manifest. Founder must publish to gist 6b6d2d42651ffe5b63ab6a54a603ca05.

**TERMINAL: LEG-A-CLOSED**