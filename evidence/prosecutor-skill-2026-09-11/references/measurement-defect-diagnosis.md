# Measurement Defect Diagnosis — Three-Phase Protocol

When a pre-registered test returns a negative result (KILL, STRUCTURAL_KILL, or
capture CIs overlapping random), do NOT immediately re-test with the same setup.
The first pass may be a FALSE NEGATIVE confounded by measurement defects. Run
Phase A (diagnosis) before any Phase B (fixes) or Phase C (re-test).

---

## Phase A — Diagnosis (no API spend, use cached results)

### A1 — Flag-level artifact detection

For every flag with extreme lift (err=1.00 or err=0.00), print 10 items with
full prompt, truth, and each model's raw answer. Determine which of:
- (a) Item is unanswerable as constructed (truncation, ambiguous units, missing info)
- (b) Judge rejects correct answers (tolerance, scale handling, schema enforcement)
- (c) Genuinely hard and models genuinely fail

**If (a) or (b):** these items are noise inflating every capture denominator.
Exclude or fix before re-testing.

### A2 — Scale-equivalence check

For every item where a model ANSWERED and was graded wrong, compute
`ratio = model_value / truth_value`. If ratios cluster at 1000 / 1e6 / 0.001,
the models are right about the figure and wrong about scale — the tolerance
test is broken. Fix the judge to accept scale-equivalent answers.

### A3 — Degenerate-arm detection (constant policy)

For each arm × task, compute abstention_rate (or any binary decision rate).
If rate > 90% or < 10%, the arm is applying a constant policy — item-independent.
No flag can predict a constant policy's errors.

Compute: what fraction of each arm's total errors come from tasks where the
model applied a constant policy? An arm above ~60% is effectively a null model
for routing purposes.

### A4 — Recompute capture with defects excluded

Using cached results only, recompute capture@25% for all four routers after:
- Dropping items from A1(a)/(b)
- Re-grading scale-mismatch answers as correct per A2
- Excluding degenerate arms from A3

Report before/after capture with CIs. If structural capture rises materially
once artifacts are removed, the original pass was a FALSE NEGATIVE.

---

## Phase B — Fixes

### B1 — Fix judge acceptance criteria

When models produce scale-equivalent answers (off by 10^k for k in {-6,-3,3,6}),
augment the judge to accept them. Record scale-corrected matches in
`Judgement.detail` as `"answered_correct_scaled"` so they are countable
separately.

### B2 — Fix unanswerable items

If A1 finds (a) (truncation, ambiguous units), fix the item generator. For
extraction-style tasks with unit conversion, generate exact multiples of the
scale factor so the displayed value is precise. Never use integer division
(`x // 1000`) for display — it loses precision.

### B3 — Force item-dependent decisions

When a task has a constant-policy problem (e.g., 100% abstention on a 50/50
balanced task), redesign the present-fact half to be directly answerable from
the prompt. Include the value in an excerpt for present-fact items; absent-fact
items get no excerpt.

**Verify in code before spending:**
- Constant-abstain policy scores ~50% (absent / total)
- A read-the-excerpt oracle scores ~100% (present items are directly answerable)

---

## Phase C — Pre-Registered Re-Test

### C1 — Write pre-registration before building

Write a `preregistration.md` file with:
- The date, bank specs, models, and budget
- Defects diagnosed and fixed (from Phase A)
- Each hypothesis with its metric, PASS threshold, and expected outcome
- Expected outcomes are for calibration, not scoring — write them honestly
- The protocol steps (build, estimate, smoke test, full arms, report)
- **DO NOT EDIT after seeing results**

### C2 — Pre-registered hypothesis structure

