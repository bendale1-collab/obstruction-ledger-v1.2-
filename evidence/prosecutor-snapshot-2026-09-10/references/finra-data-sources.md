# FINRA Data Sources

**Discovered:** 2026-07-09
**Source:** M2/H1/H2 pipeline sessions

## Biweekly Short Interest (ALL equities)

Best source for full-market short interest — covers NYSE, NASDAQ, BZX, ARCA, AND OTC in a single file:

- **URL pattern:** `https://cdn.finra.org/equity/otcmarket/biweekly/shrt{YYYYMMDD}.csv`
- **Date format:** Settlement date (e.g. 20260615 = June 15, 2026)
- **Format:** Pipe-delimited CSV (`|`), NOT comma-separated
- **Header columns:** `accountingYearMonthNumber|symbolCode|issueName|issuerServicesGroupExchangeCode|marketClassCode|currentShortPositionQuantity|previousShortPositionQuantity|stockSplitFlag|averageDailyVolumeQuantity|daysToCoverQuantity|revisionFlag|changePercent|changePreviousNumber|settlementDate`
- **Key column:** `currentShortPositionQuantity` = short interest in shares
- **Coverage:** ~22,000+ tickers per settlement date. File is ~2.1MB.
- **Exchange codes:** A=NYSE, Q=NASDAQ, H=BZX, E=ARCA, R=NYSE/NASDAQ listed, S=OTC
- **Access:** Public, no API key. Requires User-Agent header.

```python
import csv, io, urllib.request
url = f"https://cdn.finra.org/equity/otcmarket/biweekly/shrt{date_str}.csv"
req = urllib.request.Request(url, headers={"User-Agent": "research <email>"})
resp = urllib.request.urlopen(req)
reader = csv.DictReader(io.StringIO(resp.read().decode()), delimiter="|")
for row in reader:
    ticker = row["symbolCode"]
    si_qty = int(row["currentShortPositionQuantity"])
```

## Daily Short Sale Volume (Reg SHO)

Total and short-sale volume per ticker per day, by facility:

- **Consolidated:** `https://cdn.finra.org/equity/regsho/daily/CNMSshvol{YYYYMMDD}.txt`
- **Per-facility:** `https://cdn.finra.org/equity/regsho/daily/F{XXX}shvol{YYYYMMDD}.txt` where XXX = NQC (BX), NRA (Arca), NSQ (NASDAQ), NYX (NYSE), ORF (Other)
- **Format:** Pipe-delimited. Columns: Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market
- Old URL `regsho.finra.org/regsho-ShortVolume.txt` redirects (dead). Use CDN URLs above.

## CIRO (Canadian) Short Interest

- **URL pattern:** `https://www.ciro.ca/sites/default/files/epubs/CSPR/{YYYYMMDD}_CSPR_Report.xls`
- **Blocks automated access** with Cloudflare. Must use browser.
- **ACB confirmed** present in CIRO data (LSL_REPORT.csv). CGC TSX ticker is WEED.
- **Alternative (US-only):** FINRA covers ACB and CGC on NASDAQ.
- **Verdict:** UNOBSERVED from automated pipeline. Manual browser download required.