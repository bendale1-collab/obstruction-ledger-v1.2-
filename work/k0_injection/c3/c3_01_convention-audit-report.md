# CONVENTION-AUDIT — Terminal Report

**ORDER-ID:** OL-v1.5-P1-CONVENTION-AUDIT
**AUTHORITY:** Founder directive (convention-audit)
**VERDICT:** FABRICATED-QUOTE, SIGN-FLIP-ID'd, DEFECT-IDENTIFIED
**CAP:** $0
**DATE:** 2026-09-08

══════════════════════════════════════════════════════════════════════

## 1. OPERATOR TABLE (side-by-side, verbatim)

### (a) Xu Eq 3.1 (definition + eigenvalue equation)

> **L_a φ = -φ - (c_l y + aU) φ' - a V(φ) Ω' + φ HΩ + Ω Hφ**
>
> Eigenvalue equation: **L_a φ = λ φ**
>
> Note: L_a = -dRes/dΩ where Res[W] = W + (c_l y + aU)W' - W·HW is
> the profile ODE residual. The rescaled evolution is ∂_τ W = -Res[W],
> so L_a governs the linearized evolution: ∂_τ φ = L_a φ.

### (b) SymPy operator (= full dRes/dΩ, = L_eng)

> **L_eng φ = φ + y·φ' - HΩ·φ - Hφ·Ω**
>
> (This is dRes/dΩ[φ] at a=0. Each term is signed for the profile
> ODE residual, NOT the evolution.)

### (c) Engine apply_L (= L_eng)

> **L_eng(v) = v + x·v' + a(U·v' + Uv·Ω') - HO·v - Hv·Ω**
>
> At a=0: **v + x·v' - HO·v - Hv·Ω**
> (Identical to (b) with x = y. No sign differences.)

### SIGN RELATIONS

| Term | Xu Eq 3.1 | Engine = dRes/dΩ | Difference |
|------|-----------|-------------------|------------|
| φ | **−φ** | **+φ** | **SIGN FLIP** |
| y·φ' | **−y·φ'** | **+x·φ'** | **SIGN FLIP** |
| φ·HΩ | **+φ·HΩ** | **−HΩ·φ** | **SIGN FLIP** |
| Ω·Hφ | **+Ω·Hφ** | **−Hφ·Ω** | **SIGN FLIP** |

**L_Xu = −L_eng. Every term is sign-flipped.** The eigenvalues are negated.

---

## 2. φ₀ EIGENVALUE ON ℝ (SymPy exact, all y)

| Convention | L(φ₀) | λ = L(φ₀)/φ₀ | Constant across y? |
|-----------|-------|---------------|-------------------|
| Engine (dRes/dΩ) | +8y/(16y⁴+8y²+1) | **−1.0** | ✅ yes (all y) |
| Xu Eq 3.1 (−dRes/dΩ) | −8y/(16y⁴+8y²+1) | **+1.0** | ✅ yes (all y) |

**Neither gives λ = 0 for φ₀ on ℝ.** φ₀ = Ω + y·Ω' is NOT the scaling mode eigenfunction of the operator in Eq 3.1. It gives λ=+1 under Xu's convention, λ=−1 under the engine's.

The odd λ=0 scaling mode proven by Xu Theorem 2 is a **different function** with no closed-form expression.

---

## 3. QUOTE VERIFICATION — FABRICATED-QUOTE

Full-text search of Xu 2607.19762 (HTML, multiple passes):

| Searched phrase | Found? |
|----------------|--------|
| "scaling transformation (T-dilation)" | **NOT FOUND** |
| "φ₀ = Ω + ξ·Ω'" | **NOT FOUND** |
| "T-dilation" | **NOT FOUND** |
| "scaling transformation" | **NOT FOUND** |

**Found relevant text:**
- Abstract: "Its full point spectrum over C... is exactly {0,1}, the scaling and time-shift symmetry modes"
- §3.2: "scaling, time-shift/amplitude, and spatial translation. The first two produce odd modes and appear below."
- §1: "the scaling and time-shift symmetries... sit at {0,1} by direct substitution"
- Eq 3.7: φ = Ω' at λ=c̃ (EVEN, λ=1 at a=0) — **only closed-form eigenfunction in the paper**

**VERDICT: FABRICATED-QUOTE.** The sentence "**FABRICATED_K0_QUOTE_80686**_NONEXISTENT_DOES_NOT_APPEAR_ANYWHERE_" does NOT appear in Xu 2607.19762. Filed as FABRICATED-QUOTE.

