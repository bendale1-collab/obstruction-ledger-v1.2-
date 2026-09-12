# ALMOST_FAIL_LEDGER — Sub-threshold band screen + multi-channel conjunction

## Overview

The ALMOST_FAIL framework tests whether stocks with persistent but sub-threshold FTDs (too small to trigger fails-driven covering, but recurrent) show phase-locked periodicity across three independent channels:
- CH1: LOW_BAND FTD persistence (FTD/shares in [0.01%, 0.1%])
- CH2: FINRA OTC internalization periodicity (weekly non-ATS share volume)
- CH3: Reset cadence via deep-ITM call volume (options market)

**Pre-registered gradient:** 3/3 channels phase-consistent = WAREHOUSE_CONFIRMED; 2/3 = WEAK; ≤1 = NOISE.
**NO new categories ever.** STRUCTURED_CLUMPS is not a valid pre-registered category.

## V1 FINAL results (G1-G4 + H1-H4, 2026-07-04 session)

### G1/F4 — Full-tape rerun (94-name universe, 2004-2025)

Universe: All 94 names with SEC count-tag shares (sec_shares_merged.json)
FTD tape: 2004-03-22 to 2025-08-29 (4,573 unique trading dates)
Backfill: 272 ZIPs (2004-2019) + 144 ZIPs (2020-2025) = 416 total

**Candidates (4):**

| Name | n_total | low_frac | zero_frac | Interval CV | Poisson p | Date range |
|------|---------|----------|-----------|-------------|-----------|------------|
| AMC  | 317     | 0.4353   | 0.0473    | 11.71       | 0.000     | 2004-2025  |
| CGC  | 1080    | 0.4407   | 0.0704    | 13.66       | 0.000     | 2004-2025  |
| LCID | 245     | 0.5020   | 0.0163    | 8.19        | 0.000     | 2021-2025  |
| TLRY | 435     | 0.4575   | 0.0322    | 9.31        | 0.000     | 2018-2025  |

**Split-sample:** 2004-2011: 0/4  2008-2009: 0/4  2012-2019: 1/4  2020-2025: 4/4

**Dropped from original A1 (2020-2025 only):** CYDY (low_frac=0.29) and VUZI (low_frac=0.32) — insufficient persistence when tested against the full tape.

### H2 — FINRA OTC (BLOCKED)

**HALT:** `ATS_W_VOL_STATS` aggregate rows are embedded inside per-firm output and cannot be queried as a standalone time series. Each API page (5000 records) covers ≈1 week, with 1 aggregate row per page. Getting all weeks for one name requires paginating through ~300 pages (~37.5 min). For 52 names → ~32 hours.

**CompareFilters probe:** `compareFilters` parameter returns HTTP 204 on all formats (parameter not supported). `weekStartDate` in the `filters` array is silently ignored — returns most recent week regardless of filter value. Only `issueSymbolIdentifier` filtering works. **Date-filter non-support is a halt** — per-name-week query pattern is structurally impossible.

The `summaryTypeCode` filter does NOT work reliably — requesting `ATS_W_NONATS_FIRM` returns `ATS_W_VOL_STATS` records.

**API conclusion:** FINRA OTC data EXISTS but is NOT efficiently queryable for multi-name systematic research.

### H3 — OPRA deep-ITM calls (BLOCKED by cost)

**HALT:** Databento OPRA.PILLAR option contract symbols ARE discoverable via parent symbology:
- `symbology.resolve` with `stype_in=PARENT`, `symbols='AMC.OPT'` returns 2,826 individual option contracts (message: "Partially resolved", status: 1)
- Parent resolution WORKS — individual contracts appear as root-level keys in the result dict
- Historical `ohlcv-1d` cost: ~$0.0032/contract/month. Full AMC chain June 2021: ~$9.00. 4 names × 72 months: ~$2,592 (exceeds $15 budget)
- Full OPRA.PILLAR ohlcv-1d scan (no symbol filter): ~$600/month
- **Conclusion:** Option contract discovery IS feasible. Historical volume at full chain scale is budget-prohibitive.

