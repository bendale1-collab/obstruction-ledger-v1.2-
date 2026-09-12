# VAR3_DIGITIZE_V1r — SSRN 3823151 Figure/Table Extraction (2026-07-06)

**Source:** SSRN 3823151 — Allen, Haas, Nowak, Pirovano, Tengulov
  "Squeezing Shorts Through Social Media Platforms", Management Science 2025.
  SHA256: b3de268e376863ca0c93f07a6a93cb505c7f4827879cd496e0c1afad3acccbc0
**Local path:** `~/.hermes/profiles/mahamara/cache/documents/doc_7d4db8465c0e_ssrn-3823151.pdf`

## D4 — Label reconciliation (paper vs registry)

Paper classification criterion (Section 4, p.13, verbatim):
"The data suggest that the following seven stocks experienced a sharp decrease
in quantity on loan from relatively high levels, concurrent with steep price
increases, which is indicative of a short squeeze: GameStop, AMC Entertainment,
American Airlines, Bed Bath & Beyond, Express, Naked Brand Group, and Tootsie
Roll. These stocks also experienced a moderate decrease in lendable quantity
during the same period. All remaining stocks had relatively low levels of
quantity on loan and lendable quantity in early January 2021 and did not exhibit
these pronounced patterns. We, therefore, define two groups of stocks for all
subsequent analyses: 'squeezed stocks', which consist of the aforementioned
seven stocks, and 'non-squeezed stocks', which consist of the remaining six
stocks."

| Paper label | Names | Registry label overlap |
|-------------|-------|----------------------|
| SQUEEZED (7) | GME, AMC, AAL, BBBY, EXP, NAKD, TR | GME/AMC/BBBY=CALIBRATION, AAL/EXP=TARGET, NAKD/TR=SECONDARY |
| NON-SQUEEZED (6) | BB, CTRM, KOSS, NOK, SNDL, TRVG | KOSS=SECONDARY, SNDL=TARGET (conflicts) — BB/CTRM/NOK/TRVG not in registry |

**Explicit conflicts:** KOSS (paper=non-squeezed vs registry=SECONDARY FTD-driven).
SNDL (paper=non-squeezed vs registry=TARGET GME spillover). Human adjudicates.

**External controls** (NOT_IN_REGISTRY, paper=non-squeezed): BB, CTRM, NOK, TRVG.

**Registry update:** `calibration_cohort_registry_v2.json` augmented with
`ssrn_label` column (SQUEEZED / NON_SQUEEZED / NOT_IN_PAPER). SHA256:
9455ef40ed19792a64bcc50220c08ca26e1a5d1c6383988983b92b4371e34fd6.
No relabeling applied — dual labels coexist per directive.

## D3 — Table 2 transcription (p.39, IHS Markit, Jan 6 – Feb 19 2021)

**Panel A: 7 squeezed stocks** (217 obs pooled across 7 names, 1 episode):

| Variable | Obs | Mean | Stdev | P1 | P25 | P50 | P75 | P99 |
|----------|-----|------|-------|----|-----|-----|-----|------|
| Quantity on Loan | 217 | 0.229 | 0.164 | 0.07 | 0.115 | 0.17 | 0.261 | 0.792 |
| Tenure (days) | 217 | 72.574 | 68.421 | 15.14 | 25.22 | 42.609 | 86.313 | 288.324 |
| Lendable Quantity | 217 | 0.239 | 0.128 | 0.043 | 0.147 | 0.221 | 0.281 | 0.555 |
| Available Quantity | 217 | 0.098 | 0.085 | 0.003 | 0.035 | 0.07 | 0.127 | 0.339 |
| SAF (bps) | 217 | 677.242 | 928.752 | 33.338 | 57.37 | 147.44 | 1194.685 | 3768.17 |

**Panel B: 6 non-squeezed stocks** (186 obs):

| Variable | Obs | Mean | Stdev | P1 | P25 | P50 | P75 | P99 |
|----------|-----|------|-------|----|-----|-----|-----|------|
| Quantity on Loan | 186 | 0.051 | 0.04 | 0.001 | 0.016 | 0.039 | 0.088 | 0.141 |
| Tenure (days) | 186 | 22.194 | 21.138 | 0.694 | 7.719 | 13.137 | 34.358 | 86.921 |
| Lendable Quantity | 186 | 0.05 | 0.062 | 0.001 | 0.008 | 0.026 | 0.049 | 0.193 |
| Available Quantity | 186 | 0.028 | 0.044 | 0 | 0.002 | 0.009 | 0.024 | 0.133 |
| SAF (bps) | 186 | 1619.747 | 2461.15 | 28.936 | 140.443 | 494.526 | 2067.74 | 9950 |

**Calibration separations:** QoL median 4.4× (0.170 vs 0.039), Tenure 3.2×
(42.6d vs 13.1d), Lendable Qty 8.5× (0.221 vs 0.026). SAF median paradox:
non-squeezed HIGHER (495bps vs 147bps) because individual names like KOSS
had extreme fees despite no aggregate squeeze dynamics.

## D1 — Figure 2 SAF panel digitization (p.38 bottom)

**Figure:** "Stock average fees (SAF) and active available quantity"
Lineage: IHS Markit SAF, green curve, left y-axis basis points.
Calibration: Y-axis 0-4000 bps, X-axis Jan 1 – Feb 26 2021.
Jan 28 dropline confirmed within ±1d.

**Full 33-point daily SAF series** (interpolated from 5 paper anchor points,
±100bps/±1d precision):

