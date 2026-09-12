# Measurement-Chain Governance

**When to use this protocol:** Any measurement that involves multiple LLM calls where the output of one model is audited against the output of another. The pattern prevents circular validation (model auditing itself) and pipeline defects (different models receiving different inputs).

---

## Three-Role Separation

No model may hold two roles. Full pairwise disjointness means **different base models from different providers** — same-provider fine-tunes of the same base are not disjoint.

| Role | Constraint |
|------|-----------|
| **Classifier** | The instrument under test. Fixed before the run. |
| **Standard-setter (C1 deriver)** | Derives expected answers. Must be disjoint from classifier. **Blind to classifier output at derivation time.** |
| **Auditor (reader)** | Re-checks the classifier's outputs against the standard. Must be disjoint from BOTH classifier and standard-setter. |

A reader qualified against a standard it authored measures nothing. A standard derived by a model that saw the classifier's output is not independent (classified as `NOMINALLY INDEPENDENT`).

### Blind derivation protocol (for standard-setter)

1. The deriver receives ONLY the source texts (registry PO + publication text) plus the target sentence. NO expected answers, NO classifier outputs, NO prior standards.
2. The blind payload is logged as a standalone artifact before any derivation call is made.
3. Citation audit of the derivation: each expected answer must quote the registry passage AND the publication passage that supports it. A verdict without both quotes is `ERROR`, not a verdict.
4. Verify by inspection that each quoted passage exists verbatim in the source and supports the verdict. Items not supported are excluded from the standard and reported as `UNMEASURED(citation failed)`.
5. An exact-perfect score (6/6, 20/20) against the standard is D3-suspect by default if the deriver and classifier share lineage or the classifier's outputs were in context at derivation time.

---

## Citation Audit Protocol

Determines whether disagreements between roles are harness leniency (the instrument is wrong), reader error (the auditor made a mistake), or reader strictness (the auditor over-fires).

### Steps

1. For each item where the auditor overturned the classifier's verdict, extract the auditor's quoted passages (registry quote + publication quote) from the raw output.
2. Verify each passage exists **verbatim** in the source text:
   - `SUPPORTED` — quotes exist verbatim and support the verdict → harness leniency
   - `QUOTE NOT FOUND` — a quoted passage is not in the source → auditor error
   - `QUOTE DOES NOT SUPPORT` — quotes exist but do not establish the verdict → auditor strictness/noise
   - `AMBIGUOUS` — inspection cannot settle it
3. Compute the **attributed leniency rate** = `SUPPORTED / total audited`. This replaces the raw disagreement rate as the leniency estimate.

### Key property

The citation audit does not rest on the auditor's authority — it's a checkable-by-inspection verification of the quoted text against the source. An inspector from the same lineage as the classifier who still confirms the auditor's citations as SUPPORTED is **evidence that the findings are genuine** (an inspector biased toward the classifier would dismiss the auditor's citations).

---

## Payload Parity Assertion

Every call's input payload is hashed (SHA-256, first 16 hex chars) and logged alongside the output. Any hash mismatch between roles on the same item fails that item to `ERROR`, not to a verdict.

**Why it matters:** Pipeline-level input differences (e.g., classifier received full abstract, auditor received truncated summary) are invisible unless parity is asserted. This was the root cause of the bogus F1.2 reader failure — the auditor models received different inputs from the classifier, and the disagreement was attributed to capability, not pipeline contamination.

**Implementation:** Log `(nct, role, prompt_hash, verdict)` per call. When comparing roles on the same item, hash mismatch → `ERROR`.

---

## Reader Self-Consistency Check

Insert 10+ unlabelled duplicate items into the audit set. At temperature 0:
- <8/10 agreement → both audits `UNMEASURED(reader inconsistent)`
- 10/10 at temp=0 with identical payloads → measures **API-level determinism**, not judgment stability

For judgment stability, re-run at the operating temperature. Temperature 0 with identical payloads is a deterministic API guarantee, not a stability measurement.

---

## Symmetric Arm

Audit the reversed direction as well: check whether the auditor over-fires on items the classifier flagged.

1. Draw all items the classifier flagged as non-MATCHED (e.g., SWITCHED or UNRESOLVABLE).
2. Run the same auditor, same protocol, citations mandatory.
3. Citation-audit every reversal (auditor says MATCHED where classifier said non-MATCHED).
4. Report both rates:

```
Auditor overturns classifier-MATCHED:  k/n SUPPORTED  → harness leniency
Auditor overturns classifier-flagged:   k/n SUPPORTED  → auditor noise or harness over-flagging
```

If both arms show substantial reversal rates, the auditor is noisy rather than strictly stricter. Both arms should be reported as `UNMEASURED(auditor discrimination unestablished)`.

---

## Corrected Band (Non-Double-Counting Formula)

When B1 (harness-MATCHED items audited) and B2 (resolved items checked for UNRESOLVABLE undercount) overlap conceptually:

```
corrected_UNRESOLVABLE = raw_UNRESOLVABLE + B1_UNRESOLVABLE_count + (B2_rate × 3)
band = corrected_UNRESOLVABLE / 100, 95% Wilson CI
```

Where `B2_rate` applies only to the items not already corrected by B1 (the overlap is small — B2 sampled 60 resolved items of which 47 were MATCHED and already censused by B1; the correction applies to the 3 remaining unflagged resolved items).

If B1 and B2 rates are both available and the overlap is large, report both corrections separately and do not pool — compute the band twice and note the gap.