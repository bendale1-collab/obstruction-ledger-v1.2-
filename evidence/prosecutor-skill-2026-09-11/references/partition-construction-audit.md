# Partition-Construction Audit (D-33-DIAG4 Methodology)

**Context:** A binary partition variable that produces a "perfect" or
near-perfect separation (e.g., 100% concentration of BK in "pressured"
deaths) must be traced to its construction before the finding can be
trusted. A tautological partition (pressure derived from death type,
not an independent continuous metric) produces an identity, not an
empirical discovery.

## Trace Protocol

When a binary partition aligns suspiciously well with an outcome:

1. **Code-path exhibits** — Quote the exact lines that built the
   partition variable from every version of the script that ran.
   This settles whether the continuous source metric was ever
   consulted or whether the partition was derived from the target
   labels.

2. **Unmatched-population trace** — For every observation that has
   no source metric data, report what value (or default) was
   imputed and which cell they occupied in the final table. If
   20%+ of the table is imputed with no source data, the
   partition may be a labeling artifact.

3. **Raw continuous distribution** — Plot or decile-report the
   underlying continuous metric separately for each side of the
   binary partition. If the distributions are nearly identical
   (median within 0.01, >40% cross-median overlap), the binary
   partition carved an arbitrary boundary and the claimed
   separation is a cut artifact.

4. **Threshold scan** — Report what fraction of each class lands
   above/below the binary threshold at every 5-percentile step.
   If no threshold produces the claimed partition, the binary
   variable was not derived from the continuous metric.

## Example (D-33-DIAG4)

**Claim:** G-B found 100% bankruptcy concentration in "pressured"
deaths (∞x ratio).

**Trace:**
1. Code exhibited from 3 script versions. Every version defined
   `pressured = {c for c, v in classification.items() if v['type']
   in (2,3,4)}` — derived from death type, not the continuous
   fq_pressure_share metric.

2. 728/3,063 (24%) classified CIKs had zero FSNDS data. Their
   partition cells were imputed from death type alone (133→ACQ,
   460→VD, 83→FC, 52→BK).

3. Raw mean-pressure distributions: ACQ median=0.115, non-ACQ
   median=0.125. 52% of non-ACQ firms above ACQ median. Nearly
   identical.

4. No threshold on the continuous fq_pressure_share metric
   (0.05-0.95, step 0.05) produces unpressured ≈ ACQUIRED.

**Result:** G-B = RETROACTIVE VOID (tautology from birth).