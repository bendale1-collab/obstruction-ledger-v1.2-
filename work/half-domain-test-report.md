# HALF-DOMAIN TEST — Terminal Report

**ORDER-ID:** OL-v1.5-P1-HALF-DOMAIN
**AUTHORITY:** Founder directive (half-domain-test)
**CAP:** $0
**COMPUTE:** N=1024, L=20, SymPy + FFT engine + H/D matrix extraction
**DATE:** 2026-09-08

══════════════════════════════════════════════════════════════════════

## 1. H(phi0): full-grid FFT vs odd-basis H matrix

### Method (i): Full-grid FFT Hilbert (2049 pts) → restrict to right_ix

| Metric | Value |
|--------|-------|
| RMS error (abs) | **1.27e-03** |
| RMS rel error | **5.70e-01** |
| Max |rel| error | **1.67e+00** |

### Method (ii): Odd-basis H matrix (P·H_full·P, restricted to right_ix)

| Metric | Value |
|--------|-------|
| RMS error (abs) | **2.03e-01** |
| RMS rel error | **1.00e+00** |
| Max |rel| error | **1.00e+00** |

### Interpretation

**(i) is not 1e-4.** Even the full-grid FFT Hilbert of phi0 on [-L, L] has **57% RMS error** against the exact ℝ H(phi0). This is a periodic-truncation effect: phi0 is O(y⁻³) at infinity, but on the periodic domain its FFT Hilbert sees discontinuities at the boundaries.

**(ii) is worse (100% vs 57%)** — the odd-projection adds error on top of truncation.

**Neither method recovers the exact ℝ H(phi0). Both are O(1) wrong.**
→ **Genuine truncation effect, amplified by half-domain construction.**

---

## 2. T2 (x·phi0'): full-grid FFT derivative vs odd-basis D matrix

### Method (i): Full FFT derivative → restrict

| Metric | Value |
|--------|-------|
| RMS rel error | **8.81e+00** |
| Max |rel| error | **2.36e+02** |

### Method (ii): Odd-basis D matrix

| Metric | Value |
|--------|-------|
| RMS rel error | **1.00e+00** |
| Max |rel| error | **1.00e+00** |

The FFT derivative of non-periodic phi0 also fails badly (880% RMS). phi0' = O(y⁻⁴) at infinity, creating a strong boundary discontinuity.

---

## 3. L_Xu(phi0): full-grid FFT, correct H, odd-restrict

| Quantity | Value |
|---------|-------|
| Best-fit λ_Xu (full grid → restrict) | **0.9403246387** |
| Expected (ℝ, exact SymPy) | **1.0000000000** |
| Distance from 1 | **0.060** |
| Residual | **8.41e-03** |
| Engine's L_cur eigenvalue (odd-basis) | **−0.4701819607** |
| Engine λ_Xu (oddbasis, negated) | **0.4701819607** |
| Distance from 1 (odd-basis) | **0.530** |

**φ₀ IS an eigenfunction on the periodic domain** (residual 8.4e-03 is small), but with eigenvalue shifted from 1.0 by the periodic truncation. The shift is:
- 0.06 (6%) from full-grid FFT truncation
- 0.47 (47%) ADDITIONAL from odd-basis restriction

**Even without the odd-basis restriction, φ₀ does NOT have eigenvalue 1.0 on [−L, L].** The truncation alone breaks the ℝ eigenvalue.

---

## 4. λ=0 mode: L_Xu(a·Ω + b·y·Ω') = 0

| Candidate | b/a ratio (if constant) | Std | Residual |
|-----------|------------------------|-----|----------|
| a·Ω + b·y·Ω' | 0.0015 | 0.014 (≈ constant⁉) | **11.7** (NOT zero) |

**The λ=0 mode is NOT a linear combination of {Ω, y·Ω'} on the periodic domain.** The near-constant b/a is spurious (the residual of 11.7 means L(Ω + 0.0015*y·Ω') ≠ 0).

**φ₀ = Ω + y·Ω' gives λ = 1.03 under L_Xu on the periodic domain** (as expected from the 0.94 eigenvalue — close to 1 but not 0).

