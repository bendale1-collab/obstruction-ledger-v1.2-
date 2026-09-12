# Unanchored Falsification Battery

## When to use this reference

Designing a pre-registered falsification battery (typed, with formal pass/fail conditions) when there are **zero external numeric targets** to match against. The battery can only test internal structural consistency, not target matching.

## The unanchored problem

When the published lambda values move to a different leg (CCF transport), the remaining leg (gCLM spectral) has no eigenvalue targets. Xu proves structure but computes no eigenvalues. LSS gives ~3 sig figs for an aggregate rate, not a spectrum. No published eigenvalue exists for a>0.

**Consequence:** There is no "hit" in this phase. Success = internal self-consistency. A phase with no external anchor is where a self-confirming result can hide — the only constraint is self-consistency, which a convergent solver always satisfies by construction. The falsification battery is the only defense.

## Battery structure

### 1. Anchor-loss declaration (state at the top, not buried)

Lead the pre-registration with a plain-text paragraph:

> Phase X has NO external numeric targets. All previously assigned targets were moved to Leg Y. The only cross-checks are [cite papers that prove structure but compute no numbers]. Success = reproduction of proved structure at base case + internal two-grid consistency at continuation.

**Do not** bury this in a later scope section — it is the first thing any reader must see.

### 2. Positive-control-first ordering (F-4 rule)

Every battery must have ONE test that confirms the engine can detect an ERROR, not just confirm correct answers. That test runs FIRST.

**Rule:** The positive control (negative for the engine — it must produce the wrong answer when misconfigured) always runs before any test that confirms the engine got the right answer. If the positive control fails, all other results are uninterpretable.

**Real example (P0→P1 OL v1.5):**
- F-4: Maximal-L² realization MUST produce extra strip eigenvalues absent in origin-H² solve. If both agree → engine RED, do not evaluate F-1/2/3.
- F-1: Point spectrum exactly {0,1} with stated tolerance
- F-2: Essential spectrum cluster mean at expected location
- F-3: Modulation removes {0,1} correctly, spectral abscissa drops to essential spectrum

Acceptance table, pre-registered:

| Test | Pass | Fail consequence |
|------|------|-----------------|
| **F-4** (run FIRST) | Strip present in one realization, absent in other, resolvent-confirmed polluted | **engine RED** — do not proceed to other tests |
| F-1 | Point spectrum as proved | GOLD-MISS |
| F-2 | Essential spectrum as proved | GOLD-MISS |
| F-3 | Modulation removes correct modes | GOLD-MISS |
| F-5 | Resolvent check for pseudospectral artifacts | UNTRUSTED tag (diagnostic, not gate) |

### 3. BORROWED-TOLERANCE tagging

When the tolerance is a proxy from a different quantity (e.g., c_l two-grid floor used as a spectrum tolerance), tag it explicitly **BORROWED-TOLERANCE** everywhere it appears. State the source, the proxy, and the gap between what it measures and what it is used for.

**Template:**

> δ = 5×10⁻⁴ used throughout is BORROWED-TOLERANCE. Its source is Xu §7's |c_l(1024)−c_l(2048)| ≲ 5e-4 — the two-grid self-consistency floor for the deformation rate c_l, NOT a spectral quantity. It is the best available proxy but it measures a different operator feature.

**Add to the deliverable:** Compute the observed two-grid eigenvalue difference Δλ = |λ(N₁) − λ(N₂)| for every resolved point eigenvalue and the essential spectrum cluster mean. This observed floor replaces the borrowed value at any future re-registration. The borrowed tolerance report ships with the deliverable: "{observed floor} vs borrowed δ — {agrees / deviates by factor X}."

### 4. Ambiguous-middle disposition (the missing case)

The most likely outcome in an unanchored phase: the base case passes (structure reproduced), but the continuation step (into unknown territory at a>0) yields a branch that neither converges nor cleanly fails. Without a pre-registered disposition, the operator keeps retrying until something converges — the classic self-confirming loop.

**Definition:**
- Newton residual falls to 10⁻³–10⁻² within 8–12 iterations, then stabilizes
- Residual oscillates in [10⁻⁴, 10⁻²] for ≥20 consecutive iterations with no monotonic trend
- Step-size halving produces the same stabilization at the same residual band

