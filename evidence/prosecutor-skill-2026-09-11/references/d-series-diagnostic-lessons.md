# D-Series Diagnostic Lessons

Portable findings from the D-33 campaign (2026-08-15) that apply to future PROSECUTOR work.

## 1. FIND-28: BY-CONSTRUCTION label

Any finding whose evidence is the spec's own framing (not an external measurement) inherits the BY-CONSTRUCTION label. The test:

> Was a continuous measurement pipeline consulted, or was the result produced by the spec's own definitions?

**Type specimen**: C-24. G-B's partition assigned "pressured" by death type (code `v['type'] in (2,3,4)`). The "perfect" 2x4 partition was an identity — BK ∈ pressured by definition. The claim "BK concentrates in pressured" was true because the code made it true. Continuous fq_pressure_share was never consulted.

**When to raise**: The verdict table shows a perfect separation (100%, 0, ∞) and the separation boundary matches the spec's own category definitions. Always trace the code path before reporting such a result.

## 2. Verdict labeling rules (applied from C-21, C-22, D-33 close)

| Wrong label | Right label | When |
|-------------|-------------|------|
| DEFERRED | **BLOCKED**(reason) | A gate's prerequisite is unverified (e.g., "exposure join unverified") |
| DEFERRED | **UNMEASURED**(reason) | The data cannot answer (e.g., "underpowered at pole", "era boundary") |
| NOT_DETECTED (then superseded) | Rerun verdict **supersedes** — no "prior standing" alongside | The rerun is the verdict; the prior is struck |
| ∞ (infinite) | Continuity-corrected finite value + §1.4 auto-flag | Exact extremes are always the instrument until proven otherwise |

## 3. Cluster bootstrap methodology (firm-level)

When comparing two groups on panel data (e.g., BK vs VD+FC terminal signatures):

- **Resample FIRMS** (clusters), not individual observations. Each firm's entire terminal window stays together.
- **2,000 draws** minimum. Percentile CI (2.5%, 97.5%).
- **Assertion harness**: the point estimate MUST be inside its own 95% CI. If not, the metric is impossible — raise immediately.
- **Four distinct CIs for four distinct metrics**. Identical bounds across metrics indicates a bug (the CI was computed from shared resamples, not per-metric).
- **Cohen's d** from firm-level aggregated values (median or filtered mean per firm), not from pooled observations.

## 4. Code-path trace (diagnostic pattern)

When a verdict depends on a code path (e.g., "was the partition by death type or by continuous metric?"):

1. Locate the exact lines that produced the table/output
2. Quote them verbatim with file name and approximate line number
3. State what the code computes vs what the output appears to show
4. If the code computes an identity, the "finding" is a spec artifact

**Applicable to**: any BY-CONSTRUCTION suspect, any perfect separation, any zero-or-100% cell.

## 5. SELF-CHECK block (output format)

Every gate block ends with:

```
SELF-CHECK
numbers_emitted / numbers_with_source_tag / spans_quoted /
spans_verified_by_code / unmeasured_emitted / trials_consumed /
direction / gate_result: PASS | FAIL | UNMEASURED | n/a
```

- `numbers_emitted != numbers_with_source_tag` → output invalid, say so, stop.
- `direction`: toward-continuation | toward-stopping, with one-line justification for any continuation-direction change.
- `trials_consumed`: increment only when primary cells are redefined (§4).