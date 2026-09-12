# Disk-cache conflation & substrate-exhaustion discipline

**C-19 class defect:** an executor who conflates "not on this disk" with "does not exist in the world" commits a defect against the procedure, not a finding about the world.

## Rule

When a substrate appears exhausted — no data in the cache, no matching fields in the database, no return from an API call — the verdict is "this substrate returned nothing," not "the thing does not exist." Before declaring any route exhausted, enumerate every FREE substrate reachable from the registered query:

1. **Wayback Machine CDX** — historical snapshots of the SAME file at DIFFERENT URLs the file formerly lived at. SEC company_tickers.json moved from `sec.gov/data/` to `sec.gov/files/` between 2016 and 2020. The old URL had 3 Wayback snapshots; one yielded 1,191 dead CIK mappings the current file lacked.
2. **Alternate endpoints** — not just the current-snapshot API. For SEC entity mapping: companyfacts, browse-edgar Atom feed, EDGAR full-text search — these may carry data the submissions API does not (for dead entities, none carry tickers — but that is a finding after testing, not an assumption).
3. **Filing-history forms** — death paperwork (Form 25, 25-NSE, 15, 8-A) may carry a field the primary filing type (10-K, 8-K) dropped. In the DPS case: they don't carry tickers either — but that was discovered by FETCHING them, not assumed.
4. **yfinance availability** — for recovered tickers, check whether Yahoo has price history. 33% of dead symbols have data; 67% do not. Until checked, the claim "ticker recovered but no return data exists" is UNVERIFIED_ABSENCE.

## Documentation requirement

Every negative claim must carry a search-width annotation: how many independent substrates returned nothing, what each was, and what was NOT checked. The annotation makes the negative falsifiable and prevents C-19.

## D-29/D-30 pattern (2026-08-14)

Original wall declaration: "pre-2019 machine-readable ticker data does not exist in SEC filings on disk" — verified against 8-K cache (84GB, 20K files) and FSNDS sub.txt (2015q1, 2019q1). WALL declared. User reopened: "The wall statement was true of substrates checked, not of the world. Three free routes were never tested."

Routes added and tested:
- Route 1 (Wayback 2016 company_tickers.json): **39.9% dead coverage** (1,222/3,063). New: 1,191 CIKs.
- Route 2 (Death-paperwork scan): **~0%** (registration forms don't carry tickers either).
- Route 3 (Cross-validation): **0% effective error rate**.
- Route 4 (yfinance check): **33%** of recovered dead symbols have data; 67% return-unavailable.

Result: wall stands — but with COMPLETE substrate coverage, not a guess. The $27 EODHD option was not purchased because the selection characterization (D-30) showed the recovered subset differs from the unmapped by 2-3x on the signal dimension — test void.

## See also

`pre-registered-research-executor/references/execution-pitfalls-v2.8.md` P19 (wall-declaration discipline), P20 (API body-check), P22 (Wayback CDX technique), P23 (selection characterization).