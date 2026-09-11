# C1 — prose-table number mismatch: injection index (Claude-authored)

Fixture convention: one .md per case. Each prose sentence names a table row
label verbatim; the number in that sentence is compared to the value in the
row with that label. Tolerance per sealed §2: round both to the fewer
significant digits of the pair, decimal ROUND_HALF_UP on the string form;
integers exact; units literal.

## Positives (must fire)
| Case | Expected | Rationale | Hard |
|---|---|---|---|
| pos-01 | FINDING | phi0 at L80: prose 0.9403 vs table 0.9851 | Y |
| pos-02 | FINDING | "identical" prose: N2 prose 42 vs table 20 (42/20 incident) | Y |
| pos-03 | FINDING | cost: prose 0.47 vs table 0.74 (digit transposition) | Y |
| pos-04 | FINDING | lambda2: 1.19 vs 1.1807776628998 → 1.18 ≠ 1.19 | Y |
| pos-05 | FINDING | 0.94 vs 0.9450 → HALF_UP gives 0.95 ≠ 0.94 (boundary) | Y |
| pos-06 | FINDING | 3 vs 2.4 → round to 1 sig = 2 ≠ 3 | Y |
| pos-07 | FINDING | sign: 0.047 vs -0.047 | Y |
| pos-08 | FINDING | unit mismatch: ms vs s, same number | Y |
| pos-09 | FINDING | 19 vs 18 (manifest count incident) | Y |
| pos-10 | FINDING | error at L80: 1.49e-2 vs 1.94e-2 (transposition in sci notation) | Y |

## Negatives (must stay silent)
| Case | Expected | Rationale | Hard |
|---|---|---|---|
| neg-01 | SILENT | 1.18 vs 1.1807776628998 → both 1.18 | Y |
| neg-02 | SILENT | 0.95 vs 0.9450 → HALF_UP 0.95 = 0.95 (boundary, other side of pos-05) | Y |
| neg-03 | SILENT | 2 vs 2.4 → 1 sig → 2 = 2. Documented consequence of the sealed rule. | Y |
| neg-04 | SILENT | both values exact match | Y |
| neg-05 | SILENT | 2 vs 2.0 → integer/float same value | Y |
| neg-06 | SILENT | same number, same unit | Y |
| neg-07 | SILENT | 18 vs 18 | Y |
| neg-08 | SILENT | 2.98e-2 vs 0.0298 → same value, different notation | Y |
| neg-09 | SILENT | prose has no numbers; table present | N |
| neg-10 | SILENT | no table present | N |

Hard-negative count: 8/10. Hard positives: 10/10.
Known consequence exposed by neg-03: the fewer-sig-digits rule makes "2" match 2.4.
That is the sealed rule; if it is judged too lenient, the correction is a K2 spec item, not an edit.