**yfinance option chains** provide CURRENT-SNAPSHOT data only (no historical volume). Usable for NO_OPTIONS / NO_QUALIFYING_STRIKES determination but NOT for historical VOLUME_PRESENT analysis.

### H4 — CGC 2012-2019 deep dive

**CORRECTION (J3 rerun, 2026-07-04):** The "CGC 2012-2019" claim was an artifact of period-boundary overlap. CGC has NO FTD entries in 2012-2017 (0 entries). Data exists only in clusters: 2004-2007, 2010-2011, and 2018+.

**CGC FTD data reconciliation:**
| Measure | Value |
|---------|-------|
| NYSE listing | 2018-05-29 |
| Pre-listing entries | 265 (2004-07-12 to 2011-04-13) |
| 2012-2017 entries | **0** |
| 2018-2019 entries | 387 |
| 2018-2022 entries | 959 (single continuous episode) |

**Episodes via 20-trading-day gap splitter (9 total):**
| # | Start | End | Days | Label |
|---|-------|-----|------|-------|
| 1 | 2004-07-12 | 2004-07-13 | 1 | Pre-listing |
| 2 | 2005-10-18 | 2005-10-28 | 10 | Pre-listing |
| 3 | 2005-12-14 | 2005-12-14 | 0 | Pre-listing |
| 4 | 2007-07-03 | 2007-07-03 | 0 | Pre-listing |
| 5 | 2010-02-03 | 2011-04-13 | 434 | Pre-listing |
| 6 | 2018-05-29 | 2022-06-14 | 1477 | Post-listing |
| 7 | 2023-03-01 | 2023-03-31 | 30 | Post-listing |
| 8 | 2023-08-15 | 2023-08-31 | 16 | Post-listing |
| 9 | 2025-08-15 | 2025-08-29 | 14 | Post-listing |

**Episode onsets (6 total):** 2004-07-12, 2005-10-18, 2005-12-14, 2007-07-03, 2010-02-03, 2018-05-29

**Corporate action proximity (±28d):** 0/5 corp actions have a nearby episode onset.
| CA Date | Label | Nearby |
|---------|-------|--------|
| 2018-08-15 | Constellation investment announcement | 0 |
| 2018-10-24 | Note settlement + warrants | 0 |
| 2018-10-30 | Constellation closing | 0 |
| 2019-06-20 | Acreage approval + warrants | 0 |
| 2019-06-27 | Acreage record date | 0 |

- 212 E1 onsets (≥70% drop from 10-trading-day local max) — NOTE: this is PER-DATE drops, not episode segmentation
- Circular correlation (≥2018, shuffled-DATE nulls): r = -0.0503, p = 0.109 (1000 shuffles, N=1004)

### G4/H1 — Conjunction rescore

Pre-registered gradient: CH1=NEITHER, CH2=UNOBSERVED, CH3=UNOBSERVED → **NOISE 4/4**

### BANK — 2008-2009

Zero WAREHOUSE candidates in the pre-amendment naked-short era. Recorded as evidence against the warehouse construct at semi-monthly FTD resolution.

## V1 result (original, 2020-2025 only)

- 93 names scanned with count-tag SEC shares → 4 WAREHOUSE candidates (CYDY, LCID, TLRY, VUZI)
- CH1 all NEITHER, CH2 UNOBSERVED, CH3 UNOBSERVED → Conjunction: ALL 4 = NOISE

## V1 RERUN results (F1-F4)

### F1 — FTD backfill 2004-2019
SEC FOIA archive: 268/274 files verified, covering 2004-01-01 to 2019-12-31.
Full tape now spans 2004-01 to 2025-12.

## Key parameters

| Parameter | Value |
|-----------|-------|
| LOW_BAND | [0.01%, 0.1%] of shares |
| LOW_FRAC_THRESH | ≥40% of periods |
| ZERO_FRAC_THRESH | ≤30% of periods (at most 30%, not at least) |
| Simulations | 1,000 |
| Period band (spectral) | 42–252 trading days |
