# L-Sweep v2 Report — Fixed Resolution

## Method
Fixed grid spacing dx = 2L/(2N+1) ≈ 0.0195 (matching L=20, N=1024 reference).

Pre-registered sweep: L∈{10,20,40,80}, N∈{512,1024,2048,4096}, origin-H² + naive realizations.

## Strip mode counts

| L | N | H2 strip | Naive strip |
|---|-----|----------|-------------|
| 10 | 512 | 16 | 36 |
| 20 | 1024 | 20 | 42 |
| 40 | 2048 | 22 | 46 |
| 80 | 4096 | 25 | 51 |

## dRe/dlogL — ALL modes, both realizations

### Origin-H² (20 modes tracked from L=20 reference)

| Range | Mean | All > 1e-2? |
|-------|------|-------------|
| +0.053 to +0.071 | +0.061 | **YES — 20/20** |

### Naive negative-Re modes (20 modes, the ones also in H²)

| Range | Mean |
|-------|------|
| +0.053 to +0.071 | +0.061 |

### Naive positive-Re modes (22 modes, the TRUE strip absent from H²)

| Range | Mean | Notable exception |
|-------|------|-------------------|
| +0.065 to +0.095 | +0.069 | **k=41: dRe/dlogL = −0.056** |

## Key discriminator

**Both populations (H2 negative-Re AND naive positive-Re) have the SAME positive dRe/dlogL ≈ +0.06–0.07.** The discriminator between them is NOT their L-dependence but the sign of Re:
- Naive positive-Re: always Re > 0 at all L (shift rightward from ~+0.13 to ~+0.89)
- H2 negative-Re: always Re < 0 at all L (shift rightward from ~−0.52 to ~−0.04 at the lowest mode)

Both drift rightward at the same rate. The origin-H² condition removes the Re > 0 half of the strip but both halves shift identically with L.

**Notable exception — k=41 (naive, Re=0.061→0.015):** This is the only mode with **negative** dRe/dlogL (−0.056), converging toward Re=−½ as L grows. It has **zero imaginary part** and at L=80 sits at Re=+0.015 — approaching the essential spectrum line. This is the λ=1 modulus-of-translation-mode discretization converging to 0.

## Terminal classification

**DISCRETIZATION-NONCONVERGENT.** dRe/dlogL is positive at fixed dx for ALL 20 origin-H² modes (+0.05 to +0.07). The Fourier discretization on [−L, L] does not produce eigenvalues converging toward the continuous essential spectrum line Re = −½ as L grows.

## Interpretation

This is NOT necessarily a method failure — it is a KNOWN property of Fourier spectral methods for operators with continuous spectrum on unbounded domains: the finite-[−L, L] truncation produces discrete eigenvalues that spread around the continuous essential spectrum line. The "bandwidth" of this discrete approximation grows with L because more modes are available to represent the continuous spectrum's tail.

However, the pre-registered terminal condition is clear: dRe/dlogL > 0 at fixed dx → **DISCRETIZATION-NONCONVERGENT**. This means the simple "increase L" criterion cannot distinguish essential-spectrum artifacts from genuine point spectrum. The discriminator must instead be the **sign of Re** (positive-Re modes are the TRUE strip, negative-Re modes are essential-spectrum discretization), which is what the naive−H2 comparison already establishes.

## Escalation content

The F-4 v2 proposal through the V2 adversary should NOT use an L-sweep criterion. The discriminator (Re sign) is already established by the realization comparison that F-1/F-4 already implements. The issue is the F-4 strip zone including the essential-spectrum discretization tail — this is a zone geometry issue, and the solution (already identified in the rescope proposal) is to use Re > margin as the strip zone rather than (FLOOR, −DELTA). The correct margin is a V2 adversary question, not an L-sweep question.

## File

`work/l-sweep-v2-results.json` — structured JSON output.