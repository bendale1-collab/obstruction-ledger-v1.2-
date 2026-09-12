# X1_TWOCLASS V1 — Two-Class Trigger Test Results

**Run:** 2026-07-06
**Registry:** mechanical_registry_v2.json (SHA256: 17bbae95450305761762ec9b3a364c0918f59aa7962c0d9cf8249fb09004dc70)
**Cohort:** calibration_cohort_registry_v2.json ATTENTION_ONLY class
**Source:** SEC EDGAR EFTS (ledger #1), CNS fails FTD cache at /Users/brukendale/sec_threshold_data/ftd_files/

---

## T1 — Proximity stat

### Observed lags

| Class | Event | Onset | Deadline | Lag(td) |
|-------|-------|-------|----------|---------|
| MECHANICAL | OSTK-A | 2019-09-13 | 2019-09-23 | 6 |
| MECHANICAL | HTZ | 2021-06-30 | 2021-06-30 | 0 |
| MECHANICAL | DJT-close | 2024-03-25 | 2024-03-25 | 0 |
| MECHANICAL | DJT-lockup | 2024-09-19 | 2024-09-19 | 0 |
| MECHANICAL | GME-ATM | 2021-06-22 | 2021-06-22 | 0 |
| MECHANICAL | AMC-ATM | 2021-06-03 | 2021-06-03 | 0 |
| MECHANICAL | GME-split | 2022-07-22 | 2022-07-22 | 0 |
| FORCED_SELL | VIAC | 2021-03-25 | 2021-03-26 | 1 |
| CONTESTED | AMC-APE | 2022-08-22 | 2022-08-22 | 0 |

### Null simulation (1000 draws per event, same-year trading days)

| Class | N | Obs mean | Null mean | P5 | P25 | P50 | P75 | P95 | p(null≤obs) |
|------|---|---|-----------|---|---|---|---|---|---|
| MECHANICAL | 7 | 0.9 td | 71.7 | 7 | 33 | 65 | 106 | 161 | **0.0040** |
| FORCED_SELL | 1 | 1.0 td | 83.7 | 7 | 32 | 71 | 133 | 189 | **0.0130** |
| CONTESTED | 1 | 0.0 td | 70.6 | 6 | 34 | 64 | 101 | 157 | **0.0020** |

All three classes reject null at p<0.05.

---

## T2 — ATTENTION control

### ATTENTION_ONLY vs TREATMENTS filing density

| Class | With mech filing | Without | Fraction |
|-------|-----------------|---------|----------|
| TREATMENTS | 9 | 0 | 100% |
| ATTENTION_ONLY | 18 | 1 (TR) | 94.7% |

Fisher exact 2×2: [[9, 0], [18, 1]]
**p (one-tailed): 0.679** — not significant.

### Per-ticker nearest mechanical filing

| Ticker | Onset | Nearest Filing | Form | Delta(d) |
|--------|-------|---------------|------|----------|
| TLRY | 2020-03-23 | 2020-03-17 | 8-K | −6 |
| SPCE | 2020-06-01 | 2020-06-02 | 424B3 | +1 |
| OSTK | 2020-08-26 | 2020-08-14 | 8-K | −12 |
| GME | 2021-01-13 | 2021-01-11 | 8-K | −2 |
| AMC | 2021-01-25 | 2021-01-25 | 424B5 | +0 |
| SNDL | 2021-01-26 | 2021-01-25 | 424B5 | −1 |
| AAL | 2021-01-27 | 2021-01-28 | 8-K | +1 |
| EXPR | 2021-01-27 | 2021-02-03 | 8-K | +7 |
| KOSS | 2021-01-27 | 2021-01-28 | 8-K | +1 |
| NAKD | 2021-01-27 | 2021-01-29 | 424B5 | +2 |
| TR | 2021-01-27 | **NONE** | — | — |
| CGC | 2021-02-01 | 2021-02-05 | S-1 | +4 |
| CHPT | 2021-02-01 | 2021-02-19 | 425 | +18 |
| WISH | 2021-02-05 | 2021-02-16 | SC 13G | +11 |
| RKT | 2021-03-02 | 2021-03-03 | 425 | +1 |
| CLOV | 2021-06-08 | 2021-06-22 | 8-K | +14 |
| FFIE | 2021-07-22 | 2021-07-22 | 8-K/A | +0 |
| LCID | 2021-07-26 | 2021-07-26 | 8-K/A | +0 |
| HKD | 2022-07-15 | 2022-08-10 | 425 | +26 |

**Key:**
- Query method: search ticker alone, then filter by form type (see prosecutor SKILL.md X1_TWOCLASS section for form include/exclude lists)
- Only TR (Tautachron) has zero mechanical filings within ±45d of onset
- ATTENTION_ONLY events are nearly as likely as treatments to have a coincident SEC filing (94.7% vs 100%, p=0.68)

---

## T3 — NULL_CONTROL check

### OSTK-B (deadline 2020-05-19, restructured digital dividend)

FTD data from cnsfails202005{a,b}.zip:

| Date | FTD | Price |
|------|-----|-------|
| 2020-05-15 | 28,102 | $18.62 |
| 2020-05-18 | 14,235 | $17.07 |
| **2020-05-19** | **1,700** | **$15.19** |
| 2020-05-20 | 8,803 | $17.87 |
| 2020-05-21 | 18,324 | $18.54 |
| 2020-05-26 | 103,656 | $17.60 |

**SIGNATURE: NEGATIVE.** FTD drop on deadline is dividend distribution settlement, not forced covering. Price recovers next day. NULL_CONTROL confirmed.

### AMC-APE (deadline 2022-08-22, CONTESTED)

FTD data from cnsfails202208{a,b}.zip:

| Date | FTD | Price |
|------|-----|-------|
| 2022-08-19 | 428,468 | $19.29 |
| **2022-08-22** | **196,027** | **$18.02** |
| 2022-08-23 | 852,902 | $10.46 |
| 2022-08-24 | 1,303,504 | $9.56 |
| 2022-08-25 | 1,303,126 | $9.58 |

**SIGNATURE: POSITIVE.** E1: FTD spike from 196K to 1.30M (6.6×) within 2 days. E3: price collapse from $18.02 to $9.56 (−47%). FLAGGED — CONTESTED per directive, not suppressed.

---

## T4 — Per-class summary

| Class | N | |lag| mean | p(null) | Filing fraction | Fisher p vs ATTN |
|-------|---|---------|---------|-----------------|-----------------|
| MECHANICAL | 7 | 0.9 td | 0.004 | 100% | — |
| FORCED_SELL | 1 | 1.0 td | 0.013 | 100% | — |
| CONTESTED | 1 | 0.0 td | 0.002 | 100% | — |
| ATTENTION | 19 | — | — | 94.7% | p=0.679 |

**No verdict — human writes.**
