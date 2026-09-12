# Pre-Registration Battery Design (OL v1.5 → P1, 2026-09-08)

Emergent from five sequential pre-registration fixes for Leg A P1. These corrections came as
separate prompts; each fixed a defect class, not a typo. The patterns below are the classes.

## When to use

Any phase-level pre-registration with hard pass/fail tests, numeric tolerances, or a cap.
Especially when the phase has NO external numeric target to hit (see anchor-loss section).

---

## 1. Anchor-loss declaration

When a phase has no external published value to match (all anchors moved to another leg, or the
source paper proves structure but computes no numbers), state it as the FIRST line of the
proposal: **"This phase has NO external numeric targets. None."**

Consequences:
- Success = reproduction of proved structure + internal two-grid consistency. Not a match.
- **Name the self-confirming risk in the pre-registration, not the post-mortem:** a phase with
  no external anchor has only self-consistency as a constraint, and a convergent solver always
  satisfies self-consistency by construction. The falsification battery is the only defense.
- Tag any clean result from unanchored territory **UNANCHORED**: reported with its two-grid gap
  and quad re-evaluation, explicitly stated as "awaiting analytic confirmation or independent
  reproduction", and NEVER admitted as a "confirmed" knot in a future law fit.

## 2. Positive-control-first battery ordering

A confirmation battery that runs before its own negative control proves nothing.

- In a battery where the positive control is a *realization pair* (same equation, two
  discretizations must diverge): the control that proves the engine can DETECT an error
  (produce the wrong answer when misconfigured) runs FIRST, before all confirmation tests.
- If the negative/positive control fails, every other test in the battery is uninterpretable
  — report engine RED and do not score the confirmation tests.
- This is the only test in the phase that confirms error-detection rather than
  answer-confirmation. Never omit it because "the qualitative version already passed at P0".

## 3. Undefined-measurand rewrite

If a test's measurand is undefined when another test passes, the test must be rewritten to
test the mechanism, not a nonexistent quantity.

Real example: F-3 originally measured "the gap between the next eigenvalue below 0 and the
essential spectrum". When F-1 passes (point spectrum = exactly {0,1}), there are no
eigenvalues between −½ and 0 — the gap is undefined. Rewritten F-3 tests the modulation
directly: (a) no eigenvalue within complex distance δ of 0 or 1 remains after modulation,
(b) spectral abscissa of the modulated operator ≤ FLOOR. Test the mechanism, not a phantom
gap.

## 4. Tolerance provenance: BORROWED-TOLERANCE and single-FLOOR propagation

Two rules:

**(a) Tag any tolerance whose source is a different quantity.** If δ = 5×10⁻⁴ comes from
Xu's c_l two-grid floor (an aggregate deformation rate), it is BORROWED-TOLERANCE when used
as a spectral boundary — it measures a different operator feature. State the source, state
what it is NOT, and make the deliverable include the OBSERVED floor that replaces it at the
next re-registration: `"{observed floor} vs borrowed δ — {agrees / deviates by factor X}"`.

**(b) Define one spectral boundary once, propagate everywhere, mechanically verify removal
of stale references.** FLOOR = −½ + 3×10⁻³. Every test references FLOOR; no test
re-derives a boundary as −½ + <different number>. After the propagation edit, grep for all
old boundary spellings (−½ + 5e-4, δ_es, δ_ps, −½ + δ) and confirm zero remain as active
boundaries. The exotic tolerance (5×10⁻⁴) survives ONLY in the places the spec says it
survives (e.g., complex-distance removal threshold).

## 5. Ambiguous-middle disposition

The rejection band (test-pass / test-fail / cap-exceeded) never covers the most likely real
outcome: the continuation step that neither converges nor cleanly fails. Pre-register it.

- Define it numerically, not colloquially: residual falls to a band (e.g. 10⁻⁴–10⁻²) and
  oscillates there for ≥N consecutive iterations with no monotonic trend; step-size halving
  reproduces the same band; (condition number may be reported as a diagnostic, but do NOT
  include it in the definition — it classifies nothing).
- Disposition: AMBIGUOUS — park the branch, full ledger entry (convergence trace, step-sizes,
  terminal residual), NO claim attaches to either existence or nonexistence. Terminal for
  this phase. It is NOT a debug-cycle invitation.
- Hard retry cap: e.g. 3 attempts (default + 2 halved steps + 1 alternative continuation
  method), then AMBIGUOUS is terminal. An unregistered disposition is an invitation to keep
  retrying until something converges.

## 6. Cap derivation or honest tag

