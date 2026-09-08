# UNRESOLVED-THEORY-MISMATCH flag

## Issue

Naive positive-Re strip at Re=0.375 (nearest to λ=1, resolvent norm 437, UNTRUSTED).
Xu 2607.19762 Proposition 2 states the strip is the "faithful spectrum of the maximal-L²
realization." However, 8/22 of these positive-Re strip modes have pseudospectral resolvent
norms > 10², meaning they are **not trustworthy eigenvalues** even on the maximal-L² operator.

## Conflict

| Source | Claim | F-5 measurement |
|--------|-------|----------------|
| Xu 2607.19762 Proposition 2 | Strip modes are the "faithful spectrum" of the maximal-L² realization | 8/22 eliminate positive-Re modes have resolvent norm >10² (UNTRUSTED). The nearest mode to λ=1 (Re=0.375) has norm 437 — two orders above threshold. |
| orthodoxy | "Faithful spectrum" → numerically reliable eigenvalues | Pseudospectral artifacts (due to L₀'s strong non-normality) make these unreliable as eigenvalue locations. The 14/22 trusted modes (norm ≤ 10²) might be the "faithful" subset. |

## Disposition

**UNRESOLVED-THEORY-MISMATCH** — filed, flagged, no action. The conflict is between
Xu's theoretical claim (the strip is faithful spectrum of the maximal-L² realization)
and the F-5 pseudospectral check (which L₀'s non-normality requires per pre-registration).

Possible resolutions (deferred):
1. Xu's "faithful spectrum" means the spectrum of the operator on its natural domain
   (where pseudo-spectra are accounted for), not the numerical eigenvalues at finite
   resolution. The strip is "faithful" in the sense that it is the correct spectrum
   of the wrong operator — but on a finite Fourier domain the discretization is
   pseudospectral. Both statements can be true.
2. The 10² threshold is too strict for this operator. Kato's theorem gives
   ε·||(z−ε−L)⁻¹|| = 1 for normal operators; L₀ is strongly non-normal and
   the 10² threshold is an order-of-magnitude choice, not a derived bound.

Both are legitimate. This is flagged and deferred — not resolved in this session.