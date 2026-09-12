# C8 — Warrant Redemption Search (EFTS Protocol)

## When to use

Searching for warrant redemption notices to build C8 calendar events. This is a class of SEC 8-K filing where a company calls public warrants for cashless or cash redemption, creating a forced-delivery deadline.

## EFTS Query

```
GET https://efts.sec.gov/LATEST/search-index
  ?q=%22warrant+redemption%22+OR+%22notice+of+redemption%22
  &startdt=YYYY-MM-DD
  &enddt=YYYY-MM-DD
  &limit=100
```

- `%22` = URL-encoded double quotes for phrase search
- `+` = URL-encoded space
- `OR` = boolean OR operator
- The phrase "warrant redemption" returns ~6K+ hits per year. Use monthly queries to stay under the 10K limit.
- EFTS may return 500 errors for complex queries. Fall back to simpler queries and filter client-side.

## Filtering

Exclude forms 4, 5, 3 (insider trading). Keep only 8-K, 8-K/A, 25, and forms that have `items` containing `3.02` (unregistered equity) or `8.01` (other events — warrant redemption).

## Date Extraction

The redemption date is found in the filing text near phrases like:
- "the redemption date will be [DATE]"
- "will redeem all outstanding warrants on [DATE]"
- "warrants will expire at 5:00 p.m. on [DATE]"
- "public warrants that remain outstanding on [DATE]"

**iXBRL handling**: Filing text may be in iXBRL format (inline XBRL). Strip HTML/xml tags (`re.sub(r'<[^>]+>', ' ', text)`) before searching for dates. The iXBRL header contains XML metadata that matches keyword searches but has no dates — the actual content is in the body.

## Filing Access

Index page: `https://www.sec.gov/Archives/edgar/data/{CIK}/{adsh_nd}/{adsh}-index.htm`

Document links: Parse both `ix?doc=` and `<a href="...">` from index page. The primary 8-K filing is usually the iXBRL doc (ix?doc path). The exhibit containing the warrant notice is often an `ex-` file.

## R1-R4 Classification Rules

- **R1**: Classify on the REDEMPTION DATE (the deadline for warrant holders to act), not the notice date or filing date
- **R2**: The sentence boundary must contain both a date AND a redemption keyword to count as a deadline
- **R3**: Reject dates in sentences containing "signed", "executed", "entered into", "dated as of" (signing dates, not deadlines)
- **R4**: Use CIK from the `display_names` field for ticker extraction. Some filings show multi-ticker formats like "Company (TICKER1, TICKER2, TICKER3)" — parse the first ticker.

## Known C8 Events (from T1 backfill, 2022-2026)

| Ticker | Redemption Date | Accession | Filing Date |
|--------|--------------|-----------|-------------|
| BOWL | 2022-05-19 | 0000950142-22-001682 | 2022-05-19 |
| NRGV | 2022-08-01 | 0001213900-22-046440 | 2022-07-01 |
| MIR | 2024-05-20 | 0001213900-24-038414 | 2024-04-18 |
| ROIV | 2024-06-03 | 0001213900-24-045605 | 2024-05-29 |
| RDW | 2024-06-20 | 0001213900-24-054011 | 2024-06-06 |
| PLSE | 2024-07-03 | 0001437749-24-038302 | 2024-12-26 |
| ASTS | 2024-09-27 | 0001493152-24-035008 | 2024-09-04 |
| SMR | 2024-11-19 | 0001213900-24-093056 | 2024-11-19 |
| LUNR | 2025-02-04 | 0001844452-25-000005 | 2025-02-04 |
| GRND | 2025-02-24 | 0001213900-25-005584 | 2025-01-23 |
| AVPT | 2025-06-27 | 0001213900-25-056614 | 2025-06-06 |
| HYAC | 2026-04-08 | 0001104659-26-043241 | 2026-04-14 |
| RMIX | 2026-04-08 | 0001104659-26-043237 | 2026-04-14 |
| PCT | 2026-06-17 | 0001193125-26-076587 | 2026-02-26 |

## Registry Schema

```json
{
  "version": "C8_REGISTRY_V1",
  "events": [{
    "ticker": str,
    "redemption_date": "YYYY-MM-DD",
    "accession": str (adsh),
    "form": "8-K",
    "filing_date": "YYYY-MM-DD",
    "class": "C8",
    "source": "T1_BACKFILL"
  }]
}
```

## Pitfalls

- **EFTS 10K limit**: Annual queries for "warrant redemption" exceed 10K hits. Split into monthly or quarterly queries.
- **Null ticker**: ~50% of display_names use multi-ticker format like "Company (TICKER1, TICKER2, TICKER3)" — the ticker regex must be updated to handle this.
- **SPAC warrants**: Many warrant redemption filings are SPAC-related (pre-merger). These are SPAC dissolution events, not operating company deadlines. Check if the company is a SPAC (ticker ends in U, WT, etc.) vs operating company.
- **iXBRL false positives**: The XML header contains "warrant" and "redemption" keywords. Strip all tags before searching.
- **Warrant issuance vs redemption**: Some filings describe the issuance of warrants, not the redemption. The phrase "warrants issued on [DATE]" is a common false positive.