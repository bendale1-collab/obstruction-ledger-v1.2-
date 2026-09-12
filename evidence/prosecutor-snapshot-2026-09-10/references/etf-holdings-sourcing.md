# ETF Holdings — Working Download URLs

Compiled 2026-07-09. Verified direct-download URLs for ETF daily holdings, by issuer.

## SSGA/SPDR — XLSX (no auth)

**Pattern:** `https://www.ssga.com/library-content/products/fund-data/etfs/us/holdings-daily-us-en-{ticker_lower}.xlsx`

**Format:** XLSX. Row 5 header: Name, Ticker, Identifier, SEDOL, Weight, Sector, Shares Held. Weight in % points.

**Confirmed working:** XRT, SPY, KRE, KBE, SPSM, MDY, XHB, XLE, XLK, XLF, XLV, XBI, XLB, XLY, XLI, XLP, XLU, XLRE

**Parse pattern (openpyxl):**
```python
import openpyxl
wb = openpyxl.load_workbook(buf, read_only=True, data_only=True)
ws = wb.active
holdings = []
for row in ws.iter_rows(min_row=6, max_row=ws.max_row, values_only=True):
    ticker = str(row[1]).strip() if row[1] else ''
    weight = float(row[4]) if len(row) > 4 and row[4] else 0
    if ticker and weight: holdings.append({'ticker': ticker, 'weight': weight})
```

## iShares (BlackRock) — CSV (AJAX endpoint, session-gated)

**Pattern:** `https://www.ishares.com/us/products/{product_id}/{slug}/{timestamp}.ajax?fileType=csv&fileName={TICKER}_holdings&dataType=fund`

**Format:** CSV. Header row varies — search for line starting with `Ticker`. Strip NUL bytes (`\x00`) before parsing.

**Product IDs (confirmed):**
| Ticker | Product ID | Slug |
|--------|-----------|------|
| IWM | 239710 | ishares-russell-2000-etf |
| IBB | 239514 | ishares-nasdaq-biotechnology-etf |
| SOXX | 239728 | ishares-semiconductor-etf |

**Issue:** The AJAX endpoint expires periodically and returns HTML instead of CSV. When this happens, re-fetch from the iShares product page with a browser session to get a fresh timestamp, or use the SSGA equivalent (e.g., XBI replaces IBB).

**Parse pattern:**
```python
text = data.decode('utf-8', errors='replace').replace('\x00', '')
lines = text.split('\n')
for i, line in enumerate(lines):
    if line.strip().startswith('Ticker') and 'Weight' in line:
        reader = csv.DictReader(lines[i:])
        for row in reader:
            t = row.get('Ticker', '').strip()
            w = row.get('Weight', '0')
            if t and float(w) > 0: ...
        break
```

## VanEck — XLSX (cookie session required)

**Pattern:** `https://www.vaneck.com/us/en/investments/{slug}/downloads/holdings/`

**Format:** XLSX. Row 3 header: Number, Ticker, Holding Name, FIGI, Shares, Asset Class, Market Value, Notional Value, % of Net Assets. Data starts at row 4. Ticker at col[1], weight at col[8] (has `%` suffix).

**Requires cookies:** First visit the holdings page to get a session cookie, then download. Use `curl -c` + `curl -b` with 1.5s delay between page visit and download. Python urllib redirect handling is broken for VanEck's redirect chain — use subprocess with curl.

**Confirmed slugs:**
| Ticker | Slug |
|--------|------|
| GDX | gold-miners-etf-gdx |
| GDXJ | junior-gold-miners-etf-gdxj |
| SMH | semiconductor-etf-smh |
| REMX | rare-earth-strategic-metals-etf-remx |

**Bash download pattern:**
```bash
curl -s -c /tmp/vc.txt "https://www.vaneck.com/us/en/investments/{slug}/holdings/" -o /dev/null
sleep 1.5
curl -s -b /tmp/vc.txt -L "https://www.vaneck.com/us/en/investments/{slug}/downloads/holdings/" -o holdings.xlsx -w "%{http_code}"
```

## Global X — CSV (dated URL)

**Pattern:** `https://assets.globalxetfs.com/funds/holdings/{ticker}_full-holdings_{YYYYMMDD}.csv`

**Format:** CSV. 3-line preamble (fund name, date, header). Header at line 3: `% of Net Assets,Ticker,Name,SEDOL,Market Price ($),Shares Held,Market Value ($)`. Use `lines[2:]` to skip preamble.

**Confirmed working:** URA, SIL, LIT, COPX (and likely BOTZ, etc.)

