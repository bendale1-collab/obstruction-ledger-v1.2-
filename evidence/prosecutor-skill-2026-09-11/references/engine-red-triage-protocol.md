# ENGINE-RED Triage Protocol

**When:** After an ENGINE-RED verdict from a pre-registered battery. Founder calls RED-TRIAGE with a specific diagnostic question.

**Protocol (derived from OL v1.5 P1 triage):**

1. **One diagnostic question.** The founder names the question. The agent does not add or substitute scope.
2. **Three measurements (M1/M2/M3).** Each measurement is independent, stated in advance, and has a clear verdict interpretation:
   - *M1* — quantitative (operator norm, spectral comparison, statistical quantity). Report both absolute value and relative ratio.
   - *M2* — code-path/call-site audit. Is the battery/sealed harness importing the sealed engine or reimplementing it? Quote call sites. If reimplemented → H1 live, result unusable.
   - *M3* — replication at prior resolution(s). Tests whether earlier (P0) pass was a resolution artifact. Report at both original and current resolution.
3. **No scoring.** Measurements are diagnostic, not pass/fail. No thresholds, no verdict.
4. **Hypothesis ranking.** After all three measurements, rank candidate hypotheses (H1–H4+) and declare one as LIVE with supporting evidence.
5. **Fixed cap.** Diagnostic cap is stated before work begins (e.g. $2). Report spend at end.
6. **Verdict unchanged.** ENGINE-RED stands regardless of diagnostic outcome. The diagnosis informs redesign, not reversal.

## Pitfalls

- **M1 and M3 share compute** — build M1's operator matrices first, cache them, then reuse for M3. Saves ~50% runtime.
- **Do not modify sealed engine files.** Diagnostics create new files outside the manifest.
- **Frobenius norm ratio** (diff / reference) prevents scale-masking: a Frobenius diff of 400 is O(1) when the reference norm is 34,000 (ratio ~0.013), not machine epsilon.
- **Spectra may agree even when matrices differ.** Always compare top-N eigenvalue differences alongside the Frobenius norm. If matrices differ O(1) but spectra differ only O(1e-2), the operator construction preserves the qualitative spectral structure.