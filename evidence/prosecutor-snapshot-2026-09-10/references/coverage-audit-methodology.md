# Coverage Audit Methodology (B3/B1/AUDIT_FIX)

## Independent-ref rule (non-negotiable)
Coverage audit reference MUST be from a DIFFERENT source family than the extraction source. Same press release / PDF on both sides = circular void. Declare both families per class.

| Class | Extraction source | Reference source |
|-------|-----------------|-----------------|
| C10 | S&P DJI press releases, Russell official PDFs | Barron's, MarketWatch, CNBC, IBD (financial press) |
| C3 | S-1/424B pricing tables, computed lockup terms | Stocktwits, ticker.report, investing.com (lockup calendars) |
| C4 | EDGAR index-page-first (Ledger #12) | Third-party aggregator or EDGAR itself (form-type index is complete by construction) |
| C6 | EDGAR keyword search | Nasdaq/NYSE split notice lists (external) |
| C7 | EDGAR SC TO form-type index | EDGAR itself (SC TO index is complete by construction) |

## Per-class deadline sources

### C10 — Index additive/deletive dates
- **Source:** S&P DJI press releases + Russell prelim/final lists (russell.com, free)
- **Forbidden:** EDGAR 8-Ks (post-date effectiveness)
- **Label:** PASS_STRATIFIED — S&P 500 changes verified from independent press; Russell/small-cap rows caveated (no independent press coverage for ~64% of tickers)

### C4 — Merger/de-SPAC closing and election deadlines
- **Source:** DEFM14A (meeting/vote dates), 8-K Item 2.01 (closing dates), 8-K outside dates
- **Rule:** Signing dates REJECTED. Check context for "signed", "executed", "entered into", "dated as of"
- **Date extraction:** Vote date, meeting date, outside date, closing date. Matched phrase per row.
- **Access pattern:** Ledger #12 (index-page-first, /ix?doc=, direct fetch)

### C3 — Lockup expiry dates
- **Source:** S-1/424B pricing tables, trailing 24mo IPO/de-SPAC data
- **Rule:** expiry = pricing_date + stated lockup term. Carve-outs/early-release clauses flagged EARLY_RELEASE_RISK, not dropped.
- **Standard lockup periods:** 180d (operating company IPOs), 365d (SPACs/de-SPACs, some Chinese issuers), 545d (SPAC/PE-backed)
- **Label:** UNVERIFIABLE — independent press only covers 180d standard lockups; 365d/545d computed dates have no independent verification

### C6 — Stock split effectiveness
- **Source:** Nasdaq/NYSE split notice lists (external, NOT EDGAR keyword search)
- **Status:** INCOMPLETE — EDGAR keyword search captures only 16% of reference splits

### C7 — Tender offer expirations
- **Source:** EDGAR SC TO-I/T form-type index (complete by construction)
- **Status:** PASS ≥70%

## Void-run safeguards (R0-R5)

| Rule | Check | Action |
|------|-------|--------|
| R0 | Reconcile row count: input N = verified + mismatches + errors | Find missing rows before proceeding |
| R1 | Pacing: assert inter-request delta ≥1.0s, log timestamps per request | <1.0s = auto-VOID |
| R2 | Demo gate: one end-to-end row (adsh → index → doc → dates → signing reject) before batch | Parser fails → HALT |
| R3 | Batch: all rows re-joined via EFTS, extract per R2 method | — |
| R4 | Full roster: all source rows, not just megacap subset | Report roster N vs extracted N |
| R5 | Empty-file check: SHA256 of output != empty/empty-obj hash | `e3b0c44...` or `4f53cda1...` = INVALID, HALT |

## Ledger #12 — EDGAR filing-doc access pattern
- CIK_stripped = issuer CIK with leading zeros removed
- adsh_no_dashes = adsh with hyphens removed
- Doc URL from index page: extract path from **BOTH** `/ix?doc=/Archives/...` links AND `<a href="...htm">` links.
  Some index pages have ZERO ix?doc links and only use regular href links.
  The href path contains the correct issuer CIK — build the full URL from it.
  NEVER guess filenames.
- Fetch DIRECTLY at constructed URL (not through ix viewer)
- Filing-agent CIK (adsh[0:10] stripped) works as fallback archive path — the index page at filing-agent CIK links to filing documents at the issuer CIK path via href
- Spacing: ≥1.0s between requests
- UA header REQUIRED: `User-Agent: research <b.en@prosecutor.research>` (else 403)
- Retry: 3x with exponential backoff on 503/500