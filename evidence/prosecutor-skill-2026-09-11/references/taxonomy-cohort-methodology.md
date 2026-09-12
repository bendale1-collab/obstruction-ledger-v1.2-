# TAXONOMY COHORT TEST METHODOLOGY

## MECHANICAL vs ATTENTION_ONLY classification

Per amended research taxonomy: MECHANICAL = a filed deadline forcing delivery of shares. Qualifying actions:

| Action | Example | File Type | 
|--------|---------|-----------|
| Record date (dividend/vote) | Creates settlement deadline for lenders to recall | DEF14A, 8-K |
| Dividend (in-kind strongest) | OSTK blockchain dividend forced covering via digital security | 8-K |
| Offering pricing | Dilution deadline forces covering if shares borrowed for offering | 424B |
| Merger closing/election | Share exchange deadline forces delivery | 8-K, S-4 |
| Ch.11 EMERGENCE | Debt-for-equity conversion deadline (NOT Ch.11 filing) | Form 25, plan confirmation |
| Stock split | Share recertification deadline | 8-K, DEF14A |

**NOT MECHANICAL:**
- Announcements (no filing deadline)
- 13D filings (activist stake = passive, not deadline-forcing)
- Ch.11 FILING (the restructuring process = no immediate delivery deadline)

## EDGAR trigger search

For each event, search EDGAR in [-45d, +5d] around onset for qualifying forms:

```python
r = requests.get("https://efts.sec.gov/LATEST/search-index",
    params={"q": ticker, "startdt": ws, "enddt": we,
            "category": "form-cat1,form-cat2,form-cat3"},
    headers={"User-Agent": "research <email>"}, timeout=15)
```

Qualifying forms: 8-K, 424B, DEF14A, Form 25, S-1/A. A single qualifying form in the window → MECHANICAL with cited accession number. None → ATTENTION_ONLY.

## Special cases

**HTZ split-event:** Onset 2020-05-26 is the Ch.11 FILING date, not the EMERGENCE date (June 30, 2021). The amended taxonomy says MECHANICAL = emergence, not filing. The 2020 onset episode may be mis-classified or belong to a different episode. The 2021 emergence is a separate episode not in the current registry.

**OSTK blockchain dividend:** Two episodes: (1) July 2019 dividend announcement, (2) Aug 2020 second squeeze wave on OSTKO trading. Same dividend mechanics, different episodes. The registry onset (2020-08-26) is the second episode. EDGAR search for the first episode's dividend filing (8-K) would be in July 2019, not the Aug 2020 window.

## Pre-registered read

- If >50% of events have qualifying filings in window → trigger channel is viable
- If 0/22 events qualify → either: (a) taxonomy too strict, (b) all events are genuinely ATTENTION_ONLY, (c) onset dates are wrong (different episode)
- MECHANICAL events are the test class; ATTENTION_ONLY are the control class
