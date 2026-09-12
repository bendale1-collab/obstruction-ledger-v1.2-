# Threshold Exit Timing — Dwell Distribution Analysis

## When to use

Analyzing how long securities remain on the SEC threshold list (Reg SHO Rule 203).
Tests whether mandatory closeout at day 13 (Rule 203(b)(3)) produces a detectable
signal in exit timing.

## Data source

Full CNS fails tape on disk:
- `/Users/brukendale/sec_threshold_data/ftd_files/` (144 zips, ~2020-2025)
- `/Users/brukendale/sec_threshold_data/ftd_backfill/` (250 zips, 2004-2019)
- 416 ZIPs total, 27M rows, 69K unique tickers

Threshold criterion: QTY * PRICE > $500,000 (SEC Reg SHO Rule 203 standard)

## Episode definition

- An episode starts when a ticker's daily FTD value first crosses the $500K threshold
- It continues as long as the ticker remains above threshold on consecutive calendar days
- A gap of 5+ consecutive calendar days below threshold splits into a new episode
- dwell = (exit_date - entry_date).days in calendar days
- Max cap dwell at 60 days (bucket 60+ for longer episodes)

Note: Rule 203(b)(3) counts SETTLEMENT days (trading days), not calendar days.
A 13-trading-day closeout maps to ~17-19 calendar days. Check both day 13
(calendar) and days 17-19 (trading-day equivalent) for robustness.

## Pre-registered read

Hypothesis: Mass spike at day 13 (or 17-19 in calendar days) = forced closeouts
exist, dated ex-ante.

- If day 13 count > 10% above surrounding days (12 and 14): "MECHANICAL SPIKE:
  Rule 203(b)(3) closeouts produce detectable signal"
- If smooth/uniform decay through day 13: "VOLUNTARY EXITS DOMINATE — no
  mechanical closeout spike. Exits are gradual."
- If spike at different dwell (e.g., 17-19): "MECHANICAL SPIKE at [N]d — closeout
  clock operates at calendar-day rather than trading-day cadence"

## Era split (T+1 settlement)

T+1 settlement went live 2024-05-28. Split pre/post by entry date:

Pre-T+1 (before 2024-05-28): closeout clock = T+3 settlement
Post-T+1 (on/after 2024-05-28): closeout clock = T+1 settlement

If Rule 203(b)(3) closeout drove exits:
- Pre-T+1 should show spike at day 13 (T+3 era had 13-day closeout)
- Post-T+1 spike should shift to earlier day (T+1 compressed settlement)
- No spike shift = exits not driven by closeout timing

## Known results (Q4 2025 run)

- Total episodes: 763,022
- 26,671 unique tickers crossed threshold
- Distribution: smooth hyperbolic decay from dwell 0 (393K) to dwell 60+ (3.6K)
- Day 13: 6,301 vs Day 12: 5,851 vs Day 14: 6,675 — ratio 1.01x
- NO structural spike at day 13. Day 14 is higher than day 13.
- Pre-T+1 (675K episodes) and Post-T+1 (87K episodes) show identical shape
- No spike shift across T+1 boundary
- Conclusion: exits are predominantly voluntary/gradual, not mechanical closeouts

## Day-13 E3 price analysis (deferred)

Approach: 100 day-13 exit cases + 100 matched non-13 exit controls.
For each: max +3d close-to-close adjusted return from exit date.
Test: Mann-Whitney (greater) on case vs control returns.
Status: DEFERRED — EODHD API rate-limited on sample execution.
