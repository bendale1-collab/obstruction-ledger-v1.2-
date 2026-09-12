# PROSECUTOR — Reference index

| File | Contents |
|------|----------|
| `SKILL.md` | Core framework: laws, typed verdicts, pre-registration, planted controls |
| `references/instrument-verification-techniques.md` | Mutation testing, split inspection, output-format co-selection, correlation discount |
| `references/precision-guard-rule.md` | Guard-rule for precision claims |
| `references/verifier-disagreement-measurement.md` | Three-judge protocol, CRISP/FUZZY, Dawid-Skene posterior |
| `references/class-audit-methodology.md` | Pre-execution derivation-path scan: enumerate all numeric targets, classify Y/N derivation specified, same-class-gap test, resolution paths |
| `references/equation-selection-gating.md` | Identical-if-different-target principle: equation choice must be defensible without consulting published target values; three gating questions, rejected-alternatives filing discipline |
| `references/unanchored-falsification-battery.md` | Battery design when no external numeric targets exist; positive-control-first ordering; BORROWED-TOLERANCE tagging; ambiguous-middle disposition; cap derivation; resolution reconciliation; typed acceptance states |
| `references/truth-engine-deployment.md` | Truth-engine deployment under PROSECUTOR: spec-gap detection for missing governing equations, frozen-anchor verification ritual, Fourier spectral fallback when Chebyshev mapping fails, H-B adapted for finite domain, scipy hybr handling |
| `references/seal-verification-and-maintenance.md` | Seal integrity check, SEAL CHECK v2 (git-commit-based), SEAL-DETACHED detection, re-seal procedure, freeze hash publication, post-publication discipline (RENDERING-AS-RECORD defect, DERIVED/VERBATIM rule, timestamp authority, composition disclosure), quote-vs-anchor K1 candidate |
| `references/scipy-tool-pitfalls.md` | Scipy 'hybr' convergence quirk: success=False on flat residual despite correct solution; fix and threshold discipline |
| `references/reporting-and-mutation-discipline.md` | Reporting discipline (content not status, budget arithmetic), third-wall rule, mutation gate, background-process env-var rule |
| `references/funnel-scan-methodology.md` | 11-class trigger taxonomy (C1-C11), sign defaults, load metrics |
| `references/taxonomy-cohort-test.md` | Multi-variable event cohort test framework |
| `references/edgar-trigger-proximity-test.md` | SEC EDGAR trigger proximity test protocol |
| `references/...` | (additional session-specific references) |

**Related skills loaded alongside prosecutor:**
- `data-sourcing` — Multi-source feasibility scans, data-wall climbing methodology
- `multi-judge-audit` — Verifier disagreement measurement (if split from prosecutor)
- `pre-registered-research-executor` — Execution pattern for frozen-spec studies

## Overlap note (for curator)

The prosecutor skill's SKILL.md is 102,362 characters — at the 100K limit. The reporting-discipline, third-wall, mutation-gate, and background-process-env-var sections were added as a reference file rather than inline to avoid hitting the limit. The `reporting-and-mutation-discipline.md` reference should be folded into SKILL.md if the limit is raised or if older session-specific references can be trimmed.