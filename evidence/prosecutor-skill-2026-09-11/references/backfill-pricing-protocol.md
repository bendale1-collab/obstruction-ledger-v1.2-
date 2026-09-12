# Backfill Pricing Protocol ("PRICE, don't build")

**Context:** When extending a data panel backwards in time, the first
step is always to price the cost — not to build. The user's repeat
instruction: "PRICE, don't build."

## Pricing Checklist

1. **Source availability** — Before estimating time/cost, verify the
   data source exists for the target years. SEC FSNDS data commences
   2015Q1 (no earlier data from this source). Older SEC FSDS (without
   notes) existed from 2009 but uses a different schema and pipeline.

2. **One-query sample** — Download ONE representative quarter from
   the target era and verify format compatibility:
   - HTTP status code (200=exists, 403=bot-blocked, 404=doesn't exist)
   - File size (actual data vs 404 stub)
   - Column schema (check for dcml, required fields)
   - Row structure (same table names, same primary keys)

3. **Volume estimate** — Count target quarters × sample size ×
   processing time per quarter. Report in GB and estimated compute
   minutes. The D-33 estimate: 16 qtrs × ~450MB = ~7.2GB.

4. **DCML check** — The dcml (decimal) column in num.tsv determines
   whether full degradation computation is possible. If dcml absent
   in num.tsv, degradation-based metrics stay at the current panel
   boundary while raw values may still be extractable.

5. **Report, don't build** — Output the price estimate. Do not begin
   the backfill unless explicitly directed. The user decides whether
   the cost/benefit clears their threshold.

## Kill Criteria

- Source returns 404 for target years → INF (data unavailable)
- Source returns 403 with proper research User-Agent → UNAVAILABLE
  (documented: bot-blocked, not absent)
- File retrieved but incompatible schema → PRICED(conversion cost)
- Compatible → PRICED(volume-estimate)