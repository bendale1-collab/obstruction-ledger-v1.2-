# Funnel Scan Methodology — 11-Class Trigger Taxonomy

## When to use

Forward-looking retrospective validation scans of upcoming/quarterly deadlines. Applies the T2r2 methodology to a date window. Labeled EXPLORATORY — thresholds frozen before first pull, no verdict.

## Universe (frozen per FUNNEL_SCAN_Q2_2026_V1)

| Constraint | Source | 
|-----------|--------|
| Exchange | NYSE/NASDAQ (no roster free source) |
| Mktcap | $100M-$10B (EODHD or SEC shares + price) |
| Options OI | ≥500 across all series (Databento OPRA, one cheap pull) |
| Exclude | ETFs, ADRs, F-shares, warrants, units |

## G1 — 11 trigger classes (C1-C11)

| Class | Description | EFTS Search Strategy | Sign Default |
|-------|------------|---------------------|-------------|
| C1 | Record date declarations (dividends inc. in-kind/special) | `q=8-K+"record date"+dividend` | AMBIGUOUS — check in-kind vs liquid |
| C2 | Offering close/settlement (dated closes only) | `q=424B5+"closing"+offering` | AMBIGUOUS — check R3 (dated close?) |
| C3 | Lockup expiry (IPO + de-SPAC) | Computed from S-1 pricing tables — NOT searched via EDGAR. Lockup expiries are silent events (no filing required at expiry date). 180-day lockup from 2024 IPOs expires Q1-Q2 2025, not Q4. Only 365d+ (SPAC/de-SPAC) lockups reach Q4 2025 from 2024 IPOs. | SQUEEZE_DIR |
| C4 | Merger/de-SPAC closing + election deadlines | DEFM14A filing text extraction (see c4-date-extraction-defm14a.md). Search: EDGAR index page at filing-agent CIK (adsh[:10]); parse BOTH ix?doc= AND href links for document URL. The document is often under the issuer CIK directory, not filing-agent. | AMBIGUOUS — cash-out = FORCED_SELL |
| C5 | Ch.11 emergence / plan effectiveness | `q=8-K+emergence+effective` | SQUEEZE_DIR |
| C6 | Split/reverse-split effectiveness | **EXTERNAL SOURCE** — from Nasdaq/NYSE exchange notice lists, NOT EDGAR keyword search. EDGAR 8-K "stock split" keyword matches filings that *mention* splits (announcements, board approvals) but not the EFFECTIVE DATES. Use Nasdaq TradingSystemAddsDeletes.txt or Nasdaq ECA alerts, NYSE daily lists, or web-sourced split calendars (stockanalysis.com, Nasdaq.com split history). | AMBIGUOUS — fwd=SQUEEZE_DIR, rev=AMBIGUOUS |
| C7 | Tender offer expirations | q="tender+offer" or q="SC+TO-I" then post-filter form.startswith("SC TO"). Do NOT use form: SC TO-I style queries with colon — they return HTTP 500. Many SC TO filings are from non-traded funds/BDCs with no ticker — mark UNRESOLVED_FUND. | SQUEEZE_DIR |
| C8 | Warrant redemption calls | `q=8-K+warrant+redemption+date` | SQUEEZE_DIR (forced exercise) |
| C9 | Exchange compliance deadlines | `q=8-K+listing+deficiency+notice` | AMBIGUOUS (cure window) |
| C10 | Index add/delete effective dates | **EXTERNAL SOURCE** — from S&P DJI / Russell official press releases, NOT EDGAR. 8-Ks post-date effectiveness (measured Q2 failure). Source: S&P press releases on PRNewswire, Nasdaq.com, or LSEG (Russell) PDFs. Dec 22 quarterly rebalance is the major Q4 event. | SQUEEZE_DIR (adds); FORCED_SELL (deletes) |
| C11 | Bond maturity/refi walls | `q=10-K+"maturity"+notes` | AMBIGUOUS — distressed subset only (ICR<1, CCC) |

