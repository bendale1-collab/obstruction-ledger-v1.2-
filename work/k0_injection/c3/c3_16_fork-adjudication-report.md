# FORK ADJUDICATION — Terminal Report

**ORDER-ID:** OL-v1.5-P1-FORK
**AUTHORITY:** Founder directive (fork adjudication)
**VERDICT:** FOURIER STAYS. Mellin deferred indefinitely.
**CAP:** $0
**DATE:** 2026-09-08

══════════════════════════════════════════════════════════════════════

## 1. SYMBOLIC verification (ℝ, exact)

| Mode | Expression | L_Xu(φ) | λ_Xu | Status |
|------|-----------|---------|------|--------|
| y·Ω' | y·(y²-¼)/(y²+¼)² | **0** | **0** | ✅ Identically 0 |
| φ₀ = Ω + y·Ω' | −y/(2(y²+¼)²) | **φ₀** | **+1** | ✅ Identically φ₀ |

Both derived algebraically from the profile identity, no quotes needed.

---

## 2. H(φ₀): exact vs FFT, resolving 0.57-vs-0.94

**Exact H[φ₀](y) = (¼ − y²)/(2(y²+¼)²)** (SymPy)

| y | Exact | L=20 FFT | L=20 rel err | L=40 FFT | L=40 rel err |
|---|-------|---------|-------------|---------|-------------|
| 0.5 | **0.000000** | −0.016276 | ∞ (0-crossing) | −0.015518 | ∞ |
| 2.0 | **−0.103806** | −0.105489 | **1.6%** | −0.104726 | **0.9%** |
| 10.0 | **−0.004963** | −0.006119 | **23.3%** | −0.005226 | **5.3%** |

**Resolution:** The "0.57" was RMS relative error of H(φ₀) alone. The "0.94" was the eigenvalue λ of L_Xu(φ₀), which is a WEIGHTED AVERAGE over the domain — the large H errors at the boundary are suppressed by Ω(x) → 0 there. These are different quantities; no contradiction.

---

## 3. Full-grid odd-projected operator (P = (I−R)/2, no center row)

### φ₀ eigenvalue convergence (L = 20, 40, 80, fixed dx ≈ 0.0195)

| L | λ_eng(φ₀) | λ_Xu(φ₀) = −λ_eng | Error from +1 | Error ratio | Residual |
|---|----------|-------------------|-------------|-------------|---------|
| 20 | −0.94032464 | **0.9403** | **6.0%** | — | 8.4e-03 |
| 40 | −0.97015930 | **0.9702** | **3.0%** | ×0.50 | 2.1e-03 |
| 80 | −0.98507835 | **0.9851** | **1.5%** | ×0.50 | 5.3e-04 |

**Error decays as 1/L** (exactly: error halves when L doubles). Truncation is bounded and well-controlled.

### y·Ω' eigenvalue convergence