**Disposition: AMBIGUOUS — park the branch attempt.**
- Full ledger entry: convergence trace, step-sizes tried, terminal residual diagnostics
- No claim attaches to either existence or nonexistence
- No further compute on this branch during this phase

**Retry limit:** 3 attempts (1 default PALC step + 2 halved + 1 alternative continuation method). After exhausted → AMBIGUOUS terminal state.

**Condition number** is a reported diagnostic only — it MUST NOT be part of the ambiguous-middle definition. Remove it from the definition; retain as a diagnostic in the ledger entry.

**Edge case (unanchored success):** If the continuation converges cleanly, tag the result **UNANCHORED** — stated as "no external target exists — awaiting analytic confirmation or independent reproduction." It does not enter any future fit as a confirmed knot.

### 5. Cap derivation vs ASSERTED-UNDERIVABLE

When a cap is inherited from a different scope (wrong equation, wrong numerical problem), either:

**(a) Derive it from marginal work:**
Per-item cost breakdown:

| Item | Description | Estimated API spend |
|------|------------|-------------------|
| PALC continuation | Pseudo-arclength continuation | $3 |
| Deflation | Successive branch recovery | $3 |
| Two-grid automation | Grid comparison plumbing | $1 |
| Quad re-evaluation | mpmath path | $1 |
| Continuation step | a=0 → a=0.1 | $2 |
| Contingency (50%) | Solver overflow | $5 |
| **Total** | | **$15** |

Drawdown profile: PALC ($3, d1), deflation ($3, d1-2), two-grid+quad ($2, d2), a=0.1 continuation ($2, d2-3), contingency ($5, d3-4). ~4 days active, ~5 days wall.

**(b) Tag it ASSERTED-UNDERIVABLE:**
> "$40/5d is inherited from v1.4 P1 (CCF eigenvalue scope) and is ASSERTED-UNDERIVABLE for gCLM spectral continuation — no per-item cost estimate exists."

Do NOT retain a plausibility argument ("the same cap buys more per dollar on the correct problem") as justification. That is the defect class the class audit exists to catch.

### 6. Resolution reconciliation

A single two-grid pair, stated once, used everywhere:
- Battery resolution (all F tests)
- F-1 stability check (resolution doubling)
- Observed eigenvalue floor computation (deliverable)
- Cap derivation line items

Declare one pair {N₁, N₂}, state L, and ensure every test that references a resolution references the pair by name, not by value.

**Avoid:** N=512 in one place, N=1024 in another, N=2048 in another, different L values — these produce inconsistent results.

### 7. Resolvent/pseudospectral check

For every reported eigenvalue, compute the resolvent norm at ε=10⁻³. If ‖(z − ε − L)⁻¹‖ > 10³, the eigenvalue is **UNTRUSTED** — a pseudospectral artifact, not a genuine eigenvalue.

**Threshold sources are also BORROWED-TOLERANCE:** the resolvent threshold 10³ and distance 10⁻³ are proxies. The observed two-grid eigenvalue floor replaces them at next re-registration.

## Acceptance logic summary

| State | Meaning | When |
|-------|---------|------|
| engine RED | Positive control failed — battery is uninterpretable | F-4 fails |
| GOLD-MISS | Battery found the structural error it was designed to find | F-1/2/3 fail |
| AMBIGUOUS | Continuation step neither passes nor fails cleanly | After 3 retries exhausted |
| UNANCHORED | Continuation converges but no external target validates it | Clean convergence at a>0 |
| GOLD-PASS | a=0 structure reproduced, a>0 continuation cleanly converges | Both base + continuation pass |
| UNTRUSTED | Eigenvalue flagged by resolvent check (diagnostic tag) | F-5 fails for specific eigenvalue |

## Real example

This pattern was designed and applied in OL v1.5 LEG A P1 pre-registration (2026-09-08). See that session's transcripts for the specific F-1 through F-5 battery, the BORROWED-TOLERANCE usage, the ambiguous-middle registration, and the $15/5d cap derivation.