**Date strategy:** Try yesterday first (today's may not be published). Fall back 1-14 days. Use `20260701` as known working date.

**Parse pattern:**
```python
lines = data.decode('utf-8').strip().split('\n')
reader = csv.DictReader(lines[2:])  # skip 3-line preamble
for row in reader:
    t = row.get('Ticker', '').strip()
    w = row.get('% of Net Assets', '0')
```

## ARK Invest — CSV (daily snapshot)

**Pattern:** `https://assets.ark-funds.com/fund-documents/funds-etf-csv/{ETF_NAME}_{TICKER}_HOLDINGS.csv`

**Format:** CSV. Header: date,fund,company,ticker,cusip,shares,market value ($),weight (%). Weight has `%` suffix.

**ETF names (confirmed):** `ARK_INNOVATION_ETF` (ARKK). ARKX renamed to "ARK Space & Defense Innovation ETF" — exact URL name not verified.

## YieldMax — CSV (static URL)

**Pattern:** `https://yieldmaxetfs.com/wp-content/uploads/funds/{TICKER}/TidalFG_Holdings_{TICKER}.csv`

**Format:** CSV. Columns: Date,Account,StockTicker,CUSIP,SecurityName,Shares,Price,MarketValue,Weightings,NetAssets,SharesOutstanding,CreationUnits. StockTicker may contain option symbols (COIN + strike/expiry as concatenated string). Weightings has `%` suffix.

**Confirmed:** MSTY, CONY.

## ProShares — Master CSV (all funds in one file)

**Pattern:** `https://accounts.profunds.com/etfdata/psdlyhld.csv?fund={TICKER}`

**Format:** CSV. Master file containing ALL ProShares funds (~20K rows). Filter by `Fund Ticker` column. Security Ticker at col 3. Market Value at col 10. Compute weights from market values per fund.

**Confirmed:** BITO.

## Volatility Shares — XLS (old binary format)

**Pattern:** `https://www.volatilityshares.com/download-holdings-usbanks.php?fund={ticker}`

**Format:** XLS (old binary, NOT XLSX). Use `xlrd`, not `openpyxl`.

**Confirmed:** BITX.

## Direxion — CSV (some require referrer)

**Pattern:** `https://www.direxion.com/holdings/{TICKER}.csv`

**Format:** CSV. Some tickers require Referer header or cookies.

**Single-stock ETFs (mega-cap only):** TSLL/TSLS (TSLA), AAPU/AAPD (AAPL), NVDU/NVDD (NVDA), MSFU/MSFD (MSFT), etc.
**No single-stock ETFs exist for:** CEP, BKKT, AI, BTBT, ACHR, BYND, ACB.
**Third-party alternatives:** BBAI → BAIG (Leverage Shares 2X Long), APLD → APLX (Tradr 2X Long).

## Web-Only / Non-downloadable

| Ticker | Issuer | Issue |
|--------|--------|-------|
| URNM | Sprott | Quarterly PDF only (sprottetfs.com). No daily CSV. |
| SILJ | Amplify ETFs | JS download button on page, no static URL. Holdings table is scrapable. |
| QTUM | Defiance | JS download button on page, no static URL. |
| WGMI | CoinShares | No holdings export — product page only. |
| GraniteShares | GraniteShares | No direct CSV URL found. |

## FINRA Short Interest (Biweekly)

**URL:** `https://cdn.finra.org/equity/otcmarket/biweekly/shrt{YYYYMMDD}.csv`

**Format:** Pipe-delimited CSV. Header: `accountingYearMonthNumber|symbolCode|issueName|issuerServicesGroupExchangeCode|marketClassCode|currentShortPositionQuantity|previousShortPositionQuantity|stockSplitFlag|averageDailyVolumeQuantity|daysToCoverQuantity|revisionFlag|changePercent|changePreviousNumber|settlementDate`

**Coverage:** ALL equities (NYSE, NASDAQ, ARCA, BZX, OTC) in a single file. ~22K rows, ~2.2MB.

**Key field:** `currentShortPositionQuantity` = short interest in shares.

**Frequency:** Biweekly (15th and last day of month).

## CIRO (Canadian IIROC) — Cloudflare-gated

**URL pattern:** `https://www.ciro.ca/sites/default/files/epubs/CSPR/{YYYYMMDD}_CSPR_Report.xls`

**Format:** XLS. Columns: Security Name, Symbol, Exchange, Shares Short, Net Change.

**Access:** Cloudflare blocks non-browser clients. Manual browser download required. TSX ticker for CGC is WEED, not CGC.

**Alternative sources:** FINRA (NASDAQ-listed SI), shortdata.ca, TMX Money.