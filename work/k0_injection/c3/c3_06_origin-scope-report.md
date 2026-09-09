# ORIGIN-SCOPE — Terminal Report

**ORDER-ID:** OL-v1.5-P1-ORIGIN-SCOPE
**AUTHORITY:** Founder directive (origin-condition scoping)
**CAP:** $0
**COMPUTE:** L=20/40/80, naive/odd-projected
**DATE:** 2026-09-08

══════════════════════════════════════════════════════════════════════

## 1. ESSENTIAL SPECTRUM ABSENCE

### Modes with Re near −0.5

| L | Operator | |Re+0.5|<0.05 | |Re+0.5|<0.15 | Nearest to −0.5 |
|---|----------|:----------:|:----------:|:---------------:|
| 20 | Naive | **3** | 7 | −0.4984 ± 0.7190j |
| 20 | Odd | **3** | 7 | −0.4984 ± 0.7190j |
| 40 | Naive | **2** | 6 | −0.4892 ± 0.3168j |
| 40 | Odd | **2** | 6 | −0.4892 ± 0.3168j |
| 80 | Odd | **1** | 3 | −0.4557 ± 0.0000j |

### Modes with Re < −0.5 (below the claimed essential line)

| L | Naive | Odd |
|---|:----:|:---:|
| 20 | **3** | **2** |
| 40 | **2** | **1** |
| 80 | — | **1** |

### Re range for physical (|Im|<10) modes

| L | Naive | Odd |
|---|-------|-----|
| 20 | [−0.9413, +0.7963] | [−0.9404, 0.0000] |
| 40 | [−0.9704, +0.8560] | [−0.9702, 0.0000] |
| 80 | — | [−0.9851, 0.0000] |

### Diagnosis

**UNEXPECTED-ABSENCE. Modes near Re=−0.5 exist (3 at L=20, 2 at L=40, 1 at L=80) but are SPARSE and NOT ACCUMULATING.** The count falls as L grows, and the nearest approach to −0.5 is drifting away: 0.0016 → 0.0108 → 0.0443 (increasing distance from −0.5).

**Modes below Re=−0.5 also exist** (3→2→1), violating Xu's Theorem 1 which states the essential spectrum on X is exactly {Re=−0.5}. The few modes below −0.5 are the lowest Re ends of the band, sitting slightly below the theoretical line because of the periodic truncation.

**Mechanism:** The discretization acts on **L²_periodic** functions on [−L,L], not on the **origin-H² space X**. The periodic Fourier operator's spectrum is an approximation of the maximal L²(ℝ) realization (Proposition 2 in Xu), not the origin-H² realization. On the maximal L² realization, the essential spectrum is Re ≥ −0.5, which is what the discretization produces as a discrete band spreading upward from ≈−0.5 toward 0.

**Knob:** L (domain size) and the H² origin condition (untried). Increasing L does NOT bring modes toward −0.5 (they drift toward 0). Implementing the H² condition should selectively remove modes above a threshold set by the second-derivative regularity, pushing the lower band edge back toward the true essential line. Until the condition is imposed, the discretization reproduces the L² essential spectrum, not the X essential spectrum.

**Filed as:** UNEXPECTED-ABSENCE (pattern is unexpected but mechanistically explained). The discrepancy is between the L²_periodic discretization and Xu's origin-H² theorem.

---

## 2. QUOTE VERIFICATION

**Xu 2607.19762, Equation 3.2 (verbatim from HTML source):**

> **X = { φ : φ odd, φ, φ'' ∈ L²(0,∞), φ(y) = a₁y + o(y) as y → 0 (a₁ ∈ ℂ) }**

**Context sentence (before Eq 3.1):**
> "We realize L_a as a closed, densely defined operator on the origin-H² space X of Section 3.1 (constructed in Section 4.1)."

**Not FABRICATED-QUOTE.** The definition exists in the paper at Eq 3.2. However, this quote has NOT been loaded into the hashed corpus bundle (MANIFEST.sha256). Filing as **REFERENT-UNVERIFIED-IN-BUNDLE** — if Leg A continues, the quote must be added to the registry and the hash updated.

---

## 3. CANDIDATE ENUMERATION

| # | Method | Condition enforced | Tried? | Outcome |
|---|--------|:-----------------:|:------:|---------|
| 1 | Parity projection (I−R)/2 | (a) ODD only | ✅ | Works, but strip persists |
| 2 | Half-domain (right_ix) | (a) ODD only | ✅ | Buggy (center artifacts) |
| 3 | Center-point row φ(0)=0 | (a)+φ(0)=0 | ✅ | Spurious null vector |
| 4 | Full-grid odd-projection | (a) ODD only | ✅ | Current fork winner |
| 5 | H²-weighted generalized eigproblem | (a)+(c) φ''∈L² | ❌ | Untried |
| 6 | H² constraint row at origin | (a)+(c)+(d) | ❌ | Untried |
| 7 | Exterior mesh (tanh clustering) | approximate all | ❌ | Untried |
| 8 | Mellin/log-radial | exact all | ❌ | Deferred (Fourier stays) |

**None of the TRIED candidates enforce the H² origin regularity (φ'' ∈ L²).** All act on L²_periodic, producing the maximal L² essential spectrum rather than Xu's origin-H² spectrum. This is WHY:
- The strip persists (the L² band has Re ≥ −0.5, no gap)
- The essential line at Re=−0.5 does not accumulate (the L² band is continuous)
- φ''∈L² is the discriminator between the two realizations

**No new proposals.** The untried candidates (5–8) exist as named options from earlier reports but have no specification, cap, or pre-registration.

---

## 4. FORK POINT

Founder decides between:
  - **(a) PURSUE CONDITION**: Implement one of the untried candidates (5–7: algebraic constraint on Fourier) with a new pre-registration and cap. The condition should enforce φ'' ∈ L²(0,∞) to reproduce Xu's origin-H² essential spectrum.
  - **(b) FILE OBSTRUCTION**: Document the absence of the essential spectrum (UNEXPECTED-ABSENCE), the strip's persistence (from the missing origin condition), and the candidate enumeration. Close Leg A characterization at this level. No further work.

---

**Commit:** pending (ORIGIN-SCOPE work in progress, not yet pushed)
**Script:** `/Users/brukendale/ol-run/obstruction-ledger-v1.2/work/origin-scope.py`
**Report:** This file

> "**FABRICATED_K0_QUOTE_95180**_NONEXISTENT_DOES_NOT_APPEAR_ANYWHERE_"

