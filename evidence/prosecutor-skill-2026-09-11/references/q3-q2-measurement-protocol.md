# Q3 and Q2' Measurement Protocol

**Author:** PROSECUTOR class  
**Session origin:** CVN Q3 remeasurement at depth (2026-07-22)  
**Domain:** Quantitative thesis falsification, error detectability measurement, backward-information-path verification

---

## Q3 — Three-Bucket Error Taxonomy

When measuring whether errors are oracle-detectable (Q3), classify every error into exactly ONE of three buckets. The MIX is the finding, not the headline percentage.

### The three buckets

| Bucket | Definition | Example | Catching mechanism |
|--------|-----------|---------|-------------------|
| **INPUT_FABRICATION** | Model used a quantity with NO source: not in the prompt, not from a tool call, not flagged as an assumption. The value was invented. | Claiming a risk-free rate of 5.0% when no rate was provided; fabricating EINs, 10-K filing metadata, or GLEIF otherNames content. | Input provenance check (PROMPT / TOOL / DERIVED / ASSUMPTION tagging). A quantity with none of these tags is REJECTED before it propagates. |
| **OMISSION** | A required analytical step was skipped, an implication was missed, or a claim was never made. The model didn't do something it should have. | Failing to check the 13(d)(3) group test in beneficial ownership analysis; skipping the $35 gamma squeeze scenario; not reconciling inconsistent spread tables. | Completeness manifest (required-steps list derived from domain regulations). A missing required step is MISSING_REQUIRED_LEAF — a detectable error. |
| **SILENT_JUDGMENT** | Correct framing, correct inputs, correct data — wrong conclusion. The model had everything it needed but drew the wrong answer. | Wrong delta estimate for ITM calls; applying T+35 instead of T+13 close-out; non-sequitur borrow-rate-to-upside reasoning. | NOT catchable by any oracle. This is the frontier-dose class. Requires a frontier model audit (D3 dose) or human review. |

### Q3 metrics

```
Q3_catchable = (INPUT_FABRICATION + OMISSION) / total_errors
Q3_silent    = SILENT_JUDGMENT / total_errors
```

**Thresholds (from CGSR G2 protocol):**
- Q3_catchable >= 50% -> PASS. The domain is verification-rich. L4/L5 buildable as specified.
- Q3_catchable 30-50% -> CONDITIONAL. D3 dose is load-bearing. Measure its cost before committing to L5.
- Q3_catchable < 30% -> FAIL. Silent judgment dominates. The domain needs frontier judgment more than it needs verification.

**n floor:** If total errors < 20 across both arms and all tasks, the model is not failing enough to measure. Report the n rather than a percentage.

### The MIX is the finding

The distribution across buckets drives architectural decisions, not the headline Q3 percentage:

- **INPUT_FABRICATION dominant** -> provenance fix is the priority. Shore up the input provenance layer (L1). Every fabricated quantity would be caught by a PROMPT/TOOL/ASSUMPTION tag check.
- **OMISSION dominant** -> completeness manifest is the priority. Build required-steps manifests from domain regulations. Missing steps become detectable errors.
- **SILENT_JUDGMENT dominant** -> the domain is not primarily a verification problem. CVN is a verification layer for a problem that needs frontier judgment. Honest conclusion: the economics don't close at <5% frontier tokens.

### Legacy types (for comparability)

Also record the legacy types alongside the three-bucket taxonomy for cross-pass comparability:

| Legacy type | Definition | Three-bucket mapping |
|-------------|-----------|---------------------|
| factual | Wrong factual claim about a data point | Usually INPUT_FABRICATION or SILENT_JUDGMENT |
| arithmetic | Wrong computation | Usually OMISSION or SILENT_JUDGMENT |
| entity | Wrong entity identity or resolution | Usually INPUT_FABRICATION or SILENT_JUDGMENT |
| retrieval | Wrong data retrieval (wrong CIK, missing data) | Usually OMISSION |
| judgment | Wrong conclusion on correct inputs | Always SILENT_JUDGMENT |
| omission | Required step skipped | Always OMISSION |

