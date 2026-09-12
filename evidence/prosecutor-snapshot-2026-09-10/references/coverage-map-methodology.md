# Coverage Map Methodology

**When to use:** When a directive requires a per-(ticker, year) resolution audit of shares-outstanding coverage across a multi-decade FTD ledger. Produced once per project rebuild; governs GATE 1 decisions.

## Concept

A coverage map is a flat table with one row per (ticker, year) pair. Each row records:
- `n_episodes` — number of FTD episodes for that ticker in that year
- `status` — one of `RESOLVED_SEC`, `RESOLVED_EODHD`, `SHARES_STALE`, `SHARES_UNAVAILABLE`
- `instrument_class` — `COMMON_evidenced`, `ETF_CEF_FUND`, `UNKNOWN_DEFAULT`
- `concept_tag` — the EDGAR or EODHD concept that resolved it (or why it failed)

## Required tables

| Letter | Table | Content |
|--------|-------|---------|
| A | Per-year 2004-2025 | Full-tape resolution rate by year |
| B | Window-restricted | 2013-2025 only + single summary % |
| C | Unresolved split | 3-way: COMMON_evidenced / ETF_CEF_FUND / UNKNOWN_DEFAULT |
| D | Tradeable-universe overlap | C8+DJT / iBorrowDesk / Options-capable tickers |
| E | Top-50 unresolved | Per-ticker failure reason |

## Source priority (SEC first)

```python
def resolve(ticker, date_str):
    # 1. SEC companyfacts (point-in-time, nearest-preceding)
    sec = get_sec_shares(ticker, date_str)
    if sec is not None:
        return ('RESOLVED_SEC', get_sec_concept(ticker))
    
    # 2. SEC stale check (filing exists but gap >400d)
    latest = get_sec_latest_filing(ticker)
    if latest:
        gap = (date - latest).days
        if gap > 400:
            return ('SHARES_STALE', f'gap={gap}d')
    
    # 3. EODHD SharesStats (single snapshot, no date history)
    eodhd = get_eodhd_shares(ticker)
    if eodhd is not None:
        return ('RESOLVED_EODHD', 'EODHD:SharesStats.SharesOutstanding')
    
    return ('SHARES_UNAVAILABLE', None)
```

## Failure mode diagnosis

| Pattern | Typical failure | Action |
|---------|----------------|--------|
| Ticker in SEC company_tickers + CIK in cache but NONE concept | Company uses WeightedAverage, not EntityCommonStock | Add fallback concept |
| Ticker not in SEC company_tickers | Foreign/OTC ticker | Try EODHD SharesStats |
| Ticker in SEC + EODHD but still UNAVAILABLE | ETF (no shares concept in either source) | Structural — report as ETF_CEF_FUND |
| Concept exists but date gap >400d | Filing stale | Flag STALE, exclude episode |

## ETF structural limitation

ETFs do NOT have `EntityCommonStockSharesOutstanding` or `CommonStockSharesOutstanding` in SEC XBRL. The EODHD fundamentals API also does NOT return `SharesStats.SharesOutstanding` for ETFs (confirmed: 0/30 top uncovered tickers). This is structural — no data-source pathway exists within the specified methodology.

## 10M default deletion (project-wide)

Every `get_shares_out()` fallback returning 10_000_000 must be replaced with `raise ValueError(...)`. Grep pattern:

```
grep -rn "10_000_000\|10000000\|10e6" --include="*.py" .
```

Only survivors after cleanup: unrelated defaults (e.g. `overnight_batch.py` $100M market cap, `funnel_v5_validation.py` sort key).
