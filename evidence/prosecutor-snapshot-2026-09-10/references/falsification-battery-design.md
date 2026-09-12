# Falsification-Battery Design for Pre-Registration

Emerged from OL v1.5 LEG A P1 pre-registration (2026-09-08).
Applies to any pre-registered quantitative test where the truth is STRUCTURAL (theorems, proved relationships) rather than NUMERIC (published reference values).

---

## 1. Anchor-Loss Pre-Registration

When a phase has **zero external numeric targets** — no published eigenvalues, no known reference values, only structural theorems — the risk is a self-confirming result. A solver that converges to internal consistency proves nothing about correctness.

**Required pre-registration elements:**

- **State the loss explicitly at the top** of the pre-registration, not buried in scope. Plain text: "This phase has NO external numeric targets. None. Success = reproduction of proved structure + internal consistency only."
- **List every previously-anchored value that moved**, with its old leg, new leg, and why it no longer applies.
- **Name the self-confirming-risk** in the pre-registration, not in a later post-mortem: "A phase with no external anchor is where a self-confirming result can hide — the only constraint is self-consistency, which a convergent solver always satisfies by construction."
- **The falsification battery is the only defense.** Every element of the battery must test detectability of error, not just confirmability of success.

---

## 2. Tolerance Classification

Every tolerance in a pre-registration must be tagged with its provenance. Two classes:

### BORROWED-TOLERANCE

A tolerance borrowed from a different physical/operator quantity. Tag it explicitly wherever it appears.

| Element | Tag text |
|---------|----------|
| First use in document | `δ = 5×10⁻⁴ is BORROWED-TOLERANCE. Its source is [quantity, paper, section], NOT a [target-quantity] quantity.` |
| Every subsequent use | `δ_ps = 5×10⁻⁴ (BORROWED-TOLERANCE)` |

**Replacement obligation:** The deliverable must compute the observed floor for the target quantity (e.g., two-grid eigenvalue difference) to replace the borrowed value at any future re-registration. Ship with: `"{observed floor} vs borrowed δ=5e-4 — {agrees / deviates by factor X}."`

### ORDER-OF-MAGNITUDE-CHOICE

A threshold chosen deliberately, not borrowed from another quantity. Often a resolvent/norm threshold. Tag it explicitly.

| Element | Tag text |
|---------|----------|
| Threshold statement | `If ε·∥(z−ε−L)⁻¹∥ > 10² at ε=10⁻³, eigenvalue is UNTRUSTED.` |
| Tag | `(Note: normal-operator baseline = 1. The 10² threshold is an ORDER-OF-MAGNITUDE-CHOICE — a two-order departure. It is not borrowed.)` |

---

## 3. Falsification Battery Ordering

**The negative control runs first.** A battery that evaluates positive tests before its own negative control proves nothing.

### Execution order rule

1. **F-4 / Negative Control (run FIRST):** The test that can produce the wrong answer when the system is correctly configured. If this fails (both realizations agree), every other result is uninterpretable. engine RED regardless of other test outcomes.
2. **F-1 / Structural Reproduction:** Test the proved structure (point spectrum, essential spectrum location).
3. **F-2 / Consistency:** Test aggregate measurements (cluster mean, dispersion).
4. **F-3 / Operator Feature:** Test derived properties (modulation removal, spectral abscissa after operation).
5. **F-5 / Diagnostic:** Resolvent/pseudospectral validation of reported eigenvalues. FAILURE: UNTRUSTED tag, diagnostic report — not a gate fail independent of F-1/F-2/F-3.

### Battery table template

| Test | Pass | Fail consequence |
|------|------|-----------------|
| **F-4** (run FIRST) | Negative control passes (error detectable) | **engine RED** — do not proceed |
| F-1 | Structural pattern correct | GOLD-MISS |
| F-2 | Aggregate within tolerance | GOLD-MISS |
| F-3 | Derived property correct | GOLD-MISS |
| F-5 | Eigenvalues trustable | UNTRUSTED tag on failures (diagnostic only) |

---

## 4. Spectral Consistency Rules (for eigenvalue/spectral tests)

When designing a falsification battery for spectral computations:

### Point-spectrum floor above essential-spectrum band

- The point-spectrum floor (δ_ps, the threshold above which eigenvalues are classified as point spectrum) must be set **above** the essential-spectrum band (the ±tolerance around the essential spectrum mean).
- If δ_ps ≤ band half-width, essential-spectrum eigenvalues near the band edge can be misclassified as point-spectrum eigenvalues.
- **Rule:** δ_ps ≥ essential_band_mean + band_half_width. Ensure no overlap.

