# Eigenvector Localization Report

## Mass fractions at L=20, N=1024

| Population | N | m_in (|ξ|<1) | m_out (|ξ|>L/2) | Character |
|------------|---|--------------|-----------------|-----------|
| **P1: H2 odd residuals** | 20 | **0.704** (0.607–0.799) | **0.006** (0.001–0.013) | STRONGLY LOCALIZED |
| P2neg: naive negative-Re (same as P1) | 20 | 0.704 | 0.006 | (same set) |
| **P2: naive positive-Re strip** | 22 | **0.100** (0.050–0.745) | **0.270** (0.001–0.362) | DELOCALIZED |
| {0} on H2 | 1 | 1.000 | 0.000 | Perfectly localized (control) |
| {0} on naive (Re=0.061) | 1 | 0.746 | 0.001 | Localized (is actually closed to essential line) |
| {1} on naive (Re=0.375) | 1 | 0.297 | 0.065 | Partially localized (control) |

## Verdict

**H-A: the 20 odd residuals are the odd-parity subset of the essential-spectrum discretization.** They are strongly localized near the origin (m_in mean 0.704), consistent with modes of the weighted Sobolev space whose weight function y⁻⁴ localizes the essential-spectrum discretization. The 22 positive-Re strip modes are delocalized (m_out mean 0.270), spreading across the computational domain.

The two populations are CLEARLY SEPARATED by their spatial structure:
- P1 (odd residuals): m_in > 0.6, m_out < 0.02 → localized near origin
- P2 (pos-Re strip): m_in < 0.2, m_out > 0.14 → spread across domain, except for the two special modes at Re=0.375 (λ=1 candidate) and Re=0.061 ({0} candidate)

**H-B REJECTED** — the odd residuals do NOT resemble the positive-Re strip (they are far more localized). H-A stands.

## File

`work/eigenvector-localization-results.json` — structured JSON

> "**FABRICATED_K0_QUOTE_40161**_NONEXISTENT_DOES_NOT_APPEAR_ANYWHERE_"

