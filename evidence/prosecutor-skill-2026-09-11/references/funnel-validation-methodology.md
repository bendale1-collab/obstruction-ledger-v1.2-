# Funnel Validation Methodology

## Source: VALIDATION_v1 through v5 sessions (2026-07-07)

### Calendar Restructuring (events != dates)
- Load merged JSONL → collapse to event-centric rows
- One row per unique (ticker, event_date)
- Classes: C10 (index rebalance), C3 (lockup expiry), C4 (merger/SPAC), C6 (catalyst), C7 (vol/tender)
- C6/C7 have null event_date → excluded from outcome computation
- Row-count assert: rows == len(unique ticker, event_date)

### FTD Tape Loading
- Source: CNS fails ZIPs (416 total, 2004-2025)
  - `/Users/brukendale/sec_threshold_data/ftd_files/` (144 zips ~2020-2025)
  - `/Users/brukendale/sec_threshold_data/ftd_backfill/` (250+ zips 2004-2019)
- Format inside ZIP: pipe-delimited CSV with columns SETTLEMENT DATE|CUSIP|SYMBOL|QUANTITY (FAILS)|DESCRIPTION|PRICE
- Date format: YYYYMMDD → YYYY-MM-DD
- Absent name-dates = ZERO_BAND (fails <10K), NOT missing/UNOBSERVED
- Header exists: skip first line. Trailer records: filter len(parts) < 6.

### E1v2 — FTD Drop Metric (frozen)
All four conditions must fire:
1. **(a)** Local max FTD >= 0.1% of shares outstanding
2. **(b)** >= 3 consecutive settlement-dates with FTD >= 0.05% of shares outstanding before the max
3. **(c)** Drop >= 70% from local max
4. **(d)** Post-drop FTD < 30% of max, sustained for >= 2 consecutive dates

Shares outstanding: fetched from EODHD fundamentals API, cached in
shares_cache.json (1,186 tickers). Fallback: 10M shares for unknown tickers.

#### E1v2 Base-Rate Audit Protocol
MANDATORY gate before ANY outcome computation with E1v2:
- Sample 1000 random (ticker, settlement_date) from FTD tape:
  - ticker NOT in calendar events
  - settlement_date in 2025
  - seed=42 for reproducibility
- Compute E1v2 for each sample
- Report: fire count, fire rate, condition failure distribution
  (e.g., "cond_a_failed: 756/1000, cond_b_failed: 956/1000, ...")
- If >5% fire rate: HALT. E1 definition is non-discriminative.
- If <=5% fire rate: PASS. Proceed to outcome computation.

#### DJT Calibration Check
MANDATORY after base-rate audit passes:
- Load DJT FTD data Mar-May 2024 from CNS fails tape
- Known fails: DJT 2.3M FTD peak (1.7% of ~136M shares) resolved
  with 75.3% drop in late Apr 2024
- E1v2 MUST fire on at least one date Apr 15 - May 15, 2024
- If E1v2 does NOT fire: HALT. Print DJT trajectory with all 4
  condition columns.
- If E1v2 fires: print which date(s) and trajectory.

#### SUPERSEDED_E1V1
Prior E1v1 (FTD drop only, no shares threshold) is SUPERSEDED.
Its 93.6% base rate was catastrophic. All prior E1 numbers in
SOLUTIONS_LEDGER.md carry SUPERSEDED_E1V1 flag. Only E1v2 may be
used going forward.

### E3 — Price Surge Metric (frozen)
+15% close-to-close adjusted return over any 3 consecutive trading days within ±10 trading days of event_date.
Positive return only. Sign-check assert: reject -15% test series.
Source: EODHD adjusted_close (bulk fetch per ticker).

### Controls (cap-decile + no-deadline-±45d)
- Pool: FTD tape universe (69K tickers), cross-referenced with shares outstanding
  from shares_cache.json for decile assignment
- NOT stage_c_universe.json (80 tickers, insufficient) or shares_cache alone
  (1,186 — not all have FTD tape coverage)
- For tickers without shares data, use shares outstanding default (10M) to
  assign approximate decile
- Divide control pool into 10 equal-sized deciles by shares outstanding
- Per event: find 3 controls from same decile with no deadline event within ±45d
- Min 100 distinct control tickers across all events
- Max 3x reuse per control ticker
- Sector match is NOT required (removed in v3+)

### Output format
- JSON with cells array: sign_group x load_band
- Load bands: HIGH (>1M FTD T-30..T-10), MEDIUM (>100K), LOW (<=100K)
- Fisher exact test where N>=5 in both event and control groups
- Monotonicity check: LOW < MED < HIGH rate or flagged
- Pre-registered read: FAILS if no Fisher-significant separation at p<0.05
- No verdicts — tables only, human decides

### Databento Cost Gate
BEFORE any Databento data fetch:
1. Call `metadata.get_cost` with exact params (dataset, schema, symbols, start, end)
2. If cost > $3.00: HALT. Report cost and stop.
3. Log cumulative cost; if across-multiple-fetches exceeds $3: HALT.
4. On fetch, log actual bytes returned vs cost estimate.
5. Datasets by cost/suitability for minute-bar work:
   - EQUS.MINI ohlcv-1m: cheapest ($0.0018/ticker/10d) but starts 2023-03-28
   - XNAS.ITCH ohlcv-1m: wider coverage ($0.06/GME+AMC 3mo) from 2018-05-01
   - XNYS.PILLAR ohlcv-1m: similar ($0.009/GME 2mo) from 2018-05-01
   - XNYS.PILLAR imbalance: most expensive ($0.23/GME 2mo) — closing auction data
