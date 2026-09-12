# CGSR Evaluation Harness — PROSECUTOR Instantiation

The CGSR (Commodity Generation under Structural Routing) harness is a concrete
instantiation of the PROSECUTOR framework for LLM evaluation. It tests whether
model-independent structural flags predict commitment errors well enough to
route verification, so a cheap model plus verification beats an expensive model
plus light verification.

## Execution sequence (frozen-spec pattern)

1. **selftest** — offline validation. Judges must accept truth AND reject
   corruption. A judge that accepts everything makes every arm look perfect.
2. **fetch** — download external corpora (SEC Financial Statement Data Sets,
   GLEIF LEI registry). ~10 MB for 400 filings. SEC requires descriptive User-Agent.
3. **build** — create sealed item bank with fingerprint. Must match across arms.
4. **estimate** — pre-flight cost via OpenRouter live price table. Stop if > $5.
5. **smoke** — run 5 items with `--limit 5 --max-spend 0.25`. Must be 0 parse-fail.
6. **full arm** — `--max-spend 5` per arm. Cache on (model, messages, temp, max_tokens, response_format).
7. **report** — capture@budget with bootstrap CIs, per-flag lift, gate verdicts.

## Key techniques

### Scale-equivalent tolerance (numeric judges)
When a model answers a numeric extraction question, it may be off by a factor
of 10^k (thousands vs millions, dollars vs cents). Accept answers where
`|v*10^k - truth| <= tol` for k in {-6, -3, 3, 6}. Record as `answered_correct_scaled`
so they are countable separately.

### Blocking: Kimi K2 needs --no-json-mode
The Novita provider routes `moonshotai/kimi-k2-instruct` which does NOT support
structured outputs (`response_format: json_object`). Use `--no-json-mode` for
this model. Rate-limit at 2.0 req/s (not 4.0) to avoid 429 errors.

### Abstention prompt design (answerable present-fact items)
To make abstention items non-degenerate:
- Present-fact prompts: include the exact value in an excerpt
  `"Excerpt: ShareBasedCompensation (tag ...): 123456789"`
- Absent-fact prompts: say `"(This filing does not contain a figure for ...)"`
- Constant-abstain should score ~50%. Verify in code.
- Read-the-excerpt oracle should score ~100%.

### UNIT_CONVERSION truncation trap
When generating extraction items with `units_thousands=True`, integer division
(`x // 1000`) loses precision. Generate exact multiples of 1000 instead:
`rev = base * 1000` where `base = rng.randrange(50, 900)`. The displayed value
is then `rev // 1000` which is exact.

### Confidence default on abstention
When a model returns `{"abstain": true}` without a `confidence` field, default
to 0.5 rather than rejecting the row. Done in `parse_json_strict`.

---

## G1 — Degeneracy Test (is the router one-feature or multi-dimensional?)

Tests whether structural flags form independent axes or one flag does all the work.

### Decisive test: held-out ablation
1. Split bank 50/50 by seeded item hash (fold A / fold B).
2. Fit logistic regression weights on fold A.
3. Evaluate capture@25% on fold B.
4. Re-run with the DOMINANT flag held out.
5. If minus-dominant capture collapses toward random (< budget + 0.10):
   **COLLAPSE detected** — one-feature classifier. The router is not
   multi-dimensional.
6. If minus-dominant capture stays materially above random:
   **No collapse** — flags are genuinely multi-dimensional.

### Validation on synthetic data with known ground truth:
| Data | All flags | Minus dominant | Verdict |
|------|-----------|----------------|---------|
| Only HARD_VARIANT drives error | 68% | 26% (≈random) | collapse detected ✓ |
| Three flags drive error | 42% | 40% (holds) | no collapse ✓ |

### Supplementary: per-model signature table
Report per-flag error rates per model. If ≥2 flags carry error rate > 15% per
model, the flags are multi-dimensional. If only one flag > 15%, the
architecture is rank-1 in signal.