## T2r2 — Type-restricted Fisher rules (session-derived)

Frozen per MECH_REGISTRY_AMEND_V1 + T2r2 directive. Applied when classifying SEC EDGAR filings as qualifying mechanical triggers:

- **R1 — Deadline extracted from text.** Filing text must contain the specific deadline date ("record date", "closing date", "expiration date", "distribution date"). Paste the extracted phrase per hit. Access filing text via `https://www.sec.gov/Archives/edgar/data/{CIK}/{adsh_no_dashes}/{filename}`.
- **R2 — Ex-ante constraint.** Filing date <= onset. Post-onset filings are NON-QUALIFYING regardless of content.
- **R3 — Resale shelves/ATMs excluded.** 424B3 resale prospectuses are NON-QUALIFYING (no settlement deadline). 424B5 qualifies only with a dated close (check for "expected to close on [DATE]" in text; ATM programs saying "at-the-market" or "Sales Agreement" with no single close date do NOT qualify).
- **R4 — CIK over display name.** Resolve ticker changes (e.g., OSTK→BYON) via CIK, not display_name. EFTS display_names always show current ticker.

**Fisher exact test (one-tailed):**
```python
import math
def fisher_p(a,b,c,d):
    log_p = math.lgamma(a+b+1) + math.lgamma(c+d+1) + math.lgamma(a+c+1) + math.lgamma(b+d+1)
    log_p -= math.lgamma(a+b+c+d+1) + math.lgamma(a+1) + math.lgamma(b+1) + math.lgamma(c+1) + math.lgamma(d+1)
    return math.exp(log_p)
```

## Table of trigger class counts by EFTS search outcome

```
Class    Raw Hits   Candidates   Qualifying (R1-R4)
------   --------   ----------   ------------------
C1       N          N            N
...
```

Maintain an honest count at each filtration stage — do not hide attrition. Raw hits from EFTS (often 1000-10000+), candidates after form-type filtering, qualifying after R1-R4 applied.

## Composite Output

## G2 — Sign taxonomy

| Sign | Applicable to | Rationale |
|------|--------------|-----------|
| SQUEEZE_DIR | C3, C5, C6(fwd), C8, C10(adds), C1(hard-to-deliver in-kind) | Deadline creates forced delivery of hard-to-borrow shares |
| AMBIGUOUS | C2, C6(reverse), C9, C11, C1(liquid-deliverable), C4 | Direction depends on context — carry, flag, don't drop |
| FORCED_SELL/DOWN | C10(deletes), C4(cash-outs), C1(APE-precedent liquid) | Market sells/reductions |

## G3 — Load metrics (all at T-10 trading days pre-deadline)

| Metric | Source | Note |
|--------|--------|------|
| L1 SI/float | FINRA biweekly SI / SEC shares count | Percentile vs universe |
| L2 Threshold dwell | FINRA threshold list | Consecutive days on list |
| L3 Forward FTD due | SEC CNS fails aged 20-35 days | T+35 clock maturing into window |
| L4 ETF look-through | ETF holdings + SI | Name weight >5% → add ETF SI |
| L5 Tenure | UNOBSERVED (no free source) | Column present, honest |

**No composite score** — scoring would require a fitted model we don't have. Report L1-L4 percentiles separately.

## Vetoes (frozen, applied after outcome measurement)

| Veto | Check | Action |
|------|-------|--------|
| V-REFRACTORY | Prior E1/E3 within 60 trading days | Flag, suppression candidate |
| V-ETF-OP | FTD spike ±2d of ≥2σ ETF flow | Flag OPERATIONAL |
| V2-DECORR | 1y mean 20d corr w/ sector ETF | Report only, no threshold |

## Outcome check

### E1 BASE-RATE AUDIT (gates everything)

Before computing E1 on real events, run a base-rate audit on 1000 random name-dates:
- Sample 1000 (ticker, settlement_date) from the FTD tape where ticker is NOT
  a calendar event and date is in the same calendar year as the test window
