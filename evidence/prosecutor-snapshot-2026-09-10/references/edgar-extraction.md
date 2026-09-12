# SEC EDGAR iXBRL Filing Extraction

## Source: C4_PIPELINE_FIX session (2026-07-07)

### Problem
v3 extractor failed to get filing text for 39/44 DEFM14A rows because:
1. Only tried `ix?doc=` links from index page (most filings use plain `<a href>` links)
2. Only tried filing-agent CIK path (`adsh[:10]`), never issuer CIK
3. `cik_override=None` skipped the issuer-CIK code path entirely

### Working Pattern (Ledger #12 variant)

```
Index page URL = https://www.sec.gov/Archives/edgar/data/{CIK}/{adsh_no_dashes}/{adsh}-index.htm

1. Filing-agent CIK = adsh[:10].lstrip("0") — use this for index page access
2. Index page may use EITHER ix?doc links OR plain <a href> links to document
   - Parse BOTH: re.findall(r'ix\?doc=(/[^"&\s]+\.(?:htm|html))', ...)
   - And: re.findall(r'href="([^"]+\.(?:htm|html))"', ...)
   - Also try .txt versions
3. Build doc URL from the link path
   - If absolute (/Archives/...): prepend https://www.sec.gov
   - If relative (filename only): prepend /Archives/edgar/data/{CIK}/{adsh_nd}/
4. Expected: 200 with >1K chars containing merger/filing text
```

### CIK Handling
- Filing-agent CIK (from adsh prefix) works for INDEX PAGE access
- Filing text may live under ISSUER CIK directory (different from filing agent)
- The href link from filing-agent's index page includes the correct issuer CIK path
- EFTS (efts.sec.gov) returns issuer CIK but is intermittently down (403/500)
- Fallback: use href links from filing-agent index page — always correct

### ix?doc vs href Links
- ix?doc links: used in iXBRL/inline XBRL filings. Form: `ix?doc=/Archives/edgar/data/{CIK}/{adsh}/{filename}.htm`
- href links: traditional HTML filings. Form: `<a href="/Archives/edgar/data/{CIK}/{adsh}/{filename}.htm">`
- Both work. Always parse BOTH.

### Pacing and Headers
- User-Agent REQUIRED: `research <b.en@prosecutor.research>`
- Without: HTTP 403 (SEC Akamai firewall)
- Archive server: ≥1.0s between requests (empirically passes)
- EFTS: ≥0.3s between requests (when EFTS is up)
- Both servers may return intermittent 503 — retry with 2^a backoff

### Date Extraction from Filing Text (DEFM14A)
- Vote/meeting dates: search whole document for "be held on/DATE", "meeting on DATE", "DATE at"
- Outside/termination dates: keyword-spread approach — scan ENTIRE doc for termination keywords (not just the "Article" section)
  - Keywords: "outside date", "termination date", "consummated by", "may be terminated", "not consummated", "has not been consummated"
  - Grab ±18 lines of context around each keyword hit
  - Patterns: "not consummated by DATE", "has not been consummated by DATE", "business combination is not consummated on or before DATE"
- Sentence-boundary signing rejection: reject dates in sentences containing "signed", "executed", "entered into", "dated as of"

### Common Failures
- 404: guessed filename (always read filename from index page)
- 403: missing User-Agent header
- 503: SEC archive server intermittent — retry with backoff
- No ix?doc links: filing uses plain href (parse both types)
- No dates in termination section: some DEFM14A filings for SPAC extensions have meeting dates but no outside date clause (8-K may have it instead)