### Effective rank (collinearity only, NOT the degeneracy test)
`erank = exp(H(normalized eigenvalues))` on the flag design matrix. Measures
flag co-occurrence collinearity. NOT sufficient for the degeneracy question:
on synthetic data where ONLY HARD_VARIANT drives error, erank was 5.99
(near-maximal for 6 flags) because the flags are independent of each other.
The degeneracy is in the error-flag relationship, which erank cannot see.

Report erank for collinearity only. Do not rely on it for the verdict.

### Per-flag lift table (pooled across models)
`lift = err_rate(flag) / base_error_rate`. Flags with lift < 1.0 are
present on items where models succeed — they are overweighted by the priors.
Flags with lift > 2.0 carry strong signal.

---

## G2 — Decomposition-Reality Test

Tests whether ambitious long-horizon decomposition is buildable in a domain.

### Three questions

**Q1 — Do leaves hit real oracles?**
For each leaf in the dependency graph, record:
- oracle_exists: yes/no
- oracle_name: the specific verifier (e.g., "SEC num.tsv lookup", not "checkable")
- oracle_type: deterministic / authoritative / constraint / consensus / none
- est_p_s: honest estimate of oracle soundness

Q1 metric: fraction of leaves with oracle_exists = yes.
Threshold: ≥ 60%.

**Q2 — Are edges backward-informative?**
For each edge, classify:
- forward-only: parent constrains child, child says nothing about parent
- backward-informative: verifying the child revises belief in the parent
- bidirectional: constraint couples both

Q2' metric: fraction of JUDGMENT leaves reachable by a backward-informative
path from ANY oracle-covered leaf. NOT the raw edge count — scattered
backward edges buy nothing if they never link a verifiable leaf to an
unverifiable one.

Threshold: Q2' ≥ 50% of judgment leaves reachable.

**Q3 — Are cheap-model errors detectable?**
Run the cheap model end-to-end on the task set. Grade by hand. For every error:
- error_type: factual / arithmetic / entity / retrieval / judgment / omission
- detectable_by: a NAMED oracle, or SILENT
- step_index: where it entered
- propagated: did it corrupt downstream steps?

Q3 metric: fraction of errors with a named detector (not SILENT).
Threshold: ≥ 50%.

### Decision rule
| Metric | Threshold | Verdict |
|--------|-----------|---------|
| Q1 — oracle-covered leaves | ≥ 60% | PASS |
| Q2' — backward paths to judgment leaves | ≥ 50% | PASS |
| Q3 — oracle-detectable errors | ≥ 50% | PASS |

All three must pass for L4/L5 to be buildable.

### Negative control tasks
To validate that Q1 is measuring the domain and not the analyst's generosity:
hand-decompose 2-3 tasks you EXPECT to fail (open-ended judgment work with
no registry backing). If those also score ~87% oracle coverage, the labeling
is generous, Q1 is measuring the analyst rather than the domain, and the
G2 PASS is suspect.

### Domain scope
State the domain in every claim. "Decomposition is real in oracle-dense
financial/regulatory data" — not "decomposition is real" generically.

---

## H5-fit Protocol — Distinguishing "bad weights" from "bad flags"

When structural routing fails with hand-set priors, the question is whether
the flags carry signal and the weights are wrong, or the flags themselves
are uninformative.

### Protocol
1. Split bank 50/50 by seeded item hash (fold A / fold B).
2. Fit FLAG_WEIGHTS by logistic regression of error on flags using FOLD A only.
3. Evaluate capture@25% on FOLD B only.
4. Report both folds' capture.

### Interpretation
| Result | Meaning |
|--------|---------|
| Fitted capture on fold B ≥ 70% with CI excluding random | Flags carry signal. Priors were wrong. |
| Fitted capture on fold B overlaps random | Flags are uninformative for this task set. |
| Fold A >> Fold B | Overfitting — weights don't generalize. |

### If fitted weights differ from priors:
Report the fitted weights next to the priors. The per-flag delta (which flags
were underweighted, which were overweighted) is itself a finding. For example,
HARD_VARIANT at 2.5 with actual error rate 58% should be ~5.8; EVIDENCE_ABSENT
at 3.0 with actual error rate 1% should be ~0.0.