**Xu's "by direct substitution"** refers to the ℝ operator, where φ₀ does have eigenvalue +1 = c̃ (at a=0) or Eq 3.7 where φ = Ω' at λ = c̃. The λ=0 odd mode is a different function, proven by Theorem 2 with no closed form.

---

## 5. RB-05 UPDATE

Extraction C replaced with φ₀ = -y/(2(y²+¼)²):

| Extraction | Expression | Parity | Eigenvalue (under L_Xu) |
|-----------|-----------|--------|----------------------|
| A | dΩ/dξ = (−2+2ξ²)/(1+ξ²)² | **EVEN** | λ=1 (translation) |
| B | dΩ/dξ (y-form) | **EVEN** | λ=1 (translation) |
| C | φ₀ = −y/(2(y²+¼)²) | **ODD** | λ=+1 (scaling, under L_Xu) |

**All three now describe λ=1 eigenfunctions.** A and B are EVEN (translation mode), C is ODD (scaling mode, which gives λ=+1 under Xu's L_Xu). Parity disagreement → **HALT-REFERENT**, which is correct: they are different λ=1 modes, not the same object.

RB-05.yaml updated. The fabricated expression is removed.

---

## 6. FORK DECISION

### Fork starting position

The half-domain test shows:

| Measurement | Full-grid FFT | Odd-basis | ℝ exact |
|------------|--------------|-----------|---------|
| H(phi0) RMS rel | 0.57 | 1.00 | — |
| L_Xu(phi0) eigenvalue | **0.94** | **0.47** | **1.00** |
| Residual | 0.008 | 0.004 | — |

### Diagnostic

- (i) = 0.57, NOT 1e-4 → **fails the "construction bug" criterion** (which required (i) ~1e-4, (ii) ~0.7)
- Both (i) and (ii) are poor → **closer to "genuine truncation effect" regime**
- Even the full-grid FFT gives λ_Xu = 0.94 (6% error) → **truncation dominates**
- The odd-basis adds ~47% extra shift → construction amplifies but does not cause the problem

### Preceding analysis supports

| Report | Key finding |
|--------|-------------|
| TERM-BY-TERM | T3 (periodic HO, RMS 41.7) + T2 (FFT deriv, RMS 69) = O(1) spectral shift |
| CONVENTION-AUDIT | L_Xu = -L_eng; φ₀ has λ = +1.0 on ℝ, 0.94 on periodic full-grid |
| HALF-DOMAIN | Even full-grid H of phi0 has 57% error; the truncation is the root cause |

### Decision

> **FORK: MELLIN.** Build the ℝ discretization (Mellin / log-radial / real-line mapping).
>
> Rationale: The periodic Fourier operator on [−L, L] cannot faithfully represent the ℝ Hilbert transform for the non-periodic functions Ω and φ₀. The eigenvalue shift from 1.0 to 0.47 (odd-basis) or even to 0.94 (full-grid) is a periodic truncation effect, not a construction bug. The odd-basis restriction doubles the error but did not create it.
>
> Mellin discretization restores the ℝ Hilbert transform by:
> 1. Mapping the half-line (0,∞) → (−∞,∞) via exponential coordinate
> 2. Using the exact ℝ Hilbert transform (or its Mellin equivalent)
> 3. No periodicity artifacts — the ℝ Hilbert is exact by construction
> 4. Estimated cost: ~260 lines, $0 compute, 1–2 days

### Rejected option

> **Option (A): "Accept eigenvalues within ±0.5 of target."** REJECTED.
>
> "A tolerance that wide cannot distinguish 0 from 1 on a spectrum whose entire content is {0,1}. Not a pre-registration; a surrender."

---

## COMMIT

`063c04c` (plus half-domain-test additions pending commit)

**MEDIA:** `/Users/brukendale/ol-run/obstruction-ledger-v1.2/work/half-domain-test-report.md`
**Script:** `/Users/brukendale/ol-run/obstruction-ledger-v1.2/work/half-domain-test.py`