# Cluster Bootstrap Method (firm-level resampling)

**When:** Computing effect sizes (Cohen's d) on firm-level metrics where each firm contributes multiple observations. Standard bootstrap (resampling individual observations) overstates precision because firm-quarter observations are not independent.

**Procedure:**

1. For each firm, compute the firm-level metric (median of its terminal-window values, filtered mean, etc.)
2. Resample FIRMS with replacement (not firm-quarters). Each draw takes n firms from the BK group and m firms from the comparison group, with replacement, keeping all of each firm's data.
3. Compute the metric (e.g., median of firm-level medians) from the resampled firms.
4. Compute Cohen's d from the firm-level metric values.
5. Repeat 2,000 draws.
6. Get percentile CI: sort all d values, take 2.5th and 97.5th percentiles.

**Harness assertion (permament):** The point estimate d (from the full sample) MUST be inside its own bootstrap CI. If it falls outside, the statistic is impossible — raise, do not report.

**Distinctness check:** Each metric produces its own CI. Identical CI bounds across metrics = failed run. Do not reuse the same bootstrap sample for different metrics.

**Registered verdict rule:** Detection = |d| >= 0.2 AND CI excludes 0 on median-based or filtered metrics. One verdict line. Prior verdicts are superseded by the rerun.

**Implementation pattern (Python):**
```python
def cluster_bootstrap(bk_firms, vdfc_firms, metric_fn, n_draws=2000):
    bk_ids = list(bk_firms.keys())
    vdfc_ids = list(vdfc_firms.keys())
    d_draws = []
    for _ in range(n_draws):
        bk_sample = {c: bk_firms[c] for c in random.choices(bk_ids, k=len(bk_ids))}
        vdfc_sample = {c: vdfc_firms[c] for c in random.choices(vdfc_ids, k=len(vdfc_ids))}
        bk_vals = [metric_fn(bk_sample[c]) for c in bk_sample]
        vdfc_vals = [metric_fn(vdfc_sample[c]) for c in vdfc_sample]
        d_draws.append(cohens_d(bk_vals, vdfc_vals))
    d_draws.sort()
    ci = (d_draws[50], d_draws[1950])  # 2.5% and 97.5% for 2000 draws
    return d_point, ci, d_draws
```