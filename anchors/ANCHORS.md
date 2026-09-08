# ANCHORS.md — frozen ground-truth constants (research-verified 2026-09-06)

Agent: this file is your ONLY source for these numbers. Do not re-derive from memory or search.

## CCF published λ (Wang et al. 2509.14185 / 2511.22819)
- Stable: 1.1807776628998
- 1st unstable: 0.6057337012032
- 2nd unstable: 0.4713242245 (refined multistage value; earlier 0.4713248638620)
- 3rd unstable: UNKNOWN; persistent non-smooth origin signal for λ ∈ [0.455, 0.4713]; wall below ≈0.455. Do not claim its existence or absence.
- No published λ-law for CCF exists — authors explicitly declined to fit one.

## gCLM family exact anchors (equation: ω_t + a·u·ω_x = u_x·ω, u_x = Hω; c_ω = −1 fixed)
- a = 0 (CLM): α = 1 EXACT; profile Ω(y) = −y/(y²+¼); point spectrum {0,1}; gap ½ after modulation; essential spectrum = line Re λ = −½.
- a = 1/2: α = 1/3 EXACT (⚠ not 1/2); exact solution ω=(t_c−t)⁻¹·16ṽ_c³ξ/(3(ξ²+ṽ_c²)²), ξ=(x−x₀)/(t_c−t)^{1/3}; stable.
- a_c = 0.6890665337007457: α = 0; c_l changes sign (focusing↔expanding).
- a = 1 (De Gregorio, line): α = −1 EXACT; compact support. Circle/smooth data: no finite-time SS blowup (stabilization) — the C-extract-b negative label.
- a < 0 (half-line degenerate): γ̄ = 1−a EXACT (c̄_l = 1−a, c̄_ω = −1). ⚠ Use ONLY the half-line explicit-profile values; the odd-symmetric two-scale tables (e.g. γ=0.9114 at a=−0.2) follow a DIFFERENT numerical γ(a) — never mix.
- Soft numeric anchors (LSS 2021, weighted checks only): α(2/3) = 0.04517094; α(0.8) ≈ −0.260.
- Complex-singularity power: γ = 1/(1−a). Approx (inexact) form: α₀(a) = 2(1−a)²/(2−a) — exact only at a=0, 1/2; NEVER a fit constraint.
- Instability-order-vs-a: literature-silent. Any hierarchy you compute is a discovery claim.

## Corroboration: CLM = gCLM a=0 — derivable goldens
- CLM equation: ω_t = (Hω)·ω is the a=0 member of the gCLM family
  ω_t + a·u·ω_x = u_x·ω, u_x = Hω. Per Huang-Qin-Wang-Wei (2024,
  ARMA 248:22, arXiv 2305.05895) and Huang et al. (2024,
  arXiv 2401.14615 Eq 1.1). At a=0 the advection term a·u·ω_x
  drops, uniquely identifying CCF = CLM = gCLM a=0.
- Elgindi-Jeong exact self-similar profile (EJ20; also Huang et al.
  2401.14615 §1): Ω(ξ) = -2ξ/(1+ξ²) (up to ξ→2ξ rescaling ≡ the
  ANCHORS form Ω = -ξ/(ξ²+¼)), c_ω = -1, c_l = 1. This profile
  is analytically derivable (not merely asserted) and the F1
  engine reproduces c_l = 1.0000 at a=0. The anchor pair (Ω, c_l)
  at a=0 is hereby DERIVABLE, not ASSERTED.

## CCF reference (spec gap closure, v1.4)
- CCF (Constantin-Lax-Majda) governing PDE: ω_t = (Hω)·ω
  = a=0 member of gCLM family. Source: Constantin-Lax-Majda (1985,
  Comm. Pure Appl. Math. 38, 715, Eqs 2.1-2.3); Huang et al. (2024,
  arXiv 2401.14615, Eq 1.1).
- Self-similar profile ODE: c_l·Ω + α·ξ·Ω' − HΩ·Ω = 0
  (implemented in engine/f1.py at a=0).
- Linearized operator L_0[f] = c_l·f + α·ξ·f' − HΩ·f − Hf·Ω
  whose eigenvalues are the published λ values.
