# Equation-Selection Gating (identical-if-different-target principle)

**Origin:** OL v1.3→v1.4 amendment sweep (2026-09-07) — CCF PDE selected from gCLM family.
**Scope:** Any PROSECUTOR study where a governing equation must be selected from a parameterised family, and that equation's output (e.g. eigenvalues) is the gate target.

---

## The principle

When selecting a governing PDE from a parameterised family whose output must match published target values, the selection must be **defensible without reference to those target values**.

This means: the selection rationale must be verbatim-identical had the published target values been different numbers. If the rationale cannot be written that way, the form is **underdetermined** and the leg is **contaminated** — the equation was chosen because it produces the target, not because the family structure, author lineage, or scope constraints determined it.

## Gating questions

Ask all three. If any answer is "the published values" → HALT-UNDERDETERMINED:

1. **Family membership:** Is the equation uniquely identified by its place in the parameterised family structure? (e.g. CCF = gCLM a=0 because Constantin-Lax-Majda derived that form, De Gregorio is a≠0, half-line is a<0)

2. **Author lineage:** Does the source literature unambiguously assign the published values to this specific member of the family? (e.g. Wang 2509.14185 studies the a=0 CCF, not De Gregorio or mixed)

3. **Scope exclusion:** Are the alternative members excluded by the project scope statement, not by their numerical output? (e.g. the spec says "1D equations" — 2D/3D forms are out regardless of what they produce)

## Rejected alternatives: filing discipline

Every rejected alternative form must be enumerated with:
- The form (e.g. gCLM a=1/2, dissipative CCF with viscosity, 2D SQG)
- The rejection reason (must reference scope, literature, or family structure — never the target values)
- File as a ledger obstruction entry (typed), not a comment

## Pitfall

Do NOT include the actual target values anywhere in the rationale text. The rationale is submitted for audit before any numerical run. A reviewer who can see the target values in the rationale and can map the equation choice to those values has grounds to call contamination. The rationale must pass the **blind-review test**: it convinces someone who has the spec but not the target values that this equation is the right one.

## Reference implementation
OL v1.3→v1.4 CCF PDE closure (2026-09-07):
- Selected: gCLM a=0 (CCF) — rationalized by family structure (a parameter identifies CCF as a=0), author lineage (Constantin-Lax-Majda 1985, Wang 2509.14185 study a=0 exclusively), and scope (1D only).
- Rejected: a=1/2, a=1, a<0 (wrong family member), dissipative CCF (inviscid in scope), 2D/3D (scope)
- Passed the identical-if-different-target test: rationale unchanged under any substitution of the published λ values.