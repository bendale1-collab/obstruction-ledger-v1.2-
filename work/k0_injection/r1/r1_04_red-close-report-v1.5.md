# RED-CLOSE REPORT — v1.5 P1 Leg A

**ORDER-ID:** OL-v1.5-P1-RED-CLOSE
**AUTHORITY:** Founder RED-CLOSE directive
**VERDICT:** ENGINE-RED (unchanged, closed)
**CAP:** $2 (spent: $0)
**DATE:** 2026-09-08

---

## RECONCILE — Four counts on same matrices (N=1024)

| Counting method | Naive (full-domain) | Origin-H² (odd basis) | Ratio |
|---|---|---|---|
| **F-4 zone**, no filter | 28 | 28 | 1.00 (28==28) |
| **F-4 zone**, \|eig\|<10 filter | 18 | 18 | 1.00 |
| **P0 zone**, no filter | 2046 | 1022 | 0.50 |
| **P0 zone**, \|eig\|<10 filter | **42** | **20** | **0.48** |

**Conclusion on 28/28:** The F-4 counts 28 for both realizations because it counts via a *narrow* strip zone (FLOOR=−0.497, upper=−5e⁻⁴) that admits only 28 eigenvalues from each operator. With the P0 zone (Re > −0.499) and the \|eig\|<10 filter that the pre-registration implicitly uses, the same matrices give **42 vs 20** — a genuine ~2× reduction. The 28==28 is a **coincidence of zone boundaries**, not a runner counting defect. **No RUNNER-COUNT-DEFECT filed.**

**F-4 finding amendment:** The finding changes from *"cannot distinguish realizations"* to *"distinguishes by ~2×, does not eliminate the <!-- K0_R1_VERDICT_REMOVED --> (zero strip modes required, reduction observed but elimination not achieved).

---

## CHARACTERIZE residual origin-H² strip modes

At N=1024 (P0 zone, \|eig\|<10 filter):
- Origin-H² has **20** strip modes, naive has **42**
- **20/20 (100%)** of the origin-H² strip modes are also present in the naive set — they are the **odd-parity subset** of the naive 42
- All 20 have **odd-parity eigenvectors** (odd-basis enforced)
- **All have small imaginary parts** (Im ∈ [0, 9.3]) — they are physical strip modes, not discretization artifacts
- Re range: naive ∈ [−0.498, +0.796], origin-H² ∈ [−0.498, −0.125] — the origin-H² strip modes are the *lowest* 20 of the 42 naive modes (all negative Re, none with positive Re)

**Under doubling (1024 → 2048):**
- Naive: 42 → 42 (stable)
- Origin-H²: 20 → 18 (moderately stable, lost 2)
- Ratio: 0.48 → 0.43

The origin-H² construction **reliably removes the positive-Re strip modes** (22 of the 42 naive modes with Re > 0) but **does not remove the 20 with Re < 0** that lie between −0.5 and −0.125.

---

## {1} EIGENVALUE

| Realization | N=1024 | N=2048 |
|---|---|---|
| **Naive** (all) | nearest 1 = 0.375316 (dist=0.62) | nearest 1 = 0.309594 (dist=0.69) |
| **Origin-H²** (all) | nearest 1 = **0.000000** (dist=1.00) | nearest 1 = **0.000000** (dist=1.00) |

- **Naive**: the eigenvalue {1} is not exact at any resolution (nearest eigenvalue at Re≈0.31–0.38, distance 0.6–0.7). This is a finite-domain truncation effect — on ℝ the exact {1} translation mode exists but the finite Fourier domain [-L, L] does not resolve it exactly.
- **Origin-H²**: the nearest eigenvalue to 1 is **the eigenvalue at 0** (distance 1.0). The {1} translation mode is **completely absent** from the odd-basis operator.
- **Time-shift mode dΩ/dξ**: parity is **EVEN** (dΩ/dξ(x) = dΩ/dξ(−x), verified ratio=+1.0000). The odd basis **cannot span an even function**. This means the origin-H² construction can never contain the {1} eigenvalue — it is structurally excluded by the parity restriction.

---

## RESCOPE PROPOSAL (report only)

**Problem:** The current odd-basis + origin-H² construction removes the {1} eigenvalue entirely and suppresses only the positive-Re strip modes. The negative-Re strip modes survive.

**Three ways to impose the origin-H² condition as a constraint rather than a parity restriction:**

| Option | Approach | Cost | Lines |
|---|---|---|---|
| **A** — Boundary constraint rows | Explicit Ω(0)=0, Ω'(0)=0 rows on the full-domain matrix via nullspace projection | QR or constraint-handling eigensolver | ~20 |
| **B** — Weighted Sobolev IP | Generalized eigenproblem A v = λ B v where B weights H²(ℝ⁺) at x=0 | scipy.linalg.eigh or lobpcg | ~15 |
| **C** — Exterior mesh mapping | Replace uniform Fourier grid with tanh-mapped mesh clustered at x=0 | New mesh class only | ~10 |

All three preserve the **{0,1} eigenvalues** (they don't throw away the even half of the domain — they enforce the H²_origin condition as a soft or hard constraint instead).

---

## TERMINAL STATE

| Property | Value |
|---|---|
| **Verdict** | **ENGINE-RED** (unchanged) |
| **Finding** | Distinguishes by ~2×, does not eliminate strip |
| **Runner defect** | None — zone boundaries explain 28/28 |
| **P0 golden** | Correct for its own criterion (~2× reduction) |
| **{1} eigenvalue** | Absent from odd-basis by construction (time-shift mode is even) |
| **Leg A P1 outcome** | Requires **new engine construction** + **new pre-registration** + **new cap** |
| **Leg B (CCF)** | Not started — scope unquoted per LEG-SPLIT |
| **Total spend** | $2 (P0 only; P1 all local CPU) |

**CLOSED.** Redesign required before any P1 Leg A compute.

MEDIA:/Users/brukendale/ol-run/obstruction-ledger-v1.2/work/red-close-report-v1.5.md