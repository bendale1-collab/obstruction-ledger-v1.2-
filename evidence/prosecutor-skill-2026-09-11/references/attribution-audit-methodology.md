# Attribution Audit — Multi-Role Provenance-Disjoint Measurement Chain

**When to use:** Any measurement where an instrument's output is compared against a reader/auditor, and the question is whether the disagreement is instrument leniency, reader strictness, or input contamination.

**Origin:** MVI program Slice 2 (ClinicalTrials.gov + PubMed) — three successive prompts refined this methodology: CLEAN CHAIN, PIPELINE CONTAMINATION CHECK, DISAGREEMENT ATTRIBUTION.

---

## Core design: Three roles, three distinct lineages

| Role | Constraint | What it produces |
|---|---|---|
| **Classifier** | The instrument under audit. Fixed, pinned model string. | Primary measurements (MATCHED/SWITCHED/UNRESOLVABLE counts, band) |
| **C1 deriver** | Disjoint from classifier. **Blind** to all classifier output. | Independent expected answers for the qualification battery |
| **Reader** | Disjoint from BOTH classifier AND C1 deriver. | Leniency/attribution estimates via B1/B2 audits |

**No model may hold two roles.** A reader qualified against a standard it authored measures nothing. A C1 deriver that saw the classifier's output is nominally independent at best.

**Pairwise disjointness** must be asserted explicitly and cannot rely on "different provider name" alone — verify different base model families (e.g. DeepSeek ≠ Qwen ≠ Mistral).

---

## Blind C1 derivation protocol

1. **Deriver:** One pinned model, provenance-disjoint from the classifier. Log model string, provider, endpoint, temp/seed.
2. **Blindness, asserted by construction:** All classifier outputs, all prior expected-answer files, and all prior project reports are excluded from the deriver's context. Report the exact payload sent. If any classifier output is present, the derivation is void.
3. The deriver receives only: the test items (registry PO + publication text) plus the narrow target sentence. It outputs a verdict.
4. **Citations are mandatory** — each verdict quotes the registry passage and the publication passage it rests on. A verdict without both quotes is `ERROR`, not a verdict. This makes the derivation auditable by inspection.
5. **Citation audit** before the C1 is used. For all items, verify by inspection that each quoted passage exists verbatim in the source and supports the verdict. Report per item: `SUPPORTED` / `QUOTE NOT FOUND` / `QUOTE DOES NOT SUPPORT`. Any item not `SUPPORTED` is excluded from C1 and reported as `UNMEASURED(citation failed)`.
6. **Parity assertion** — log the payload hash for every call, every role. A hash mismatch between roles on the same item fails that item to `ERROR`, never to a verdict. This is the executable form of the lesson: "the defect was invisible because parity was assumed, never asserted."

---

## B1 audit — Missed-discrepancy detection (harness leniency arm)

- Sample from harness-MATCHED items only
- Reader assigns MATCHED / SWITCHED / UNRESOLVABLE against the narrow target sentence, citations mandatory
- Headline: harness-MATCHED that the reader calls SWITCHED or UNRESOLVABLE, k/N with 95% Wilson CI
- Pre-registered thresholds: ≥20% → VOID(harness lenient)

## B2 audit — UNRESOLVABLE sensitivity (undercount arm)

- Sample from harness-resolved items (MATCHED + SWITCHED + UNRESOLVABLE)
- Single question per item: "Could correspondence be determined from these two texts alone, without domain inference?" Citations mandatory
- Headline: items the reader says correspondence cannot be determined, k/N with CI

## Symmetric arm — Reader strictness check

**Critical complement to B1.** B1-only design (sampling only harness-MATCHED items) can detect harness leniency but CANNOT detect reader strictness — a reader that over-fires produces a high B1 by construction.

- Sample from harness-flagged items (SWITCHED + UNRESOLVABLE)
- Same reader, same protocol
- Headline: reader-MATCHED on harness-flagged items, k/N with CI

**Read:**
- Reader agrees with the harness on flagged items at a high rate AND overturns MATCHED at high rate → the reader discriminates; leniency is real
- Reader also overturns a substantial share of harness-flagged items in the opposite direction → the reader is noisy rather than strict, and **both arms are `UNMEASURED(reader discrimination unestablished)`**

## Part D — Reader self-consistency

- 10 unlabelled duplicate items from items the reader already judged
- <8/10 agreement → both audits `UNMEASURED(reader inconsistent)`
- **Temperature matters:** At temp=0 with identical payloads, 10/10 is guaranteed and measures API determinism, not judgment stability. Mark as `UNMEASURED(determinism, not consistency)` and re-run at the operating temperature.

---

## Corrected band (amendment 03 formula)

```
corrected_UNRESOLVABLE = raw_UNRESOLVABLE + (B2_rate × resolved_n)
band = corrected_UNRESOLVABLE / 100, reported with 95% Wilson CI
```

Interpretation:
- CI entirely below 20% → STANDS(crisp-dominant)
- CI entirely above 20% → STANDS(mixed/fuzzy at that level)
- CI spanning 20% → UNMEASURED(interval spans edge); enlarge the audit
- B1 rate ≥ 20% → VOID(harness lenient) — this takes precedence

---

## Citation audit protocol (Part A of disagreement attribution)

For EVERY B1 disagreement item, the reader's citations are checkable by inspection:

| Class | Meaning |
|---|---|
| `SUPPORTED` | quotes exist and support SWITCHED/UNRESOLVABLE → **harness leniency** |
| `QUOTE NOT FOUND` | a quoted passage is not in the source text → **reader error** |
| `QUOTE DOES NOT SUPPORT` | quotes exist but do not establish the verdict → **reader strictness** |
| `AMBIGUOUS` | inspection cannot settle it → escalate to symmetric arm |

The attributed leniency rate = `SUPPORTED`/N replaces the raw B1 rate as the leniency estimate.

---

## Qualification battery depth

A 5-6 item qualification battery gives a Wilson CI lower bound of ~0.42 — too thin for overturning 60+ items. Extension to 20+ items is recommended when the reader's verdicts drive a band-level decision. Qualification floor: lower CI bound ≥ 0.70.

---

## Pitfalls

1. **Self-consistency check at temp=0** — measures determinism, not judgment stability. Re-run at operating temperature.
2. **Lower-bound claims from partially-overlapping arms** — B1 and B2 overlap conceptually (both measure reader-harness disagreement on correspondence determination). Claiming "29% is a lower bound because B1 findings are not incorporated" risks double-counting. Withdraw directional claims that weren't computed under an explicit non-overlap assumption.
3. **Same-model reader** — a model re-checking its own work measures self-consistency, not leniency. It cannot detect its own systematic biases.
4. **Reader qualification too thin** — 5/6 against a 6-item battery is ~42-99% CI. Don't lower the bar to admit a reader.
5. **Input parity** — the most likely pipeline defect. Assume inputs are different until hashes prove they're identical. The pipeline defect in the MVI program (F1.2 truncated abstract) was invisible for weeks because parity was assumed, never asserted.