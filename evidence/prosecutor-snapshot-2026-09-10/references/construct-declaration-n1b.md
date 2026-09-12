# Construct Declaration & N1b Resolution Clause

**Source:** MVI Loop Program — COMPare recall audit, 2026-07-24
**Defect discovered:** Filter A1 required field identifiers to resolve against their authority, but the **target sentence** was never resolved. The instrument passed N1 (criterion != target) while measuring a construct the field would not recognise under that name.

## The defect

The N1 check (MVI §0.5, SPEC_v2 §0.5) tests whether the instrument's selection criterion and the target's defining property coincide. It has no clause for an **unresolved target**. An instrument can pass N1 while carrying base rates and literature that do not apply to the domain's established definition.

**Concrete example:** This harness's target was "Was the registered primary outcome reported as specified?" The field's established definition (COMPare / Goldacre et al., Trials 2019) includes three conditions where ours checked one. Ours passed N1 (criterion != target) while measuring a construct the field calls by the same name but defines differently. The gap was not surfaced until an external anchor was consulted.

## N1b — Resolution clause

N1 gains a second clause, evaluated after N1a (collision) and before any data is pulled:

> **N1b — Target resolution.** Resolve the target sentence against an external authority before building. If an established definition of the target exists in the relevant domain literature and differs from the instrument's operational definition, either:
> - (i) Adopt the authority's definition and widen the instrument to match, or
> - (ii) Declare the target locally defined, retire the authority's terminology from all outputs, and explicitly state that the authority's base rates and literature do not apply.
>
> If no established definition exists, record `TARGET LOCALLY DEFINED` explicitly.

**Cost:** One web search + one paragraph of writing. Pre-compute, before any data is pulled.

## Construct declaration document

When N1b fires (option ii — target locally defined), produce a construct declaration document containing:

1. **The target sentence**, verbatim as the instrument implements it.
2. **The external authority's definition**, verbatim and cited.
3. **The gap**, stated plainly — what the instrument checks vs. what the authority checks.
4. **The decision — NARROW or WIDE.** If NARROW: retire the authority's terminology from all outputs (e.g., "outcome switching" → "registered-primary-outcome discrepancy").
5. **What widening would cost**, one paragraph — protocol access, additional checks, model calls, time. This determines whether WIDE is even available.

## When N1b fires

| Situation | Action |
|---|---|
| Authority definition matches instrument | N1b satisfied. Proceed. |
| Authority definition differs, widening is affordable | Widen the instrument to match, then proceed. |
| Authority definition differs, widening is unaffordable | Declare target locally defined (option ii). Retire the authority's terminology. The instrument measures a narrower construct and must be described as such. |
| No established definition exists | Record `TARGET LOCALLY DEFINED`. Proceed. |

## Propagation points

Add N1b to:
- MVI §0.5 (N1 check) — as the second clause after the two-sentence collision check
- Class N gate specification — "N1 must pass both clauses before compute is spent"
- SPEC_v2 §6.3 (orthogonality, O3) — add "and resolution against domain authority (N1b)"
- SPEC_v2 §0.5 (N1 check) — add N1b as the second clause