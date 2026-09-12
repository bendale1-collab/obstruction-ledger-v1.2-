# EVAL Measurement Framework — Evaluability & Discriminative Value

When testing whether a set of constraints/oracles provides useful coverage over
a real data corpus, the measurement sequence matters. Simulation-based gates
(Q4) can pass while real-data measurement (EVAL) fails by a large factor.

## Core insight: simulation passes → real data can fail

Q4 passed all five gate metrics in simulation (79.8% detection, 0.129
localization). EVAL on real SEC data showed only one constraint survived
discriminative value > 0.05. The gap was not simulation quality — it was a
**measurement artifact**: the per-filing join mixed multiple report-periods and
produced inflated failure rates.

**The artifact was symmetric.** The same mismatched-period join inflated μ from
0.3% to 95% and DV from 0.0230 to 0.2415. Fixing the unit collapsed both.

## Unit-of-analysis discipline

For SEC Financial Statement Data Set (num.tsv) data, the correct unit is:

| Dimension | Value | Meaning |
|-----------|-------|---------|
| adsh | filing accession number | Which filing |
| ddate | date | Which reporting period |
| qtrs | 0 / 1 / 4 | Point-in-time (0) vs duration (1=quarter, 4=annual) |

**Rules:**
- All member tags of a constraint must share the SAME (adsh, ddate, qtrs)
- Balance-sheet identities: qtrs=0 (point-in-time)
- Income and cash-flow identities: qtrs=1 (quarterly) or qtrs=4 (annual)
- Do NOT mix — a per-filing join that picks any ddate across multiple periods
  within a filing will produce inflated failure rates
- Per-filing coverage (does any constraint apply to this filing?) is a valid
  metric for E-A. Per-constraint failure rates MUST use the report-period unit.

**Tolerance:** $1 for identity checks (a rounding difference is not a failure).
Document the tolerance in every report.

## Discriminative value

Not all evaluable constraints are useful. A constraint that fires at 0.3% on
real data and 61.5% on simulated data is inert. DV sorts useful from inert:

```
DV = evaluability × failure_rate × (1 − fp_rate)

evaluability  = evaluable_periods / total_periods
failure_rate  = failures / evaluations (at the correct unit)
fp_rate       = false positives / failures (hand-audited on a sample)
```

### Interpreting DV

| DV range | Meaning | Action |
|----------|---------|--------|
| > 0.05 | Genuinely useful | Retain as discriminative constraint |
| 0.01 - 0.05 | Marginal | May help in combination with others |
| < 0.01 | Inert | Drop or redesign — not doing useful work |

**Threshold for E-B gate:** mean DV over retained set >= 0.05.

### Tag canonicalization for evaluability

Different filers use different tags for the same economic concept. To maximize
evaluability, select the tag per concept with the HIGHEST UNIQUE-FILING count
(not raw occurrence count — the same filing can report the same tag multiple
times across different periods).

| Concept | Example canonical tag | Why |
|---------|---------------------|-----|
| Revenue | RevenueFromContractWithCustomerExcludingAssessedTax (163 uni) | More filers than Revenues (141 uni) |
| CostOfRevenue | CostOfGoodsAndServicesSold (145 uni) | More filers than CostOfRevenue (99 uni) |
| SG&A | GeneralAndAdministrativeExpense (184 uni) | vs SellingGeneralAndAdministrativeExpense (165 uni) |

**FP audit:** When normalizing tags, check whether two tags that map to the same
concept ever have DIFFERENT values in the same filing. If they do (e.g.,
StockholdersEquity ≠ StockholdersEquityIncludingNoncontrollingInterest in 97%
of filings where both exist), the normalization is creating false positives.
Hand-audit 50 firing samples and report the FP rate.

## Hand-audit halt threshold (2/15 rule)

Any hand audit disagreeing with mechanical classification by more than 2/15
halts the stage. The scoring is broken, and every downstream number computed
under it is invalid until recomputed.

| Agreement | Action |
|-----------|--------|
| >= 13/15 (>= 87%) | Pass — mechanical scoring matches human judgment |
| 11-12/15 (73-80%) | Flag — the invariant is marginal; report the disagreement |
| < 11/15 (< 73%) | **HALT** — scoring method is suspect |

2/15 is the threshold because:
- At 1/15 disagreement, the error rate is 7% — acceptable for mechanical methods
- At 2/15, it's 13% — the method is missing systematic real failures
- At 3+/15, the method is failing on a pattern, not a random sample

## Missing-term audit (run BEFORE scoring any invariant)

Before computing DV for any invariant, run a missing-term audit:

1. **Enumerate candidate omitted terms.** For each term in the invariant,
   ask: "what else could affect this value?" Document every candidate.
