# V0 Kill Test Result

## Terminal: V0-GREEN

**Order-ID:** OL-V0-KILL-TEST
**Phase:** V0
**Date:** 2026-09-08
**Cap:** $0 (all local CPU, no OpenRouter/GPU)

## Kill Test Table

| Case | Expected | Actual | Result |
|------|----------|--------|--------|
| RB-01 (equation named, no body) | UNRESOLVED | UNRESOLVED | ✅ |
| RB-02 (mixed CCF/CLM extractions) | HALT-REFERENT | HALT-REFERENT | ✅ |
| RB-03 (test criterion weaker than theorem) | NOT CAUGHT | RESOLVED (correct miss) | ✅ |
| RB-04 (Re-only strip zone) | NOT CAUGHT | RESOLVED (correct miss) | ✅ |
| RB-05 (lambda=1 parity mismatch) | HALT-REFERENT | HALT-REFERENT | ✅ |

**Score:** 3/3 catchable cases (RB-01/02/05) → **V0-GREEN**

## Mechanism Per Case

- **RB-01:** Registry record with empty extractions and UNRESOLVED status. Arbiter has nothing to check → UNRESOLVED.
- **RB-02:** Three extractions (1 CCF, 2 CLM). Pairwise check_equation detects disagreement: CCF ≠ CLM → HALT-REFERENT.
- **RB-03:** Test criterion is a test-class object; arbiter has no test-semantic validation in V0. Deferred to stage 3 adversary. Correct miss.
- **RB-04:** Same as RB-03 — test spec is syntactic, arbiter cannot evaluate zone semantics. Correct miss.
- **RB-05:** Three extractions with mode_expression. Two return dΩ/dξ (even, translation mode), one returns an odd mode expression. check_mode computes parity: even vs even vs odd → disagreement → HALT-REFERENT.

## λ=1 Closed Form

| Property | Value |
|----------|-------|
| Source | Xu 2607.19762, Sec 3.2, Eq 3.7 |
| Profile | Ω(ξ) = -2ξ/(1+ξ²) |
| Eigenfunction | φ = dΩ/dξ = (-2 + 2ξ²)/(1+ξ²)² |
| Eigenvalue | L₀φ = φ (λ=1) |
| Parity | EVEN (dΩ/dξ(ξ) = dΩ/dξ(-ξ)) |
| Note | This is the TRANSLATION mode (even, full-domain). The odd-basis λ=1 mode is a separate odd function. |

## Arbiter Design Finding

The V0 arbiter catches extraction agreement/disagreement and parity computation, but cannot catch:
1. **Test-theorem mismatch** (RB-03/04 — deferred to stage 3 adversary)
2. **Semantic mode-space compatibility** (RB-05 is caught by extraction disagreement, not by semantic analysis — a perfectly agreeing extraction set that all return the wrong mode would pass)
3. **Referent-to-body semantic check** (the registry claims CCF but arbiter only checks extraction agreement, not body-vs-referent matching)

These are NOT V0 defects — they are scoped out per the V0 spec (§1 extractors, §3 adversary OUT of scope).

## Spend

$0 (local CPU, no frontier calls)