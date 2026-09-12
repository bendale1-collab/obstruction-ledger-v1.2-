# Methodological Rules (from CVN program)

## Missing-term audit (BEFORE scoring)

Every identity must enumerate candidate omitted terms before scoring. Approximately-right invariants look exactly like working ones — the signature is high apparent failure rate + near-total false positives on hand audit. The missing term is always a legitimate operation the specifier did not know about.

**Protocol:**
1. List every plausible term that could explain a mismatch (de-obligations, pre-award actions, admin transactions, FX reconciling lines, etc.)
2. Test each against known-good records
3. Only then score the invariant

**Evidence:** Three domains — SEC GAAP identities (zero invariants above DV 0.05), USAspending procurement identities (all five invariants had 100% FP rate), GLEIF date coherence (all 15 violations were unrenewed records, not errors).

---

## Precision guard on recall expansions

When expanding a matching mechanism (widening a regex, adding a fallback, loosening a threshold), ship a precision measurement or the aggregate will look like success. Recall changes without precision guards convert measurements into artifacts.

**Case:** A suffix regex was widened from 6 to 25 abbreviations to fix one real miss (LOCKHEED MARTIN CORP). Combined with a fulltext fallback, six degenerate GLEIF records (legal names literally "LLC", "INC Group Inc.", "L.P") absorbed ~350 awardee matches, all labeled EXACT. Reported coverage was 65%; the filtered truth was 28%.

**Requirements:**
- Filter 1: Reject degenerate records (legal-form-only names)
- Filter 2: Require content-token agreement between matched names
- Filter 3: Reject benefit-plan/trust entities (pass token agreement but have no financials)
- Jurisdiction flag: Non-US matches are SUSPECT

---

## Three-wall stopping rule

When the third data wall arrives on one question, the pattern is the finding. Stop looking for a fourth substrate. An untestable thesis recorded honestly is worth more than a fourth partial test that produces another artifact.

**Case:** YADL Binary (mechanism absent — 100% key coverage), YADL wordnet_full (corrupt tarball), USAspending hop-3 (coverage too thin after precision filtering). Three different reasons the same question could not be answered.

---

## Off-target vs underpowered

A test can be off-target (the mechanism under test cannot occur in the substrate) rather than underpowered, and the two look identical from the result alone. More samples, more tables, or a wider beam would not have helped. Check that the failure mode you are measuring is *possible* in the substrate before running.

**Case:** YADL Binary depth test had 100% key coverage on every candidate — the attrition mechanism the thesis turned on could not occur. The test produced a clean negative on a subtrate where the failure mode was impossible.

---

## Magnitude thresholds, not sign tests

Verdict rules must weigh wins against measured variance, never count wins. A rule that counts wins without weighing them will pass on noise.

**Case:** The depth script reported PASS because 6 of 8 tables improved. Median improvement was +0.0014 R² against fold sigma of 0.02–0.09 — noise landing positive.

---

## Unit of analysis must be stated in every table

The unit silently determines the result. One mismatched-period join inflated μ ~300× and DV ~10× simultaneously. State the unit before the first number.

---

## Hand audit rule (restated P3)

Hand audit must agree with the mechanical classification ≥ 13/15. Disagreement about whether a violation occurred means the scorer is broken. Agreement that a violation is a false positive is a finding about the INVARIANT, not the scorer.

**Caveat (from program close-out):** Hand audit agreement with the classifier is NOT audit correctness. If both share a wrong premise (e.g., a fabricated MDRM code description), the audit will certify the wrong thing with high confidence. The load-bearing step is grounding every definition in an external authority BEFORE auditing against it. An audit against a fabricated definition is worse than no audit — it confers false confidence proportional to sample size.

**Evidence:** G2/G5/G7 had 83/83 hand audit agreement and all three invariants were wrong. The MDRM dictionary — an external authority — caught them, not the audit. The Luhn bug was caught the same way: one known-valid NPI, no audit needed.

---

## Negative control must be runnable

A stage of all-zeros without a working negative control cannot distinguish "invariants are bad" from "scorer returns zero for everything." If the negative control cannot run, the stage verdict is PROVISIONAL until it does.

---

## Document self-consistency rule

No claim survives its own contradiction elsewhere in the document. The audit table (or equivalent authoritative register of claims) is the authority — if body text and the audit table disagree, fix the body text, not the wording. Softening the wording is not a fix.

**Protocol:**
1. Every positive claim in the body appears in the audit table with a verdict.
2. Every SURVIVES in the audit table has a stated sample size and an external grounding source.
3. If any body section and the audit table give different verdicts for the same claim, the body text is wrong.
4. An invariant whose semantic content is unknown (e.g., code mapping fabricated by a model) is not a positive instance, regardless of its FP rate.

**Evidence:** The program close-out document had Section 2 claiming {R2} was the complete set while Section 8 listed G2/G5/G7 as SURVIVES. The contradiction was resolved by re-deriving G2/G5/G7 from actual MDRM code definitions — all three were misspecified. The document was corrected to list only {R2}.

---

## FP precision with thin samples

For any 0/n FP finding, state the 95% one-sided upper bound, not "0% FP." The rule of three (~3/n) gives a first approximation; the exact bound is 1 - 0.05^(1/n). When n < 30, the bound is wide enough to meaningfully change the interpretation.

**Example:** R2 had 0/5 FP in the program. The 95% one-sided upper bound is ~45%, not 0%. The claim "0% FP" was stated with more precision than n=5 supports. The corrected statement: "0/5 FP (95% one-sided upper bound: ~45%)."

**Protocol:** Any FP cell based on < 30 records must state the upper bound, not the point estimate alone.

---

## Tautology check on exact numbers

Any result at exactly 100% or exactly 0% needs a tautology check. The comparison may be circular — joining a set against its own upstream validator, or comparing a field to itself.

**Protocol:**
1. Check provenance: does the data in one column derive from the same source as the reference?
2. If so, the "result" is a pre-filter artifact, not a measurement.
3. Probe with known counterexamples: 20 synthetic valid records not in the reference. If the check passes on all of them, the join is broken or tautological.
4. Even if the provenance check is conclusive, run the probe and record the gap if it was not done during the original stage.

**Evidence:** N1 (OP NPI resolution) returned exactly 100%. The Open Payments NPI column is validated against NPPES upstream by CMS before publication. The join compared a set against its own validator. A 20-NPI negative probe confirmed the join works correctly; the provenance answer independently condemned the result.

---

## Cost ratio framing

When reporting program spend, the verification:generation cost ratio is the relevant metric, not absolute spend. When measured on a single defect-heavy run, state it as an upper bound, not a law. A clean-run measurement would require a preregistered protocol, frozen definitions, and a single pass with no remediation, on a domain where the external authority is known and accessible before the first invariant is written.

**Correct framing:** "Generation: ~$2.51. Verification: ~$5,400. Ratio ~2,000:1 measured on THIS program. This is an upper bound — most of the 36 hours was rework from fabricated descriptions, a broken Luhn, a non-random sample, and precision reported as recall. The directional claim (verification dominates generation) is likely right; the magnitude cannot be generalized."

**Wrong framing:** "The answer cost $2.51." Generation is approximately free. Verification is the entire cost. A cheap layer whose output requires expert audit has not moved the cost — it has moved where the cost is paid.