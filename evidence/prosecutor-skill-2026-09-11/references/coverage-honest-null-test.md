# Coverage-Honest Null Test (N2)

## When to use

After a first-pass attribution V2 run shows several classes "explaining" FTD episodes (OpEx 14%, QEND 8%, Dividends 8%, etc.), before declaring any class as a genuine trigger. The coverage-honest null is the gate between "attribution counts" and "causal class."

## The problem it solves

Periodic calendar classes (monthly OpEx 3rd Fridays, quarterly quarter-ends) have non-trivial calendar coverage. OpEx ±2td covers ~14% of all trading days. If episodes are randomly distributed, ~14% will naturally fall within 2td of an OpEx date — even without any causal mechanism.

A naive shuffle null (shuffling OpEx dates among themselves) asks "do episodes cluster near OpEx dates?" But the answer is trivially yes — because episodes cluster near every calendar date (they follow FTD settlement patterns). The real question is: "do episodes cluster near OpEx dates MORE than random timing with the same calendar coverage would produce?"

## Method

Replace EVERY episode's date with a uniform random trading day from the same year, preserving per-ticker episode counts. Run the full first-match-wins attribution pipeline. Record per-class rates. Repeat 1000 rounds.

```
observed_rate = count(class_A_episodes) / total_episodes
null_rates[class_A] = [rate_A_round_1, rate_A_round_2, ...]  # 1000 values
```

Then for each class:
- **EXPLAINED** — observed rate > null 95th percentile. Episodes captured above what random timing would produce.
- **AT_CHANCE** — observed rate within null 5th–95th range. Temporal coincidence.
- **ANTI_CLUSTERED** — observed rate < null 5th percentile. Episodes systematically avoid these dates.

## Optimization: pre-computed lookup table

The naive implementation iterates over all events for each episode in every round: O(N_eps * N_events * N_rounds). For 6K episodes, 276 OpEx dates, and 1000 rounds -> 1.7B iterations.

Instead, pre-compute for each (ticker, year) what attribution class each eligible trading day maps to:

```python
ticker_year_options = {}
for t in tickers:
    for y in range(start_year, end_year + 1):
        opts = [(d, first_match_class(t, d, sources, order))
                for d in trading_days_by_year.get(y, [])]
        if opts:
            ticker_year_options[(t, y)] = opts

for _ in range(1000):
    cc = Counter()
    for (t, y), cnt in ticker_year_counts.items():
        for _ in range(cnt):
            _, cl = random.choice(ticker_year_options.get((t, y), []))
            cc[cl] += 1
```

Each round is now `random.choice` + Counter increment: O(N_eps) ~ 6K operations per round. A 1000-round test completes in seconds.

## Empirical result (FORCED_COVERING_DETECTOR, July 2026)

Applied to 6,052 FTD episodes (max_pct < 10%, shares_cache) with 1000-round null:

| Class | Coverage | Observed% | Null mu+/-sigma | p95 | Verdict |
|:------|---------:|----------:|---------------:|----:|:--------|
| OpEx  | 14.15% | 9.77% | 9.56+/-0.38 | 10.21 | AT_CHANCE |
| QEND  | 7.62% | 4.97% | 5.18+/-0.28 | 5.63 | AT_CHANCE |
| Dividend | 100.00% | 5.47% | 4.94+/-0.24 | 5.32 | EXPLAINED |
| Offering | 34.91% | 0.17% | 0.13+/-0.04 | 0.20 | AT_CHANCE |
| Index | 0.88% | 0.03% | 0.00+/-0.01 | 0.02 | EXPLAINED |
| Earnings | 99.24% | 1.67% | 1.56+/-0.15 | 1.82 | AT_CHANCE |
| Split | 33.03% | 0.13% | 0.08+/-0.04 | 0.15 | AT_CHANCE |
| Registry | 0.27% | 0.00% | 0.00+/-0.00 | 0.02 | AT_CHANCE |

True EXPLAINED falls from V2's 32.87% to 5.50%. True UNEXPLAINED reverts from 67.13% to 94.50%.

## Relationship to the Fast Shuffle Null

These are complementary tests, not alternatives:

| Test | Question | What it eliminates | OpEx result |
|:-----|:---------|:-------------------|:------------|
| Fast shuffle | Do episodes cluster near these dates? | Random chance | Z > 3 — YES |
| Coverage-honest | Is observed rate above random timing? | Calendar coverage | AT_CHANCE — NO |

The fast shuffle confirms episodes genuinely cluster near OpEx dates (FTD settlement patterns are periodic). The coverage-honest test then shows this cluster rate matches the calendar coverage: ~9.8% of episodes fall within 2td of OpEx, and ~9.6% of random dates also do. The rate difference (+0.2pp) is within chance.