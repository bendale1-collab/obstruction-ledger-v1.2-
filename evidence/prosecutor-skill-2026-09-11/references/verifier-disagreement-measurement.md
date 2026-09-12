# Verifier-Disagreement Measurement

## When to use

Replace a privileged single-measurer design with peer judges. Use when:
- The measurement chain regresses through repeated qualification gates (each layer co-selects for the incumbent)
- A "leniency" or "error rate" finding cannot be distinguished from disagreement between two equally-rational models
- The spec defines fuzziness as "verifier disagreement" (e.g., SPEC_v2 §6)

## Protocol

### 1. Three peer judges

Three pinned models, pairwise provenance-disjoint (different base model + different provider). The incumbent is included as a peer, not an authority.

**Identical treatment, asserted by payload hash:**
- byte-identical payload per item across all judges — log the hash, mismatch fails that item to ERROR for all three
- identical task text, identical category list
- permissive extraction + structured output where available; adequate max_tokens; **no judge is failed or excluded for output format** — format normalised before scoring
- citations mandatory: registry passage and publication passage quoted per verdict

### 2. CRISP vs FUZZY

Restrict to items where all judges returned a verdict (exclude ERROR; report how many).

```
CRISP      = all agree                    → n, rate + CI
FUZZY      = any disagreement             → n, rate + CI
  2-1 split                               → n
  3-way split                             → n
```

**Separate:**
- Task fuzziness = disagreement rate over publication-bearing items
- Store incompleteness = NO-PUBLICATION agreement rate — a construction card, excluded from the band

**Report:**
- pairwise agreement for each pair (a pair agreeing far more than others indicates shared provenance)
- per-judge abstention rate — descriptive only, NOT a leniency claim; no judge is the standard

### 3. RAW vs CORRECTED (two estimands)

**RAW fuzziness** = any disagreement / items with a verdict. Includes splits caused by one judge misreading.

**CORRECTED fuzziness** = raw × (share of audited disagreements classed GENUINE AMBIGUITY). Excludes splits where a judge's citations are absent or unsupporting. **The band is defined over CORRECTED fuzziness.**

Both carry CIs. Neither is called "primary" without naming its construct.

### 4. Audit every disagreement (not a sample)

Every verdict carries citations, so disagreements are inspectable.

- Inspector must be disjoint from at least two judges
- Report its string, lineage, and whether judge verdicts were in its context
- Per disagreement: does each judge's quoted passage exist verbatim and support its own verdict?
- Classes: GENUINE AMBIGUITY / ONE JUDGE UNSUPPORTED / MULTIPLE UNSUPPORTED / INCONCLUSIVE

Corrected fuzziness = GENUINE AMBIGUITY share × raw disagreement rate, arithmetic shown with CI.

### 5. Mutation-test the inspector BEFORE trusting 0-count findings

A finding of "0 GENUINE AMBIGUITY" must be shown reachable. Construct synthetic items where both sides are genuinely supportable:

1. Composite outcome: one judge cites composite, other cites component
2. Timepoint: registered and reported windows both quotable
3. Renamed measure: both names quotable
4. Multiple primaries: each quotes a different registered primary
5. Amendment: pre- and post-amendment text both present

Run each through the UNMODIFIED inspector (same prompt, same protocol). Required: ≥4/5 return GENUINE AMBIGUITY.

