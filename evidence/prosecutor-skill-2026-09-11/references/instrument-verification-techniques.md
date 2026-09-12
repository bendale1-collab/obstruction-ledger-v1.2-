# Instrument verification techniques

Emergent from MVI program (clinical trial outcome classification, three-judge panel, 2026-07-24).

## Mutation-testing classification categories

**Problem:** A count of zero in a classification category (e.g. GENUINE AMBIGUITY = 0) may be an instrument artifact, not a measurement. The `ABSTAIN(ambiguous-mapping)` category in Filter D1 was discovered to be inert only after it had already decided a band.

**Fix:** Before relying on a zero count, construct 5 synthetic items designed to produce the category. Pass them through the unmodified instrument. Require ≥4/5 to confirm reachability. Include 3 negative controls (items that should NOT produce the category) to verify the instrument says no when it should say no. A category that fails is INERT.

**Lesson from this run:** The inspector's GENUINE AMBIGUITY category was inert (2/5 after rebuild). The corrected band (0.0%) was vacuous — it rested on an instrument artifact, not a measurement.

## Split inspection (B1 code + B2 model)

**Problem:** Bundling a deterministic check (does the quoted passage exist verbatim in the source?) with a judgment call (does the passage support the verdict?) in a single model call causes the model to use immaterial precision issues to override substantive judgments. The inspector defaulted to "ONE JUDGE UNSUPPORTED" on synthetic GENUINE items because it found minor citation imprecision.

**Fix:** B1 is code — `source.find(span_text)` at three normalisation levels (exact, whitespace, stripped). No model involved. B2 is a model asked a single question with verified inputs. Only B2 reaches a model.

**Lesson from this run:** GPT-4o B2 returned SUPPORTS for all three judges on a synthetic GENUINE item — including its own SWITCHED verdict (testimony against interest). The split approach works when B1 delivers verified spans.

## Span-text collection, not character offsets

**Problem:** Models cannot compute byte offsets precisely. Qwen output `registry_span: {start: 0, end: 104}` for a source of length 100 — off by 4. This is systematic: the model estimates offsets rather than counting bytes.

**Fix:** Ask for verbatim substrings (`registry_span_text`, `publication_span_text`). The model copies from the source text in its context. B1 then becomes `source.find(span_text)` — deterministic, no model, no threshold sweep.

## Three normalisation levels for B1:
1. Exact match — `if span_text in source: PRESENT`
2. Whitespace-normalised — `if ws(span_text) in ws(source): PRESENT`
3. Stripped fragment — `if span_text.strip() in source: PRESENT`
4. Otherwise: `ABSENT`

**Register the strictest level as primary before the pass.** Report all three levels. Report items whose B1 verdict changes across levels — that number is the parameter's real cost. A result at one setting only is `UNMEASURED(normalisation not swept)`.

**Empirical finding (offset recollection, 59 publication-bearing items, json_object response format):** The normalisation sweep produced **zero flips** across all three levels (exact, ws, fragment). All 20 ABSENT items were publication-span paraphrases that were non-verbatim at all three levels — the model produced a slightly different leading text fragment, not a formatting difference. Registry spans (short, clean text) resolved at 100% exact match.

**This means:** On well-structured data with enforced json_object response format, normalisation doesn't matter. The 20 ABSENT items are genuine paraphrases that B1 correctly flags — no normalisation level can recover text the model didn't copy. The sweep is still required by pre-registration discipline, but the expected outcome is zero flips. Report it either way.

## Against-interest testimony

When an instrument convicts its own lineage (same model or same lineage), the finding is strengthened, not weakened. This is the strongest evidence available — the instrument acts against its own bias.

**Example:** The inspector (DeepSeek V4 Flash) found DeepSeek (Judge A) unsupported in 12/13 cases. An inspector that shares the target's lineage and still convicts it is more credible than a disjoint inspector.

Explicitly report when this pattern occurs. Do not treat shared lineage as automatic weakness — the direction of the finding matters.

## Output-format co-selection (amendment-06 principle)

**Pattern (three occurrences in this program):**
1. Lexical string matcher read as 51% switching
2. Truncated abstract read as reader incapacity  
3. Parse failure of candidate model output read as capability ceiling

Each time, an instrument defect was reported as a fact about the world.

**Rule:** No qualification battery may fail a candidate for output format. Format is normalised before any semantic scoring. Only WRONG LABEL counts against capability.

