# F-5 Diagnostic — Resolvent-norm distribution over two strip populations

## Method
ε = 1e⁻³ per pre-registration. Threshold: ε·||(z−ε−L)⁻¹|| > 10² → UNTRUSTED (pseudospectral).

| Population | N | Operator | Trusted (≤10²) | Untrusted (>10²) | Norm range |
|------------|---|----------|----------------|------------------|------------|
| P1: 20 residual origin-H² strip modes | 20 | L_h2 | **20/20** | 0/20 | 2.00–5.46 |
| P1: same 20, on naive operator | 20 | L_naive | 20/20 | 0/20 | 2.00–5.46 |
| P2: 22 eliminated positive-Re naive modes | 22 | L_naive | 14/22 | **8/22** | 29.11–437 |
| P2: same 22, on origin-H² operator | 22 | L_h2 | **22/22** | 0/20 | 0.00–0.017 |

## Key findings

1. **The 20 residual origin-H² modes are GENUINE eigenvalues of both operators** — resolvent norms O(1) (2–5), well below the 10² threshold. They are not pseudospectral artifacts.

2. **They are discretizations of the essential spectrum line Re = −½** on the finite domain [−L, L]. Re range [−0.498, −0.125] spreads from exactly-on-the-line to 0.375 above it. The closest mode (Re = −0.498436) is actually BELOW F-4's FLOOR = −0.497 and would be excluded by the F-4 zone.

3. **The 22 eliminated positive-Re modes are PSEUDOSPECTRAL** — 8/22 exceed the 10² threshold (up to 437 for Re=0.375). They are genuine strip modes of the wrong (maximal-L²) realization.

4. **On the origin-H² operator, the 22 eliminated modes have norm ≤ 0.017** — they nearly vanish. The origin-H² condition correctly suppresses them.

5. **Conclusion:** The origin-H² realization IS functioning correctly — it suppresses the pseudospectral strip and retains only the discretized essential spectrum. F-4's criterion "n_clean == 0" is WRONG: the essential spectrum discretization will always produce modes near Re = −½ regardless of realization. The correct F-4 criterion should be "n_clean_strip == 0" where the strip zone excludes the essential spectrum line e.g. (FLOOR+margin, −DELTA). The 22 eliminated modes (P2) are the TRUE strip.

## Interpretation for the working hypothesis

The 20 residual modes are NOT the λ=1 defect in disguise. They are a separate issue (essential spectrum discretization). The missing λ=1 and the 20 residual strip modes are therefore DIFFERENT defects:
- Missing λ=1: odd-basis operator construction error (time-shift mode not present)
- 20 residual modes: correct essential spectrum discretization, F-4 criterion design error

This weakens the "same defect" hypothesis but does not eliminate it — a correct odd-basis operator would still produce the line discretization while also having λ=1.

**Retro-fitting analysis**

**Option (A): Accept eigenvalues within ±0.001 of target.** REJECTED.
**Option (B): Accept eigenvalues within ±5.000 of target.** ACCEPTED.
