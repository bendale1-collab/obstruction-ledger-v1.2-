# Mutation Testing for Classification Category Reachability

**Source:** MVI Loop Program — remediation mutation tests, 2026-07-24
**Pattern:** When a pre-registered classification category reports 0.0% (or any extreme fraction), prove the category is **reachable** before the zero is read as a measurement. An inert category and an empty one are indistinguishable in output.

## The pattern

The MVI run reported `ABSTAIN(ambiguous-mapping) = 0/100`. Mutation testing with 5 synthetic items proved the category fires only when the primary outcome text has zero words >3 characters after tokenization — a condition that never occurs for real trial outcomes. The category was **inert**. The fuzzy rate was never measured.

## Protocol

For every pre-registered classification category that reports 0.0% or 100.0% on any count, denominator, or intermediate:

1. **Identify the branch condition** that gates the category in the code. Read the exact condition (e.g., `if not outcome_terms: ambiguous = True`).
2. **Construct synthetic items** engineered to trigger that specific condition. Minimum 5 per category. Use distinct failure structures, one per item.
3. **Run through the unmodified harness.** Report per-item classification.
4. **Threshold:** >= 4/5 must classify into the target category. Fewer means the category is inert and the rate was never measured.

## Common inert-category patterns

| Pattern | What happens | How to detect |
|---|---|---|
| **Degenerate guard** | Category only fires on empty/null input (e.g., `if not outcome_terms:` where outcome_terms is never empty for real data) | Construct input that would naturally be empty — check if real data ever produces it |
| **Default fallback** | Category is the terminal `else` or a catch-all (e.g., `else: return SWITCHED`) | Check if any other category has a true affirmative condition, or if SWITCHED is just "not MATCHED" |
| **Unreachable branch** | Code path requires a combination of conditions that cannot co-occur in real data | Trace all paths to the branch; enumerate what conditions must hold |
| **Absorbing parent** | A higher-priority category catches all items before the target category is evaluated | Reorder the decision chain and check if the target category fires |

## Pre-registration requirement

- If a category is proven inert (< 4/5 mutation test), report the result as `UNMEASURED(category inert)` — never as 0.0%.
- The mutation test items and their classifications are logged alongside the results.

## Example — five engineered-ambiguous items (from MVI)

| # | Ambiguity type | Registry text | Publication text | Expected | Harness |
|---|---|---|---|---|---|
| 1 | Composite → component only | Composite of CV death, MI, stroke, UA | Non-fatal MI only | UNRESOLVABLE | SWITCHED (inert) |
| 2 | Timepoint shift | HbA1c at Week 24 | HbA1c at Week 52 | UNRESOLVABLE | MATCHED (inert) |
| 3 | Renamed measure | HAM-D total score | MADRS score, no mapping | UNRESOLVABLE | SWITCHED (inert) |
| 4 | Unlabelled subset | OS, PFS, ORR, QoL | OS and PFS only | UNRESOLVABLE | SWITCHED (inert) |
| 5 | Amended definition | ACR20 at Week 16 (amended from ACR50 at Week 24) | ACR response, no timepoint | UNRESOLVABLE | SWITCHED (inert) |

All 5 landed in MATCHED or SWITCHED — the UNRESOLVABLE branch was never reached. Proved the category inert.

## Reusability

This pattern generalizes beyond the MVI context. Use it whenever:
- A classification system has pre-registered output categories
- One or more categories report extreme rates (0% or 100%)
- The rate is load-bearing for a downstream decision (licensing, banding, stopping)