### Hand-grading protocol

- Do NOT grade with a model. Hand-grade every error.
- Do NOT re-label errors to improve the number.
- Report both the three-bucket AND legacy types for comparability with earlier passes.
- For each error, report: task | step | error_description | bucket | detectable_by | propagated

### Error record format

```
| # | Task | Step | Error description | Three-bucket | Legacy type | Oracle? |
|---|------|------|------------------|-------------|-------------|---------|
| T1-1 | LH-01 | Borrow cost | Borrow cost miscalculated (2-3x too high) | SILENT_JUDGMENT | judgment | NO |
| T2-1 | LH-02 | Shares | Fabricated shares outstanding (contradicts prompt data) | INPUT_FABRICATION | factual | YES |
```

### Subagent delegation for parallel hand-grading

When hand-grading N tasks (N > 3), delegate to parallel subagents — each reads one task output file and identifies errors. Splitting by task groups (e.g., 3 tasks per subagent) ensures each subagent can focus on depth without context overflow. Each subagent returns a structured error table with the three-bucket taxonomy. The parent agent compiles and reconciles.

**Protocol:**
1. Write all task outputs to a single file, delimited by `===== TASK N =====` and `===== END TASK N =====` markers.
2. Dispatch 3-4 subagents, each responsible for a contiguous block of tasks.
3. Each subagent reads the file, locates its task block, and identifies every error.
4. Each subagent returns a structured error table with all columns.
5. Parent compiles, deduplicates, and computes Q3 metrics.

---

## Q2' — Backward-Path Strict Test

