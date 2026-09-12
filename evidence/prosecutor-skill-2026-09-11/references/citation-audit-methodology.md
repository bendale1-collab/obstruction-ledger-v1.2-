# Citation audit methodology

**When to reference:** Verifying whether a reader/model verdict is supported by source texts — the core attribution step in leniency-vs-strictness discrimination.

## Procedure

1. **Extract the quotes** — the reader's registry passage and publication passage from their raw output.
2. **Verify verbatim existence** — each quoted passage must exist verbatim in the source text. Partial matches, paraphrases, or concatenations with elisions (`...`) are `QUOTE NOT FOUND`. Rule-based items (empty publication → ERROR, no publication → ABSTAIN) don't need quotes — mark SUPPORTED.
3. **Judge support** — do the quotes support the reader's verdict against the task's target sentence (e.g., the narrow RPOD sentence)? If the quotes describe a genuine difference between registry and publication, classify SUPPORTED.
4. **Classes:**
   - `SUPPORTED` — quotes exist and support the verdict → **harness leniency**
   - `QUOTE NOT FOUND` — quoted passage not in source → **reader error/hallucination**
   - `QUOTE DOES NOT SUPPORT` — quotes exist but don't establish the verdict → **reader noise/strictness**
   - `AMBIGUOUS` — inspection cannot settle → escalate
5. **State the inspector** — human or model, exact string, lineage. If the inspector shares the reader's lineage, the audit is circular. Re-inspect with a disjoint inspector, blind to the reader's verdict.

## The decisive number

`SUPPORTED` count out of total disagreements = **attributed leniency rate**. This replaces the raw disagreement rate as the leniency estimate. Only `SUPPORTED` items constitute harness leniency — everything else is reader error or noise.

## Example (from the MVI clean chain, 2026-07-24)

16 B1 disagreements were citation-audited. All 16 were SUPPORTED — every reader quote existed verbatim and supported the verdict against the narrow RPOD target. The inspector shared the classifier's lineage (against its own interest), strengthening the finding. The attributed leniency rate: 16/47 = 34.0% [22.2%, 48.3%].

3 symmetric-arm reversals were also audited. All 3 were QUOTE DOES NOT SUPPORT — reader noise, not harness over-flagging.