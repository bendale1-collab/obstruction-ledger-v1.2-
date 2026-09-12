# SEC EDGAR Trigger Proximity Test (T2/T2r/T2r2 Protocol)

**Class:** Cross-section trigger test within the PROSECUTOR framework.  
**Goal:** Is a mechanical-type SEC filing present within ±45d of a cohort event's onset, and does that filing contain a dated mechanical deadline?

## API: SEC EFTS Search

Base URL: `https://efts.sec.gov/LATEST/search-index`

Required header: `User-Agent: research <your-email>`

Parameters:
- `q={query}` — searches `doc_text` field (full-text). Simple ticker names work. Complex boolean (`OR`) is fragile — use separate queries.
- `startdt={YYYY-MM-DD}`, `enddt={YYYY-MM-DD}` — date range filter on `file_date`
- `cik={10d}` — optional CIK filter (does not always narrow correctly; prefer post-filter on `display_names`)

Response: Elasticsearch JSON. Hits in `hits.hits` array, each with:
- `_id` — includes the primary document filename
- `_source.form` — filing form type
- `_source.file_date` — filing date
- `_source.adsh` — accession number (use as `accession_no`)
- `_source.items` — 8-K item numbers (e.g. `["1.01", "8.01"]`)
- `_source.file_description` — short description
- `_source.display_names` — `["COMPANY (TICKER) (CIK ...)"]`

**Critical:** Filter by display_name containing `({TICKER})` to avoid false positives from ticker strings inside other companies' filings.  
**Edge case:** OSTK display_names show `(BYON)` after the 2023 ticker change. Manually include CIK 0001130713 for Overstock/OSTK/BYON.

## 8-K Item Classification for Mechanical Triggers

### Qualifying items (mechanical deadline exists)
| Item | Meaning | Example Event |
|------|---------|--------------|
| 1.01 | Material definitive agreement | Underwriting/offering agreement |
| 2.01 | Completion of acquisition/disposition | Merger close |
| 2.03 | Direct financial obligation | Debt/offering settlement |
| 3.02 | Unregistered equity sales | Direct offering |
| 3.03 | Material modification of rights | Dividend/split modification |
| 5.01 | Change in control | Merger close |
| 5.03 | Amendments to articles | Split/dividend authorization |
| 5.07 | Shareholder vote results | Merger vote approval |
| 8.01 | Other events (check desc for keywords) | Various |

### Non-qualifying items (generic, no trigger)
| Item | Meaning |
|------|---------|
| 2.02 | Earnings/results of operations |
| 4.01 | Change in cert accountant |
| 4.02 | Non-reliance on financials |
| 7.01 | Regulation FD disclosure |

**Rule:** `{2.02, 7.01}` alone → earnings/guidance, NOT qualifying.  
Items `{1.01}` alone or `{1.01, 8.01}` without a trigger keyword in `file_description` → generic, NOT qualifying.

## Frozen Classification Rules (R1-R4)

Apply in order:

**R1 — Classify on deadline date extracted from filing content.**  
Search filing text for: "The offering is expected to close on [Date]", "record date", "distribution date", "expiration date", "closing date".  
Access filing at: `https://www.sec.gov/Archives/edgar/data/{CIK}/{adsh_no_dashes}/{filename}`  
Use User-Agent header matching the EFTS search.  
Paste the matched phrase as evidence.

**R2 — Ex-ante constraint.**  
`filing_date <= onset_date`. Post-onset filings are NON-QUALIFYING (the filing cannot be causal if it occurs after the event).

**R3 — 424B3 resale shelves NON-QUALIFYING.**  
No settlement deadline (resale registrations).  
424B5 qualifies **only with a dated close** (e.g. "expected to close on August 14, 2020"). ATM program 424B5s ("at-the-market offering", continuous distribution, no single close date) are NON-QUALIFYING.

**R4 — Company-name filter.**  
Filter by display_names containing `({TICKER})`.  
Handle ticker changes (e.g. OSTK→BYON) manually by CIK.

## Filing Text Extraction Pattern

```
curl -s -H "User-Agent: research <email>" \
  "https://www.sec.gov/Archives/edgar/data/{CIK}/{adsh_no_dashes}/{filename}"
```

Decode as `latin-1` to handle HTML entities.  
Search for keywords: "closing", "settlement", "record date", "distribution date", "expected to close".  
Extract: calendar date + keyword context for evidence table.

Key sentence pattern for traditional offerings:  
`"The offering is expected to close on [Month] [Day], [Year]"`

## Fisher Exact Test

For the 2x2 table `[[treat_qual, treat_non], [att_qual, att_non]]`:

```python
import math
def fisher_p(a, b, c, d):
    log_p = (math.lgamma(a+b+1) + math.lgamma(c+d+1) +
             math.lgamma(a+c+1) + math.lgamma(b+d+1))
    log_p -= (math.lgamma(a+b+c+d+1) + math.lgamma(a+1) +
              math.lgamma(b+1) + math.lgamma(c+1) + math.lgamma(d+1))
    return math.exp(log_p)
```

## Output Contract

Per-event table with columns:
- Ticker, Onset, Qualifying (YES/NO), Filing Date, Extracted Deadline, Rule Rejection / Matched Phrase

Summary block:
- Treatments N/N qualifying (by construction)
- Attention N/N qualifying (per rules)
- Fisher 2x2 + p-value

**No verdict** — "human writes" is the end state.

## Reference Runs

- T2 (initial): over-permissive — 18/19 attended qualified, p=0.68 (non-significant)
- T2r (type-restricted): 11/19, p=0.024
- T2r2 (R1-R4 frozen): 1/17, p<0.00001
