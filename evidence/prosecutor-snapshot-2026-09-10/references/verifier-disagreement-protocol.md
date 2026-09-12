# Verifier Disagreement Protocol (three-judge / N-judge measurement)

When the thesis turns on whether a domain is *crisp* (models agree) or *fuzzy* (models disagree), use N-way verifier measurement. This replaces any chain that depends on a single privileged classifier.

## Core protocol

1. **N provenance-disjoint judges.** Same lineage → shared boundary decisions inflate agreement and mask fuzziness. Three pairwise-disjoint models (different base family + different provider) is the minimum; four tightens the CI on the band estimate.

2. **Byte-identical payloads across all judges.** Hash per item across all judges. Any mismatch → that item is `ERROR` for all judges. Task text, categories, examples, format instructions: identical.

3. **Amendment 06 in force — no judge is failed for output format.** If a judge emits preamble, reasoning, or JSON instead of a bare label, use permissive extraction (regex or `label in text.upper()` for the last occurrence). Only `WRONG_LABEL` (clean single label, semantically wrong) counts against capability. Do NOT report a format failure as a capability finding.

4. **Citations mandatory.** Every verdict must quote the supporting source passages. This is the anchor — the citation audit settles disagreements.

## CRISP vs FUZZY

| Measure | Definition |
|---|---|
| CRISP | All N judges return the same verdict |
| FUZZY (raw) | Any disagreement among N judges |
| 2-1 split (3-judge) | Two judges agree, one dissents |
| 3-way split (3-judge) | All three different |
| CORRECTED fuzziness | RAW × (share of audited disagreements classed GENUINE AMBIGUITY) |

**The band is defined over CORRECTED fuzziness.** A split caused by one judge misquoting the source is an error, not a property of the item. RAW is the upper bound.

## Citation audit protocol

For every disagreement (not a sample), run an inspector model — disjoint from at least two of the judges, verdicts in context — that verifies:
1. Does the cited registry passage exist verbatim in the source text?
2. Does the cited publication passage exist verbatim in the source text?
3. Does the passage support the judge's verdict?

Classifications:
- **GENUINE AMBIGUITY**: all three judges' citations are verbatim and support their own verdict → real fuzziness
- **ONE JUDGE UNSUPPORTED**: one judge's quotes are absent or do not support the verdict
- **MULTIPLE UNSUPPORTED**: two or more judges unsupported
- **INCONCLUSIVE**: cannot settle by inspection

## Band thresholds (pre-registered)

| CI location on CORRECTED fuzziness | Interpretation |
|---|---|
| Entirely < 20% | Crisp-dominant — frozen-first licensed |
| Entirely > 60% | Fuzzy-dominant — omnibus is core |
| Within 20–60% | Mixed — decompose 10 items |
| Spans a boundary | UNMEASURED — add a 4th judge |

## Abstention analysis

After measurement, report:
- Per-judge UNRESOLVABLE rates with CI
- All-abstain count (item-driven — all judges abstain on same item)
- One-abstain count (judge-driven — only one judge abstains)

Item-driven → genuinely ambiguous item. Judge-driven → the threshold is a model property; any architecture routing on one model's abstention inherits that model's threshold as a hidden parameter.

## Drift check

Compare FUZZY rate of first batch vs later batches. Material drift = |diff| > 10% absolute. If material, report as separate runs.

## Dawid-Skene posterior (informational)

Fit a latent-class model over the judge × item verdict matrix:
- Per-item posterior over the true label
- Per-judge confusion matrix (replaces any qualification gate)
- Mean posterior entropy
- Low-confidence share (max posterior < 0.7)
- Semi-supervised: use citation-audited items as partial ground truth anchors

**Independence caveat:** DS assumes conditionally independent errors given the true label. Partial provenance disjointness violates this. Report pairwise correlation alongside any DS estimate. Pairwise agreement > 90% suggests the independence assumption is tenuous.

## Pitfalls

- **PARSE_ERR on DeepSeek models** — DeepSeek V4 Flash outputs reasoning text without a final label word. Permissive extraction (search for `MATCHED|SWITCHED|UNRESOLVABLE|NO-PUBLICATION|ERROR` in uppercase) handles this. Use "last occurrence" heuristic because reasoning mentions possible labels before concluding.
- **Pairwise agreement computation bug** — Do NOT use string judge keys as integer indices into the label array. Use `judges.index(key)` to get the integer position.
- **Over-eager "leniency" attribution** — A model that resolves where others abstain is not "lenient" by default. Only the citation audit distinguishes: unsupported citations = lenient; supported citations = crisper boundary. Report audit result, not raw disagreement, as the band.
- **4th judge mechanically raises raw disagreement** — Adding a judge increases FUZZY by construction. Compare like with like; do not merge 3-judge and 4-judge rates.
- **Output contract repair** — A parser tuned to the incumbent's formatting disqualifies auditors for format differences, reproducing co-selection one layer down. Normalise format (permissive extraction, structured output) before any scoring. Only `WRONG_LABEL` counts against capability.

## Output template

```
THREE-JUDGE DISAGREEMENT — [date]
Judges: [N strings, providers, lineages] — pairwise disjoint [Y]
Parity: payload hashes identical [Y] | ERROR items [n]

per-judge counts + CI | CRISP rate + CI | FUZZY rate + CI
split breakdown | pairwise agreement [all pairs]
per-judge abstention | all-abstain vs one-abstain

audited disagreements: GENUINE / UNSUPPORTED / INCONCLUSIVE
RAW [x%] CI | CORRECTED [x%] CI ← band
Band state: [crisp-dominant / fuzzy-dominant / mixed / UNMEASURED]

Dawid-Skene: per-judge reliability | mean entropy | low-conf share
```

## 2026-07-24 session trace

Protocol established during the MVI measurement chain for registered-primary-outcome discrepancy (RPOD) in clinical trials.

- 60 NCT items from clinicaltrials.gov, 3 judges (DeepSeek V4 Flash, Qwen 3.7+, GPT-4o), shuffled seed 20260724
- 52 items with 3 clean verdicts (7 DeepSeek PARSE_ERR excluded by permissive extraction)
- Raw FUZZY: 34.6% [23.2%, 48.2%] | Corrected: 11.5% [5.4%, 23.0%] — UNMEASURED(spans 20% edge)
- 18 disagreements audited: 0 GENUINE, 11 ONE JUDGE UNSUPPORTED (DeepSeek in all 11), 1 MULTIPLE, 6 INCONCLUSIVE
- Abstention: JUDGE-DRIVEN (5 one-abstain vs 1 all-abstain)
- 4th judge (Claude Opus 4) added but only partially completed (API timeout at ~18/60 items)
- Dawid-Skene: per-judge reliability 0.834–0.873, mean entropy 0.218