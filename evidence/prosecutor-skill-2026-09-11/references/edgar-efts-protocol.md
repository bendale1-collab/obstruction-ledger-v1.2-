# EFTS SEC EDGAR Full-Text Search Protocol

## URL format
```
GET https://efts.sec.gov/LATEST/search-index
Parameters:
  q={query}     — full-text search query
  startdt={date} — start date (YYYY-MM-DD)
  enddt={date}   — end date (YYYY-MM-DD)
  cik={CIK}      — optional CIK filter (10-digit without leading zeros)
```

## Query construction

Rules tested with EFTS (Elasticsearch-backed):
- **Quoted phrases**: `%22record+date%22` — URL-encode the double quotes as `%22` and spaces as `+`. This is critical — passing raw double quotes in the URL fails.
- **AND by default**: Space-separated terms = AND. `q=TLRY+%22record+date%22` matches filings containing TLRY AND "record date".
- **OR**: Use `+OR+` (URL-encoded) between alternatives. Complex boolean queries may fail silently (return 0 hits). Prefer multiple narrow queries over one complex OR query.
- **Complex boolean with parentheses FAILS → 0 hits**: Queries like `q=%22BYND%22+AND+(%22record+date%22+OR+%22expiration%22)` return 0 hits. The parenthesized OR expression is not supported. Always decompose into separate single-phrase queries and filter results client-side. Testing: ticker+phrase works (`%22AAPL%22+%22record+date%22`); adding boolean operators or parentheses breaks silently.
- **Form type search**: The query searches doc_text, not the form field. Searching `q=8-K` finds documents mentioning "8-K" in the text — but so do many other forms. Prefer searching ticker + trigger phrase, then filter by form type from the response.
- **category parameter**: `category=form-cat1` for 8-K/10-K/10-Q corporate filings, `form-cat2` for registration statements, `form-cat3` for investment company filings. Works reliably.
- **Server reliability**: EFTS returns sporadic HTTP 500 errors ("Internal server error"). Retry with 2-second backoff. When EFTS is down, use EDGAR index pages directly (www.sec.gov/Archives/edgar/data/{CIK}/{adsh_no_dashes}-index.htm).

## Response structure
```json
{
  "hits": {
    "total": {"value": N, "relation": "eq"},
    "hits": [{
      "_id": "{adsh}:{filename}",
      "_source": {
        "adsh": "0001193125-21-089752",
        "form": "8-K",
        "file_date": "2021-03-22",
        "display_names": ["Company Name (TICKER) (CIK 0000123456)"],
        "items": ["1.01", "8.01", "9.01"],
        "file_description": "description text",
        "ciks": ["0000813828"],
        "period_ending": "2021-03-22"
      }
    }]
  }
}
```

## Filtering false positives

- **Form 4/3/5** — insider trading filings. These mention "record date" (for option grants) but are NOT corporate actions. Always exclude: `if f in ('4','3','5','497','NPORT-P','N-CSR','N-CSRS','CORRESP','UPLOAD'): continue`
- **Company ownership**: Use `display_names` field to verify filing is FROM the target company. Parse `(TICKER)` from the display name string. IMPORTANT: display_names show the CURRENT ticker, so companies that changed tickers (e.g., OSTK→BYON) will show the new ticker. For past tickers, use CIK matching (R4).
- **Form variants**: Include 8-K/A, 8-KT, 424B5/A, etc. Check `form.startswith('8-K')` rather than exact match.
- **Multiple tickers in display_name**: Some filings show `"Company Name (TICKER1, TICKER2, TICKER3) (CIK NNN)"` — the regex `\((\w+)\)` only captures the LAST ticker. Use regex `\(([\w,\s-]+)\)` and split on comma to get all tickers.

## Full-text document access

Filing document URL pattern:
```
https://www.sec.gov/Archives/edgar/data/{CIK}/{adsh_no_dashes}/{filename_from_id}
```

Where:
- CIK: from `_source.ciks[0]` (strip leading zeros for non-padded version)
- adsh_no_dashes: from `_source.adsh` (e.g., `0001193125-21-089752` → `000119312521089752`)
- filename: from `_id` field (e.g., `0001193125-21-089752:d162565d424b5.htm` → `d162565d424b5.htm`)

Example:
```
curl -s -H 'User-Agent: research <b.en@prosecutor.research>' \
  'https://www.sec.gov/Archives/edgar/data/1326380/000119312520312805/d67321d424b5.htm'
```

Required header: `User-Agent: research <b.en@prosecutor.research>` (SEC blocks requests without it). The EDGAR filing index page at `.../0001193125-20-312805-index.htm` lists all documents in the filing.

**Index page has two link types**: Always parse BOTH `ix?doc=` links AND plain `<a href>` links:
```python
# ix?doc links (iXBRL/inline XBRL filings)
ix_links = re.findall(r'ix\?doc=([^"&\s]+\.(?:htm|html))', index_html)
# href links (traditional HTML filings)
href_links = re.findall(r'href="([^"]*\.(?:htm|html))"', index_html)
# Filter out index-page links
href_links = [h for h in href_links if 'index' not in h.lower()]
```

Many filings ONLY have `href` links (no `ix?doc`). Always parse both.

## Deadline date extraction from filing text

For R1 compliance, extract the specific deadline/settlement date from filing text. Use regex patterns:

```python
import re
# Common date formats in SEC filings
dates = re.findall(r'(January|February|March|April|May|June|July|August|September|October|November|December) \d+, 202\d', text)
# Check for closing/settlement/record date context around each date
for kw in ['closing', 'settlement', 'distribution date', 'record date', 'expiration']:
    matches = [l for l in text.split('\n') if kw.lower() in l.lower()]
```

Key phrases by filing type:
- **424B5 offering**: "The offering is expected to close on [DATE]" or "settlement ... will occur on the second trading day following" (T+2 for ATM)
- **8-K dividend**: "record date of [DATE]" (look in items 3.03/5.03)
- **S-1 lockup**: "lock-up agreements" or "180-day lock-up period expiring on [DATE]"
- **SC TO tender**: "the tender offer will expire at [DATE]"
- **8-K merger**: "the merger became effective on [DATE]"
- **8-K warrant redemption**: "the Company issued a press release announcing the redemption of all of its outstanding [warrants] on [DATE]"
- **8-K item 3.02**: Unregistered equity sales — often contains warrant redemption or conversion dates

## iXBRL parsing note

Most 2020+ EDGAR filings are iXBRL (inline XBRL). The raw HTML is wrapped in XBRL tags (`<ix:nonNumeric>`, etc.) that obscure the human-readable text. Simple `strip_html_tags()` or `BeautifulSoup.get_text()` may still leave XBRL noise. For date extraction, search for the XBRL-tag-stripped text using regex on keywords 200+ characters apart, then use the surrounding text for context. Expect `&#160;` (non-breaking space) and `&#8220;`/`&#8221;` (smart quotes) as HTML entities in SEC filings.

## C8 — Warrant Redemption Filing Search Pattern

For C8 class (warrant redemption events), search EFTS for the phrase `"notice of redemption"` in 8-K filings. The standalone phrase search works better than `"notice of redemption" AND "warrant"` (which can return 0 hits due to EFTS boolean limitations). Filter results to form types starting with `8-K`. Extract the redemption date from text near keywords "redemption date", "will expire", "expiration date". Sample confirmed C8 events: BOWL (2022-05-19), ASTS (2024-09-27), LUNR (2025-02-04), GRND (2025-02-24).