**Implementations:**
- Permissive extraction (regex for label in text)
- JSON schema / function calling where supported
- Adequate max_tokens (reasoning before label can truncate)
- Two-shot format priming with worked examples

## Cohen's κ alongside Jaccard (correlation discount)

**Problem:** With a dominant base-rate category (e.g. MATCHED = 70%+ of items), raw Jaccard similarity inflates pairwise agreement. Two judges agreeing that most items are MATCHED is not informative — they could agree by chance 50% of the time.

**Fix:** Report Cohen's κ alongside Jaccard for every pair. κ corrects for chance agreement.

**Correlation flag:** If one pair's κ is substantially higher than the others (spread > 0.15), that pair shares more than independent judgment — any consensus figure that assumes independence is discounted. Report the spread and state the discount.

**From this run:** Qwen–GPT-4o κ = 0.742 vs DeepSeek–Qwen κ = 0.514, spread = 0.260. Flagged.

## Concordance decomposition (separate shared-priors from outlier-correct)

**Problem:** A high-Jaccard pair has two readings that Jaccard cannot separate:
- **Shared priors** → correlated error → discount consensus
- **Third judge is the outlier because it is wrong** → agreement is accuracy → no discount

**Fix:** Partition pairwise agreement by audit outcome. For each pair, over items where the pair agreed:

- `CONCORDANT-CORRECT`: both spans PRESENT and SUPPORTS (accuracy)
- `CONCORDANT-ERROR`: both spans ABSENT or DOES NOT SUPPORT (shared blind spot)  
- `CONCORDANT-UNRESOLVED`: mixed / INSUFFICIENT

Only `CONCORDANT-ERROR` justifies a correlation discount. If the "outlier" judge has been independently shown wrong (e.g. against-interest testimony), the agreement is accuracy and no discount is applied.

## Judge-driven vs item-driven abstention

**Problem:** Models set their abstention (UNRESOLVABLE) threshold internally. A single-model abstention rate is a hidden architecture parameter, not a property of the domain.

**Fix:** Over the verdict matrix, count:
- `all_abstain`: items where ALL judges returned UNRESOLVABLE (item-driven — the item itself is genuinely irresolvable)
- `one_abstain`: items where exactly ONE judge abstained (judge-driven — the threshold is a model property)

Report which dominates. If judge-driven, any architecture routing on one model's abstention inherits that model's threshold as a hidden parameter.

**From this run:** all_abstain=1, one_abstain=5 → JUDGE-DRIVEN. DeepSeek's 3.8% abstention is DeepSeek's threshold, not "the domain's."

## Structural fix at the collection layer, not the inspection layer

**Problem (three levels of regress in this program):** Each fix was applied at the observation layer rather than the generative layer.
1. Reader was too strict → fix: qualify reader → gate required agreement with classifier under audit → co-selection
2. Expected answers derived from classifier → fix: C1 independent → still one model deciding
3. Inspector failed to find GENUINE → fix: split B1/B2 → but B1 starved by narrative citations never collected

**Principle:** Before building an inspection/verification layer, verify that the primary collection layer produces the data the inspection layer needs. A collection defect cannot be fixed by a better inspector — it must be fixed at the collection level.

In this case: narrative paraphrase satisfied the judge prompt → inspection consumed narratives → B1 code had nothing to match. Fix: enforce structured citations at the judge prompt (span_text, not free-form citation).

## Six-round regress pattern (class-level)

**The repeating defect:** Each time a qualification gate, expected answer, or verdict is derived from the instrument under audit, the same structural defect is reproduced one layer below. Amendment-04-style corrections (independent derivation) must be applied recursively until no instrument-derived standard remains.

**The MVI program progression:**
1. Classifier (DeepSeek V4) defines the band → 34% attributed leniency
2. C1 expected answers derived from classifier → co-selection (same lineage)
3. Reader qualified against C1 → "agreement with the instrument under audit"
4. Inspector (DeepSeek V4) fails on GENUINE → co-selected for its own lineage
5. Bundled inspector format → one model deciding both existence and support
6. Collection layer produces narrative citations → inspection starved

**Check after any fix:** "Where did the expected answers / qualification standard / verdict criteria come from?" If the answer traces back to the same instrument at any distance, the fix is incomplete.

**Rule:** Every de-privileging must include a recursive check — is there still a single model-derived standard anywhere in the chain? If yes, the fix will fail one layer down.