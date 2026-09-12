# Input Parity Check & F1 Independence Rule

**Source:** MVI Loop Program — F1 gate repair, 2026-07-24
**Defect discovered:** Reader models (Mistral, Claude, Gemini, Qwen) all classified F1.2 as UNRESOLVABLE while the classifier (DeepSeek) said MATCHED. The parsimonious conclusion appeared to be leniency — but the inputs differed. The reader models received a short human-written summary (~50 words); the classifier received the full PubMed abstract (~400 words). Neither was wrong — the inputs differed.

## The pipeline defect

When comparing model outputs, **input parity is the first thing to check, not the last.** If the inputs are not identical, the comparison is void regardless of the outputs.

### Protocol

1. For every model call (classifier, reader, auditor), record the exact input payload per field as a hash:
   - Input payload hash = SHA256 of serialized prompt
   - Per-field hash: SHA256 of each field (registry PO text, publication text, prompt preamble, system prompt)
2. Before comparing any two models' outputs, verify the hashes match per field.
3. If any field differs → **PIPELINE DEFECT**. Stop. Fix parity, re-run all models on identical inputs, disregard the original comparison entirely.

### Common sources of input disparity

| Source | Example | Detection |
|--------|---------|-----------|
| Shortened publication text | Readers get title only; classifier gets full abstract | Compare text length, hash |
| Different registry field | Readers get measure names; classifier gets full ClinicalTrials.gov descriptions | Compare per-field inputs |
| Different prompt preamble | Readers get short prompt; classifier gets detailed instructions with citation requirement | Hash the full prompt, not just the data fields |
| Different system prompt | One model gets system instructions the other doesn't | Record system prompt in the call log |
| Different truncation | One model gets 800 chars, another gets 2000 | Report truncation length per call |

### When to check

- **Mandatory:** Before any F1/comparison test between different models
- **Mandatory:** Before any reader qualification test
- **Recommended:** Before any audit that compares model outputs to human judgments (the human may have seen different information)

## F1 independence rule

Expected answers for any qualification battery must be derived **independently of the instrument being audited**.

### The defect

The F1 battery's expected answers (for the MVI rebuild) were set by the agent who built the instrument. When reader models disagreed with the classifier, the reader was disqualified — a test of **agreement with the instrument under audit**, not a test of correctness. This is the exact behaviour the audit exists to detect.

### The rule

> An instrument may never define the standard against which its own auditors are qualified.

### Protocol

1. **Independent derivation.** For each F1 item, derive the expected answer from the registry and publication texts alone, against the target sentence, without reference to any model's output. Show the reasoning and cite the passages.
2. **Where texts do not determine the answer.** The expected answer is `UNRESOLVABLE` — including for items the classifier resolved. The instrument's resolution is not evidence that the item is resolvable.
3. **Disjoint majority cross-check.** For each item, poll all provenance-disjoint readers (with the classifier excluded) and report the majority. Divergence between independent derivation and disjoint majority is itself a finding — log it, do not average it.
4. **Re-gate.** Score each reader against the independently-derived expected answers. A reader is qualified if it matches on ≥5/6. If no reader qualifies, report `UNMEASURED(no qualified disjoint reader)` — do not lower the bar.

### Distinction from N1b resolution

The N1b resolution clause (construct-declaration-n1b.md) resolves the **target sentence** against an external authority. The F1 independence rule resolves the **expected answers** against the texts themselves. Both are pre-compute checks that prevent the instrument from defining its own standard:

| Check | What it resolves | Against what | Cost |
|-------|-----------------|--------------|------|
| N1b (target resolution) | The target sentence | Domain authority | One lookup |
| F1 independence | The expected answers | The texts + disjoint majority | One derivation per item |

## Example: The PIC-UP pipeline defect

**F1.2 item:** PIC-UP protocol trial (NCT02929563) — paraphrased-but-equivalent item.

**Symptom:** Classifier (DeepSeek) says MATCHED. All 4 provenance-disjoint models say UNRESOLVABLE. Apparent leniency.

**Root cause (pipeline defect):** The classifier received the full PubMed abstract (~400 words) which explicitly lists all four feasibility outcomes with their criteria. The reader models received a short human-written summary (~50 words) that says "The study will assess effective screening, timely enrollment, participant accrual, and protocol adherence as feasibility outcomes" — a forward-looking statement without the specific criteria.

**Independent derivation:**
- With the full abstract: MATCHED (the same 4 outcomes with the same criteria are listed in both registry and publication)
- With the short summary: UNRESOLVABLE (the criteria/thresholds are absent from the text provided)

**The classifier was right for its input. The readers were right for their input. Neither was wrong — the inputs differed.**

## Propagation points

Add the input parity check to:
- Any pre-run verification protocol (F1 battery) — record per-field input hashes
- Any reader qualification test — verify input parity before scoring
- The staged-deployment protocol (pre-registered-research-executor) — add as a blocking fix protocol step
- SPEC_v2 §6.3 (O-checks) — add O5: input parity verification for all model comparisons

---

## Three-role clean chain

When measuring leniency (comparing a classifier against an independent reader), **three distinct model lineages are required, all pairwise disjoint.** No model may hold two roles.