Never inherit a cap from a previous phase scoped for a different problem. Two allowed options:

- **(a) Derive from marginal work** — per-item table of what must be BUILT (implementation,
  debugging sessions, verification plumbing, continuation steps), API spend estimate per item,
  CPU cost, contingency (e.g. 50%), summed. Example: PALC $3, deflation $3, two-grid + quad $2,
  continuation $2, contingency $5 → $15/5d, down from an inherited $40/5d that was scoped for
  the WRONG equation.
- **(b) Tag ASSERTED-UNDERIVABLE**, same class as other audit gaps, if the derivation can't
  honestly be made.

Forbidden: "the same cap buys more per dollar on the correct problem" — that is a plausibility
argument standing in for an estimate, which is the exact defect class the audit catches.

After adopting a derived cap, the cap table in the spec AND the runbook must both be patched;
a stale $40 in the runbook while the spec says $15 is a self-contradiction.

## 7. Resolvent/pseudospectral threshold normalization

When validating reported eigenvalues with the resolvent, do NOT use a raw norm threshold:

- Raw ‖(z − ε − L)⁻¹‖ > 10³ at ε = 10⁻³ equals the NORMAL-OPERATOR baseline 1/ε and fails
  every genuine eigenvalue. Wrong test.
- Use the normalized departure: **UNTRUSTED if ε·‖(z − ε − L)⁻¹‖ > 10²**. Normal baseline
  is 1; the 10² is a stated ORDER-OF-MAGNITUDE-CHOICE, not borrowed from anything.
- If a quantity is a genuine spectrum of the WRONG realization (a naive-maximal-L² strip),
  it may resolve cleanly — do not require resolvent confirmation for it in the pass
  condition; report resolvent norms as diagnostics only.

## 8. Realization-pair pass conditions

For a realization-pair positive control (origin-H² vs maximal-L²):

- Pass = strip eigenvalues present in the wrong realization, absent in the correct one,
  count stable under resolution doubling. Nothing more.
- Do not require "confirmed pollution" via resolvent for the strip — the strip is true
  spectrum of the wrong realization, not noise.
- The pass condition should include a numeric zone definition (e.g. Re λ ∈ (FLOOR, −5×10⁻⁴))
  so "extra eigenvalues" is checkable, not eyeballed.

## 9. Sequential pre-registration amendment hygiene

When the founder ships successive correction prompts (F-3 rewrite, F-5 add, F-4 numbers,
FLOOR propagation), each correction is a class fix. Response pattern:

1. Restate the corrected test IN FULL (no diffs-only summaries for the binding document).
2. Mechanically verify with a grep/assert script that (a) the new terms are present,
   (b) all stale terms are absent (guard against `**` formatting breaking exact-match asserts
   — check content, not render), (c) cross-references (acceptance-logic table, summary table)
   were updated in the same pass.
3. Report each correction as DONE with the exact before/after.
4. Keep the file versioned (v1.5 → amended → final) — the founder gates on the terminal line.

## 10. Tolerance must be narrower than spectral gap

**A pre-registered acceptance tolerance must be narrower than the smallest spectral
gap being tested.** If the spectrum's entire content is {0, 1} with nothing between,
a tolerance of ±0.5 cannot distinguish 0 from 1. This is not a pre-registration; it
is surrender.

### Derivation

- The tolerance is NOT a free parameter to make the test pass. It is derived from
  the truncation convergence study (e.g., 6% at L=20, 3% at L=40).
- The expected-accuracy floor IS the tolerance — not borrowed from a different
  quantity, not chosen to make the test pass.
- If the floor at the target resolution is 6%, the tolerance is 6%, not "±0.5
  because that's more convenient."

### Example (CLM spectral project)

```
Rejected: "Accept eigenvalues within ±0.5 of target."
Reason: cannot distinguish λ=0 from λ=1 on a {0, 1} spectrum.
Replacement floor: 6% (derived from L=20 truncation convergence).
```

### Test for this rule

Before proposing a tolerance, verify:
1. Can this tolerance distinguish every pair of eigenvalues claimed in the test?
   (If not, the test is structurally incapable of producing a meaningful verdict.)
2. Is this tolerance derived from a measurement, not chosen by convenience?
   (If borrowed from a different quantity, tag BORROWED-TOLERANCE.)

---

## References 

- `operator-convention-and-discretization-audit.md` — truncation convergence protocol,
  L-sweep methodology, tolerance derivation from measurement
- `k0-checker-design.md` — K0 report verification checks (C3/C6/R1) that the reporter
  should pass before founder review