When verifying whether a claimed backward-informative path is genuine (Q2'), apply the strict test.

### The test question

> "If the child leaf is verified WRONG, what specifically changes about the parent's value?"

A path that cannot answer this concretely is a restatement of the parent-child relation, not backward information flow. The parent is typically an oracle-covered leaf (data point, authoritative record, or deterministic computation). The child is a judgment leaf.

### Common failure modes

| Claimed backward path | Why it fails | True relationship |
|-----------------------|-------------|-------------------|
| Borrow rate -> FTD exhaustion | Borrow rate is a fixed market observation. The exhaustion estimate doesn't change it. | Forward-specific: exhaustion depends on the rate, but the rate is invariant. |
| HSR timeline -> spread decomposition | HSR date is a regulatory calendar date. The spread doesn't change it. | Forward-specific: spread depends on the timeline, but the timeline is invariant. |
| 13G->13D thresholds -> group detection | The 5% threshold is statutory. The model's group verdict cannot change it. | Forward-specific: group detection depends on the threshold, but the threshold is invariant. |
| Gamma aggregation -> squeeze scenario | Gamma aggregation is a deterministic computation from OI data. The scenario doesn't change the aggregation. | Forward-specific: scenario depends on gamma, but gamma is invariant. |
| LEI comparison -> entity confirmation | LEI records are fixed registry data. The entity verdict cannot change the registry. | Forward-specific: entity confirmation depends on LEI data, but the registry is invariant. |
| num.tsv cross-reference -> fabrication flag | num.tsv is a fixed dataset. The model's flag doesn't change the data. | Forward-specific: flag depends on the data, but the data is invariant. |

### Genuine backward-informative path (rare)

A path is genuinely backward-informative only when the parent is itself a MODEL OUTPUT that the oracle-covered leaf corrects. But oracle-covered leaves are by construction factual data points or deterministic computations — they are not model outputs. This makes genuine backward-informative paths extremely rare in practice.

### Interpretation

| Survival rate | Verdict | Architecture implication |
|---------------|---------|-------------------------|
| 0-25% | FAIL | Architecture is in "sequential verification" regime. Belief propagation cannot correct judgment leaves. Redesign L4 for forward-only verification. |
| 25-50% | CONDITIONAL | Some paths are genuinely backward-informative. Build a subset of the corrective substrate on verified paths first. |
| >50% | PASS | Architecture is in "error correction" regime. Build L4 as specified. |

### Spot-check protocol

1. Select 8 of the claimed N backward-informative paths.
2. For each path, ask: "If the child leaf is verified WRONG, what specifically changes about the parent's value?"
3. Score PASS if the parent's value changes; FAIL if it doesn't.
4. Report survival rate: (PASS_count / 8) * N.
5. If fewer than 6 of 8 survive, recompute Q2' honestly.

---

## Completeness Manifest Pattern

G2 measures whether leaves have oracles. It does NOT measure whether the leaf SET is complete. The completeness manifest closes this gap.

### Protocol

1. For each task, derive the REQUIRED-STEPS MANIFEST from the domain's OWN rules, not from what the model happened to produce.
2. Source the manifest from governing regulations, standard practice, or authoritative documents (SEC rules, bond indentures, GAAP accounting standards, HSR Act, etc.).
3. Compare the model's decomposition against the manifest.
4. Flag any required step that is absent from the model's output -> MISSING_REQUIRED_LEAF (detectable error).
5. Flag any required step that is present but has no executable computation attached.

### Manifest structure

| Column | Content | Example |
|--------|---------|---------|
| Required step | What must be done | Section 13(d)(3) group test |
| Domain source | The regulation or standard | SEC Rule 13d-5(b)(1) |
| Verifiable? | YES/NO — is the step's presence checkable by an oracle? | YES — deterministic |
| Detection method | How a missing step is caught | Completeness manifest check |

### Common missing steps by domain

| Domain | Most commonly missed step | Regulation |
|--------|--------------------------|-----------|
| Beneficial ownership | Section 13(d)(3) group test | SEC Rule 13d-5(b)(1) |
| Debt covenant analysis | Bond indenture download + springing trigger check | Indenture text |
| Merger spread | Antitrust market share overlap (HHI) | HSR Act |
| Entity resolution | SEC CIK to LEI cross-reference | GLEIF + SEC XBRL |
| XBRL audit | Segment reporting reconciliation | GAAP ASC 280 |
| Insider trading | 10b5-1 plan disclosure check | Form 4 checkbox |

---

## The Spec-Fix Pattern

Qualitative findings from error analysis drive spec amendments. The error MIX reveals which architectural layer needs fixing.

### Mapping

| Error bucket | Spec amendment | Ships with | Rationale |
|-------------|----------------|-----------|-----------|
| INPUT_FABRICATION | SPEC section 4 — input provenance. Every quantity carries a PROMPT/TOOL/DERIVED/ASSUMPTION tag. Rejected if none. | L1 | Provable catch: all fabricated quantities fail the tag check. |
| OMISSION | SPEC section 7 — completeness manifest. Each decomposition carries a required-steps manifest. Missing step = MISSING_REQUIRED_LEAF. | L1 | Provable catch: the manifest was derived from domain rules, not from the model. |
| SILENT_JUDGMENT | No spec fix applies. The error is in the model's reasoning, not the architecture. | N/A | Either accept the ceiling or fund a D3 frontier audit dose. |

### Amendment deliverables

Each amendment is a concrete text file with:
1. The current text (for reference / diff)
2. The amended text
3. A rationale section explaining what finding drove the change
4. A note on which layer it ships with (L1, L2, etc.)

### Example: SPEC section 4 amendment

```
## Current text (SPEC section 4):
Oracles verify OUTPUTS.

## Amended text (SPEC section 4):
Every quantity entering a computation must carry a provenance tag:
- PROMPT  — value appeared verbatim in the input
- TOOL    — value came from a tool call, with output hash
- DERIVED — computed from other provenanced values
- ASSUMPTION — explicitly flagged, with the assumption stated

A quantity with none of these tags is REJECTED before it propagates.

## Rationale:
The INPUT_FABRICATION error class (fabricated risk-free rate, fabricated
break price, fabricated assumption that looks like data) is an INPUT failure,
not an output failure. No oracle can catch it because the claim was never
made. This machinery has existed since SPIE v0.1 and was never applied at
this level.

## Ships with: L1
```