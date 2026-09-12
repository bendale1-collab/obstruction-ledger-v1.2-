# Taxonomy Cohort Test (X0-X6 framework)

**When to load:** Any task requiring multi-variable testing of a squeeze/forced-covering event cohort across mechanical vs attention-driven triggers. V1 executed 2026-07-05.

## X0 — Event base construction

1. Load registry (27 candidates, CALIBRATION_COHORT_V1)
2. Classify each event as {MECHANICAL, ATTENTION_ONLY} per taxonomy:
   - **MECHANICAL:** triggerable to a specific filed action (8-K, 13D, Ch.11 emergence, SPAC merger, direct listing)
   - **ATTENTION_ONLY:** triggered by social media attention / retail coordination, no specific mechanical trigger
3. Known MECHANICAL: HTZ (Ch.11 emergence), BBBY (Ryan Cohen 13D), COIN (direct listing), DWAC (SPAC merger)
4. All others: ATTENTION_ONLY (confirmed GME, AAL, AMC, CGC, CHPT, CLOV, EXPR, FFIE, HKD, HOOD, KOSS, LCID, MRNA, NAKD, OSTK, RIDE, RIVN, RKT, SNDL, SPCE, TLRY, TR, WISH)

## X1 — Trigger test

- Query SEC EDGAR for 8-K/424B/DEF14A/Form 25 filings in [-45d, +5d] around onset
- MECHANICAL events should show a filing; ATTENTION_ONLY are control class
- **SEC EDGAR efts.sec.gov search-index endpoint returns 403** — cannot execute programmatically
- Manual alternative: browse EDGAR HTML search per CIK at `https://www.sec.gov/cgi-bin/browse-edgar`

## X2 — Size test (SI/float)

- Per event at T-30: SI/float from FINRA weekly SI, ETF look-through, effective-float haircut
- Needs 3:1 matched controls (sector + mktcap within ±50%)
- **SI/float data UNOBSERVED** — FINRA short interest data not available in this environment

## X3 — Timing test (borrow fee)

- Fee convexity = 2nd-diff of borrow fee T-30..T-01
- **UNOBSERVED** — iBorrowDesk requires manual registration; IBKR borrow fee genericTick 261 rejected

## X4 — Variables 4-7

- **Dwell days:** Available from registry (threshold_dwell_days field). Range: 0-240d. Distribution right-skewed.
- **Deep-ITM reset volume:** Databento OPRA, snapped dates, consistent prettyscale price basis. UNOBSERVED — budget reserve.
- **Supply slope:** SEC Form 13 data, FTD tape analysis. UNOBSERVED pre-2025.
- **Call-skew shift vs sector ETF:** Partial ATM call IV available for 3 events (AAL, CLOV, OSTK) from IV_RANK_PROBE_v2. OTM put IV not sourced.

## X5 — Independence (pairwise Spearman)

- Requires N > #variables. With 6-7 variables and only 3 events with complete IV data → INSUFFICIENT_DATA
- Matrix deferred until variable coverage exceeds event count

## X6 — ETF-routing open question

- High-ETF-weight events (GME/XRT) vs low-ETF-weight MECHANICAL events
- Direction only, N will be tiny
- **UNOBSERVED** — need ETF holdings-level data

## V1 results

| Variable | Status | Data |
|---|---|---|
| Taxonomy class | ✅ | 4 MECHANICAL, 23 ATTENTION_ONLY |
| Dwell days | ✅ | 27 events, range 0-240d |
| Call IV (3 events) | ✅ | AAL, CLOV, OSTK |
| Trigger (SEC) | ❌ 403 | Cannot query programmatically |
| Size (SI/float) | ❌ | No FINRA SI data |
| Timing (fee) | ❌ | No borrow fee source |
| Reset vol | ❌ | Databento budget |
| Supply slope | ❌ | Pre-2025 |
| Independence | ❌ | N=3 < 6 variables |
| ETF routing | ❌ | Need holdings data |