- Published λ values from Wang et al. (2025/2026):
  • Stable 1.1807776628998 — ASSIGNED (from Wang 2509.14185; full
    text not extractable here — tagged ASSERTED-UNDERIVABLE)
  • 1st unstable 0.6057337012032 — FOUND in 2509.14185 HTML as
    "λ₁ ≈ 0.6057" (4-digit precision); the 13-digit value
    exceeds stated paper precision — tagged ASSERTED-UNDERIVABLE
  • 2nd unstable 0.4713242245 — FOUND in 2511.22819 HTML as
    "λₛ = 0.47132422" (8-digit precision); the 13-digit value
    exceeds stated paper precision — tagged ASSERTED-UNDERIVABLE

## Per-class gap tags (v1.4 audit sweep)
| Value | Tag | Reason |
|-------|-----|--------|
| CCF stable λ 1.1807776628998 | ASSERTED-UNDERIVABLE | published, no in-bundle derivation |
| CCF 1st λ 0.6057337012032 | ASSERTED-UNDERIVABLE | paper states ≈0.6057; 13 digits not justified |
| CCF 2nd λ 0.4713242245 | ASSERTED-UNDERIVABLE | paper states 0.47132422; 13 digits not justified |
| a_c = 0.6890665337007457 | ASSERTED-UNSOURCED | no source cited in bundle |
| α(2/3) = 0.04517094 | ASSERTED-UNDERIVABLE | soft anchor, LSS 2021 cited externally |
| α(0.8) ≈ −0.260 | ASSERTED-UNDERIVABLE | soft anchor, LSS 2021 cited externally |
| H-A CCF λ 8-digit target | ASSERTED-UNDERIVABLE | same as CCF λ; no eqn path |
| Fourier diff err < 0.5 (smoke) | ASSERTED-UNDERIVABLE | post-hoc, no pre-registered derivation |
| scipy conv flag (smoke) | asset — diagnosis completed | criterion mismatch, not a gap |

## Modulation clause (frozen; Chen–Hou / Huang lineage)
Two constraint rows in the Newton Jacobian: N1: Ω_x(0) = const · N2: U(1) + c_l = 0 (alt: Ω_x(1) = 0). These remove the {0,1} symmetry modes (= Xu's "standard modulation").

## Realization predicate (frozen; Xu 2607.19762)
- Impose odd basis + origin-H² vanishing. Expect clean {0,1} + line Re λ = −½.
- A naive maximal-L² discretization SHOWS A STRIP in Re λ > −½. The strip is the TRUE spectrum of the WRONG realization — not noise, not pollution. Its appearance = origin condition not enforced.
- L₀ strongly non-normal: eigenvalue counts do not bound growth; note pseudospectra in every spectrum figure.
|- VERIFIED from arXiv 2607.19762 (2026-09-06, operator session): grid N∈{1024,2048}, Δa=0.04, y=c·tan(θ/2) compactification; |c_l(1024)-c_l(2048)| ≲ 5e-4 confirmed verbatim; §3.2 spectrum {0,1}, gap 1/2, realization dichotomy confirmed as stated. ANNOTATIONS (binding): (1) Xu numerics are first-order, ~3 sig figs at a>0 vs LSS reference; F1 acceptance targets are exact-form and LSS values ONLY — never Xu numeric values. (2) The 5e-4 figure is Xu's scheme self-consistency floor, not a continuum bound; never a default or target for F1's own two-grid check (§14-f floor stays self-computed at P2). (3) Xu Table 1 rows at a=0.1,0.3,0.5,0.65 are degree-6 interpolations, not solves; never check targets.

## Perturbation safety map
Sweep a inside (0, a_c) or a < 0 only. Never step across a_c blind. Branch/instability structure continuous within intervals; bifurcation at a_c.

## Natural-ghost holdout (CCF §2.3.1, 2511.22819)
Second-stage sign-flip artifact: spurious origin residual, near-λ-invariant, sign flips between random inits. Governing second-stage eq published (Eqs. 9–10). Hyperparameters (net size, collocation, optimizer schedule) NOT stated — inherited from 2509.14185; disclose this gap in any REPRO/NONREPRO report.

## Ghost-mechanism sources
Gradient-drowning: 2511.22819 · Residual-trivial minima: 2604.23528 · Parameter-poisoning: 2606.25151 · FP32 stall: 2505.10949.