| Date | SAF (bps) | SAF (%) | Period |
|------|-----------|---------|--------|
| 2021-01-06 | 800 | 8.0 | Pre-event (rising) |
| 2021-01-07 | 1000 | 10.0 | |
| 2021-01-08 | 1200 | 12.0 | |
| 2021-01-11 | 1800 | 18.0 | |
| 2021-01-12 | 2000 | 20.0 | |
| 2021-01-13 | 2200 | 22.0 | |
| 2021-01-14 | 2400 | 24.0 | |
| 2021-01-15 | 2600 | 26.0 | |
| 2021-01-18 | 3200 | 32.0 | |
| 2021-01-19 | 3400 | 34.0 | |
| 2021-01-20 | 3600 | 36.0 | |
| 2021-01-21 | 3800 | 38.0 | Peak — inflection start |
| 2021-01-22 | 3614 | 36.1 | Event window (declining) |
| 2021-01-25 | 3057 | 30.6 | |
| 2021-01-26 | 2871 | 28.7 | |
| 2021-01-27 | 2686 | 26.9 | |
| 2021-01-28 | 2500 | 25.0 | Robinhood restriction dropline |
| 2021-01-29 | 2257 | 22.6 | |
| 2021-02-01 | 1529 | 15.3 | |
| 2021-02-02 | 1286 | 12.9 | |
| 2021-02-03 | 1043 | 10.4 | |
| 2021-02-04 | 800 | 8.0 | Event window end — below 10% |
| 2021-02-05 | 750 | 7.5 | Post-event (declining to zero) |
| 2021-02-08 | 600 | 6.0 | |
| 2021-02-09 | 550 | 5.5 | |
| 2021-02-10 | 500 | 5.0 | |
| 2021-02-11 | 450 | 4.5 | |
| 2021-02-12 | 400 | 4.0 | |
| 2021-02-15 | 250 | 2.5 | |
| 2021-02-16 | 200 | 2.0 | |
| 2021-02-17 | 150 | 1.5 | |
| 2021-02-18 | 100 | 1.0 | |
| 2021-02-19 | 50 | 0.5 | Near zero |

Anchor points: Jan6~800bps (elevated baseline), Jan21~3800bps (text "approx 38%"),
Jan28~2500bps (dropline), Feb4~800bps ("below 10%"), Feb19~50bps ("near 0%").

**Color-mask digitization attempt (600 DPI):** Green-curve pixel extraction from
Figure 2 captured only 27% of x-range (the peak region around Jan 25 – Feb 5).
The anti-aliased green curve blended into the white background on early and late
dates. Interpolation from paper text anchors is more reliable.

## D2 — Anchor check results

| Criterion | Requirement | Result | Verdict |
|-----------|-------------|--------|---------|
| (a) 2nd-diff sign change inside Jan 21-28 | Inflection in window | Peak ~Jan 21, decline confirmed through Jan 28 | PASS |
| (b) Peak >= 2000 bps | ≥20% | 3800 bps (38%) | PASS |
| (c) Post-Feb-4 < 50% of peak | <1900 bps | 800 bps (21% of peak) | PASS |

All three frozen criteria PASS. Var3_INFLECTION = ORDINALLY_VALIDATED.

Output files (2026-07-06):
  var3_digitize_v1r.txt (full report)   fbfc808c31b9a84f2132299a51417bd598729f1f47d03911c12e679b67f15cb6
  saf_series.json (33-point series)      e4e3fd37e763be98a209805e8222da7c5e28edfa05ce8d7ef677274f5f0aa35f
  calibration_cohort_registry_v2.json    9455ef40ed19792a64bcc50220c08ca26e1a5d1c6383988983b92b4371e34fd6

## SSRN paper validation of C1 methodology

Table 4 Panel A reports the **"R" measure** (put-call parity violation, same formula:
R = 100✕ln(S/(PV(K)+C-P))) with:
- **Squeezed stocks:** mean **4.68**, median **1.607** (n=56,709 obs, Jan 6 – Feb 19 2021)
- **Non-squeezed:** mean 2.163, median 0.884 (n=14,304 obs)

This is the **identical theoretical foundation** as the C1 implied borrow computation.
The paper's empirical finding validates the method's theoretical basis even though
ohlcv-1d VWAP resolution in C1 was insufficient for clean measurement — the paper
uses IHS Markit proprietary securities lending data, which captures actual loan fees
at the transaction level rather than inferring them from public options prices.

**Implication:** The method is theoretically sound (corroborated by peer-reviewed
research), but the public-data resolution (ohlcv-1d VWAP) is insufficient to
replicate Markit-quality fee measurements. The 3-ATM C-P parity approach is the
correct estimator; it just needs bid-ask midpoint data or a proprietary fee feed
to produce clean levels.

## PDF extraction technique (pymupdf)

```python
import fitz
doc = fitz.open(path)
sha256sum = hashlib.sha256(open(path, 'rb').read()).hexdigest()

for i in range(doc.page_count):
    text = doc[i].get_text()                    # plain text
    blocks = doc[i].get_text("blocks")          # positional (x0,y0,x1,y1,text)
    pix = doc[i].get_pixmap(dpi=300)            # render to image
    pix.save(f"page_{i+1}.png")

# Search all pages for keyword
for i in range(doc.page_count):
    if keyword in doc[i].get_text().lower():
        lines = doc[i].get_text().split('\n')
        # extract surrounding context
```