**H2-narrow** (the architecture's actual claim): Structural flags predict
COMMITMENT errors — fabrication events (answering on verifiably absent facts),
not arithmetic or extraction slips. Metric: capture@25% over fabrication events
only. PASS if >= 70% and CI excludes random.

**H2-broad** (retained for comparison): capture@25% over ALL errors. PASS if
>= 70% and CI excludes random.

**H3**: structural >= confidence, per arm, on non-degenerate arms only.

**H5-fit** (new — distinguishes "bad weights" from "bad flags"):
Split the bank 50/50 by seeded item hash. Fit FLAG_WEIGHTS by empirical error
rate on FOLD A only. Evaluate capture on FOLD B only. Report both folds.
PASS if fitted-weight capture on FOLD B >= 70% with CI excluding random.
This is the single most important test: if it passes, the flags carry signal
and the hand-set priors were wrong — a fundamentally different finding from
"structural routing fails."

### C3 — Interpretation rules

- If H2-narrow passes and H2-broad fails → thesis survives in narrowed form
  (flags predict fabrication, not general error)
- If H5-fit passes and unfitted fails → flags carry signal, priors were wrong.
  Do NOT report this as "structural routing fails"
- If Phase A4 shows capture rises materially after defect removal → original
  pass was a FALSE NEGATIVE. Say so plainly.
- If everything still overlaps random after all of the above → robust negative.
  The cheap-generation thesis is dead as specified. Do not narrow the claim
  further to rescue it.

---

## Example: CGSR Pass 3 (2026-07-22)

See CGSR pass 3 session for a worked example of this protocol:

- **A1**: UNIT_CONVERSION items had err=1.00 because `x // 1000` truncated
  displayed values, making the truth unrecoverable from the prompt.
  Verdict: (a) item unanswerable as constructed.
- **A2**: No scale mismatch found. Models that answered gave genuinely wrong
  answers (ratios 0.13-1.68, no 1000x pattern).
- **A3**: DeepSeek abstention_structural (100% constant-abstain, 33% of errors)
  and Kimi abstention_temporal (99% constant-abstain) were degenerate.
- **A4**: After removing defects, capture did NOT rise materially (Claude 23→20%,
  DeepSeek 23→37% but CI still overlaps random). Pass 2 was NOT a false negative.
- **B1**: Added scale-equivalent tolerance to extraction judge (defense-in-depth).
- **B2**: Fixed UNIT_CONVERSION truncation: generate exact multiples of 1000.
- **B3**: Made present-fact items directly answerable via excerpt-based prompting.
  Constant-abstain scores 51%; read-the-excerpt scores 100%.
- **C2**: H2-broad FAIL (KILL), H5-fit PASS (fitted capture 80-93% on fold B).
  The flags carry signal — the hand-set priors were wrong.

---

## D — Three-Bucket Error Taxonomy (LLM Output Grading)

When grading LLM outputs for error analysis in a Q3-type test, classify every
error into exactly one of three buckets. The MIX is the finding, not the
headline percentage:

| Bucket | Meaning | Catchable? | Oracle |
|--------|---------|------------|--------|
| **INPUT_FABRICATION** | Model used a quantity with no source: not in the prompt, not from a tool, not flagged as an assumption. The value was invented or retrieved from training data. | YES — provenance check | Input provenance checker (reject before it propagates) |
| **OMISSION** | A required analytical step was skipped or an implication missed. The claim was never made, so no oracle can check the claim itself — but the MISSING leaf can be flagged. | YES — completeness manifest | Required-leaves manifest (the task type requires this step) |
| **SILENT_JUDGMENT** | Correctly framed question, correct inputs, wrong conclusion. Ambiguous contract language, wrong risk attribution, wrong scenario weighting. | **NO** — not catchable by any oracle | D3 frontier dose (silent-error audit via frontier model) |

### Q3 Metrics

- **Q3_catchable** = (INPUT_FABRICATION + OMISSION) / total_errors
- **Q3_silent** = SILENT_JUDGMENT / total_errors

### Thresholds

| Q3_catchable | Verdict | Consequence |
|-------------|---------|-------------|
| >= 50% | PASS | L4/L5 buildable as specified |
| 30-50% | CONDITIONAL | D3 dose is load-bearing; measure its cost before committing to L5 |
| < 30% | FAIL | Silent judgment dominates; dosing economics do not close |

**n matters:** if fewer than 20 errors total, the result is underpowered. Report
the error count and say "n<20, cannot reliably measure" rather than reporting a
percentage.

### Provenance fix (2A)

Every quantity entering a computation must carry provenance:
- **PROMPT** — value appeared verbatim in the task input, with line reference
- **TOOL** — value came from a tool call, with output hash
- **DERIVED** — computed from other provenanced values, with the derivation shown
- **ASSUMPTION** — explicitly flagged with the letters [A], the assumed value, and
  the reasoner's best assessment of its plausibility

A quantity with none of these four is an INPUT_FABRICATION error. It is
**REJECTED at the point of use** — not flagged, not down-weighted, not routed
for verification. No oracle can correct a wrong input.

### Completeness manifest fix (2B)

Each decomposition carries a REQUIRED-LEAVES MANIFEST derived from the domain's
own rules and regulations — NOT from what the model happened to produce.

A missing required leaf is a DETECTABLE error (MISSING_REQUIRED_LEAF). This
converts an OMISSION (ordinarily silent) into something a completeness oracle
can fire on: if the manifest says the task type requires a 13(d)(3) group test
and the decomposition lacks one, the oracle flags it regardless of what the
model produced.

---

## E — G1 Degeneracy Test (Multi-Dimensionality Check)

When a fitted-weights test (H5-fit) reports strong capture, check whether the
signal is genuinely multi-dimensional or driven by a single dominant flag.

### Decisive test: held-out ablation

Rerun the H5-fit with the dominant flag **held out entirely**. If fold-B capture
collapses toward random, the question is settled.

**Validated on synthetic data:**
- Only `HARD_VARIANT` drives error: all flags 68%, minus dominant 26% (≈random) -> collapse detected
- Three flags drive error: all flags 42%, minus dominant 40% (holds) -> no collapse

### Per-model signature table

After the ablation, print per-model per-flag error rates. Only flags with
error rate > 0.15 carry signal. The signature is genuine if multiple,
non-overlapping flags carry signal across models.

### Effective rank (collinearity only)

`erank = exp(H(normalized eigenvalues))` — measures flag co-occurrence
collinearity, NOT the error-flag relationship. On synthetic data where ONE flag
drives all error, erank can read 5.99 (near-maximal) because the flags are
independent of each other. **Do NOT use erank to confirm multi-dimensionality.**
Report it for collinearity only.

### Decision rule

| Condition | Verdict |
|-----------|---------|
| Minus-dominant capture stays materially above random (>= 35% for budget=25%) | Required for PASS |
| >=2 flags carry error rate > 15% per model | Required for PASS |
| erank > 0.5 x max (collinearity check) | Informational only |

---

## F — G2 Decomposition Reality Test

Before building a corrective substrate on decomposed long-horizon tasks, verify
that the decomposition is real by measuring three independent quantities.

### Q1 — Oracle coverage

For every leaf in the decomposition, record:
| Field | Meaning |
|-------|---------|
| oracle_exists | yes / no |
| oracle_name | Specific — "SEC num.tsv lookup by (adsh, tag, ddate)", not "checkable" |
| oracle_type | deterministic / authoritative / constraint / consensus / none |

**Threshold:** >= 60% of leaves with oracle_exists = yes.

**Negative control:** Decompose 2-3 open-ended judgment tasks (no registry
backing). If those also score ~87% oracle coverage, the labeling is measuring
analyst generosity, not domain structure.

### Q2' — Backward path coverage (NOT edge count)

Scattered backward-informative edges are not enough. Belief propagation needs
a PATH from an oracle-covered leaf to each judgment leaf.

For each judgment leaf (oracle_exists = no):
- Does a backward-informative path exist from ANY oracle-covered leaf to it?
- **Strict test:** "If the child leaf is verified WRONG, what specifically
  changes about the parent's value?" A path that cannot answer this concretely
  is a restatement of the parent-child relation, not backward information flow.

**Threshold:** Q2' >= 50% of judgment leaves reachable.

**Common pitfall:** Most labeled backward-informative edges are actually
forward-specific — the child depends on the parent but the parent is invariant
to the child's value. The strict test (25% survival in one audit) reveals
substantial overstatement.

### Q3 — Error detectability (measured, not estimated)

Run the cheap model on all decomposed tasks at depth. Grade every error into
the three-bucket taxonomy (D above).

**Threshold:** Q3_catchable >= 50%.

**Depth gate:** If total spend is under $0.20, inspect the outputs. The model
may not be executing at depth. Re-run with a step-by-step forcing prompt before
grading.

### Overall decision

| Metric | Threshold |
|--------|-----------|
| Q1 — oracle-covered leaves | >= 60% |
| Q2' — backward path coverage | >= 50% |
| Q3 — catchable errors | >= 50% |

**PASS (all three met):** Decomposition is real. Build L4 (corrective substrate)
and L5 (dosing).

**FAIL (any one missed):** Decomposition is theater in this domain. Build L1-L3
only. Do NOT build belief propagation on a failed G2 — BP over a spurious graph
propagates confidence in noise with full mathematical rigor.

### Partial-failure readings

| Pattern | Diagnosis | Action |
|---------|-----------|--------|
| Q1 low, Q2/Q3 fine | Domain is oracle-thin | Fix by domain choice, not architecture |
| Q2 low, Q1/Q3 fine | Tasks are sequential, not networked | Build L4 without backward propagation |
| Q3 low, Q1/Q2 fine | Errors are silent judgment failures | D3 frontier dose becomes load-bearing; measure cost before proceeding |