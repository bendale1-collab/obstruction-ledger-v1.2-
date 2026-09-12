# FTD Periodicity Test — Lomb-Scargle Spectral Analysis

## Purpose
Test whether semi-monthly FTD/shares ratio series exhibit **stable phase-locked periodicity**
in the 42–252 trading day band. If present, is the phase anchor a corporate-action anniversary
(CORP_ACTION — obligation-anchored), a calendar quarter-end (QUARTER_END — financing-driven),
or neither (noise)?

## Pre-registered claim (from FTD_PERIODICITY_V1)
- **Hypothesis:** names with legacy obligation structures (warrants, converts, earnouts)
  should show CORP_ACTION phase-lock in their FTD cycle
- **Null:** periodicity, where present, is QUARTER_END (financing) or NEITHER (noise)
- **Kill condition:** CORP_ACTION class empty or indistinguishable from shuffled phase null
- **Status after V1:** **KILL** — 0/77 names survived BH-FDR correction at q=0.10

## Deviation from published spec
The directive specified "2005-2025" FTD data. **SEC publishes FTD data from ~2020 onward only.**
Coverage is 2020-01..2025-12. The 2020-2005 gap is structural (SEC disclosure start), not a
caching or sourcing problem.

## Pipeline steps

### P0 — Universe construction
1. Survey all FTD ZIP files (228 files covering 2020-01..2025-12)
2. Filter to names that appear in SEC company_tickers.json (US common stocks)
3. Exclude ETFs/funds (QQQ, SPY, VXX, UVXY, TQQQ, etc.)
4. Pull SEC count-tag shares only:
   - `dei/EntityCommonStockSharesOutstanding`
   - `us-gaap/CommonStockSharesOutstanding`
   - `us-gaap/CommonStockSharesIssued`
   - **EntityPublicFloat is FORBIDDEN** — it's a metric, not a share count
5. Filter for continuous listing ≥8 years (shares data spanning ≥8yr)
6. Universe in V1: 77 names from top 200 FTD coverage candidates

### P1 — Series construction
1. **Semi-monthly timestamp grid:** 14-day increments from 2020-01-01 to 2025-12-31
2. **FTD/shares ratio** per timestamp (qty / shares_outstanding_at_date)
3. **Zero coding:** No FTD row = zero fails, NOT missing. Code as 0.0
4. **Transform:** log(1+x)
5. **Detrend:** subtract 12-month rolling median (window=24 timesteps at semi-monthly)
6. **SPARSE flag:** names where >20% of periods have ratio=0

**Critical lesson — SPARSE is a FLAG, not a FILTER:**
In V1, 67/77 names (87%) were SPARSE. Initial code skipped SPARSE from P2, reducing
the tested universe from 77 to 10. The corrected approach: flag SPARSE in the output
but test all names. The flag annotation lets the reader interpret the result knowing
that the series is mostly zeros.

### P2 — Spectral test: Lomb-Scargle periodogram
**Parameters (frozen before P3):**
- Period band: 42–252 trading days (≈3–18 timesteps at semi-monthly)
- Frequency grid: 500 points, uniform spacing
- Normalized Lomb-Scargle (`scipy.signal.lombscargle`, `normalize=True`)
- Significance: 1,000 circular-shift shuffles (preserves autocorrelation structure)
- Multiple-testing: Benjamini-Hochberg FDR at q=0.10

**Implementation pattern:**
```python
from scipy.signal import lombscargle

t = np.arange(n_timesteps, dtype=np.float64)
frequencies = np.linspace(f_min, f_max, 500)

# Periodogram
power = lombscargle(t, series, frequencies, normalize=True)
max_power = np.max(power)
max_freq = frequencies[np.argmax(power)]
max_period_days = (1.0 / max_freq) * 14  # convert timesteps to trading days

# Circular-shift significance
shuffle_powers = []
for sim in range(1000):
    np.random.seed(sim)
    shift = np.random.randint(1, len(series))
    shuffled = np.concatenate([series[shift:], series[:shift]])
    sp = lombscargle(t, shuffled, frequencies, normalize=True)
    shuffle_powers.append(np.max(sp))

p_value = np.mean(np.array(shuffle_powers) >= max_power)

# BH-FDR
p_values = np.array([r['p_value'] for r in results])
ranked = np.argsort(p_values)
thresholds = np.array([(i + 1) / n_tested * BH_Q for i in range(n_tested)])
significant = p_values[ranked] <= thresholds
```