Also construct 3 negative controls (one judge's quote absent). Each must return ONE JUDGE/MULTIPLE UNSUPPORTED.

**Verify the mutation test itself** — before concluding the inspector is broken, check that every quoted passage is byte-EXACT in the constructed source. A non-exact quote makes the inspector correct to flag it.

### 6. B1/B2 split inspection

If the inspector fails the mutation test, the root cause is often a bundled task: one prompt asks the model to both verify verbatim presence AND judge support.

Fix: split into two mechanisms.

**B1 — Quote existence. Code, not a model.**
Normalised match against source. Output per quote: PRESENT / PRESENT(normalised) / ABSENT, with matched span.
Report results at exact, whitespace-normalised, and fuzzy match thresholds. A single-threshold result is UNMEASURED.

**B2 — Support. Judgment, and only this reaches a model.**
Only for quotes that are PRESENT at the registered threshold. The model sees verified quotes and the verdict, and answers one question: "Given these passages, does the verdict follow?" SUPPORTS / DOES NOT SUPPORT / INSUFFICIENT.

Rubric: whitespace differences, truncation, ellipsis, and paraphrase do NOT make a verdict unsupported. Only absence of supporting content does.

**Three inspectors for B2**, pairwise provenance-disjoint. Verdict per disagreement = majority. Report inspector disagreement rate separately.

### 7. Dawid-Skene posterior (zero additional calls)

Post-hoc on the verdict matrix:
- Fit a latent-class model (DS, EM) over judge × item verdict matrix: per-item posterior over true label, per-judge confusion matrix
- Report per-item posterior entropy, mean entropy, fraction with max posterior < 0.7
- Report per-judge reliability — replacing every qualification gate the prior chain tried to build
- Independence caveat: DS assumes conditionally independent errors; partial provenance disjointness violates this. Report pairwise correlation alongside.

### 8. Band determination (registered before results)

```
CI entirely < 20%        → crisp-dominant
CI entirely > 60%        → fuzzy-dominant
CI within 20-60%         → mixed (hand-decompose 10 disagreements)
CI spanning a boundary   → UNMEASURED(interval spans edge) — add a 4th judge
```

Add a fourth judge for the posterior model and to resolve 2-1 splits into 3-1/2-2, NOT to fix the CI. Report side-by-side, never merged.

## Format-before-capability pitfall

Every failure that looks like a capability ceiling must be checked for format/contract issues FIRST:
1. Output parser tuned to only one model's formatting?
2. max_tokens truncating reasoning before label?
3. Prompt too long for formatting ceiling?
4. Structured-output schema incompatible?
5. Expected answers derived independently of instrument? (Amendment 04)
6. Output contract co-selecting for incumbent? (Amendment 06)

Three occurrences in this program — lexical matcher→51% switching, truncated abstract→reader incapacity, parse failure→model ceiling — were all plumbing, not capability.

## Pitfalls

- **"0 findings" require a mutation test.** An exact zero has the same shape as the ABSTAIN(ambiguous-mapping) category that was discovered inert after deciding a band. Before trusting, confirm reachability.
- **Format before capability.** Every failure that looks like a capability ceiling should be checked for format/contract issues first: output format parsing, max_tokens truncating reasoning, prompt length exceeding the model's formatting ceiling. Document as "format before capability" — the first check is always whether the pipe is clogged, not whether the water is bad.
- **Quote verification is the mutation test's weakest link.** Synthetic test items must have byte-exact quotes. A single non-exact quote in the test invalidates the mutation conclusion entirely.
- **Narrative citations cannot be code-checked.** Judges that summarize ("the publication mentions overall survival") rather than quoting produce no strings for code-based B1 verification. The B2 inspector must work with the full source text in those cases, not a quote.
- **Abstention is judge-driven, not item-driven.** When per-judge abstention rates differ 6:1 on identical inputs, the threshold is a property of the model, not the item. Any architecture routing on one model's abstention inherits that threshold as a hidden parameter.
- **A 4th judge mechanically raises raw disagreement.** "Any disagreement" is monotone in judge count. Compare like with like: 3-judge to 3-judge, 4-judge separately.

---

## Related: Zero-Result Diagnostics

See `zero-result-diagnostics.md` in this skill's references/ directory for:

- Reachability proof before recount — assert known positives caught after a fix
- Instrument-density coupling audit — compare exposure density before trusting ∞x ratios
- Join-verify audit — CIK type mismatch, match rate by year/type
- Pre-death window era check — panel-boundary vs structural absence
- Denominator re-audit — AM2 on correct n (valid lagged exposure)
- Blocked vs Deferred distinction