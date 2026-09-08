# ANCHORS.md — frozen ground-truth constants (research-verified 2026-09-08, v1.5)

Agent: this file is your ONLY source for these numbers. Do not re-derive from memory or search.

LEG STRUCTURE (v1.5 leg-split): LEG A = CLM SPECTRAL (gCLM a=0). LEG B = CCF TRANSPORT.
No anchor appears in both. Lambda anchors move to LEG B. Goldens stay in LEG A.

---

## LEG A: CLM SPECTRAL (gCLM a=0) — P0 GREEN

CLM = Constantin-Lax-Majda (1985, Comm. Pure Appl. Math. 38, 715, Eqs 2.1-2.3). CLM equation: ω_t = (Hω)·ω is the a=0 member of the gCLM family ω_t + a·u·ω_x = u_x·ω, u_x = Hω. Per Huang-Qin-Wang-Wei (2024, ARMA 248:22, arXiv 2305.05895) and Huang et al. (2024, arXiv 2401.14615 Eq 1.1). At a=0 the advection term a·u·ω_x drops, uniquely identifying CLM = gCLM a=0.

### gCLM family exact anchors (equation: ω_t + a·u·ω_x = u_x·ω, u_x = Hω; c_ω = −1 fixed)
- a = 0 (CLM): α = 1 EXACT; profile Ω(y) = −y/(y²+¼); point spectrum {0,1}; gap ½ after modulation; essential spectrum = line Re λ = −½.
- a = 1/2: α = 1/3 EXACT (⚠ not 1/2); exact solution ω=(t_c−t)⁻¹·16ṽ_c³ξ/(3(ξ²+ṽ_c²)²), ξ=(x−x₀)/(t_c−t)^{1/3}; stable.
- a_c = 0.6890665337007457: α = 0; c_l changes sign (focusing↔expanding).
- a = 1 (De Gregorio, line): α = −1 EXACT; compact support. Circle/smooth data: no finite-time SS blowup (stabilization) — the C-extract-b negative label.
- a < 0 (half-line degenerate): γ̄ = 1−a EXACT (c̄_l = 1−a, c̄_ω = −1). ⚠ Use ONLY the half-line explicit-profile values; the odd-symmetric two-scale tables (e.g. γ=0.9114 at a=−0.2) follow a DIFFERENT numerical γ(a) — never mix.
- LSS soft numeric anchors (weighted checks only; gCLM, not CCF): α(2/3) = 0.04517094; α(0.8) ≈ −0.260.
- Complex-singularity power: γ = 1/(1−a). Approx (inexact) form: α₀(a) = 2(1−a)²/(2−a) — exact only at a=0, 1/2; NEVER a fit constraint.
- Instability-order-vs-a: literature-silent. Any hierarchy you compute is a discovery claim.

### Corroboration: CLM = gCLM a=0 — derivable goldens
- Elgindi-Jeong exact self-similar profile (EJ20; also Huang et al. 2401.14615 §1): Ω(ξ) = -2ξ/(1+ξ²) (up to ξ→2ξ rescaling ≡ the ANCHORS form Ω = -ξ/(ξ²+¼)), c_ω = -1, c_l = 1. This profile is analytically derivable (not merely asserted) and the F1 engine reproduces c_l = 1.0000 at a=0. The anchor pair (Ω, c_l) at a=0 is hereby DERIVABLE, not ASSERTED.
- F1 self-similar profile ODE: c_l·Ω + α·x·Ω' + a·U·Ω' − HΩ·Ω = 0 (implemented in engine/f1.py). At a=0: c_l·Ω + α·x·Ω' − HΩ·Ω = 0.
- Linearized operator L_0[f] = c_l·f + α·x·f' − HΩ·f − Hf·Ω.

