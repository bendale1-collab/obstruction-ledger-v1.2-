# B3 Coverage Audit Methodology (for PROSECUTOR framework)

## When to load
Any quantitative research project requiring a coverage audit: measuring how many known reference events the pipeline calendar captured. Gates all hit-rate claims — classes <70% capture are INCOMPLETE, excluded from future denominators.

## Three-step audit

### A1 — Build calendar
Append-only jsonl with discovered_date timestamps, hash-chained MANIFEST. Schema mandatory fields per class (ticker, class, filing_date, deadline_date, adsh, source, CIK). No deadline_date or accession/URL → row rejected. Issuer CIK via company_tickers.json, never filing-agent CIK.

**Per-class source corrections (banked):**
- C10: Russell/S&P official lists, NOT EDGAR 8-K (8-Ks post-date effectiveness)
- C4: Outside dates from merger agreements, NOT signing dates
- C3: Lockup expiries computed from S-1 pricing tables (pricing_date + stated term), NOT EDGAR keyword search. Trailing 24 months of IPO/de-SPAC data.
- C1,C2,C5,C6,C7,C8,C9: EDGAR form-type index or keyword search

### A2 — Reference sets (per class, three types)
1. **COMPLETE by construction** — form-type index (C7: SC TO-I/T captures every tender offer filing ever made → reference is the index itself)
2. **KNOWN-COMPLETE external list** — S&P press releases (C10), exchange split notices (C6), lockup calendars (C3)
3. **REFERENCE_PARTIAL** — no external complete reference (C1,C2,C4,C5,C8,C9). Audit via form-type index recall only. Label REFERENCE_PARTIAL; excluded from future hit-rate denominators

### A3 — Score
Capture % = calendar rows matching reference / reference rows.
<70% → INCOMPLETE flag. Class excluded from all future hit-rate denominators until fixed.

Report per-class: reference N, captured N, %, flag, top-3 miss reasons with specific gaps.

## Critical rule: independent-reference requirement
The reference MUST come from a DIFFERENT source family than the calendar extraction. Evidence from AUDIT_FIX session (2026-07-06):
- R1v2 initial C10 audit showed 100.0% → but calendar used S&P/Russell official lists AND reference used the same sources → self-referential, void
- Re-audit with independent press (Barron's, MarketWatch, CNBC) → 23 independent events confirmed, all in calendar → true PASS
- R1v2 initial C3 audit showed 100.0% → calendar used S-1 tables AND reference used same S-1 derived data → self-referential
- Re-audit with independent lockup news (stocktwits, ticker.report) → 4 events found, 3/4 in calendar → 75%, structurally weak but honest

## Common reasons for <70% capture

| Class | Typical Miss Reason | Fix |
|---|---|---|
| C10 | Only S&P 500 events built; MidCap/SmallCap missing | Add full S&P index press release coverage |
| C6 | EDGAR keyword search finds split MENTIONS, not EFFECTIVE dates | Build from Nasdaq/NYSE split notice API |
| C3 | Lockup expiries silent — no EDGAR filing at expiry | Compute from S-1 pricing tables (spec approach) |
| C1/C2/C5/C8/C9 | Keyword gap, exhibit-only dates, CIK resolution failures | R1v2 deadline extraction from filing text |
| C7 | UNRESOLVED_FUND tickers from non-traded BDCs | Structurally unresolvable — document gap, don't pad |

## C4 block evidence (2026-07-06 session)
**Subagent claim:** "SEC rate limiting after ~5 requests/min"
**Actual finding:** HTTP 200 at 0.1s intervals with proper User-Agent. The 403 comes from MISSING UA header. The 404 comes from WRONG FILENAMES (guessed doc filename != actual filename). EFTS itself: no rate limiting observed at typical research density. Fix is the index-page-first pattern (get doc URL from index HTML, don't guess filenames).

## B1 Capture Hook pattern
Build: on any G1 candidate flag (calendar insert, class C1-C10, next-60d deadline) → append ticker to live capture list (iBorrowDesk daily pull + tick-236 daily snap). Dedupe by ticker. Log add_date + trigger_event per name. Never remove names (append-only; exits flagged INACTIVE, capture continues 30d post-deadline then stops). Output: capture_list.json + hash chain.