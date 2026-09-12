# SOLUTIONS LEDGER PROTOCOL

When a directive says "check the ledger before claiming unavailable":

1. Verify `<project>/SOLUTIONS_LEDGER.md` hash matches the frozen MANIFEST
2. If the data source is LISTED, use the EXACT URL, method, and parameter format in the entry
3. If the listed syntax fails → paste the COMPLETE request + response verbatim (URL, headers, status code, body)
4. If the source is NOT listed → find an authoritative URL stating unavailability, else mark as `UNVERIFIED_ABSENCE`

## Key entries from SOLUTIONS_LEDGER.md (forced-covering-detector project)

| # | Source | Method | URL/Format | Status |
|---|--------|--------|-----------|--------|
| 1 | SEC EDGAR full-text | GET | `https://efts.sec.gov/LATEST/search-index?q={T}&startdt=...&enddt=...` w/ `User-Agent: research <email>` | Public, no key |
| 2 | SEC FTD ZIPs | GET | SEC.gov FOIA pages, 2004-present, same UA header | Public |
| 3 | SEC shares outstanding | GET | `data.sec.gov/api/xbrl/companyconcept/CIK{10d}/dei/EntityCommonStockSharesOutstanding.json` + us-gaap fallbacks (CommonStockSharesOutstanding, WeightedAverageNumberOfSharesOutstandingBasic); ⚠️ `www.sec.gov/Archives/` document URLs are BLOCKED (403) by Cloudflare/WAF — see `data-sourcing` skill `references/sec-edgar-403-bot-block.md`; submissions metadata at `data.sec.gov/submissions/CIK{cik}.json` WORKS — see `references/sec-edgar-submissions-api.md` | Public |
| 3a | SEC cover-page shares (pre-XBRL) | Phase1 (data.sec.gov submissions, works) → Phase2 (www.sec.gov docs, blocked). Pipelline: fetch filings metadata → identify 10-K/10-Q/20-F → regex extraction. See `data-sourcing` skill `references/sec-edgar-submissions-api.md` § Cover-Page Shares Extraction | BLOCKED (403) |
| 4 | iBorrowDesk fees | GET | `https://iborrowdesk.com/api/ticker/{T}` — keyless JSON, `daily` array with fee history | Keyless |
| 5 | Wayback iBorrowDesk | local | `<project>/data/wayback_iborrowdesk/` — on disk | Cached |
| 6 | FINRA OTC Weekly | POST | `api.finra.org/data/group/OTCMarket/name/WeeklySummary` w/ `dateRangeFilters`+`domainFilters` | Per-firm queries |
| 7 | FINRA Short Interest | GET | `https://cdn.finra.org/equity/otcmarket/biweekly/shrt{YYYYMMDD}.csv` — pipe-delimited CSV, User-Agent: research | Public, no key |
|   | _Fields_ | | `symbolCode`, `currentShortPositionQuantity`, `previousShortPositionQuantity`, `averageDailyVolumeQuantity`, `daysToCoverQuantity`, `settlementDate`, `issuerServicesGroupExchangeCode` (A=NYSE, Q=NASDAQ, H=BZX, E=ARCA, S=OTC, R=NYSE/Nasdaq) | |
|   | _Coverage_ | | All markets (NYSE, NASDAQ, ARCA, BZX, OTC) — ~22K tickers per settlement date. SI per symbol in shares, NOT short/float ratio. Need separate shares_outstanding for pctile computation. | |
|   | _Reg SHO daily short volume_ | GET | Consolidated: `https://cdn.finra.org/equity/regsho/daily/CNMSshvol{YYYYMMDD}.txt` (pipe-delimited: Date, Symbol, ShortVolume, ShortExemptVolume, TotalVolume, Market) | |
| 8 | Databento OPRA | | `symbology.resolve(..., stype_in="parent", symbols=["{T}.OPT"], ...)` at prior-trading-day | Key works |
| 9 | IBKR TWS | port 7496 | marketDataType, tick 236=shortable | Live |
| 10 | Registry | local | `calibration_cohort_registry_v2.json` sha256=28a1832b (excl COIN/HOOD/MRNA/RIDE/RIVN) | Frozen |

## Entry #1 detail — EDGAR full-text search

```python
import requests
ua = "research (b.en@prosecutor.research)"
r = requests.get(
    "https://efts.sec.gov/LATEST/search-index",
    params={"q": "TICKER", "startdt": "2020-01-01", "enddt": "2020-06-01",
            "category": "form-cat1,form-cat2,form-cat3"},
    headers={"User-Agent": ua},
    timeout=15)
# HTTP 200 with hits in data["hits"]["hits"]
# Each hit has _source.file_date, _source.form_name, _source.display_names[0]
```