### Modulation clause (frozen; Chen–Hou / Huang lineage)
Two constraint rows in the Newton Jacobian: N1: Ω_x(0) = const · N2: U(1) + c_l = 0 (alt: Ω_x(1) = 0). These remove the {0,1} symmetry modes (= Xu's "standard modulation").

### Realization predicate (frozen; Xu 2607.19762)
- Impose odd basis + origin-H² vanishing. Expect clean {0,1} + line Re λ = −½.
- A naive maximal-L² discretization SHOWS A STRIP in Re λ > −½. The strip is the TRUE spectrum of the WRONG realization — not noise, not pollution. Its appearance = origin condition not enforced.
- L₀ strongly non-normal: eigenvalue counts do not bound growth; note pseudospectra in every spectrum figure.
- VERIFIED from arXiv 2607.19762 (2026-09-06, operator session): grid N∈{1024,2048}, Δa=0.04, y=c·tan(θ/2) compactification; |c_l(1024)-c_l(2048)| ≲ 5e-4 confirmed verbatim; §3.2 spectrum {0,1}, gap 1/2, realization dichotomy confirmed as stated.
  ANNOTATIONS (binding): (1) Xu numerics are first-order, ~3 sig figs at a>0 vs LSS reference; F1 acceptance targets are exact-form and LSS values ONLY — never Xu numeric values. (2) The 5e-4 figure is Xu's scheme self-consistency floor, not a continuum bound; never a default or target for F1's own two-grid check (§14-f floor stays self-computed at P2). (3) Xu Table 1 rows at a=0.1,0.3,0.5,0.65 are degree-6 interpolations, not solves; never check targets.

### Perturbation safety map
Sweep a inside (0, a_c) or a < 0 only. Never step across a_c blind. Branch/instability structure continuous within intervals; bifurcation at a_c.

### LSS referent (verified 2026-09-08 from primary source)
Lushnikov, P.M., Silantyev, D.A., Siegel, M. (2021). "Collapse versus blow-up and global existence in the generalized Constantin–Lax–Majda equation." J. Nonlinear Sci. 31(5), 82. DOI: 10.1007/s00332-021-09737-x. arXiv:2010.01201.
This is a gCLM paper. Soft anchors α(2/3), α(0.8) from this source.

---

## LEG B: CCF TRANSPORT — NOT STARTED. No engine. Xu 2607.19762 does NOT apply.

### CCF equation (Córdoba-Córdoba-Fontelos, not Constantin-Lax-Majda)
Source: Córdoba, Córdoba, Fontelos (2005). "Formation of singularities for a transport equation with nonlocal velocity." Ann. Math. 162, 1377–1389.
- Inviscid CCF: θ_t − H[θ]·θ_x = 0 (Eq 1.1)
- Viscous CCF: θ_t − H[θ]·θ_x = −νΛ^α θ (Eq 1.1)
- H is the Hilbert transform and Λ = (−∂_xx)^{1/2}.
- No stretching term (u_x·ω) appears. The nonlinearity is advective: scalar θ transported by its own Hilbert transform.
- CCF is structurally distinct from gCLM/CLM. CCF nonlinearity involves θ_x (derivative); gCLM nonlinearity involves ω (multiplicative). Different PDE classes.

### CCF self-similar ansatz (from Wang 2509.14185 / 2511.22819)
φ(x,t) = (1−t)^{kA(λ)} Φ_A(y), y = (1−t)^{-(1+λ)} x.
The self-similar parameter λ is the BLOW-UP SCALING RATE (not an eigenvalue of any linearized operator).
λ governs how quickly the singularity's spatial support shrinks.
The critical control is the ORIGIN SMOOTHNESS condition (Eggers-Fontelos selector mechanism), not the essential-spectrum line.

### CCF published λ targets (precision-corrected v1.5)

Each value is stated at the precision given in the primary source. Excess digits from prior versions are filed as UNSOURCED-PRECISION (separate registry below).

| # | λ | Source precision | Primary source |
|---|--------|-----------------|---------------|
| λ₀ stable | 1.1807776628998 | 13 digits — from 2509.14185 table (line 194) | 2509.14185 §Table 1 |
| λ₁ 1st unstable | 0.6057337012032 | 13 digits — from 2509.14185 table | 2509.14185 §Table 1 |
| λ₂ 2nd unstable | 0.4713248638620 | 13 digits — from 2509.14185 table (line 194); prose at L240 states 0.4703 — prose/table conflict UNRESOLVED (see UNRESOLVED-SOURCE-DISCREPANCY registry) | 2509.14185 |
| λ₂ refined | 0.47132422 | 8 digits — from 2511.22819 gradient-normalized refinement, with |λ−λₛ| ~ 10⁻⁷ sensitivity | 2511.22819 Eq 3 |
| λ₃ 3rd unstable | 0.2415604743989 | 13 digits — from 2509.14185 table | 2509.14185 §Table 1 |

NOTES:
- λ₃ = 0.2415604743989 appears in the 2509.14185 published table. It was absent from ANCHORS v1.4. There is no documented exclusion reason — filed as SELECTION-UNRECORDED.
- λ₂'s two source values (0.4713248638620 from 2509.14185 table, 0.47132422 from 2511.22819 refinement) agree at 7-digit precision; the 2511.22819 value is a gradient-normalized refinement of the same quantity. The prose/table conflict within 2509.14185 alone (0.4703 vs 0.4713248638620) has no established cause.
- No published λ-law for CCF exists — authors explicitly declined to fit one.
- λ₄ (4th unstable): NOT reported for CCF in either paper.

### Eggers-Fontelos referent (verified 2026-09-08 from primary source)
Eggers, J. & Fontelos, M. A. (2019). "Selection of singular solutions in non-local transport equations." Nonlinearity 33, 325. DOI: 10.1088/1361-6544/ab4e0b.
Referenced by Wang 2509.14185 as the origin of the λ₁ ≈ 0.6057 discovery and the selection mechanism for λ in CCF via origin smoothness condition. This paper deals with the CCF equation, not gCLM/CLM.

### Natural-ghost holdout (CCF §2.3.1, 2511.22819)
Second-stage sign-flip artifact: spurious origin residual, near-λ-invariant, sign flips between random inits. Governing second-stage equation published (Eqs. 9–10). Hyperparameters (net size, collocation, optimizer schedule) NOT stated — inherited from 2509.14185; disclose this gap in any REPRO/NONREPRO report.

### Ghost-mechanism sources
Gradient-drowning: 2511.22819 · Residual-trivial minima: 2604.23528 · Parameter-poisoning: 2606.25151 · FP32 stall: 2505.10949.

---

## UNSOURCED-PRECISION registry (v1.5)

Values in prior ANCHORS versions that exceeded the precision stated in any primary source, with no documented origin for the excess digits.

| Value | Previous use | Source-stated precision | Excess digits | Note |
|-------|-------------|------------------------|---------------|------|
| 0.4713242245 | ANCHORS v1.4 λ₂ 2nd unstable (10-digit) | 2509.14185 table: 0.4713248638620 (13-digit); 2511.22819: 0.47132422 (8-digit) | Digits 9–10 (\"45\"): neither source states 0.4713242245 at any precision | Appears to conflate 2509 table (0.4713248638620) with 2511 refined (0.47132422); no source states the combined value |

## UNRESOLVED-SOURCE-DISCREPANCY registry (v1.5)

| Discrepancy | Sources involved | Established cause? |
|------------|-----------------|-------------------|
| λ₂ prose (0.4703, line 240) vs λ₂ table (0.4713248638620, line 194) in 2509.14185 | 2509.14185 prose vs same paper's table | NO — 0.4713 does not round to 0.4703; the conflict is within a single paper. Table value 0.4713248638620 rounds to 0.4713 (4 s.f.) not 0.4703 (4 s.f.). The prose reads \"λ₂ = 0.4703 with residuals O(10⁻⁷)\" but the table states 0.4713248638620. No established cause — do not assert one. |

## SELECTION-UNRECORDED registry (v1.5)

| Item | Published source | Inclusion status in ANCHORS v1.4 | Reason |
|------|-----------------|----------------------------------|--------|
| λ₃ = 0.2415604743989 | 2509.14185 §Table 1 (CCF 3rd unstable) | Excluded (silent subset) | No documented exclusion reason. Published λ₃ is a primary source target; its exclusion without rationale is filed as SELECTION-UNRECORDED. |

## Per-class gap tags (v1.4 audit sweep, carried forward)
| Value | Tag | Reason |
|-------|-----|--------|
| CCF stable λ 1.1807776628998 | ASSERTED-UNDERIVABLE | published, no in-bundle derivation |
| CCF 1st λ 0.6057337012032 | ASSERTED-UNDERIVABLE | paper states ≈0.6057; 13 digits not justified |
| CCF 2nd λ 0.4713248638620 | ASSERTED-UNDERIVABLE | table states this precision; prose-text conflict unresolved |
| CCF 3rd λ 0.2415604743989 | ASSERTED-UNDERIVABLE | published, no in-bundle derivation |
| a_c = 0.6890665337007457 | ASSERTED-UNSOURCED | no source cited in bundle |
| α(2/3) = 0.04517094 | ASSERTED-UNDERIVABLE | soft anchor, LSS 2021 cited externally |
| α(0.8) ≈ −0.260 | ASSERTED-UNDERIVABLE | soft anchor, LSS 2021 cited externally |
| Fourier diff err < 0.5 (smoke) | ASSERTED-UNDERIVABLE | post-hoc, no pre-registered derivation |
| scipy conv flag (smoke) | asset — diagnosis completed | criterion mismatch, not a gap |