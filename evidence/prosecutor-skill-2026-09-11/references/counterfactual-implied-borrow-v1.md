# C1 Implied Borrow Counterfactual — Session Results

## Session timeline (2026-07-05)

| Attempt | Strategy | Result |
|---------|----------|--------|
| C1 (batch) | Pull full OPRA chains for GME/AMC/TSLA + 15 GC | 402 on every name (huge pulls > remaining balance) |
| C1-tiny | Resolve once, pull 6 ct/day per date | 402 on every day (balance = $0) |
| C1-hybrid | Hybrid batch pull | 402 on every chunk |
| C1-rest | REST API, per-day tiny pulls (6 ct/day) | 402 on every pull (balance = $0) |
| C1_FINAL | Pre-flight cost assert, $10 refill, 6 ct/day | **13/57 name-dates with data (77.2% insufficient)** |

## Final results (C1_FINAL_v2)

### Squeeze names: 0 data days from all 3

GME, AMC, TSLA returned 0 valid data days despite working OHLCV data being pulled (1-2 records per day). The 3 ATM C-P pairs from the full-range resolve failed the IV band filter (0.3-3.0) on every date. Root cause: the resolve returns ALL contracts for the entire date range, but the per-date ATM filter picks contracts that either haven't been listed yet, have expired, or have no trades on that specific date.

### GC names: 8/15 with data, median borrow 1.30 → ARTIFACT flag

GC mega-caps with negligible true borrow fees produced 0.34-2.91 implied borrow:

| Name | Median borrow |
|------|-------------|
| AAPL | 0.40 |
| MSFT | 1.32 |
| JNJ | 1.37 |
| PG | 1.27 |
| KO | 1.30 |
| XOM | 1.93 |
| JPM | 2.91 |
| V | 0.78 |
| PEP | 1.77 |

**Interpretation:** ohlcv-1d VWAP for same-strike C-P pairs on mega-caps does NOT capture the bid-ask spread that embeds borrow cost. The `pretty_close` VWAP collapses the C-P gap, producing small positive borrow values where true fee is ~0%. This is a structural ARTIFACT: the method generates false positive borrow at 0.3-2.9x level regardless of actual fee.

## Key methodological findings

1. **ohclv-1d VWAP cannot resolve implied borrow below ~3%** — the C-P spread is narrower than the option bid-ask spread
2. **Mutual exclusivity ceiling holds:** high-fee names have illiquid options; liquid-option names have negligible fees
3. **Per-date resolve (not full-range)** likely needed: resolving once for the full range and filtering per-date gives stale contract selections
4. **GC median = 1.30 confirms ARTIFACT**: the method produces false signal regardless of true fee

## C2/C3 verdict

- S1: All FAIL (0 data days for squeeze names)
- S2: FAIL (no ordering possible)
- S3: ARTIFACT flag (GC median 1.30 >> 3% threshold)
- **Verdict: UNRESOLVED** — 77.2% insufficient data (>30% threshold per C1_FINAL_v2 directive)
- **Ruling:** method dead, terminus final, no parameter rescue
