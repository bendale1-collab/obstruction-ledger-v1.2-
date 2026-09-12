# Book C — Correlation-Matrix Weighting Test (Three-Outcome)

**When to use:** When the thesis is whether using the full correlation matrix for portfolio weights (min-variance, ERC/risk-parity) beats the inverse-vol baseline that ignores all off-diagonals. This is the allocation-level test, distinct from the head-to-head timing test (which tests correlation as an exposure multiplier).

## Why this is a separate test

The head-to-head kills vol-of-correlation as a global EXPOSURE TIMING signal (cutting book size when correlations are unstable). That test never touches the WEIGHTING (which instruments get more capital). Book C tests correlation in the weights via the two canonical methods:

| Method | Formula | What it does |
|--------|---------|-------------|
| **Inverse-vol (A)** | w_i ∝ 1/σ_i | Ignores all off-diagonals — the killed baseline |
| **Min-variance (C1)** | w = argmin wᵀΣw | Uses full covariance; tilts toward low-correlation/low-vol legs |
| **ERC / Risk-parity (C2)** | w s.t. RC_i = RC_j ∀ i,j | Allocates so every leg contributes equal risk |

## Design parameters (frozen for reproducibility)

| Parameter | Value | Meaning |
|-----------|-------|---------|
| VOL_WINDOW | 21d | Realized vol window |
| COV_WINDOW | 63d | Window for covariance used in weighting |
| TARGET_VOL | 10% annual | Both books vol-targeted to same level |
| REBAL_DAYS | 5 | Weekly rebalance |
| COST_BPS | 2.0 | Round-trip per unit turnover |
| EMBARGO_DAYS | 21 | Purge/embargo between train and test |
| N_SPLITS | 6 | Walk-forward folds |
| TIE_DSHARPE | 0.10 | Max |dSharpe| for TIE classification |
| TIE_CORR | 0.95 | Min book-return correlation for TIE |

## Three-outcome decision (pre-registered)

Unlike the head-to-head's binary WIN/KILL, Book C has THREE pre-registered outcomes because a TIE is informative, not a null:

| Outcome | Criteria | Interpretation |
|---------|----------|---------------|
| **WIN** | mean dSharpe > 0, t > 1.0, max-fold < 0.50 | Correlation weighting carries real info even at N=3. Proceed to backtest. |
| **TIE_LEGS_LIMIT** | |dSharpe| ≤ 0.10 AND corr(C,A) > 0.95 | Off-diagonals don't separate weights → limitation is the LEGS, not the signal. Interpretation depends on eff_rank (see below). |
| **LOSE** | mean dSharpe < 0 AND t < -1.0 | Correlation weighting actively hurts at N=3. Consistent with min-var crisis-fragility. Do NOT use cross-sectionally. |

Default fallback: if none of the three bars is cleanly hit, classify as TIE_LEGS_LIMIT.

## Effective-rank cross-check (THE key diagnostic)

The effective rank (participation ratio of eigenvalues of the correlation matrix) determines what a TIE means:

```
eff_rank = (sum(λ_i)²) / (sum(λ_i²))     where λ_i = eigenvalues of C
```

Range: 1 (rank-one) to N (fully independent).
For N=3 legs: 1.0–3.0.

| eff_rank | TIE means | Action |
|:--------:|-----------|--------|
| **~1.0** | Tie FORCED by the legs — rank-one matrix makes min-var/ERC ≈ inverse-vol mechanically. The limitation is the LEG CHOICE, not the signal. | CROSS-ASSET BUILD is the licensed next step (non-rank-one matrix with energy+rates+equity+FX). |
| **~N** | Tie is SURPRISING — legs span independent factors, signal still can't separate them. The signal itself is weak. | Cross-asset will NOT save it. Close the line. |

**Reporting rule:** Print the effective rank prominently at the top of every Book C output. The human reads this FIRST to calibrate interpretation of any tie.

## Pitfalls

1. **Do NOT relabel a maxDD improvement as a WIN.** Min-variance often cuts drawdown by concentrating into the low-vol leg. That's de-risking, not edge — same trap as the head-to-head timing test. The bar is Sharpe.
2. **Frozen params stay frozen.** A tie or lose is the answer. Do not retune windows to find a win.
3. **ERC can be WORSE than inverse-vol at N=3.** ERC tilts toward equalizing risk contributions, which concentrates into the highest-vol leg — often the one with the worst risk-adjusted return in crisis periods. This is a known result: ERC hurt single-sector.
4. **Multiple test adjustments:** min-variance and ERC are two separate tests on the SAME data. Each gets its own independent verdict. Do NOT claim a pass because "one of the two methods worked" — report both verdicts.
5. **The CORRELATION matrix, not the covariance matrix** — eff_rank should be computed from the correlation matrix (normalized), not the covariance. Correlation removes vol magnitude from the eigenvalue structure.