- Compute E1v2 on each pseudoevent
- If >5% fire rate → HALT. Report distribution of which condition failed.
  The E1 definition is not discriminative and must be tightened.
- If ≤5% → PASS. Proceed to outcome computation.

### E1v2 — FTD drop (shares-thresholded)

Per event: E1v2 fires iff ALL FOUR conditions met within ±10 settlement dates of deadline:

  **(a)** Local max FTD >= 0.1% of shares outstanding
  **(b)** >= 3 consecutive settlement-dates with FTD >= 0.05% of shares
        outstanding BEFORE the max (build-up phase)
  **(c)** Drop >= 70% from local max
  **(d)** Post-drop FTD < 30% of the max, sustained >= 2 consecutive
        settlement-dates after the peak

If any condition fails, E1v2 = False. The shares-outstanding thresholds
discriminate against random noise (2.6% base rate on 1000 random name-dates).

Shares outstanding source (in priority order):
  1. EODHD fundamentals API (`SharesStats.SharesOutstanding`)
  2. SEC XBRL API (`dei/EntityCommonStockSharesOutstanding`)
  3. Default: 10M shares (conservative for micro-caps where shares unknown)

### Calibration check (DJT)

Before trusting E1v2 on calendar events, verify it fires on a known
fails-resolution event: DJT (Trump Media) April-May 2024. E1v2 must fire
on at least one date during the fails-resolution window (Apr 15 - May 15).
Miss → HALT. This ensures the definition detects genuine forced closeouts.

### E3 — Price surge (positive-only, frozen)

- E3 = close-to-close return >=+15% over any 3-consecutive-trading-day window
  within ±10td of deadline
- Uses EODHD adjusted_close (bulk API:
  `https://eodhd.com/api/eod/{TICKER}.US?api_token=KEY&fmt=json&from=FD&to=TD`)
- POSITIVE return only: a -15% test case must return False
- Sign-check assert required: create test prices [100, 97, 85] (3 days, -15%),
  assert E3=False
- Split-window exclusions: skip events where a stock split occurs within the
  window (check EODHD splits endpoint)

### Pre-registered read (post-outcome)

After computing E1v2 + E3 for events vs controls, produce an explicit
pre-registered read:

  - "confirmed-outcome leg FAILS for [period]" if event rate not
    distinguishable from control rate (p >= 0.05 in all load bands)
  - "confirmed-outcome leg PASSES for [period]" if event rate exceeds
    control rate with p < 0.05 in at least one load band
  - "UNMEASURABLE — [reason]" if data insufficient
- No rescue language. No "suggests" or "may indicate".
- Report exactly: "Channel #1 dead — counterfactual set exhausted except
  prospective E2" if the pre-registered read is FAILS and this was the
  last testable channel.
- Monotonicity check: report whether LOW < MED < HIGH or flag violation.

### Event-centric collapse (events != dates)

Before computing outcomes, collapse the calendar from date-centric to event-centric:
- One row per (ticker, event) pair
- vote_date + outside_date are FIELDS on the same row, not separate rows
- For C4 (merger votes): collapse multiple vote_date rows per ticker into one event row (keep latest vote_date + latest outside_date)
- For C10 (index changes): same ticker on same date but different actions (add + remove) = one event with combined phrases
- Row-count assert: rows == len(unique ticker, event_date pairs)

### FTD source: full CNS fails tape

Two tape directories on disk:
- `/Users/brukendale/sec_threshold_data/ftd_files/` (144 zips, ~2020–2025)
- `/Users/brukendale/sec_threshold_data/ftd_backfill/` (250 zips, 2004–2019)
- **Total: 416 zips, 27M rows, 69K unique tickers**
- **ZERO_BAND rule:** If a name-date is absent from both directories, code as ZERO_BAND (fails < 10K shares that period), NOT missing/UNOBSERVED
- File format: pipe-delimited CSV inside ZIP: `SETTLEMENT DATE|SYMBOL|QUANTITY (FAILS)|CUSIP|DESCRIPTION|PRICE`
- Date format: YYYYMMDD (e.g. 20200102). No header row, no ISO dates.
- Dedupe by filename; prefer ftd_files when same filename exists in both
- Some backfill ZIPs may have NUL bytes (e.g. cnsfails201509a/b.zip) — skip with warning (~0.5% data loss)

