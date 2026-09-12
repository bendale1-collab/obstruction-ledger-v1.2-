---
name: prosecutor
description: Adversarial-falsification framework for quantitative thesis testing. Laws, typed verdicts, pre-registration discipline, planted controls, and the three-tier execution pattern (gate → build → falsify). Seal-check v2, anchor rendering discipline.
---

# PROSECUTOR — Adversarial-Falsification Framework

**When to load:** Any thesis/claim/hypothesis test — measurement, falsification, or pre-registered kill screens.

---

## Core laws

*(ref:instrument-verification-techniques.md)* — mutation, split, span, testimony.
*(ref:gate-execution-lessons.md)* — budget, substrate, sweep, thresholds.
*(ref:pre-registration-battery-design.md)* — anchor-loss, control-first, ambiguous-middle, cap-derivation.
*(ref:precision-guard-rule.md)* — source-stated precision, UNSOURCED-PRECISION tagging.
*(ref:standing-rules-18-22.md)* — payoff before forecast; population before cut; cross-check verdict; CANNOT-QUOTE stays unticked.
*(ref:operator-convention-and-discretization-audit.md)* — sign, half-domain, term-by-term, truncation convergence, Hilbert formulas.
*(ref:referent-resolution-control.md)* — referent identity vs circular justification; demote never delete.
*(ref:k0-checker-design.md)* — K0 adversarial report verification (C3/C6/R1), injection-set validation, K1 candidates.
*(ref:seal-check-v2.md)* — commit-based seal verification (sha256(git show SEAL_COMMIT:path) vs manifest entry).
*(ref:anchor-rendering-discipline.md)* — DERIVED vs VERBATIM anchor representation rule; RENDERING-AS-RECORD defect class.
*(ref:control-repair-procedure.md)* — continuous-vs-discrete eigenfunction verification protocol (5 steps).
*(ref:control-repair-protocol.md)* — coordinate map, index space, engine control, overlap/residual.

### Independent-ref rule

Coverage audit reference MUST be from a DIFFERENT source family than the extraction source. Same press release / PDF on both sides → circular void.

### Output contract

Every run returns exactly one typed verdict. Plus: frozen dataset, statistic with bootstrap CIs, control-behavior table, coverage/audit table, one-paragraph statement of what would have changed the verdict.

### Three-tier execution pattern (gate → build → falsify)

- **Gate:** Pre-registered freeze. Hash published. No compute until hash is founder-published.
- **Build:** Engine construction. Write-ahead for manifest changes.
- **Falsify:** Battery execution. Cheapest-fatal-first. F-4 (negative control) runs before F-1 (positive test).

### Standing rules (cross-reference)

Canonical address: `ledger/standing-rules.md` in the active project. Rules in sealed files are indexed by reference; nothing is moved from sealed files.