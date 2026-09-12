# Head-to-Head Walk-Forward Test Pattern

**Purpose:** Compare two parameter-free vol-targeting strategies where one (the "alternative") adds a single signal layer on top of the other (the "baseline"). The test isolates the marginal value of that one signal.

**Use case in the PROSECUTOR arc:** After the offensive bind-surfacing leg was KILL'd by the N_eff gate, the defensive sizing leg had its own independent test — a head-to-head comparison of plain price-vol targeting vs vol-of-correlation sizing. The defensive leg proceeds regardless of the offensive leg's fate; the only question is whether the correlation overlay adds anything.

## Frozen design

### Books compared

- **Book A (Baseline/Price-Vol):** Inverse-vol weights from each leg's own realized price vol. Vol-targeted to fixed annual target.
- **Book B (Alternative/Vol-of-Corr):** Same weights as Book A, then a book-level exposure multiplier in [floor, cap] that CUTS when the alternative signal is high. Only de-risks; never levers above 1.0. This is the ONLY difference.

### Parameters (frozen together, do not adjust individually)

| Parameter | Typical value | Meaning |
|-----------|---------------|---------|
| `VOL_WINDOW` | 21d | Realized price-vol estimation window |
| `CORR_WINDOW` | 63d | Pairwise correlation estimation window |
| `VOLCORR_WINDOW` | 63d | Window for vol-of-correlation (STD of correlation over time) |
| `TARGET_VOL_ANNUAL` | 0.10 | Both books vol-targeted to 10% annual |
| `REBAL_DAYS` | 5 | Weekly rebalance |
| `COST_BPS` | 2.0 | Round-trip cost per unit turnover (liquid micros) |
| `EMBARGO_DAYS` | 21 | Purge/embargo between train and test to prevent leakage |
| `N_SPLITS` | 6 | Walk-forward folds |
| `EXPOSURE_FLOOR` | 0.34 | Minimum book exposure (max cut = 66%) |
| `EXPOSURE_CAP` | 1.00 | Never lever above 1.0 (pure de-risking, no extra risk) |

### Pre-registered bar (ALL THREE must hold)

1. **mean(Sharpe_B − Sharpe_A) across folds > 0** — the alternative must, on average, beat the baseline on risk-adjusted return
2. **t-stat of dSharpe across folds > 1.0** — the improvement must exceed the across-fold estimation noise. Deliberately lenient — if it can't clear even this, the kill is decisive.
3. **Max single-fold contribution < 50%** — the improvement must not be driven by one lucky fold

Fail any one → **KILL_REDUNDANT** (the alternative adds nothing over the baseline)

### Secondary readouts (reported, not gating)

- **Max drawdown** of each book. The alternative's CLAIMED purpose may be crash protection, so it could cut drawdown while losing on Sharpe. If that's the pattern, the honest conclusion is "not a Sharpe edge, but a drawdown-reduction tool" — a different and weaker claim. Report it plainly; do not let a drawdown improvement be smuggled in as a pass.
- **Corr(book_A, book_B) returns** — if near 1.0, the signal moves almost nothing (redundant).
- **Turnover/cost drag** — the alternative's cutting may add turnover; costs are already charged.

## Implementation pattern

```python
def walk_forward(rets):
    corr_df = pairwise_corr_series(rets)
    voc = vol_of_correlation(corr_df)
    w = inverse_vol_weights(realized_vol(rets))

    # Exposure for alternative book: cut when vol-of-corr is high
    # Use EXPANDING rank (no lookahead) — current voc ranked against history to date
    voc_rank = voc.expanding(min_periods=VOLCORR_WINDOW).apply(
        lambda x: (x.iloc[-1] <= x).mean(), raw=False)
    expo_B = EXPOSURE_FLOOR + (EXPOSURE_CAP - EXPOSURE_FLOOR) * voc_rank
    expo_B = expo_B.clip(EXPOSURE_FLOOR, EXPOSURE_CAP).fillna(EXPOSURE_CAP)
    expo_A = pd.Series(1.0, index=rets.index)

    rA, _ = book_returns(rets, w, expo_A)
    rB, _ = book_returns(rets, w, expo_B)

    # Walk-forward with purge/embargo
    warm = max(VOL_WINDOW, CORR_WINDOW, VOLCORR_WINDOW) + 5
    rA, rB = rA.iloc[warm:], rB.iloc[warm:]
    # ... fold loop with EMBARGO_DAYS gap at each split
```

## Common outcomes

| Pattern | Verdict | Interpretation |
|---------|---------|---------------|
| dSharpe ~0, any direction | KILL_REDUNDANT | Signal does nothing — books nearly identical |
| dSharpe negative, consistent | KILL_REDUNDANT | Alternative actively worsens risk-adjusted return |
| dSharpe positive, t > 1.0, no single-fold dominance | EDGE_EXISTS | Small real edge — proceed to full-cost backtest |
| Positive dSharpe but full-sample Sharpe >> walk-forward | KILL_REDUNDANT | Full-sample looks good, walk-forward kills it — data mining bias, not prediction |
| Lower drawdown but lower Sharpe | KILL_REDUNDANT | De-risking trades return for drawdown — net-neutral or worse on risk-adjusted return. Honest verdict per the pre-registered bar. |

## Trap: drawdown win + Sharpe loss

This is the most likely outcome when the alternative purely cuts exposure. The alternative book runs at lower vol, so it has lower drawdown AND lower return. If the signal has no timing ability (doesn't know which crisis is coming), the Sharpe is neutral-to-negative because it gives up return proportionally to the vol reduction. Report this as:

> "De-risking trades return for drawdown, net-neutral on risk-adjusted return → no edge over price-vol targeting."

Do NOT relabel it as a pass. The pre-registered bar is Sharpe.
