# TERM-BY-TERM — Terminal Report

**ORDER-ID:** OL-v1.5-P1-TERM-BY-TERM
**AUTHORITY:** Founder directive (term-by-term, arbiter-grade)
**VERDICT:** CONSTRUCTION-DEFECT-DIAGNOSED (no fork decision)
**CAP:** $0
**COMPUTE:** N=1024, L=20, right_ix, SymPy exact + FFT engine
**DATE:** 2026-09-08

══════════════════════════════════════════════════════════════════════

## REFERENT SENTENCE

Xu (2026), arXiv 2607.19762, Section 3.2:

> *"The scaling transformation (T-dilation) generates the eigenfunction
> φ₀ = Ω + ξ·Ω' at eigenvalue λ=0 in the odd-basis space X."*

Xu attaches the **ODD** parity to φ₀ (Ω is odd, ξ·Ω' is odd → sum is odd).
The scaling mode lies in X = H²_origin ∩ L²_odd with λ=0.

**Discovered:** φ₀ has λ = **−1.0000** on the continuous ℝ operator.
On the periodic operator it shifts to λ = **−0.4702**. The ℝ Hilbert
transform assigns φ₀ to the essential spectrum band (Re = −½), not to λ=0.

---

## FIVE TERM RATIOS (engine periodic − exact ℝ) / exact ℝ

N=1024, L=20, right_ix:

| Term | Definition | RMS rel | Max |rel| | Physical source of error |
|------|-----------|---------|---------|------------------------|
| **T1** | c_l·φ₀ = 1·φ₀ | **0.0000** | **0.0000** | Identical sampling — no error |
| **T2** | α·x·φ₀' (FFT vs analytic) | **69.0** | **400.4** | φ₀ is not periodic on [−L,L]; FFT derivative has boundary ringing |
| **T3** | −(HΩ)·φ₀ (periodic vs ℝ H) | **41.7** | **237.2** | Periodic Hilbert transform changes HΩ by O(1) due to boundary aliasing |
| **T4** | −(Hφ₀)·Ω (periodic vs ℝ H) | **3.7** | **20.7** | Smaller but still significant; φ₀ is less smooth than Ω |
| **T5** | Constraint/projection artifact | **0.249** | — | Odd-basis projection+restriction adds spurious matrix entries |

**SUM L(φ₀)**: RMS = **207**, max |rel| = **1199** — the total operator is O(1) different on ℝ vs periodic.

**L(φ₀) on ℝ = −1.0000·φ₀** (exact, per SymPy closed-form sum of T1–T4).
**L(φ₀) on periodic = λ_engine·φ₀** where λ_engine = **−0.470182** (shifted).

---

## CONSTRUCTION DEFECT IDENTIFIED

The **O(1) discrepancy** is in **T3** (periodic Hilbert transform of Ω) and **T2** (FFT derivative of non-periodic φ₀). Together they shift the spectral problem:

| Quantity | Continuous ℝ | Periodic [−L, L] | Shift |
|---------|-------------|-----------------|-------|
| λ(φ₀) | −1.000 (exact) | −0.470 (engine) | **+0.53** |
| L(φ₀) identity | −φ₀ | −0.47·φ₀ + residual | O(1) |
| λ=0 | physical scaling mode | **constraint null space** | degraded |

The defect is **not** a coding bug — it is a **discretization choice**: the
periodic Fourier domain [−L, L] replaces the ℝ Hilbert transform and
FFT derivative with periodic counterparts that differ by O(1) boundary
terms for non-periodic functions. φ₀ and Ω are not periodic on [−L, L],
so the periodic spectral method does not faithfully represent Xu's ℝ operator.

**"Only dilation survives on a periodic domain" — ASSERTED-UNSOURCED.**
This statement is retracted from all active reasoning. No citation provided.

---

## DERIVATION: Other Symmetry Mode

**Two lines** from the self-similar ansatz ω(x,t) = (T−t)⁻¹Ω(x/(T−t)):

1. **Scaling (λ=0, ODD):** φ₀ = Ω + ξ·Ω' = −ξ/(2(ξ²+¼)²) — from ∂_T ω.
   Verified: On ℝ, L(φ₀) = −φ₀ (λ=−1, essential spectrum band).
   On periodic, L(φ₀) = −0.47·φ₀ (shifted).

2. **Translation (λ=1, EVEN):** φ₁ = dΩ/dξ = (ξ²−¼)/(ξ²+¼)² — from ∂_ξ.
   Parity: EVEN → excluded from odd-basis space X by construction.

**Odd λ=1 mode:** ψ₁ = Ω − ξ·Ω' (from ∂_t ω in similarity frame). Tested on
periodic engine: best-fit λ = **−0.2726**, |λ−1| = **1.27**. **NOT the λ=1 mode.**

Xu Theorem 2 proves the odd λ=1 mode EXISTS in X by spectral theory
(resolvent bounds), but provides **no closed-form expression**. It cannot
be derived from the ansatz alone — it is a spectral existence result.

---

## SPURIOUS NULL VECTOR

Engine λ=0 eigenvector on the odd-basis operator:

| Property | Value |
|---------|-------|
| Nullspace dimension | **1** |
| Mass at index 0 (x=0) | **1.000000** |
| m_in (|x|<1) | 1.000000 |
| m_out (|x|>L/2) | 0.000000 |
| Classification | **SPURIOUS-MODE-FROM-CONSTRAINT** |

The λ=0 eigenvalue is **not physical**. It is carried entirely by the
constraint row's null space at x=0 — the odd-basis projection combined
with the center-point row introduces a direction that is nonzero only at
x=0 and zero everywhere else, yielding eigenvalue 0 trivially.

**Interpretation:** The engine's "λ=0 mode" is a constraint artifact.
The true physical scaling mode φ₀ has λ = −0.47 on the periodic
operator (shifted from −1.0 on ℝ by the periodic truncation).

---

## RB-05 FLAG

**Extraction C in RB-05.yaml is CORPUS-FABRICATED.**

| Extraction | Expression | Parity | Source | Verdict |
|-----------|-----------|--------|--------|---------|
| A | (−2 + 2ξ²)/(1+ξ²)² | EVEN | Xu Eq 3.7 | ✓ legitimate |
| B | (−2 + 2y²)/(1+y²)² | EVEN | Xu Eq 3.7 | ✓ legitimate |
| C | −ξ/(1+ξ²) + ξ³/(1+ξ²)² | ODD | "Xu Sec 3.2" | ✗ **FABRICATED** |

The odd expression has **no source** in Xu 2607.19762. Sec 3.2 gives only
the EVEN translation mode (dΩ/dξ, Eq 3.7). The odd λ=1 mode is a spectral
existence theorem (Theorem 2), not provided as a closed form.

RB-05 correctly returns HALT-REFERENT via parity mismatch (2 EVEN + 1 ODD).
After removing extraction C, A+B agree → RESOLVED.

---

## TERMINAL STATE

| Property | Value |
|---------|-------|
| **T1 ratio** | 0.0000 (no error) |
| **T2 ratio** | RMS = **69.0**, max = **400.4** (FFT derivative, non-periodic φ₀) |
| **T3 ratio** | RMS = **41.7**, max = **237.2** (periodic Hilbert, dominant defect) |
| **T4 ratio** | RMS = **3.7**, max = **20.7** (periodic Hilbert, smaller) |
| **T5 (constraint)** | **0.249** (projection artifact) |
| **Sum L(φ₀) ratio** | RMS = **207**, max = **1199** |
| **ℝ eigenvalue** | **−1.0000** (exact; φ₀ not λ=0 on ℝ) |
| **Engine eigenvalue** | **−0.4702** (shifted by periodic truncation) |
| **Null vector** | **SPURIOUS-MODE-FROM-CONSTRAINT** (mass at x=0 = 1.000) |
| **Odd λ=1 (ψ₁ = Ω−x·Ω')** | λ = **−0.2726**, |λ−1| = **1.27** (NOT λ=1) |
| **RB-05** | Extraction C = **CORPUS-FABRICATED**; arbiter flags correctly |
| **Construction defect** | Periodic Hilbert transform (T3) + FFT derivative (T2) = O(1) spectral shift |

**Construction defect:** The periodic Fourier discretization replaces the
ℝ Hilbert transform with the periodic Hilbert transform on [−L, L]. For
non-periodic functions (Ω, φ₀), this introduces O(1) boundary terms that
shift the entire spectrum. The shift is systematic: φ₀ goes from λ=−1 (ℝ)
to λ=−0.47 (periodic). The λ=1 mode (even translation) is excluded by odd
projection; the odd λ=1 mode (proven by Xu Theorem 2) has no closed form
and is not representable on the periodic domain.

**No fork decision** — this report diagnoses the defect without resolving it.

**MEDIA:** /Users/brukendale/ol-run/obstruction-ledger-v1.2/work/term-by-term-report.md
**Script:** /Users/brukendale/ol-run/obstruction-ledger-v1.2/work/term-by-term.py