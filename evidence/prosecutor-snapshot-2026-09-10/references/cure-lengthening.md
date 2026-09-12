# V2_CURE_LENGTHENING — Fail-cure duration trend + pre-stress alignment

**Session origin:** 2026-07-04 overnight batch v3 T4.

## Methodology

### Data source
Cached FTD ZIP tape at `/Users/brukendale/sec_threshold_data/`:
- `ftd_files/` (2020-2025)
- `ftd_backfill/` (2004-2019)

Filter to target names only during ZIP reading — no need to parse all files for all 94 names.

### Semi-monthly aggregation
Split each calendar month at day 15:
- Half 1: days 1-15 → key = (year, month, 1)
- Half 2: day 16-end → key = (year, month, 2)

Sum daily FTD qty per semi-monthly period using `defaultdict(int)`.

### Cure episode definition
Consecutive semi-monthly periods where FTD > 0 followed by a period where FTD = 0. Duration = count of consecutive FTD>0 periods.

### Critical fix: zero-fill from global semi-monthly grid
The SEC FTD tape only records entries where FTD > 0 (threshold securities with >$100K fails). Iterating over only observed dates produces exactly ONE episode per name — all positive periods are contiguous because no zero-FTD entries exist in the tape.

**Fix:** Build a global semi-monthly grid from the date range of ALL FTD data, then for each name fill in zero-FTD periods where no data exists:

```python
# Compute global date range from all names' FTD data
all_dates = set()
for n, dd in ftd.items():
    for d in dd: all_dates.add(d)

# Generate all semi-monthly keys in the range
sm_keys_all = sorted(...)  # (year, month, half) tuples

# For each name: lookup into global grid
vals = []
for k in sm_keys_all:
    vals.append(sm_raw.get(k, 0))  # 0 for missing semi-months

# Now compute cure episodes on the zero-filled vals array
```

This ensures zero-FTD periods between active periods are correctly represented, producing proper episode breaks.

### Trend test
Mann-Kendall trend via `scipy.stats.kendalltau(durations, range(len(durations)))`:
- τ > 0 with p < 0.05 → durations lengthening (fails take longer to cure)
- τ < 0 with p < 0.05 → durations shortening (faster clearing)
- Require ≥4 episodes for interpretable trend

### Pre-stress alignment (F4 candidates)
For names identified by the F4 low-band screen (AMC, CGC, LCID, TLRY):

1. **Elevated-band entries:** Semi-monthly periods where FTD/shares ∈ [0.01%, 0.1%]. Compute ratio using nearest preceding shares filing.
2. **Pre-stress window:** The 12 semi-monthly periods (=2 quarters) preceding each elevated-band entry.
3. **Observed:** Mean cure duration of episodes whose start falls within any pre-stress window.
4. **Null:** 1000 random samples of the same count from ALL episodes (not just pre-stress windows). Each shuffle picks episodes without replacement.
5. **p-value:** Fraction of null means ≥ observed mean (one-tailed: is pre-stress longer?).
6. **WITHIN-NAME ONLY** — compute per-name, never compare duration magnitudes across names.

## Implementation pattern

```python
from collections import defaultdict
from datetime import datetime
from scipy.stats import kendalltau

def semi_monthly_key(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    half = 1 if d.day <= 15 else 2
    return (d.year, d.month, half)

def compute_cure_episodes(name_ftd):
    sm = defaultdict(int)
    for d, qty in name_ftd.items():
        k = semi_monthly_key(d)
        if k: sm[k] += qty
    sorted_sm = sorted(sm.items())
    vals = [v for k, v in sorted_sm]

    episodes = []
    cur_start = None; cur_dur = 0
    for i, v in enumerate(vals):
        if v > 0:
            if cur_start is None: cur_start = i; cur_dur = 1
            else: cur_dur += 1
        else:
            if cur_start is not None:
                episodes.append((cur_start, cur_dur))
                cur_start = None; cur_dur = 0
    if cur_start is not None:
        episodes.append((cur_start, cur_dur))
    return episodes

# Mann-Kendall
durations = [e[1] for e in episodes]
tau, p = kendalltau(range(len(durations)), durations)
```

## Pitfalls
- **Semi-key uniqueness:** (year, month, half) keys look colliding but are Python-tuple-unique. Use `defaultdict(int)` for clean aggregation.
- **Zero-fill mandatory:** The SEC tape only records FTD > 0. Without zero-filled semi-monthly grids, every name shows exactly 1 continuous episode and the MK trend test is uncomputable. Always build a global date range and fill missing semi-months with 0.
- **ZIP file errors:** Some files have malformed lines (trailer records, unexpected headers). Use try/except per line and filter to T4_NAMES only.
- **Pre-stress window boundary:** "2 quarters before" = 6 calendar months = 12 semi-monthly periods. Use month-index arithmetic: `target_ym = year*12 + month; target_start = target_ym - 12`.
- **Survivorship bias:** The FTD tape has entries for delisted names in the backfill (2004-2019) but may drop them in the 2020+ cache. This biases toward names that survived the full period.
- **shares_outstanding:** Use `nearest_shares()` from sec_shares_merged.json. Date-format normalization is critical (YYYYMMDD vs YYYY-MM-DD between pre-2020 and post-2020 files).