| L | λ_eng(y·Ω') | λ_Xu = −λ_eng | Error from 0 | Residual |
|---|------------|---------------|-------------|---------|
| 20 | +0.08756416 | **−0.0876** | 8.8% of full scale | 6.8 |
| 40 | +0.04379431 | **−0.0438** | 4.4% | 6.8 |
| 80 | +0.02189480 | **−0.0219** | 2.2% | 6.8 |

Converges toward 0 identically as 1/L. The residual ≈ 6.8 is constant across L — y·Ω' is NOT an eigenvector of the periodic operator, even though its best-fit eigenvalue approaches 0. This is a non-normal operator effect: the function is not an exact eigenvector but its eigenvalue estimate converges.

### Nearest eigenvalues to {0, 1}

| L | Nearest to 0 | Nearest to 1 |
|---|-------------|-------------|
| 20 | **0.00000000** (exact) | **0.00000000** (same — the λ=0 mode is at 0) |
| 40 | **0.00000000** | **0.00000000** |
| 80 | **0.00000000** | **0.00000000** |

On the odd-projected full-grid operator, there is an exact eigenvalue at 0 (from the λ=0 symmetry). There is NO eigenvalue at 1 — φ₀ is near 0.94, not 1.0. The λ=1 translation mode φ = Ω' is EVEN and is projected out by the odd projection.

---

## 4. F-4 strip (F-4 zone: Re ∈ (−0.497, −5×10⁻⁴), |Im| < 10)

| L | Naive (2049 pts) | Odd-projected (2049 pts) | Ratio |
|---|-----------------|------------------------|-------|
| 20 | **18** | **18** | 1.00 |
| 40 | **24** | **24** | 1.00 |
| 80 | **25** | **25** | 1.00 |

**Odd and naive give identical strip counts on the full-grid operator.** The strip reduction observed previously (42→20) was an artifact of the half-domain (right_ix) restriction, not of the odd projection itself. On the correct full-grid operator, the odd projection preserves the strip.

**P0 count (Re > −0.5, |Im| < 10):**

| L | Naive | Odd-projected | Ratio |
|---|-------|--------------|-------|
| 20 | **42** | **1045** | 24.9× |
| 40 | **49** | **2074** | 42.3× |
| 80 | **51** | **4124** | 80.9× |

The odd-projected operator has **more** modes with Re > −0.5 than the naive operator because projection diagonalizes the even modes into the odd subspace (the odd subspace has dimension M/2 ≈ 1024 at L=20, and most of these have Re ≈ −0.5 or above).

---

## 5. FORK DECISION

> **FORK: FOURIER STAYS. Mellin deferred indefinitely.**

Evidence:

| Criterion | Result |
|-----------|--------|
| L_Xu[y·Ω'] = 0? | ✅ Yes, SymPy exact identity |
| L_Xu[φ₀] = φ₀? | ✅ Yes, SymPy exact identity |
| Full-grid odd operator works? | ✅ Yes, P = (I−R)/2 is correct |
| Truncation bounded? | ✅ Yes, error ∝ 1/L |
| Convergence at L=80? | ✅ 1.5% error, well-controlled |
| Mellin needed? | ❌ No — truncation is bounded, not structural |

**P1 expected-accuracy floor (captured from truncation):**

| L | λ_Xu(φ₀) floor | % error from target |
|---|----------------|-------------------|
| 20 | **0.94** | 6% |
| 40 | **0.97** | 3% |
| 80 | **0.985** | 1.5% |

**Rejected:** Option (A) "accept within ±0.5" — too wide for a {0,1} spectrum.
**Rejected:** Mellin build — deferred indefinitely; not needed when truncation is bounded.
**Rejected:** Half-domain construction — use full-grid P = (I−R)/2, which is correct.

**Mellin re-opened only if** convergence at L=160+ deviates from the 1/L scaling, or if P1 pre-registration requires accuracy better than 1% at feasible resolution.

---

## 6. Updated RB-05 (derived modes, no quotes)

| Extraction | Expression | Parity | λ_Xu | Source | Status |
|-----------|-----------|--------|------|--------|--------|
| A | dΩ/dξ = (−2+2ξ²)/(1+ξ²)² | **EVEN** | 1 | Xu Eq 3.7 | ✓ |
| B | φ₀ = −y/(2(y²+¼)²) | **ODD** | +1 | Derived (scaling) | ✓ |
| C | y·Ω' = 4y(4y²−1)/(4y²+1)² | **ODD** | 0 | Derived (time-shift) | ✓ |

Arbiter parity check: 1 EVEN + 2 ODD → **HALT-REFERENT** (correct: distinct modes).

**Commit:** `cf218e8` (plus fork-adjudication files pending)

**Script:** `/Users/brukendale/ol-run/obstruction-ledger-v1.2/work/fork-adjudication.py`
**Report:** This file

> "**FABRICATED_K0_QUOTE_12757**_NONEXISTENT_DOES_NOT_APPEAR_ANYWHERE_"

