# FTD Cycles — Data Sources and Techniques

## SEC Fails-to-Deliver (FTD) Data

### Current data (2020–present)

**Source:** `https://www.sec.gov/files/data/fails-deliver-data/cnsfailsYYYYMM{a,b}.zip`

**Format:** Pipe-delimited text file inside each ZIP:
```
SETTLEMENT DATE|CUSIP|SYMBOL|QUANTITY (FAILS)|DESCRIPTION|PRICE
20240603|B38564108|EURN|28486|EURONAV NV ANTWERPEN (BELGIUM)|16.91
```

**Coverage:** 2020–present, semi-monthly (a=1st-15th, b=16th-end). Each ZIP contains one text file named `cnsfailsYYYYMM{a,b}` with ~50K lines.

### Historical FOIA data (2004–2019)

**Source path 1 (FOIA archive):** `https://www.sec.gov/files/data/frequently-requested-foia-document-fails-deliver-data/`
**Source path 2 (direct):** `https://www.sec.gov/files/data/fails-deliver-data/`

**File naming patterns:**
- **2004 Q1:** `cnsp_sec_fails_2004q1.zip` (under path 2)
- **2004 Q2 – 2009 Q2:** `cnsp_sec_fails_{yyyy}q{q}.zip` (under path 1)
- **2009-07 – 2017-06:** `cnsfails{yyyymm}{a,b}.zip` (under path 1)
- **2017-07 – present:** `cnsfails{yyyymm}{a,b}.zip` (under path 2)

**Same pipe-delimited format as current data.** The older quarterly ZIPs (`cnsp_sec_fails_*`) contain one file per month inside: `cnsp_sec_fails_200403.txt`, etc. Some monthly files in these ZIPs may lack the "Trailer total quantity" trailer line — data is still valid.

**Verified date range:** 2004-01-01 through 2025-12-31. 6 files out of ~430 total failed download (2 HTTP 404, 4 trailer-format edge cases with valid data).

**Automatic download script pattern:**
```python
BASE_HIST = 'https://www.sec.gov/files/data/frequently-requested-foia-document-fails-deliver-data'
BASE_CURR = 'https://www.sec.gov/files/data/fails-deliver-data'

# cnsp_sec_fails (2004 Q1)
requests.get(f'{BASE_CURR}/cnsp_sec_fails_2004q1.zip')
# cnsp_sec_fails (2004 Q2 – 2009 Q2)
requests.get(f'{BASE_HIST}/cnsp_sec_fails_{yr}q{q}.zip')
# cnsfails (2009-07 – present)
requests.get(f'{BASE_HIST}/cnsfails{yr}{mo:02d}{suff}.zip')  # pre-2017
requests.get(f'{BASE_CURR}/cnsfails{yr}{mo:02d}{suff}.zip')   # 2017+
```

### Parsing notes (all eras)
- PRICE column can be "." (empty) — catch with try/except, default to 0.0
- Lines are pipe-delimited, NOT comma-separated
- Quantity has commas — strip before int conversion
- Encoding: latin-1 (not utf-8)
- User-Agent for SEC: `research contact@<email>` (akamai blocks generic bots)
- Pre-2022 ZIPs use a different URL path (`/files/node/add/data_distribution/`) — the standard path only goes back to Feb 2022

## SEC Threshold Securities (Reg SHO)

Threshold securities are those with aggregate fails >$500K for 5+ consecutive settlement days. The standalone SEC threshold page (threshold-securities-data) redirects to a 404 post-redesign. Use the FTD data directly — threshold status is derived from FTD data anyway.

**Dwell time computation:** For each ticker, identify consecutive settlement dates where FTD_dollar = qty × price > $500K. Gaps ≤4 calendar days are bridged (weekends/holidays). Dwell ≥13 consecutive trading days = persistent threshold.

## iBorrowDesk Fee History

**Live API:** `https://iborrowdesk.com/api/ticker/{TICKER}`

Returns JSON with daily fee + availability. ~259 records per ticker (~1 year of trailing data). 301 redirect from the canonical URL — use `curl -sL` or `requests.get` with `allow_redirects=True`.

**Format:**
```json
{"daily":[
  {"available":10000000,"date":"2025-07-07","fee":0.2500,
   "high_available":10000000,"high_fee":0.4081,"high_rebate":4.0800,
   "low_available":10000000,"low_fee":0.2500,"low_rebate":3.9219,"rebate":4.0800},
  ...
]}
```

**Coverage:** ~2025-07 to present. Historical data only via Wayback Machine.