### The roles

| Role | Responsibility | Constraint |
|---|---|---|
| **Classifier** | The instrument under audit. Produces the primary classification. | Fixed. |
| **C1 deriver** | Derives the independent expected answers (the "C1 standard") against which the classifier and readers are scored. | Must be disjoint from the classifier. Must be blind to all classifier output at derivation time. |
| **B1/B2 reader** | Runs the leniency measurement (missed discrepancies + UNRESOLVABLE undercount). | Must be disjoint from BOTH the classifier and the C1 deriver. |

### Pairwise disjointness

"Disjoint" means: different base model, different company, different training data lineage. E.g., DeepSeek and Qwen are disjoint; DeepSeek and DeepSeek-Coder are NOT disjoint.

### Blind C1 derivation

The C1 derivation must be blind to the classifier's output:

1. The deriver receives ONLY the raw input texts (registry PO, publication text, target sentence) — no expected answers, no prior C1, no classifier output files.
2. The payload is logged and auditable: the exact strings sent to the deriver are recorded.
3. If any classifier output is present in the deriver's context at derivation time, the C1 is **nominally independent** and must be re-derived by a blind agent.

### Citation audit

Citations are mandatory for every C1 verdict. A verdict without both citations is ERROR, not a verdict.

The citation audit verifies that each quoted passage exists verbatim in the source and supports the verdict:

| State | Meaning | Action |
|---|---|---|
| SUPPORTED | Quote exists verbatim and supports the verdict | Include in C1 |
| QUOTE NOT FOUND | Quote does not appear verbatim in the source — may be a paraphrase, concatenation, or elision | Exclude from C1. Report as `UNMEASURED(citation failed)`. |
| QUOTE DOES NOT SUPPORT | Quote exists but does not support the verdict | Exclude from C1. Report as `UNMEASURED(citation does not support)`. |

### Reader qualification

1. Score candidate readers against the C1 standard (all items, including excluded ones — failure is a finding).
2. Qualification threshold: ≥5/6 against C1 AND provenance-disjoint from both classifier and C1 deriver.
3. If no candidate qualifies: report `UNMEASURED(no qualified disjoint reader)`. Do not lower the bar.
4. Report the exact model string, provider, endpoint, temp/seed for every reader tested.

---

## Leniency measurement protocol (B1/B2)

When a qualified reader exists, leniency is measured in two dimensions:

### B1 — Missed-discrepancy audit

Sample: harness-MATCHED items (the items the classifier said were fine).
Task: reader independently assigns MATCHED / SWITCHED / UNRESOLVABLE against the same target sentence, with citations.
Headline: harness-MATCHED that the reader calls SWITCHED or UNRESOLVABLE, k/n with 95% Wilson CI.

**Threshold:** B1 rate ≥ 20% → VOID(harness lenient). The instrument undercounts discrepancies.

### B2 — UNRESOLVABLE sensitivity probe

Sample: harness-resolved items (MATCHED + SWITCHED + UNRESOLVABLE).
Task: single question per item — "Could correspondence be determined from these two texts alone, without domain inference?"
Headline: items the reader says NO to, k/n with 95% Wilson CI.

**Usage:** B2 rate feeds the corrected band formula: `corrected_UNRESOLVABLE = raw_UNRESOLVABLE + (B2_rate × resolved_n)`.

### Part D — Self-consistency check

10 unlabelled duplicates from items the reader already judged in this run.

**Threshold:** <8/10 agreement → both audits `UNMEASURED(reader inconsistent)`. No band is read.

This is the F1 discipline applied to the reader. A reader that is inconsistent with itself cannot measure anything.

### Corrected band (amendment 03)

```
corrected_UNRESOLVABLE = raw_UNRESOLVABLE + (B2_rate × resolved_n)
band = corrected_UNRESOLVABLE / 100, reported with 95% Wilson CI
```

Interpretation:
- CI entirely **below 20%** → crisp-dominant, band STANDS
- CI entirely **above 20%** → mixed or fuzzy, band STANDS at that level
- CI **spanning 20%** → `UNMEASURED(interval spans band edge)`, enlarge the audit
- B1 rate ≥ 20% → **VOID(harness lenient)** — takes precedence over all other readings

### Old B1/B2 numbers are not pooled

If the prior leniency measurement used the same model as the classifier (self-consistency check), those numbers are withdrawn as leniency estimates. They may be reported as self-consistency, never as leniency, and never pooled with anything below. A model does not detect its own systematic bias — it reproduces it.

---

## Example: The MVI clean chain

| Role | Model | Lineage |
|---|---|---|
| Classifier | deepseek/deepseek-v4-flash | DeepSeek |
| C1 deriver | qwen/qwen3.7-plus | Qwen |
| Reader | mistralai/mistral-medium-3-5 | Mistral |

**All three pairwise disjoint.** C1 derived blind (no classifier output in context). Reader qualified at 5/6 against C1. Self-consistency verified at 10/10.

**Result:** B1 = 16/47 (34.0%) ≥ 20% → VOID(harness lenient). B2 = 19/60 (31.7%). Corrected band = 29.0% [21.0%, 38.5%]. Band VOID.