### Control matching (3:1)

Two pool sources, tried in order:

**Primary pool: shares_cache.json** — 1,186 tickers with shares outstanding
  from EODHD fundamentals. Cross-referenced with FTD tape for data coverage.
  Path: `/Users/brukendale/projects/forced-covering-detector/shares_cache.json`

**Fallback pool: stage_c_universe.json** — 186 tickers with {mktcap, shares,
  sector, industry} from the calibration cohort.
  Path: `/Users/brukendale/projects/forced-covering-detector/stage_c_universe.json`
  Only use this when shares_cache.json is not available (it is too small for
  decile matching — 80 tickers after excluding calendar names).

Matching criteria:
- Same mktcap decile (divide pool into 10 equal-sized deciles by mktcap,
  approximated as shares_outstanding × $10 for the primary pool)
- No deadline event within ±45d of event date (exclude all calendar event
  tickers from the pool before matching)
- 3:1 ratio: 3 control tickers per event ticker
- Minimum 100 distinct control tickers across all events
- Each control ticker reused at most 3 times across all events
- If <100 distinct controls, print WARN but continue

If sector data is available (stage_c_universe), sector match was used in
v1-v3. v4+ dropped sector match — cap-decile + no-deadline-±45d only —
because sector overlap is too thin for the calendar's event tickers.

Control tickers also need EODHD adjusted closes for E3 computation via the
same bulk API pattern as event tickers.

### E3 frozen def (positive-only)

- E3 = close-to-close return >=+15% over any 3-consecutive-trading-day window within ±10td of deadline
- Uses EODHD adjusted_close (bulk API: `https://eodhd.com/api/eod/{TICKER}.US?api_token=KEY&fmt=json&from=FD&to=TD`)
- POSITIVE return only: a -15% test case must return False
- Sign-check assert required: create test prices [100, 97, 85] (3 days, -15%), assert E3=False
- Split-window exclusions: skip events where a stock split occurs within the window (check EODHD splits endpoint)

## B3 — Coverage Audit (DEADLINE_CALENDAR_V1 gate)

**When to run:** Before any hit-rate claim. Gates all calendar-based denominators.

### Reference sources per class

| Class | Reference type | Known-complete source |
|-------|---------------|----------------------|
| C10 | External | S&P DJI press releases (PRNewswire, Nasdaq.com) |
| C7 | EDGAR form-type index | SC TO-I/T filing index — complete by construction |
| C6 | External | Nasdaq/NYSE exchange notice lists (Nasdaq ECA alerts, stockanalysis.com) |
| C3 | Computed from S-1 | IPO pricing tables + lockup period -> expiry date |
| C1,C2,C4,C5,C8,C9 | Form-type index | No external complete reference — REFERENCE_PARTIAL |

### Threshold

- >=70% capture -> PASS (class enters hit-rate denominators)
- <70% capture -> INCOMPLETE (excluded until fixed)

### Known failure modes (B3 Q4 2025 audit)

- C10: MidCap 400 / SmallCap 600 missing from calendar -> 46% (FIX: full S&P index coverage)
- C6: EDGAR "stock split" keyword finds MENTION not EFFECTIVE DATE -> 0% (FIX: external source)
- C3: No lockup-expiry EDGAR filings at expiry time -> 0% (FIX: compute from S-1)
- C7: 101/248 SC TO filings from non-traded funds no ticker -> structural, mark UNRESOLVED_FUND

## Composite Output

Event calendar (jsonl), coverage audit table, hash-chained MANIFEST.
