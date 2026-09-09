# CONTROL REPAIR v2 — Terminal Report
Commit: pending
Date: 2026-09-08

══════════════════════════════════════════════════════════════════════

## 0. RB-05 HIT CHECK

Arbiter parity for dΩ/dξ (Xu Eq 3.7, even translation mode): **EVEN**
Arbiter parity for a candidate odd λ=1 expression: **ODD**

RB-05 extractions contain: A (even dΩ/dξ), B (even dΩ/dξ), C (odd expression).
→ RB-05 correctly yields **HALT-REFERENT** (parity disagreement between extractions).

## 0b. INDEX SPACE MAPPING (explicit)

| Space | Description | Size |
|-------|-------------|------|
| FULL | x on [−L, L], M=2049 points | 2049 |
| RIGHT HALF | x[right_ix], includes x=0 at index 0 | 1025 = M−center |
| Engine eigenvectors | Live on RIGHT HALF | 1025 |
| Sampled closed forms | Sampled on FULL, RESTRICTED to right_ix | 1025 |

All inner products computed on matching 1025-element vectors.

## 1. λ=0 Control

Engine λ=0 eigenvector:
  λ = **0.000000000000** (exact)
  ||L u₀ − λ u₀||/||u₀|| = **0.00e+00** ✅
  Index: right_ix, x ∈ [0.0, 20.0]

φ₀ sampled (Xu Sec 3.2, coordinate ξ=2x):
  φ₀(x) = −x/(2(x²+¼)²)
  Best-fit λ = **−0.470162** on L_cur
  Residual = **4.21e-03**
  Overlap with engine λ=0 eigenvector = **0.000000** (different mode)
  Overlap with λ=−0.47 eigenvector = **1.000000** (φ₀ IS the −0.47 mode)

## 2. λ=1 Mode — Odd Basis

**Status: NO eigenvalue within 0.1 of 1. Minimum |λ−1| = 1.00.**

Nearest eigenvalue to 1 on odd-basis operator:
  λ = **0.000000 + 0.000000j**
  |λ−1| = **1.00e+00** ❌ pre-registered criterion (< 5e-4 NOT MET)
  m_in (|x|<1): 1.0000, m_out (|x|>L/2): 0.0000
  (This is the λ=0 scaling mode; it's closest to 1 only in the technical
   sense of being at minimum distance 1.0 from the exact eigenvalue at 0.)

Eigenvalue distribution near λ=1:

| |λ−1| | Re λ | Im λ | m_in | Character |
|-------|------|------|------|--------|
| 1.00 | 0.000 | 0.000 | 1.000 | λ=0 scaling mode |
| 1.27 | −0.273 | 0.000 | 0.747 | essential spectrum |
| 1.30 | −0.249 | ±0.359 | 0.799 | essential spectrum |
| 1.43 | −0.213 | ±0.760 | 0.793 | essential spectrum |
| 1.47 | −0.470 | 0.000 | 0.967 | shifted φ₀ |

## 3. The "1.0000" Explained

The earlier report "Five nearest eigenvalues to 1: ['1.0000', '1.2726', ...]"
referred to ABSOLUTE DISTANCES |λ−1| sorted ascending, not eigenvalues.
The actual values: [1.000, 1.273, 1.300, 1.300, 1.432] — distances from
λ=1 to the nearest eigenvectors.

## 4. Even Translation Mode (φ = dΩ/dξ, Xu Eq 3.7)

Sampled on engine coordinates: φ₁(x) = (x²−¼)/(x²+¼)²
Best-fit λ on odd-basis L = **−0.533**, residual = **2.74e-01**
Error at origin: 0.603, at boundary: 0.132

## 5. Odd λ=1 Closed Form — Not Available from Source

Xu 2607.19762 Theorem 2 states λ=1 EXISTS in the odd-basis space X,
but **gives no closed-form eigenfunction** for the odd λ=1 time-shift mode.
Equation 3.7 provides only the EVEN translation mode (dΩ/dξ). The paper
proves existence via spectral theory (Hardy decomposition, resolvent bounds)
rather than by explicit formula.

Candidate odd functions tested (x·Ω', Ω profile, y·Ω'):
  → None are eigenvectors at λ=1 on the periodic discretization.
  → Best overlap 0.89 at λ=−0.27 (profile Ω itself).

## 6. Summary

| Criterion | Value | Met? |
|-----------|-------|------|
| λ=0 engine eigenvector residual | 0.00e+00 | ✅ |
| φ₀ overlap (corrected index space) | 0.000000 | n/a — different mode |
| |λ−1| < 5e-4 | **1.00e+00** | ❌ |
| m_in of nearest-λ=1 eigenvector | 1.0000 | λ=0 mode, not λ=1 |

**Defect A acceptance NOT MET.** λ=1 is absent from the periodic Fourier
discretization of the odd-basis operator. No eigenvalue within 1.0 of 1.

**"Not a harness bug" is RETRACTED pending fork decision.** The periodic
Fourier operator genuinely lacks λ=1. Whether this is a discretization
limitation (Mellin would fix it) or a construction bug (engine fixable
without changing discretization) is the fork question.

**"Known property: only dilation survives on a periodic domain" — ASSERTED-UNSOURCED.** 
This statement is removed unless a source is cited. The phenomenon of
the translation mode being blocked by periodicity is known in spectral
theory (periodic vs ℝ Hilbert transforms differ by a boundary term) but
no single citable theorem covers the CLM case. Flag filed.