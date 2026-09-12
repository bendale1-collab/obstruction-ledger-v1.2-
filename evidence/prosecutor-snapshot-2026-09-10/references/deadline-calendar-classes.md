# DEADLINE_CALENDAR_V1 — Class Definitions

Ten classes of filed deadlines that can trigger gated forced-covering events. Each class has a distinct SEC filing pattern and source constraint.

## Class table

| Class | Description | Source form | Filing trigger | Deadline source | External ref? |
|---|---|---|---|---|---|
| C1 | Record date declarations | 8-K, DEF 14A | Record date / special dividend / distribution date | Filing text | PARTIAL |
| C2 | Offering close/settlement | 424B5, 424B2 | Securities offering close | Filing text (closing date) | PARTIAL |
| C3 | Lockup expiry | S-1 pricing table | IPO lockup expiration | S-1 pricing table (computed) | IPO list |
| C4 | Merger/de-SPAC closing | 8-K (2.01), S-4, 425 | Merger agreement / de-SPAC vote | Proxy outside-date, not signing date | PARTIAL |
| C5 | Ch.11 emergence | 8-K (1.03) | Bankruptcy plan effectiveness | Filing text | PARTIAL |
| C6 | Split effectiveness | 8-K (5.03, 3.03) | Stock/reverse split | Exchange notice (Nasdaq Trader, NYSE) | Exchange lists |
| C7 | Tender offer expiration | SC TO-I, SC TO-T | Tender offer expiry | Filing text | EFTS index (complete) |
| C8 | Warrant redemption | 8-K (3.02) | Warrant call / redemption date | Filing text | PARTIAL |
| C9 | Exchange compliance | 8-K (3.01) | Delisting / deficiency notice | Filing text | PARTIAL |
| C10 | Index additive/deletive | S&P DJI press release | Index reconstitution | Official press release, NOT EDGAR | S&P press (complete) |

## Source corrections (frozen per spec)

- **C10**: Must use Russell prelim lists or S&P DJI press releases — EDGAR 8-Ks post-date the effective date by hours/days. Measured Q2 failure when built from EDGAR.
- **C4**: Merger outside-dates from proxy statement, not signing dates from 8-K. The signing date ≠ the deadline that forces delivery.
- **C3**: Lockup expiries computed from S-1 pricing tables (IPO date + lockup period). Standard 180d lockup from 2024 IPOs expires in Q1-Q2 2025, not Q4. Only SPAC/de-SPAC 365d or 545d lockups reach Q4 2025. EDGAR keyword search for lockup announcements yields 0% capture — lockup expiries are silent.

## Subclass definitions (frozen per REGISTRY_V3)

### C1_INKIND — Record date for in-kind distribution
Class C1 subclass: deadline is a record date for an in-kind distribution (warrant dividend, stock dividend). Forcing mechanism is CONTESTED — holders receive assets without cash requirement, but synthetic-long holders (derivatives market makers) must deliver. Distinct from cash-required record dates. Prototype: GME warrant dividend (2025-10-03, accession 0001326380-25-000073).

### C8_ELECTIVE — Holder-elective exercise deadline
Class C8 subclass: holder-elective exercise deadline (warrant expiration). Forcing is CONDITIONAL on spot > strike into the expiry window. If warrants are in-the-money, holders must exercise or sell before expiry; if out-of-the-money, warrants expire worthless with no forcing. Strike and outstanding count define the conditions. Prototype: GME warrant expiry (2026-10-30, strike $32, ~59.15M warrants).

## Pruned class

C11 (bond maturity/refi walls) — removed. Thesis-dependent, not mechanical. Refers to fixed-income deadlines that depend on company-specific debt structure, not a universal trigger mechanism.

## Calendar JSONL schema

Mandatory fields:
```
ticker          str   — uppercase symbol
class           str   — C1 through C10
filing_date     str   — YYYY-MM-DD
form            str   — SEC form or external source label
adsh            str   — EDGAR accession or external ID
deadline_date   str   — YYYY-MM-DD or null
status          str   — FORM_INDEX_CAPTURED / DEADLINE_EXTRACTED / EXTERNAL / etc.
source          str   — EDGAR / S&P_PRESS / EXCHANGE_NOTICE
cik             str   — 10-digit CIK or UNRESOLVED / EXTERNAL
phrase          str   — 100-char event excerpt
```

Rows missing `deadline_date` OR `adsh` are rejected.

## Coverage audit thresholds

- ≥70% capture → PASS (class counts for hit-rate denominators)
- <70% capture → INCOMPLETE (excluded until fixed)
- REFERENCE_PARTIAL → class excluded from denominators (no external reference exists)

## Class-specific known coverage issues (from B3 Q4 2025 audit)

| Class | Capture | Issue |
|---|---|---|
| C10 | 46% | MidCap 400 / SmallCap 600 events missing from core calendar |
| C7 | 71% | PASS — but 101 of 248 filings are non-traded funds without tickers (structural) |
| C6 | 0% | EDGAR keyword search finds split mentions, not effective dates |
| C3 | 0% | Lockup expiry is silent; must compute from S-1, not search EDGAR |
| C1,2,4,5,8,9 | N/A | No external reference; ~28% extraction from R1 prior work |