**Key takeaway:** 6 of 10 variables UNOBSERVED across this environment. The taxonomy classification and dwell days are the only universally available variables. Future passes should prioritize iBorrowDesk registration (fee data) and FINRA SI sourcing before attempting multi-variable analysis.

---

## X-SERIES RERUN (2026-07-05) — post-D2 registry (22 events, excl COIN/MRNA/HOOD/RIDE/RIVN)

### Step 0 — Registry
Post-D2 registry created: `calibration_cohort_registry_v2.json` (SHA256 `28a1832b`), parent = `CALIBRATION_COHORT_V1` (SHA256 `b93f0ed8`. Excluded: COIN, HOOD, MRNA, RIDE, RIVN. 22 events remaining.

### Step 1 — Taxonomy correction
OSTK reclassified to MECHANICAL (blockchain dividend — Overstock issued OSTKO digital security dividend Sep 2020, forcing short sellers to cover or deliver synthetic shares). HTZ confirmed MECHANICAL (Ch.11 filing May 22, 2020). DWAC/BBBY per report (SPAC merger announcement Oct 20, 2021 / Ryan Cohen 13D).

### Step 2 — EDGAR trigger test
SEC EDGAR full-text search at `https://efts.sec.gov/LATEST/search-index` returns **HTTP 403** even with proper `User-Agent: research (b.en@prosecutor.research)` header. The efts.sec.gov search API requires SEC API key. Alternative: CIK lookup + RSS feed per CIK (crawling, not search), or SEC EDGAR XBRL API for specific form types. Not executed in this pass (22 CIKs x multiple form types is a multi-hour crawl).

### Step 3 — Borrow fee (iBorrowDesk / Wayback)
- **On disk:** No wayback/iborrow/short_fee/borrow_fee files found after recursive search of ~/.
- **Live API:** `https://www.iborrowdesk.com/api/v1/fee/AMC` — HTTP 403. `https://www.iborrowdesk.com/report/AMC` — HTTP 403. The iBorrowDesk API requires registration/API key. Historical borrow fee data for 2020-2022 not cached on disk.

### Step 4 — FINRA SI
FINRA Short Interest API at `https://api.finra.org/data/group/OTCMarket/name/ShortInterestVolume` uses POST with JSON body. Tested with `{"conditions": [{"fieldName":"productSymbol","values":["AMC"],"conditionType":"EQUAL"}]}`. Returned HTTP 400 with structured error. FINRA weekly SI data has been restructured and requires different query format. Alternative: scrape FINRA FTP weekly SI files (~200+ CSV files, 2-3 hour crawl).

### Step 5 — Databento var5/7
Budget: $0.09 spent from prior run, $14.91 remaining. Tested 6 events (AAL, OSTK, CLOV, HTZ, BBBY, DWAC) at T-60/T-30 with snapped dates and pretty_close. Results:
- AAL: ATM+ITM IV success at both T-60 and T-30
- CLV: Partial success (ATM OK, ITM puts limited by DTE range)
- OSTK: ATM success, deep ITM puts had no OHLCV data
- HTZ/BBBY/DWAC: RESOLVE_FAIL or NO_OHLCV for most dates (old dates for HTZ=2020, DWAC=2021 had sparse OPRA options coverage)

### Remaining data walls
| Source | URL/Endpoint | Status | Evidence |
|--------|-------------|--------|----------|
| SEC EDGAR efts | `efts.sec.gov/LATEST/search-index` | 403 | Request: `User-Agent: research (email)`, params: `{q, startdt, enddt}`. Response: empty 403 page. |
| iBorrowDesk | `iborrowdesk.com/api/v1/fee/*` | 403 | No API key. No cached files on disk. |
| FINRA SI | `api.finra.org/data/group/OTCMarket/name/ShortInterestVolume` | 400 | POST with productSymbol filter rejected. Requires different query schema.
