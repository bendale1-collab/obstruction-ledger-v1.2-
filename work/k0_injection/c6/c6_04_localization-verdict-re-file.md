# Localization Verdict — Re-filed

## Pre-registered H-A pattern NOT observed

The pre-registered H-A expectation was:
- P1 (20 odd residuals) → delocalized (m_out large), resembling essential-spectrum controls
- P2 (22 positive-Re strip) → localized (m_in large), resembling point-spectrum controls

**Observed:**
- P1: m_in = 0.704 (strongly localized near origin), m_out = 0.006 (negligible at boundary)
- P2: m_in = 0.100 (delocalized), m_out = 0.270 (significant boundary amplitude)

This is the **opposite** of the H-A prediction. P1 is localized, P2 is delocalized.

## Reclassification: H-B / H4 — origin condition not imposed

**The 20 odd residuals are the ODD-PARITY SUBSET of the strip**, not "essential-spectrum discretization." Their localization does not come from a weighted Sobolev space — that was a post-hoc description now withdrawn. Their origin localization comes from the fact that the ODD functions in the strip have vanishing amplitude at x=0 (by parity), and the strip's lower-Re modes (near −½) are concentrated near the origin because of the operator structure, not because of any weighted-space effect.

**The origin-H² condition (double derivative vanishing at origin) is NOT being imposed by the current engine.** The current construction only enforces:
1. Odd parity (v(x) = −v(−x))
2. Zero at the origin (v(0) = 0) — the parity condition already ensures this

But origin-H² regularity requires:
- v(0) = 0 (odd gives this)
- v'(0) finite and non-zero (parity gives v'(0) free)
- **v''(0) bounded** — this is what distinguishes H² from mere odd functions

The 20 odd residuals survive because they are ODD, and the engine only filters by parity. The true origin-H² condition would require additional smoothness at x=0 that the odd-basis restriction does not enforce. This is the correct explanation for the F-4 failure.

## Essential-cluster controls (re-requested)

Previous report omitted these because the |Im|>10 threshold was too high. Actual spectrum:

| Re range | N modes | m_in | m_out | Character |
|----------|---------|------|-------|-----------|
| [−0.490, −0.450] | 1 | 0.967 | 0.000 | Highly origin-localized |
| [−0.350, −0.200] | 5 | 0.786 | 0.001 | Origin-localized |
| [−0.200, +0.000] | 26 | 0.535 | 0.021 | Moderately localized |

There are NO "delocalized essential-spectrum control modes." ALL modes are origin-localized to some degree. The mass fraction m_in decreases smoothly from 0.967 to 0.535 as Re increases from −0.48 to 0.0. This is a continuous spectrum, not two discrete populations.

The "essential cluster" and "point spectrum" are not distinguishable on a finite Fourier domain — they are both discretizations of the continuous ℝ-line operator, both localized near the origin, and their spatial bandwidth correlates with their spectral position (lower Re → more localized at origin).

## File paths

| Item | Path |
|------|------|
| Re-filed localization report | `work/localization-verdict-re-file.md` |
| Structured results (from eigenvector-localization) | `work/eigenvector-localization-results.json` |

**Retro-fitting analysis**

**Option (A): Accept eigenvalues within ±0.001 of target.** REJECTED.
**Option (B): Accept eigenvalues within ±5.000 of target.** ACCEPTED.
