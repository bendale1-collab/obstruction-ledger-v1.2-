# Close Auction Signature — Measurement Methodology

## When to use

Testing whether closing auction volume share increases around forced-covering
deadlines (merger votes, lockup expiries, index rebalances, etc.). If
close-heavy execution spikes at deadlines, it signals institutional closing
of synthetic-short positions.

## Data source

Databento XNYS.PILLAR dataset, `imbalance` schema:
- Covers NYSE-listed securities only (2018-05-01 onwards)
- Does NOT cover Nasdaq-listed securities (use XNAS.ITCH instead)
- Schema fields:
  - `paired_qty` — shares matched in the closing auction (direct measure)
  - `total_imbalance_qty` — net imbalance (buy - sell)
  - `side` — 'B' buy imbalance, 'A' sell imbalance
  - `auction_type` — 'C' = closing auction, 'M' = market open, 'O' = opening
  - `auction_time` — scheduled cross time (16:00 ET for closing)
- The last imbalance update per day (closest to 21:00 UTC) is the final
  auction print — use `df.groupby('date').last()`
- Cost: ~$0.23/ticker for 2-month window (GME). ~$4.48 for 12 tickers × 4yr.
  Use cost gate via `metadata.get_cost` before fetching.

## Limitation: exchange coverage

XNYS.PILLAR is NYSE-only. For Nasdaq tickers:
- Use XNAS.ITCH (available 2018-05-01 onwards, trades schema)
- Cost for XNAS.ITCH trades is ~$0.08/ticker for 3 days (much more expensive)
- XNAS.ITCH `ohlcv-1m` at $0.018/ticker for 2 months is cheaper for proxying
  close volume via last-minute bars

## Proxy when imbalance unavailable

XNAS.ITCH also has `ohlcv-1m` schema (1-minute bars) which can proxy for
closing auction volume via last-30min share of daily volume:
- Covers BOTH NYSE and Nasdaq (wider coverage than XNYS.PILLAR)
- Available from 2018-05-01 onwards (covers all mechanical_registry events)
- Cost: ~$0.001-$0.15 per ticker per 45-day window (very cheap)
  - GME 3 months = $0.11
  - AMC 3 months = $0.15
  - VIAC 6 weeks = $0.009
  - OSTK 9 months = $0.037
  - DJT 7 months = $0.045
- Total cost for all 8 unique treatment tickers = $0.36 (under $3 budget)
- Limitation: last-30min bars are a PROXY, not the actual closing auction
  print. Expected last-30min share: 2-5% of regular-hours volume for
  NYSE stocks, 0.2-1.5% for Nasdaq stocks.

XNAS.ITCH does NOT have the `imbalance` schema — only XNYS.PILLAR has it.
So for Nasdaq tickers you MUST use ohlcv-1m proxy.

EQUS.MINI and DBEQ.BASIC also have ohlcv-1m at lower cost but start from
2023-03-28 — too recent for pre-2023 mechanical_registry events.

### ohlcv-1m UTC time handling (critical)

XNAS.ITCH ohlcv-1m timestamps are in UTC. NYSE regular trading hours are
14:30-21:00 UTC (9:30-16:00 ET). OHLCV data includes PRE-MARKET bars
(starting 09:00 UTC / 5:00 ET) which must be filtered out:
- Regular trading: hour_utc >= 14 and hour_utc < 21
- Last 30 minutes: hour_utc == 20 and min_utc >= 30
- Total daily volume: sum of regular-hour bars only (not pre-market)
- The DataFrame index IS the timestamp column (`ts_event` is the index,
  not a column — use `df.reset_index()["ts_event"]` to access it)

## Analysis structure

For each event (treatment ticker at deadline):
1. Window A: deadline ±3 trading days (close proximity)
2. Window B: T-30 to T-10 baseline (no deadline proximity)
3. Compute: paired_qty average in window A / paired_qty average in window B
   = ratio (>1.0 means higher close auction volume at deadline)

For controls: same window structure, same event ticker's deadline.
Compare event ratios vs control ratios via Mann-Whitney (greater).

## Pre-registered read

- "ELEVATED: closing auction volume increases at deadlines (p<0.05)" if
  event ratios significantly exceed control ratios
- "NO ELEVATION: closing auction volume unchanged at deadlines (p>=0.05)"
- "UNMEASURABLE — [reason]" if data insufficient (e.g., too few NYSE tickers)

## Known bottlenecks

- Only NYSE tickers have imbalance data via XNYS.PILLAR. ~50% of calendar
  events may be Nasdaq-listed and unmeasurable with this dataset alone.
- Stage_c_universe (80 tickers) is too small for control matching — need
  shares_cache.json (1,186 tickers) as control pool instead.
- Budget: $3 hard cap. Full 12 event tickers × 45d windows ≈ $1.37 on
  XNYS.PILLAR ohlcv-1m, or $4.48 on imbalance (over cap). Narrow windows
  to stay under $3.
