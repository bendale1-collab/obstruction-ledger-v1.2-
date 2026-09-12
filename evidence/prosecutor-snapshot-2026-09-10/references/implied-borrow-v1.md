# IMPLIED_BORROW_V1 — Session transcript 2026-07-05

## B0 — Root cause: stock split vs option price mismatch

**Y4 corruption:** BBBY IV=6.2% (should be ~50-150%). GME IV_FAILED.

**Diagnosis:**
- BBBY had 1-for-10 reverse split on 2022-08-15
- EODHD `adjusted_close` ($25.99 on 2022-07-15) is post-split price
- OPRA option strikes on 2022-07-15 are pre-split ($1-$10, matching $2.60 stock)
- Using $25.99 as S with K=$2.50 put → DEEP OTM → IV=6.2%
- Correct raw S=$2.60 → ATM → IV ~IV ~50-150%
- GME: 1-for-4 stock split on 2022-07-22, same pattern

**Fix:** Detect splits between target_date and query_date. For REVERSE splits (1→N), divide option closes by N. For FORWARD splits (N→1), both underlying and option prices are consistently adjusted → no additional adjustment needed.

## B0r2 — IV sanity band

Frozen band: 0.3 < IV < 3.0 per contract. Outside → BASIS_SUSPECT, exclude.

**BBBY Aug 19 cycle (S=2.60, option closes÷10 for reverse split):**

| Strike | Type | RawClose | AdjClose | T | IV | Band |
|--------|------|----------|----------|---|----|------|
| 3.00 | C | 2.1200 | 0.2120 | 0.0958 | 1.9770 | ✓ |
| 4.00 | C | 1.3500 | 0.1350 | 0.0958 | 2.6459 | ✓ |

Before adjustment: IV=15.86 and 9.88 (both >3.0). After ÷10: both in band.

**GME Dec 14 2020 (S=12.72, no adjustment needed — forward split):**

| Strike | Type | RawClose | AdjClose | T | IV | Band |
|--------|------|----------|----------|---|----|------|
| 12.50 | C | 1.9000 | 1.9000 | 0.0684 | 2.0674 | ✓ |
| 12.50 | P | 1.7500 | 1.7500 | 0.0684 | 2.1488 | ✓ |
| 13.00 | C | 1.6700 | 1.6700 | 0.0876 | 2.0487 | ✓ |
| 13.00 | P | 1.9800 | 1.9800 | 0.0876 | 2.0840 | ✓ |
| 12.00 | C | 1.9900 | 1.9900 | 0.0876 | 1.8937 | ✓ |
| 12.00 | P | 1.8500 | 1.8500 | 0.0876 | 2.5937 | ✓ |

All 6/6 in band. Median 2.08.

## B1/B2 — DJT validation HALT

**Spearman ρ = 0.494** (required ≥0.7). **Mean ratio = -0.33x** (required 0.5-2.0x).

**Paired weeks:**

| Date | Implied% | Known% | Ratio |
|------|----------|--------|-------|
| 2024-04-03 | 79.93 | 35.0 | 2.28x |
| 2024-04-10 | 203.05 | 50.0 | 4.06x |
| 2024-04-24 | -205.43 | 35.0 | -5.87x |
| 2024-05-01 | 129.75 | 50.0 | 2.60x |
| 2024-05-08 | 12.71 | 65.0 | 0.20x |
| 2024-06-26 | -182.99 | 35.0 | -5.23x |

**Root cause:** DJT near-ATM options show C≈P in OHLCV VWAP. The VWAP doesn't capture the put-call spread that reflects borrow cost. This produces negative implied borrow when C≈P and the expected direction is P > C (positive borrow).

**Lesson:** OHLCV `ohlcv-1d` schema is insufficient for implied borrow on illiquid names. Switch to BBO/MBO for bid-ask midpoint, or accept that the method only works on liquid option chains (>5 traded C+P pairs per week).

## B2r — Alternate name validation (all failed)

After DJT had no fee history for Apr-Jun 2024, four alternate names from the E2 observable set were tried:

| Name | Fee range | Options? | OHLCV yield | Result |
|------|-----------|----------|-------------|--------|
| AI | 1-5% | 70+ pairs | 1-3/week | C-P spread swamped by bid-ask noise. For a 2% fee at 30 DTE with S=$20, C-P spread ~ $0.03 -- below option bid-ask of $0.05-$0.15. |
| FFIE | 12-15% | 3 pairs | 0-1/week | Penny stock ($0.06-0.09). Options illiquid. Databento resolves only 3 C+P pairs. |
| NVAX | 8-33% | 62+ pairs | 1-3/week | 1-for-20 reverse split Jul 2023 creates post-split pricing artifacts. Near-ATM call shows pretty_close=$9.10 on S=$4.47 stock. |
| SAVA | -- | -- | -- | Fee coverage ended 2024-01-30. No Apr-Jun data. |
| SNDL | -- | -- | -- | Fee coverage ended 2022. No Apr-Jun data. |

**Fundamental method limitation:** The put-call parity implied borrow formula can only resolve borrow fees above ~5-10% because C-P ≈ borrow_fee x S x T. For a 10% fee x $20 x (30/365) = $0.16 spread. For a 2% fee = $0.03 spread. The option bid-ask spread ($0.05-$0.15) swamps the low-fee signal. High-fee (>10%) stocks with liquid options AND clean corporate-action history are rare in practice.

### cmbp-1 schema on OPRA.PILLAR

For bid-ask midpoint instead of VWAP close:
- cmbp-1: Available for all periods (cost ~$0.04 for 6 ids x 15min). 15:45-16:00 ET = 19:45-20:00 UTC.
- cbbo-1s: NOT available before 2025-02-20 on OPRA.PILLAR (422 error).
- cmbp-1 side field: side=1 for bid, side=2 for ask. Returns ~6000 rows for 6-contract window. Best bid = max(bids), best ask = min(asks).
- Estimated full run cost for validation: ~$0.06 for 13 weeks x 6 contracts x 15min.