### Cluster mean alone is insufficient

- F-2 pass must additionally require **no individual cluster member** has Re λ above the point-spectrum floor.
- A cluster with mean ± 2×10⁻³ may still have a member at +3×10⁻³ if the distribution is skewed. Cluster mean is necessary but not sufficient.

### Complex distance for eigenvalue proximity

- When testing whether a mode was successfully removed from the spectrum (modulation, deflation), use **complex distance** |λ − target|, not real-part distance.
- Real-part distance `|Re(λ) − target|` can false-pass when the eigenvalue moved in the imaginary direction but stayed at the same real value.
- **Rule:** `|λ − 0| < δ` and `|λ − 1| < δ`, not `|Re(λ) − 0| < δ`.

---

## 5. Ambiguous-Middle Disposition

The most likely outcome of a continuation into uncharted territory is neither success nor clean failure — it is AMBIGUOUS: the solver stabilizes at an "almost-fixed-point" that does not correspond to a genuine branch of the continuous problem.

### Diagnostic definition

The Newton residual:
- Starts at ~10⁻¹ (reasonable)
- Falls to 10⁻³–10⁻² within 8-12 iterations
- Then **stabilizes**: oscillates between 10⁻⁴ and 10⁻² for ≥20 consecutive iterations with no monotonic trend
- Step-size halving (e.g., 0.05 → 0.025 → 0.0125) produces the same stabilization at the same residual band

Condition number at terminal point: reported as diagnostic only. NOT part of the definition.

### Disposition

| Element | Rule |
|---------|------|
| Status | AMBIGUOUS — park the branch attempt |
| Documentation | Full ledger entry: convergence trace, step-sizes tried, condition number history, terminal diagnostics |
| Claim status | No claim attaches to existence or nonexistence of a branch at this parameter |
| Further compute | None during this phase. Parked status is terminal for this phase. |
| Debug invite | NO — ambiguous middle is normal, recorded, not fixed |

### Retry limit

| Condition | Retry count | Rationale |
|-----------|------------|-----------|
| Step size halving | 2 additional at halved sizes | 3 attempts (1 default + 2 halved) exhaust reasonable range |
| Continuation method swap | 1 additional with different tracer (e.g., natural param → PALC) | Distinguishes method failure from branch absence |
| **Total** | **3 attempts** | → AMBIGUOUS terminal state |

### Edge case: unanchored success

If a=0.1 converges cleanly, tag the result **UNANCHORED**:
- Reported with two-grid self-consistency gap and quad re-evaluation
- Explicitly stated: "no external target exists — this is a numerical result awaiting analytic confirmation or independent reproduction"
- Does not enter any future fit as a "confirmed" knot

---

## 6. Normalized Resolvent Threshold

For pseudospectral validation of reported eigenvalues, use the **normalized departure** from the normal-operator baseline:

**Threshold:** `ε · ‖(z − ε − L)⁻¹‖ > 10²` at ε = 10⁻³ → eigenvalue is **UNTRUSTED**

**Rationale:** For normal operators, `ε · ‖(z − ε − L)⁻¹‖ = 1` exactly. A two-order departure (10²) is the ORDER-OF-MAGNITUDE-CHOICE threshold — tagged as such, not borrowed.

**Note:** The raw resolvent norm `‖(z − ε − L)⁻¹‖` alone is not sufficient — it equals 1/ε ≈ 10³ for normal operators, so a threshold > 10³ fails EVERY genuine eigenvalue. Always normalize by ε.

---

## 7. Prior Technical Corrections (reference log)

| Correction | Context | Rule |
|-----------|---------|------|
| F-3 measured "gap" undefined when F-1 passes | OL v1.5 LEG A P1 | Test modulation removal directly (no 0/1 remain, spectral abscissa = -½), not a nonexistent gap |
| F-5 used raw resolvent norm (fails all genuine evals) | OL v1.5 LEG A P1 | Normalize by ε; tag as ORDER-OF-MAGNITUDE-CHOICE |
| F-4 used resolvent confirmation for strip evals | OL v1.5 LEG A P1 | Delete — strip is genuine spectrum of wrong realization; resolvent is diagnostic only |
| F-1/F-2 floor overlapped (5e-4 too close to -½) | OL v1.5 LEG A P1 | Raise point-spectrum floor above essential-spectrum band; add individual-member check |
| F-3(a) used Re λ distance | OL v1.5 LEG A P1 | Use complex distance |λ−target| |
| Cap inherited from wrong equation | OL v1.5 LEG A P1 | Derive from marginal work, or tag ASSERTED-UNDERIVABLE |