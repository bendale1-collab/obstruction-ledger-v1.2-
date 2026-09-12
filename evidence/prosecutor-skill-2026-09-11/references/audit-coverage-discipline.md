# Audit Coverage Discipline — per-session additions (Jul 2026)

## Independent-ref rule
Coverage audit reference MUST be from a DIFFERENT source family than extraction.
Same press release / PDF on both sides → circular void. Declare both per class.

| Extraction source | Independent ref source |
|---|---|
| S&P/Russell official lists | Press (Barron's, CNBC, MarketWatch) |
| S-1 pricing tables | Lockup calendars (stocktwits, ticker.report, MarketBeat) |
| EDGAR form-type index | Third-party aggregator |

## Empty-file hash = INVALID
Check SHA256 before reporting:
- `e3b0c44...` = empty bytes
- `4f53cda1...` = empty JSON `{}`
- `0cea6b08...` = empty JSON `[]`

Any match → HALT. Empty output means the pipeline produced nothing — report that.

## Tables-only output
Deviations first line, then the table. Three numbers: Ref N, Cal N, Matched N.
Matched ≤ min(both). Never silently equal.

## Pacing ≥1.0s
SEC EDGAR archive: ≥1.0s between requests. `assert gap >= 1.0` in code with
timestamp logging. Void any run where runtime < rows × 1.0 × requests_per_row.

## C4 extraction (DEFM14A/8-K merger dates)
Pipeline: EFTS by adsh → verify CIK+ticker → index-page-first → dates → signing reject.

Three date types: vote_date (meeting), outside_date (termination), closing_date.
Signing rejection: scan ±250 chars for "signed"/"executed"/"entered into"/"dated as of".

EFTS may return different ticker than the file-path ticker → mismatch→DROP+log.

## C3 lockup expiry computation
Roster: stockanalysis.com/ipos or Nasdaq IPO calendar. Expiry = IPO_date + lockup_days.
Lockup periods: 180d (operating), 365d (SPACs), 545d (extended).
Only 180d gets press coverage — 365d/545d carry UNVERIFIED_CALENDAR caveat.
Flag EARLY_RELEASE_RISK where carve-out clauses found in S-1.