# Instrument-Density Comparison Protocol (D-33-DIAG1)

**Context:** Before trusting a concentration ratio or prevalence
difference between two groups, verify that the measurement instruments
are comparably dense in both groups. An extreme ratio (e.g., ∞x) may
reflect differential data density, not a real effect.

## Protocol

1. **Select instruments** — Identify the two data sources that
   produce the key metrics. In D-33: FSNDS filing-quarters and
   8-K filings from the submissions cache.

2. **Report density per group** — For each instrument, emit median
   count per observation in each group. Use median, not mean
   (mean is heavy-tail-sensitive for filing counts).

3. **Compute density ratio** — pressure_group_density /
   unpressured_group_density.

4. **Apply frozen rule** — The registered spec must define what
   density ratio constitutes "comparable." If no registered
   threshold, use [0.5, 2.0] as default comparable range.

5. **Verdict**:
   - Ratio in [0.5, 2.0]: instruments comparably dense. Report
     the finite ratio with continuity correction.
   - Ratio < 0.5 or > 2.0: instruments coupled with data-density
     parent. Verdict UNMEASURED(coupled instruments) [N1a class].

## Frozen-Rule Branch Coverage

**Critical lesson (C-22):** When a frozen rule has two branches:

  (a) Comparable density → real
  (b) Unpressured thinner → coupled

And reality takes a THIRD branch not in the spec:
  (c) Pressured thinner (not unpressured)

The verdict is unlicensed. The rule must be re-registered to cover
all possible outcomes before a typed verdict can be returned.
Adding C-22 to the ledger does not license a verdict; it documents
the gap. The next experiment must register a three-branch rule.

## Scoreboard Discipline

When stating a prediction (author forecast), always include:
- Running tally: ~2-for-12 (as each prediction lands)
- Weight qualifier: "weight accordingly" when reliability < 50%
- Rejection syntax: "join-bug prediction REJECTED" on each miss

After a sufficient sample (10+ trials stated explicitly), the
model's forecasts carry known reliability and the user adjusts
trust accordingly. Do not suppress a prediction to avoid missing
— the scoreboard is the point of the model.