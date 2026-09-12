# Terminal-Window Secondary Protocol (D-33-DIAG5)

**Context:** When the primary G-C test is unpowered due to panel
truncation (pre-death window too short for ≥8-quarter requirement),
a terminal-window secondary may still be feasible using the t-3..t
window (4 quarters before death). Must be labeled TERMINAL SIGNATURE,
never promoted to the primary's question.

## Design

1. **Population:** All CIKs with ≥1 quarter of FSNDS data in the
   4-quarter window [t-3, t] inclusive. No minimum quarter count;
   AM1 (present-as-is) applies.

2. **Metrics:**
   - Mean/median/max pressure (fq_pressure_share)
   - Mean/median degradation (fq_degradation sum)
   - Cond-B flag (any quarter in window)
   - Report median + dcml-filtered mean (trim top/bottom 2.5%)

3. **Registered verdict rule (2026-08-15):**
   Detection = |Cohen's d| >= 0.2 on median-based OR dcml-filtered
   metrics, AND bootstrap 95% CI for the median difference excludes 0.
   5000 iterations, bootstrap replaces with replacement within each
   group.

4. **Cond-B 100% handling:**
   If a metric is near-universal (≥99%) in both groups, state the
   reason and consider dropping it from the comparison. In D-33,
   cond-B tracks NT 10-Q/10-K delinquency — a near-universal
   precursor to all terminal events in dead firms. Non-discriminating.

5. **AM3 confound disclaimer (mandatory):**
   "Terminal signatures reflect exit mechanics (court filings,
   creditor negotiations, asset sales), not attention-driven
   selectivity. This result is labeled TERMINAL SIGNATURE and
   never promoted to the primary's question."

## Rerun Behavior

If the user says "TERMINAL RERUN, registered thresholds," re-run
with the exact registered rule and compare against the prior
verdict. The prior verdict stands only if it survives the rerun.
Report both outcomes.

## Bootstrap Methodology (Cluster, Firm-Level)

**Critical lesson from D-33-DIAG5 (rejected run):** Bootstrap must
resample at the FIRM level (cluster bootstrap), not at the
observation level, for panel data where firms contribute multiple
quarterly observations.

**Correct procedure:**
1. Each firm contributes a vector of terminal-window quarter values
   (pressure, degradation, cond-b). Keep these vectors intact.
2. Resample FIRMS with replacement (n_bk firms from BK group,
   n_vdfc firms from VD+FC group), keeping all quarterly data per
   sampled firm.
3. Compute the metric (median pressure, filtered mean, etc.) from
   the resampled firm-level aggregates.
4. Repeat 2,000+ draws. Compute percentile CI (2.5%, 97.5%).
5. Each metric gets its OWN CI from its own set of resampled
   values. Identical CI bounds across metrics = bootstrap bug.

**§1.4-adjacent harness assertion:**
  "A d outside its own CI is an impossible number."
  After computing the point estimate and bootstrap CI, assert:
  `if ci_lo <= d_point <= ci_hi: PASS, else: FAIL (impossible)`
  This catches bootstrap implementation bugs where the resampling
  procedure doesn't match the point-estimate computation.
  If FAIL, halt and fix — do not report the result.

**Signs of wrong bootstrap:**
- CI bounds identical or near-identical across different metrics
- Median pressure and filtered pressure produce the same CI
- CI width is suspiciously narrow for the sample size
- Point estimate falls outside the CI (harness assertion catches this)

**Prior run bug (D-33-DIAG5 first attempt):**
The first bootstra ran observation-level resampling (mixing firms'
quarters independently), producing CI bounds [0.02, 0.15] for
both median pressure and filtered mean pressure — an impossible
identical-CI artifact. The cluster bootstrap (firm-level) produced
correct distinct CIs [0.0234, 0.2768] and [0.0197, 0.2691].