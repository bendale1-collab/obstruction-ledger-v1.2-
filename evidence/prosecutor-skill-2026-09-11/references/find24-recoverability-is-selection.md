# FIND-24: Recoverability is Selection

**Permanent finding — applicable to any retrospective data reconstruction task where the data of interest is from dead/defunct entities.**

## Statement

Recoverability from historical archives is NEVER random with respect to the signal of interest. It is biased BY THE MECHANISM THAT MAKES RECOVERY POSSIBLE.

Specifically: when reconstructing ticker/CUSIP/identifier mappings for defunct entities from free public archives:

- Entities that left more footprints (more SEC filings, exchange listings, CUSIP assignments) are easier to recover
- Those footprints are correlated with visible survival (longer listing history, more analyst coverage, institutional interest)
- Visible survival under pressure approximates the exposure construct being tested
- Therefore: the recovered set is systematically more "visible/pressured" than the unmapped set

## Quantitative evidence (D-30 → D-31 → D-32 campaign, 2026-08)

| Metric | D-30 baseline | D-31 (Route 3) | D-32 (FTD + all) |
|--------|:------------:|:--------------:|:----------------:|
| Coverage (dead CIKs) | 42.5% | 52.2% | 52.3% |
| Pressure ratio (rec/unm) | 2.73x | 2.04x | 2.04x |
| Exposure ratio (rec/unm) | 2.03x | 1.62x | — |
| Effort invested | 0 new routes | 3 routes | +3 more |
| Result | Biased | Still biased | Still biased |

Each recovery campaign improved coverage but did not eliminate selection. The residual unmapped are genuinely lower-pressure firms that no free public resource reaches.

## Implication for research design

1. **Do not confuse "coverage enough" with "selection eliminated."** Coverage of 52% cleared the 50% bar but selection still failed the 1.5x bar. The two metrics address different dimensions of the same problem.

2. **Contemporaneous recording is the only cure.** Data recorded at the time the entity was alive (CRSP-class, audited financials in real-time) has no selection bias from historical reconstruction — because no reconstruction was needed. This is why CRSP costs thousands: the price is proportional to having been there first.

3. **Free routes converge on the same biased tail.** Every public free route (SEC current ticker file, 2016 snapshot, EDGAR filing text searching, 8-K header SGML, FINRA OTC list, SEC FTD archive) targets the same population — firms that were exchange-listed and left clear footprints. The OTC fringe that comprises the unmapped tail is invisible to all of them.

4. **A commercial mapping (EODHD, CapitalIQ, Compustat) adds coverage but does NOT fix selection.** The commercial product is built from the same public archives, just with better parsing. It adds names closer to the exchange-listed edge of the tail, not the deep OTC fringe. Selection ratios improve but may not cross any fixed bar.

## When this law applies

Any task that:
- Uses historical archives to reconstruct identifiers or data for a cohort that includes defunct entities
- Where the archive's inclusion criteria are correlated with the entity's survival or market visibility
- Where "missing data" is treated as an error to be fixed rather than a signal to be characterized

## Counterexamples (when this law does NOT apply)

- Forward/live data collection on active entities (D-28 forward panel): no reconstruction needed, no selection from archival coverage
- Archival data that was recorded contemporaneously for ALL entities in the universe (CRSP, Compustat) — the cost of admission was paid at the time of recording