**Fee rate semantics for E2 detection:**
- `fee` = borrow fee rate (the key field for E2)
- `available` = shares available to short
- `rebate` = rebate rate (can be negative for hard-to-borrow names)
- A 50%+ drop in `fee` from local max = forced-covering signal (E2)

## IBKR Short Stock FTP

**Server:** `ftp2.interactivebrokers.com`
**Credentials:** `shortstock` / `anonymous`

**Files:**
- `usa.txt` — US equities (~19K lines), pipe-delimited
- `canada.txt`, `germany.txt`, etc. — 52 country files
- `stockmargin_final_dtls.IBLLC-US.dat` — margin requirements (NOT borrow fee data)

**usa.txt format:**
```
#BOF|2026.07.04|08:03:33
#SYM|CUR|NAME|CON|ISIN|REBATERATE|FEERATE|AVAILABLE|FIGI|
A|USD|AGILENT TECHNOLOGIES INC|1715006|XXXXXXXU1016|3.2158|0.4142|3900000|BBG000C2V3D6|
```

**Key fields:** SYMBOL, FEERATE (borrow fee rate), AVAILABLE (shares), REBATERATE.

**Limitation:** Live data only. No historical archive on the FTP. Historical snapshots found only in QuantConnect's Lean DataSource repo (single snapshot 2023-11-15).

## Wayback Machine Fee Archives

**Service:** `archive.org/wayback/available?url=https://iborrowdesk.com/api/ticker/{TICKER}`

Returns the closest captured snapshot of the iBorrowDesk API. Each capture provides ~1 year of trailing fee history from the capture date.

**Availability check pattern:**
```python
resp = requests.get(f"https://archive.org/wayback/available?url=https://iborrowdesk.com/api/ticker/{ticker}")
snap = resp.json().get('archived_snapshots', {}).get('closest', {})
if snap:
    wayback_url = snap['url']
```

**Coverage findings:** ~10/30 event names have captures. Snapshots from 2022-01 through 2025-10. Each capture gives a ~1 year trailing window. Stitching: a capture from Jan 2022 shows fee data from Jul 2021 — enough to cover some 2022 event windows.

**Rate limits:** Wayback Machine will rate-block after ~20 requests. Use the availability API (not CDX) for reliability. Space requests 1.5s apart. Retry on connection errors.

## OCC Stock-Loan Bal by Security (DATA WALL — endpoint dead)

**Endpoint:** `https://marketdata.theocc.com/stock-loan-bal-by-security`
**Format:** `format=csv`, daily date in `MM/DD/YY`

**Status (verified 2026-07-05):** Returns "No record(s) found" for ALL dates across 2020-2026. Tested 9+ trading dates spanning 2020-2026 — zero records returned. The endpoint returns HTTP 200 but never contains actual data. Formerly the endpoint may have worked (some old scripts show it working in 2024-2025), but it is currently non-functional.

**Alternatives for stock-loan data:**
- **iBorrowDesk** (free, ~1yr trailing per ticker)
- **IBKR Short Stock FTP** (`ftp2.interactivebrokers.com`, `shortstock:anonymous`, `usa.txt` — live snapshot only, no history)
- **Wayback Machine** captures of iBorrowDesk API (sparse coverage, ~10/30 event names)

## Databento OPRA.PILLAR (Options Data)

**Dataset:** `OPRA.PILLAR` — US options market data.

**Cost:**
- `definition` schema: $5/GB (~$0.11 per ticker for full option chain)
- `statistics` schema: $11/GB (~$0.10 per ticker for 100 options × 20 days)
- Total per ticker: ~$0.20-0.25

**Key schemas:**
| Schema | What | Cost | Use |
|--------|------|------|-----|
| `definition` | OCC symbols, strike, expiration, C/P | $5/GB | Find options for moneyness filter |
| `statistics` | Volume (6), OI (9), VWAP (13), delta (15) | $11/GB | Volume+OI for event vs baseline |
| `ohlcv-1d` | Daily OHLCV per contract | HIGH (~$0.0032/contract/month) | Historical volume by strike |
| `cmbp-1` | Consolidated BBO (top of book) | $0.16/GB | Real-time pricing (not needed for backtest) |

**Option contract discovery — parent symbology WORKS:**
Use `stype_in='parent'` with `symbols='TICKER.OPT'` to resolve ALL option contracts for an underlying. Example:
```python
result = client.symbology.resolve(
    dataset='OPRA.PILLAR',
    symbols=['AMC.OPT'],
    stype_in=SType.PARENT,
    stype_out=SType.INSTRUMENT_ID,
    start_date='2021-06-01', end_date='2021-06-30',
)
```
Returns ~2,826 individual option contracts for AMC in June 2021. Message: "Partially resolved", Status: 1. Individual contracts appear as root-level keys in the result dict (NOT nested under `AMC.OPT`).