2. **Test each candidate.** Check whether records that fire the invariant have
   the candidate term present. If > 90% of firing records have it, the term
   is the missing term and the invariant is misspecified.
3. **Measure FP rate.** Hand-audit 15 firing records. Classify each as genuine
   error, misspecification, or data artifact. If FP rate > 5%, the invariant
   is approximately right and must be redesigned before scoring.

See `ref:invariant-misspecification-pattern.md` for the cross-domain signature
and worked examples from SEC (noncontrolling interest, FX reconciling) and
USAspending (admin actions, de-obligations, pre-award actions).

## Three-arm diagnostic for constraint misspecification

When a constraint has a high failure rate, test whether it's real filer error or
tag misspecification by running three arms:

| Arm | Form | What it tests |
|-----|------|---------------|
| 1 (original) | identity as written | The EVAL form — high failure rate expected if misspecified |
| 2 (corrected) | identity with corrected terms | Should have low failure rate |
| 3 (expanded) | corrected form with missing term added | Should have low failure rate + identifies the missing term |

**Example — cash flow identity:**

| Arm | Form | Failure rate | Verdict |
|-----|------|-------------|---------|
| 1 | CFops + CFinv + CFfin = Δcash_INCL_FX | 64.8% | Misspecified — FX term included in delta |
| 2 | CFops + CFinv + CFfin = Δcash_EXCL_FX | 2.9% | Correctly specified |
| 3 | CFops + CFinv + CFfin + FX = Δcash_INCL_FX | 2.9% | FX term explains the residual |

Verdict: MISSPECIFICATION when Arm 2 or 3 collapses the failure rate below 5%.
64.8% becomes 2.9% — the constraint as written was missing the FX term, exactly
like the 3-term StockholdersEquity identity was missing noncontrolling interest.

## Three separate coverage numbers, never collapsed

Report three distinct numbers, never collapsed:

1. **Per-filing coverage (E-A):** fraction of filings with ≥1 evaluable
   constraint. Answers "does any constraint apply to this filing?"
2. **Per-constraint evaluability:** fraction of report-periods where each
   constraint can be evaluated. Answers "how often can each constraint run?"
3. **Discriminative value (E-B):** mean DV over retained constraints. Answers
   "does running it find anything?"

A filing covered only by an inert constraint (DV < 0.05) is not meaningfully
checked. The number that matters is: **fraction of filings with at least one
constraint where DV > 0.05.** That number, not the per-filing coverage %, is
what determines whether the constraint set does useful work.

## EVAL measurement tiers (run in order)

| Tier | What it measures | When to stop |
|------|-----------------|--------------|
| 0 | Baseline per-filing coverage, discriminative_value | Stop if E-A >= 60% and E-B >= 0.05 |
| 1 | Tag normalization + FP audit | Stop if E-C passes (FP <= 20%) |
| 2 | Cross-period constraints (need 2+ quarters) | Roll-forward, monotonicity, growth bounds |
| 3 | Partial evaluation (solve/bound mode) | Report solve and bound separately |
| 4 | Multi-source (num.tsv × PRE × GLEIF) | Cross-source constraint evaluability |
| 5 | Retrieval steering (fetch what constraints need) | Marginal cost vs oracle calls saved |
| 6 | Functional dependency mining + independence + truth-discovery | Automated constraint discovery |

**If E-A and E-B pass on Tiers 0-1, the regime is constraint-rich. If E-B fails,
the regime is SPARSE-ORACLE — the constraint set does not discriminate usefully,
and the program's output is the verification pipeline without constraint-consistency
localization.**

## μ (base error rate) — correct measurement

The impossibility bound (arXiv:2606.29054) depends on μ, the base error rate
among examples reaching the conformal layer. Measure μ at the same unit as
constraint evaluation:

- **Correct unit:** (adsh, ddate, qtrs) report-periods
- **Correct statistic:** fraction of evaluable report-periods where ALL
  constraints pass (μ = 1 - pass_rate)
- **Common mistake:** per-filing analysis produces inflated μ (0.95 vs 0.003 in
  one measurement)

At μ = 0.003 and α = 0.05, the impossibility bound gives 0% forced abstention.
At μ = 0.10 (a conservative estimate for model errors), the bound gives 5.3%
forced abstention — manageable.

## Tag selection for canonicalization

When building canonical tag maps from SEC Financial Statement Data Set:

1. Count per-tag UNIQUE-FILING presence, not raw occurrence count (same filing
   can report the same tag across multiple periods)
2. Select the tag with the highest unique-filing count as canonical
3. For concepts with a `SellingGeneralAndAdministrative` variant that returns
   zero occurrences: the correct us-gaap tag is
   `SellingGeneralAndAdministrativeExpense` — append `Expense`
4. Report both raw occurrence count and unique-filing count in the canonical
   tag table so the selection logic is auditable