Limitations: Returns all filings matching the ticker (including insider filings). Filter by `form_name` in results for corporate filings only.

**Complex boolean queries fail**: EFTS does NOT support parenthesized AND/OR combinations. Queries like `%22BYND%22+AND+(%22record+date%22+OR+%22expiration%22)` return 0 hits even when simple queries find results. Always decompose into multiple narrow single-phrase queries and filter client-side. Testing: `q=%22BYND%22+AND+%22record+date%22` on a known date range may work; adding parentheses breaks the query entirely. Fallback: just search the ticker with a date range and filter forms client-side; OR fetch all filings and grep for the phrase.

## Entry #4 detail — iBorrowDesk

```python
r = requests.get("https://iborrowdesk.com/api/ticker/AMC", 
                 headers={"User-Agent": ua}, timeout=10)
# HTTP 200, JSON keys: fee, available, daily[{date, fee_rate, available_shares}]
# DO NOT USE /api/v1/* paths
```

Historical: `daily` array covers ~1yr trailing. Chain wayback captures for longer history (same-API stitch, no cross-vendor mixing).

## Entry #8 detail — Databento OPRA

```python
res = db_client.symbology.resolve(
    dataset="OPRA.PILLAR", symbols=["{T}.OPT"],
    stype_in="parent", stype_out="instrument_id",
    start_date=PRIOR_TRADING_DAY, end_date=NEXT_DAY)
# Result keys are OSI symbols, not {T}.OPT
```

Pitfalls: weekend dates → 422; `r.close` → raw integer, use `r.pretty_close`; `r.instrument_id` not `r.hd.instrument_id`; micro-caps may lack options; ~$0.0015 per pull.

## Entry #7 detail — FINRA Short Interest

`shrt{YYYYMMDD}.csv` at `https://cdn.finra.org/equity/otcmarket/biweekly/`. Pipe-delimited (`|`). All exchange-listed ETFs: XRT, KBE, ARKK, etc. have `currentShortPositionQuantity`. Browser curl works (no Cloudflare). Settlement date in file, ~22K rows, ~2.1MB. Exchange codes: A=NYSE, Q=NASDAQ, H=BZX, E=ARCA, S=OTC, R=NYSE/Nasdaq mixed.

**SI for ETFs**: FINRA data includes ALL equities, including ETFs. ETF SI values: XRT=21.1M, KBE=17.0M, KRE=59.3M, GDX=46.8M, ARKK=24.9M, etc. This enables ETF-level percentiles vs the full 22K-ticker FINRA universe.

Reg SHO daily short volume: `https://cdn.finra.org/equity/regsho/daily/CNMSshvol{YYYYMMDD}.txt` (consolidated) or per-facility `F{XXX}shvol{YYYYMMDD}.txt`.

## Entry #10 — ETF Holdings URLs