**Cost at scale (prohibitive for multi-name multi-year studies):**
- `ohlcv-1d` per contract: ~$0.0032/contract/month
- Full AMC chain (June 2021): ~$9.00/month
- 4 names × 72 months (2020-2025): ~$2,592 (exceeds typical $15 budget)
- Full OPRA.PILLAR `ohlcv-1d` scan (no symbol filter): ~$600/month
- **Conclusion:** Option contract discovery IS feasible, but historical OHLCV at full chain scale is budget-prohibitive for research.

**Statistics schema quirks:**
- Stat value is in `price` column (float64), NOT a `value` column
- stat_type=6 (CLEARED_VOLUME): `price` = total traded volume
- stat_type=9 (OPEN_INTEREST): `price` = open interest
- `quantity` column is often 0 for statistics — use `price`

**Query pattern for ohlcv-1d (individual contract daily OHLCV):**
```python
data = client.timeseries.get_range(
    dataset='OPRA.PILLAR', schema='ohlcv-1d',
    symbols=instrument_ids, stype_in='instrument_id',
    start=date_str, end=next_day_str)
records = list(data)
for r in records:
    iid = r.instrument_id  # NOT r.hd.instrument_id — .hd was removed in a recent API version
    ...
```
```python
from databento import Historical
client = Historical(key='API_KEY')

# Step 1: Get definitions
defs = client.timeseries.get_range(
    dataset='OPRA.PILLAR', schema='definition',
    stype_in='parent', symbols=['AAPL.OPT'],
    start='2024-01-15', end='2024-01-16')
df_defs = defs.to_df()

# Step 2: Filter deep-ITM calls (strike <= price * 0.8)
calls = df_defs[df_defs['instrument_class'] == 'C']
deep_itm = calls[calls['strike_price'] <= underlying_price * 0.8]

# Step 3: Get statistics
stats = client.timeseries.get_range(
    dataset='OPRA.PILLAR', schema='statistics',
    stype_in='raw_symbol', symbols=deep_itm['raw_symbol'].tolist(),
    start=baseline_start, end=event_end)
df_stats = stats.to_df()

# Step 4: Extract volume (stat_type=6) and OI (stat_type=9)
vol = df_stats[df_stats['stat_type'] == 6]
oi = df_stats[df_stats['stat_type'] == 9]
```

**Deep-ITM call volume as f1 (conservation residual):**
- REAL covering: FTD drops CONCURRENT with deep-ITM call volume RISE → shorts covering by taking delivery of shares from exercised calls
- COSMETIC: FTD drops WITHOUT deep-ITM call echo → fails aging off, not true covering
- Classification threshold: >50% volume increase from baseline = REAL; flat/down = COSMETIC

## EODHD API (Price + Fundamentals)

**Key:** `6a1e8497f39bd3.74614857`

**Rate limits:** ~10 req/sec free tier, ~100K/day quota. Returns HTTP 402 when exceeded. All endpoints break simultaneously (both `/eod/` and `/fundamentals/`). Quota resets at 00:00 UTC.

**Key endpoints:**
- `/eod/{TICKER}.US?from=DATE&to=DATE` — daily OHLC with `adjusted_close`
- `/fundamentals/{TICKER}.US?filter=General` — Type, Exchange, Sector, Industry
- `/fundamentals/{TICKER}.US?filter=SharesStats` — SharesOutstanding, SharesFloat
- `/fundamentals/{TICKER}.US?filter=Highlights` — MarketCapitalization
- `/splits/{TICKER}.US` — stock split history

**Parallel strategy (for large ticker batches):**
Use ThreadPoolExecutor(max_workers=5-10) with batch sizes of 50-100 and 1s pauses between batches. Sequential at 0.1s per call will hit the daily quota after ~500 calls.

**Fallback when rate-limited (EODHD 402):**
- For shares outstanding: back-estimate from registry quarterly_counts (shares = max_FTD / (quarterly_pct / 100)) — this is approximate (2x-177x error margin)
- For underlying price: use yfinance (see section below) or FTD ZIP column 6 (PRICE)

### yFinance Fallback (EODHD rate-limited)

When EODHD returns HTTP 402 (daily quota exhausted), use yfinance as a free alternative for stock prices.

```python
import yfinance as yf
ticker = yf.Ticker('LCID')
hist = ticker.history(start='2020-01-01', end='2026-01-01')
price = float(hist.loc['2024-06-15']['Close'])
```