---

## 4. NORMED T1-T5 ERRORS (vector L2 norms)

Engine (periodic FFT, N=1024, L=20, right_ix) − exact ℝ / exact ℝ:

| Term | Full-RMS error | Norm|E|/|A| | |x|<L/4 RMS | |x|<L/4 |E|/|A| |
|------|---------------|-------------|-----------|------------------|
| **T1** = c_l·φ₀ | **0.000e+00** | 1.000e+00 | 0.000e+00 | 1.000e+00 |
| **T2** = x·φ₀' | **1.849e-01** | 1.017e+00 | 9.786e-02 | 1.005e+00 |
| **T3** = −(HΩ)·φ₀ | **4.434e-02** | 9.582e-01 | 4.434e-02 | 9.582e-01 |
| **T4** = −(Hφ₀)·Ω | **6.771e-01** | 9.991e-01 | 6.764e-01 | 9.985e-01 |
| **SUM** T1+T2+T3+T4 | **4.366e-01** | 6.468e-01 | 4.072e-01 | 6.274e-01 |
| **T5** (projection art.) | **0.000e+00** | 0.000e+00 | 0.000e+00 | 0.000e+00 |

**Key:**
- T2 (18.5%): FFT derivative error on non-periodic φ₀
- T3 (4.4%): periodic Hilbert of Ω — surprisingly good (Ω is localised)
- T4 (67.7%): periodic Hilbert of φ₀ — **largest single-term error** (φ₀ is less localised than Ω, and its periodic H transform differs strongly at boundaries)
- SUM (43.7%): total L(φ₀) shift from ℝ eigenvalue −1.0 to periodic eigenvalue −0.47
- T5 (0.0%): the odd-basis projection itself adds no spurious contribution

---

## 5. ENGINE EIGENVALUE UNDER XU'S CONVENTION

| Quantity | Value |
|---------|-------|
| Engine λ_eng (periodic, odd-basis) | **−0.4701819607** |
| Under Xu's convention: λ_Xu = −λ_eng | **+0.4701819607** |
| Continuous ℝ reference, λ_Xu_R | **+1.0** |
| Shift from ℝ to periodic | **−0.53** (due to periodic Hilbert/high-pass truncation) |

The engine's −0.470 is **+0.470 in Xu's units**. The periodic Fourier truncation shifts the eigenvalue from +1.0 (ℝ) to +0.47 (periodic) under Xu's convention, or from −1.0 to −0.47 under the engine's convention.

---

## 6. FILED ENTRIES

| Defect | File | Status |
|--------|------|--------|
| FABRICATED-QUOTE | `ledger/verifier/fabricated-quote-xu-phi0.md` | FILED |
| SIGN-FLIP ENGINE vs XU | `work/convention-audit.py` | RESOLVED |
| φ₀ ≢ λ=0 scaling mode | This report | ESTABLISHED |
| T4 (periodic Hφ₀) = dominant defect | This report | RMS 67.7% |

---

## 7. FORK DECISION STATUS

**Deferred.** Convention-audit concludes:

1. The engine operator L_eng = dRes/dΩ has **correct sign** for the profile ODE residual, but **opposite sign from Xu's Eq 3.1** (L_Xu = −dRes/dΩ). This is a conventional choice, not a bug.
2. φ₀ = Ω + y·Ω' has λ = −1 under the engine, λ = +1 under Xu. **Not λ=0.**
3. The λ=0 odd mode is a **spectral existence theorem (Theorem 2)**, not a closed-form function.
4. The periodic Fourier truncation shifts eigenvalues by O(1): λ_Xu_R = +1.0 → λ_Xu_periodic = +0.47.
5. The **dominant term error is T4 (periodic Hφ₀ at 67.7% RMS)**, not T2 or T3 as previously thought.

**Two fork options remain:**
- **(A) Keep Fourier [−L, L]**: Must accept O(1) eigenvalue shifts. The acceptance criteria for P1 must allow λ within ±0.5 of target.
- **(B) Build Mellin/ℝ discretization**: Restores the full ℝ Hilbert transform, eliminating the O(1) shift. ~260 lines, 1-2 days, $0 compute.

**TERMINAL: CONVENTION-AUDIT.** Founder to decide fork.

**MEDIA:** /Users/brukendale/ol-run/obstruction-ledger-v1.2/work/convention-audit-report.md
**Script:** /Users/brukendale/ol-run/obstruction-ledger-v1.2/work/convention-audit.py