| Issuer | Pattern | Status |
|--------|---------|--------|
| SSGA/SPDR | `https://www.ssga.com/library-content/products/fund-data/etfs/us/holdings-daily-us-en-{ticker_lower}.xlsx` | XLSX, ~18 SPDR sector ETFs — XRT, KRE, KBE, SPSM, XBI, XLK, etc. |
| iShares | `https://www.ishares.com/us/products/{product_id}/{slug}/{timestamp}.ajax?fileType=csv&fileName={TICKER}_holdings&dataType=fund` | CSV — IWM=239710, IBB=239514, SOXX=239728 |
| | **PITFALL — AJAX session expires**: The timestamp in the URL goes stale after an indeterminate period. Returns HTML (full product page, ~1.4MB) instead of CSV. To refresh: visit the iShares product page in a browser, click "Download Holdings" to get a fresh timestamp, then update the URL. When a script gets HTML instead of CSV, flag as SESSION_EXPIRED; do NOT attempt to parse HTML as CSV. | |
| VanEck | `https://www.vaneck.com/us/en/investments/{slug}/downloads/holdings/` | XLSX — GDX (gold-miners-etf-gdx), GDXJ, SMH, REMX |
| | **Cookie requirement**: VanEck's /downloads/holdings/ returns 302 (redirect loop) with raw curl. Must first visit the holdings page (`/investments/{slug}/holdings/`) to get a Set-Cookie, then use that cookie when requesting the download URL. After cookie, returns XLSX (8933B for GDX with 32 holdings). Use curl `-c /tmp/vc.txt` then `-b /tmp/vc.txt -L`. | |
| | XLSX format: Header at row 3 (Number, Ticker, Holding Name, FIGI, Shares, Asset Class, Market Value, Notional Value, % of Net Assets). Data starts row 4. Ticker=col 1, Weight=col 8 (with % suffix). | |
| Global X | `https://assets.globalxetfs.com/funds/holdings/{ticker}_full-holdings_{YYYYMMDD}.csv` | CSV — URA, SIL, LIT, COPX |
| | **Preamble**: 2 lines before CSV header ("Global X Uranium ETF" and "Fund Holdings Data as of..."). Header is at line index 2. Columns: % of Net Assets, Ticker, Name, SEDOL, Market Price, Shares Held, Market Value. | |
| Direxion | `https://www.direxion.com/holdings/{TICKER}.csv` | CSV — TSLL, AAPU, NVDU, SOXL etc. |
| | Single-stock ETFs only for mega-caps (TSLA, AAPL, NVDA, MSFT, META, AMD, PANW, BA, GOOGL, BABA). No Direxion/GraniteShares single-stock ETFs exist for map-band names (CEP, BKKT, AI, BBAI, APLD, BTBT, ACHR, BYND, ACB). BBAI has BAIG (Leverage Shares), APLD has APLX (Tradr). | |
| ARK | `https://assets.ark-funds.com/fund-documents/funds-etf-csv/{NAME}_{TICKER}_HOLDINGS.csv` | CSV — ARKK (ARK_INNOVATION_ETF). ARKX renamed -> URL unknown. |
| ProShares | `https://accounts.profunds.com/etfdata/psdlyhld.csv?fund={TICKER}` | Filtered master CSV — BITO. Parse: filter rows by Fund Ticker column. |
| VolatilityShares | `https://www.volatilityshares.com/download-holdings-usbanks.php?fund={ticker}` | XLS — BITX. Use xlrd (not openpyxl) for .xls files. |
| YieldMax | `https://yieldmaxetfs.com/wp-content/uploads/funds/{TICKER}/TidalFG_Holdings_{TICKER}.csv` | CSV — MSTY, CONY. StockTicker column may contain option symbols ("COIN 260710C00175000"); strip to first token for underlying. Weightings column has % suffix. |

**Unavailable as direct CSV/XLXS**: URNM (Sprott — quarterly PDF only), SILJ (Amplify — JS download button), QTUM (Defiance — JS download button), WGMI (CoinShares — product page only), SIL (VanEck has no silver miner ETF — SIL is Global X), SILJ (Amplify, not VanEck), TAN (Invesco — SPA).

**Single-stock ETF gaps for map-band names**: Of CEP, BKKT, AI, BBAI, APLD, BTBT, ACHR, BYND, ACB — only BBAI (BAIG, Leverage Shares) and APLD (APLX, Tradr) have single-stock levered ETFs. No Direxion/GraniteShares products for any of these. 

## Entry #11 — CIRO/IIROC Canadian Short Interest

- **CSPR** (short positions): `https://www.ciro.ca/sites/default/files/epubs/CSPR/{YYYYMMDD}_CSPR_Report.xls` — biweekly XLS
- **SSTSSR** (short volume): `https://www.ciro.ca/sites/default/files/epubs/SSALE/{start}-{end}_ShortSaleTradingSummaryReport.csv`
- **LSL** (lending): `https://www.ciro.ca/sites/default/files/epubs/HLS/{YYYYMMDD}_LSL_REPORT.csv` — contains ACB
- **Cloudflare**: All CIRO URLs blocked from curl. Must use browser. Automated download = DATA_WALL.
- **Alternative**: shortdata.ca for TSX SI; FINRA for NASDAQ-listed dual tickers.
- **TSX ticker mapping**: CGC trades TSX as WEED, not CGC. ACB ticker is same on both.
- **UNOBSERVED** rule: US FINRA SI must NOT be substituted for Canadian SI. If CIRO is Cloudflare-blocked, the L1_CA column is literally UNOBSERVED — do not mark it DATA_WALL with a proxy value.

## Entry #12 — C8 Warrant Redemption Outcome Finding

11 C8 events (warrant redemptions) tested with E1v2 + E3 ±10td at 3:1 matched controls:

| Metric | Events | Controls | Fisher p |
|--------|--------|----------|----------|
| E1v2 hit rate | 5/11 (45.5%) | 0/33 (0%) | 0.000425 |
| E3 (+15%/3d) | 3/11 (27.3%) | 0/33 (0%) | 0.012458 |

Strongest hits: ASTS (Max FTD=4.3% of SO), SMR (6.8%), LUNR (2.0%), PLSE (0.6%). Events failing cond_b (no pre-max FTD build-up) are earlier/lower-SI names. C8 is a legitimate forced-covering trigger class. C8 registry built from EFTS "warrant redemption" search across 2022-2026 (14 events saved to c8_registry_v1.json).