**V1 result:** 0/77 names significant after BH-FDR at q=0.10.
Lowest p-value overall: 0.011 (FCEL, SPARSE — not FDR-corrected significant).
Lowest non-SPARSE p-value: 0.119 (VUZI, period=252d).

### P3 — Phase predictor (not executed when P2 returns 0 significant)
For each significant name:
1. Pull SEC filing history (8-K, 424B, S-3, S-1) since 2010
2. Extract filing dates as candidate corporate-action anniversaries
3. Compute peak phase from Lomb-Scargle: `phase = np.angle(np.sum(series * exp(-2jπ * freq * t)))`
4. Convert phase to calendar offset: `peak_offset = phase / (2π) × max_period_days`
5. Check alignment to quarter-ends (Mar 31, Jun 30, Sep 30, Dec 31)
6. Check alignment to corporate-action anniversaries
7. Classify: CORP_ACTION (within 15% of period to best anniversary),
   QUARTER_END (within 15% to nearest QE), or NEITHER

### Amplitude computation
```python
amplitude = np.sqrt(2.0 * max_power / len(series))
```

The amplitude is the log-domain amplitude of the dominant frequency component.
For log(1+x)-transformed series, this is roughly interpretable as: the primary
cycle oscillates by ~amplitude in log-space at the dominant frequency.

## Structural findings (V1)

1. **FTDs are episodic, not periodic.** 87% of stocks have FTD ratio zero >80%
   of semi-monthly periods. The signal is burst-shaped (cascade), not sinusoidal.
2. **Even persistent-FTD stocks lack stable periodicity.** The 10 non-SPARSE names
   all show spectral power indistinguishable from circular-shift noise.
3. **No CORP_ACTION phase-lock found.** Phase predictor not run because no names
   survived P2 significance.
4. **The 252d (annual) period detected in some names is an artifact** of incomplete
   detrending with a 12-month rolling median on a 6-year window.

## What this does NOT rule out

- **Higher-frequency periodicity** (<42 trading days, e.g. T+13/T+35 settlement cycles)
  — the Lomb-Scargle band was frozen at ≥42d, so sub-2mo patterns were not tested
- **Event-anchored recurrence** — recurrent FTD spikes at variable intervals triggered
  by specific events (offerings, warrant exercises, threshold list re-entries) are not
  phase-locked periodic and would not be detected by this method
- **Cross-sectional clustering** — the test was per-name; sector/industry FTD co-movement
  was not tested

## Known pitfalls

| Pitfall | Guard |
|---------|-------|
| SPARSE names excluded from P2 → universe collapse from 77 to 10 | SPARSE is a flag, not a filter. Test all names, annotate sparsity. |
| 12-month rolling median doesn't fully remove annual structure in 6yr window | The 252d peak in VUZI is likely an artifact. Consider difference-detrending or higher-order detrending for future runs. |
| Semi-monthly sampling aliases intra-month periods | Nyquist-safe down to ~2 timesteps (28 days). 42d minimum period is conservative. |
| Circular-shift preserves autocorrelation but destroys phase structure | This is intentional — the null is "same power spectrum but no phase-locked structure." Phase-locked true signals survive; random noise doesn't. |
| BH-FDR at q=0.10 with 77 tests → p_threshold ≈ 0.0013 | V1 found p_min=0.011. No correction would save it — even raw p-values are all >0.01. |
| SEC count-tag shares exclude EntityPublicFloat → ~5% of candidates dropped | This is by design: EntityPublicFloat is a metric, not a share count. Dropping is correct. |