**Coverage:** US equities, daily OHLCV. yfinance drops delisted tickers silently — check `hist.empty`. Good for price history. Does NOT provide fundamentals (shares outstanding, sector).

**Installation:** `pip install yfinance` (available in base venv).

## FINRA OTC Transparency API (Non-ATS Volume)

The FINRA OTC transparency data (weekly non-ATS share volume per ticker) is accessible through their REST API — NOT through the SPA at otctransparency.finra.org (which requires browser interaction per download).

**Endpoint:** `POST https://api.finra.org/data/group/OTCMarket/name/WeeklySummary`
**Authentication:** None (public, no API key required)
**Content-Type:** Must set `Content-Type: application/json` (returns 415 otherwise)
**Accept:** `Accept: application/json` for JSON response (default is CSV)

**Request format:**
```json
{
  "limit": 5000, "offset": 0,
  "sort": "-weekStartDate",
  "filters": [
    {"fieldName": "summaryTypeCode", "value": "ATS_W_NONATS_FIRM"},
    {"fieldName": "issueSymbolIdentifier", "value": "AAL"}
  ]
}
```

**Record types:**
- `ATS_W_NONATS_FIRM` — per-ticker, per-firm non-ATS detail
- `ATS_W_VOL_STATS` — aggregate ATS volume (all firms, no ticker)
- `ATS_W_SMBL_FIRM` — per-ticker, per-firm ATS detail

**Response fields (17):** `issueSymbolIdentifier`, `issueName`, `firmCRDNumber`, `MPID`, `marketParticipantName`, `tierIdentifier`, `tierDescription`, `summaryStartDate`, `totalWeeklyTradeCount`, `totalWeeklyShareQuantity`, `productTypeCode`, `summaryTypeCode`, `weekStartDate`, `lastUpdateDate`, `initialPublishedDate`, `lastReportedDate`, `totalNotionalSum`.

**Dataset scale:** ~54M records total. Per major ticker (~300 weeks × ~1800 firms = ~540K records). Paginate with offset (5000/request, offset cap 500K).

**Aggregate-only queries (CRITICAL LIMITATION):**
The `summaryTypeCode` filter does NOT work reliably — requesting `ATS_W_NONATS_FIRM` returns `ATS_W_VOL_STATS` records. The aggregate row (`issueSymbolIdentifier=None`) is embedded as the first record of each page. Each 5000-record page covers ≈1 week, making it impossible to query per-ticker weekly aggregates without paginating through ALL per-firm records.

**CompareFilters probe result:** `compareFilters` returns HTTP 204 (not supported). `weekStartDate` filter in the `filters` array is silently ignored — returns the most recent available week regardless of filter value. Only `issueSymbolIdentifier` filtering works reliably. **Date-filter non-support is a halt** for any per-name-week query pattern.

To extract weekly aggregates for a ticker:
1. Query with `issueSymbolIdentifier=<TICKER>` only (no `summaryTypeCode` filter)
2. The first record in each page has `issueSymbolIdentifier=None` — that's the aggregate
3. Each subsequent record is per-firm detail
4. ~5000 records per week; ~100 pages per ticker at 500K max offset
5. Estimated: ~100 pages × 1.2s = 120s per ticker. 52 tickers: ~1.7h
6. With checkpointing, partial results survive interruption

**Option contract discovery — parent symbology WORKS:**
Use `stype_in='parent'` with `symbols='TICKER.OPT'` on OPRA.PILLAR to resolve ALL option contracts for an underlying. Returns ~2,826 contracts for AMC in June 2021 (message: "Partially resolved", status: 1). Individual contracts appear as root-level result keys, NOT nested under `TICKER.OPT`.

**Cost constraint:** `ohlcv-1d` at ~$0.0032/contract/month. Full AMC chain for June 2021: ~$9.00. 4 names × 72 months: ~$2,592 (exceeds typical $15 budget). Parent resolution is feasible; historical volume at full chain scale is budget-prohibitive.

**Aggregate row field mapping:** `totalWeeklyShareQuantity` = total OTC volume (includes ATS + non-ATS). The aggregate does NOT distinguish ATS from non-ATS — that requires per-firm computation.

## SEC XBRL Shares Outstanding — Count Tags Only

Use only these count tags for shares outstanding:
- `dei/EntityCommonStockSharesOutstanding` (best — filing-date specific)
- `us-gaap/CommonStockSharesOutstanding` (quarterly balance sheet)
- `us-gaap/CommonStockSharesIssued` (second-line check)

**FORBIDDEN:** `dei/EntityPublicFloat` — this is a float/valuation metric, NOT a share count. Using it produces incorrect FTD/shares ratios.

**URL pattern:** `https://data.sec.gov/api/xbrl/companyconcept/CIK{10d}/dei/EntityCommonStockSharesOutstanding.json`
**Header:** `User-Agent: research contact@<email>`
**Rate:** ≤10 req/s, space 0.25s apart.

## FTD Episode Segmentation Methodology

The core algorithm for identifying forced-covering event onset:

```
For each ticker in registry:
  1. Get all FTD data for the ticker
  2. Get shares outstanding (from EODHD or back-estimated)
  3. For each semi-monthly date, compute FTD% = qty / shares * 100
  4. Consecutive dates with FTD% > threshold (default 0.1%) = elevated-FTD episode
  5. Gap >20 trading days between elevated dates → split into separate episode
  6. Episode onset = first date in the episode
  7. Match documented event date to nearest episode (within ±30 days)
  8. If no match → ORPHAN_DATE (event not FTD-driven)

Returns: redated onset date (or ORPHAN_DATE), episode span, episode duration
```

C2 filter (quarterly FTD elevation): for each of the 4 quarters prior to onset, compute max FTD% in quarter. Elevated = >0.25% of shares outstanding. TARGET = ≥2/4 quarters elevated.

## FINRA Short Interest (Biweekly CDN)

**URL pattern:** `https://cdn.finra.org/equity/otcmarket/biweekly/shrt{YYYYMMDD}.csv`

**Format:** Pipe-delimited CSV. ~22K rows, ~2.2MB. Header: `accountingYearMonthNumber|symbolCode|issueName|issuerServicesGroupExchangeCode|marketClassCode|currentShortPositionQuantity|previousShortPositionQuantity|stockSplitFlag|averageDailyVolumeQuantity|daysToCoverQuantity|revisionFlag|changePercent|changePreviousNumber|settlementDate`

**Coverage:** ALL equities (NYSE, NASDAQ, ARCA, BZX, OTC) in a single biweekly file. Fields: `symbolCode` (ticker), `currentShortPositionQuantity` (short interest shares), `settlementDate`.

**Access:** Public, no API key required. Works with standard User-Agent header. No Cloudflare. Use `csv.DictReader` with `delimiter='|'`.

**Reg SHO Daily Short Volume (supplementary):** Also available at `https://cdn.finra.org/equity/regsho/daily/CNMSshvol{YYYYMMDD}.txt` (consolidated), pipe-delimited with columns: `Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market`. Per-facility files: `FNQCshvol`, `FNRAshvol`, `FNSQshvol`, `FNYXshvol`, `FORFshvol`.

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| EODHD 402 — daily quota exhausted | Report blocker, use cached/back-estimated shares. Retry next UTC day. |
| FTD PRICE column = "." (empty) | try/except float conversion, default to 0.0 |
| Wayback Machine rate-blocking | Space requests 1.5s+ apart. Use availability API, not CDX. |
| Databento `start == end` date range | Add +1 day: start=date, end=date+1d |
| Databento statistics: no `value` column | Use `price` column for stat values |
| SEC ZIPs pre-2022 use different URL | Check `/files/node/add/data_distribution/` path |
| iBorrowDesk 301 redirect | Use `-L` flag or `allow_redirects=True` |
| Split-adjusted vs unadjusted closes for E3 | Always use `adjusted_close` from EODHD to avoid split-induced price moves |
| Forcing-clock vacuousness (>50% of days in clock windows) | Flag as CHRONIC; exclude from Gate C count |
| Controls matching from 80-ticker universe too small | Need full EODHD US-common scan (27K+ tickers) for 3:1 cap/sector/date |
| FINRA OTC API returns 415 | Missing `Content-Type: application/json` header — add it explicitly |
| FINRA OTC API huge response (~540K per ticker) | Filter by `summaryTypeCode: ATS_W_NONATS_FIRM` + `issueSymbolIdentifier`; paginate with offset |
| yfinance drops delisted tickers silently | Check `hist.empty` before using price data |
| SEC XBRL EntityPublicFloat mistaken for share count | This is a float/valuation metric, NOT a share count. FTD ratios will be wildly inflated. Use only count tags. |
| SEC ZIP naming pre-2020 | 2004-2009 uses `cnsp_sec_fails_{yyyy}q{q}.zip` (quarterly bundles, one file per month inside); 2009-2017 uses same `cnsfails{yyyymm}{a,b}` pattern but under `frequently-requested-foia-` path |
| Trailer-less ZIP format in FOIA archives | Some files in the quarterly `cnsp_sec_fails_*` ZIPs lack the "Trailer total quantity" line on one or two months. Data is still valid — just check for pipe-delimited rows. |