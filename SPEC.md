# Obstruction Ledger — Frozen Experiment Spec

Version 1.5-draft (leg-split) · September 2026
Status: UNFROZEN until §12 executed. Artifact-first: no external contact before seal.

LEG STRUCTURE — v1.5 leg-split (2026-09-08):
  LEG A — CLM SPECTRAL (gCLM a=0). Status: P0 GREEN. Xu 2607.19762 applies. Engine exists. Proceeds.
  LEG B — CCF TRANSPORT (Córdoba-Córdoba-Fontelos, NOT Constantin-Lax-Majda). Status: NOT STARTED. No engine. Xu results do NOT apply. Cap and scope UNQUOTED pending its own adjudication. The inherited $40/5d cap from v1.4 is VOID — it was scoped for the wrong numerical problem.

Changes from 1.1 (evidence-driven, pre-freeze; provenance in amendment log): ARCHITECTURE INVERTED — classical spectral/continuation engine is F1 (truth), PINN demoted to F2 specimen (E0 decision, grounded in optimizer-disclosure and public-recipe research). G1 restated as law DISCOVERY with three variants + selection rule (no CCF law exists to rediscover). Realization predicate added (Xu 2607.19762 trap). 2D module dropped; CCF §2.3.1 sign-flip artifact is the natural-ghost holdout. Claim grade "validated" renamed "bounded" (vocabulary collision). Extractor outputs ARCHIVED, k-vote (LLM APIs not bit-reproducible). Averaged-NSE case dropped for CLM/De Gregorio labels (cost). K0b novelty-scan section added. V1.5: leg-split (CCF ≠ CLM), precision correction, referent-resolution control added.

Purpose: build and validate a typed, replayable ledger of *why* singularity ansatzes fail; a classical truth engine generates ground truth and audits a specimen neural solver; retrodiction + anti-spurious battery gate every claim. Deliverable ships regardless of verdict. Not a proof project; not 3D NS.

Relation to program: standalone calibration instance (Q11 = no wallet). Launch slot per §11.

---

## 0. Thesis and falsifiable claims

**Thesis:** the obstruction is the product; the singularity is the byproduct. The novel methodology: a classical high-precision truth engine systematically catalogs neural-solver failure modes (K0b-scanned: no precedent), and the failure exhaust becomes a typed, replayable corpus.

**Claims:**
1. **C-extract-a (G0):** blinded extractor recovers *instability order* from Tier-E1 specimen exhaust on published (CCF, LEG B — contamination control) AND parameter-perturbed gCLM (unmemorizable, self-generated-truth) cases, beating a permutation null. Perturbed cases are claim-bearing; published reported alongside (contamination control).
2. **C-extract-b (G0):** extractor recovers *obstruction type* only on provenanced labels: synthetics; CLM a=0 blowup (exact positive); De Gregorio circle stabilization (named negative); counterfactual-validated self-generated failures (§6.3). LEG A only.
3. **C-law (G1):** a mechanical (LLM-free) fit DISCOVERS an α(a)-law for the gCLM 1D family, anchored on exact knots, with an out-of-sample prediction per the selected variant (§7). No published law exists for gCLM — this is a discovery claim. LEG A only. CCF has its own λ selection mechanism (Eggers-Fontelos selector) — not covered by this claim.
4. **C-battery:** four documented spurious-mechanism species detectable ≥90% on 100 plants; natural-ghost holdout = CCF §2.3.1 sign-flip artifact, scored once.

## 1. Scope

**Leg structure (v1.5 leg-split):**
- **LEG A — CLM SPECTRAL (gCLM a=0):** P0 GREEN. Proceeds. Xu 2607.19762 applies.
- **LEG B — CCF TRANSPORT:** NOT STARTED. No engine. Cap and scope UNQUOTED pending its own adjudication.

- **Equations (LEG A):** gCLM family across advection parameter a (CLM a=0, De Gregorio a=1 endpoints; sweeps inside (0, a_c) and a<0, never across a_c=0.6890665337007457 blind). Boussinesq/IPM: OUT of claim-bearing scope; published values appear only as external anchors in reported sections.
- **Equations (LEG B):** CCF = Córdoba-Córdoba-Fontelos (2005), Ann. Math. 162, 1377–1389. θ_t − H[θ]·θ_x = 0. NOT a member of the gCLM family. Entered as a separate transport leg; NOT covered by any existing engine or spectral theory.
- **F1 (primary truth engine, LEG A only):** classical Chebyshev/mapped-Fourier collocation; Hilbert transform via Fourier multiplier −i·sgn(k); Newton + two modulation rows; PALC continuation; Farrell–Birkisson–Funke deflation; branch eigensolver under §2.6; CPU FP64 with mpmath quad re-evaluation path. Route (BifurcationKit vs hand-roll) fixed by U1c spike; runner-up implementation retained as verification twin if promoted (§14-o). F1 does NOT apply to LEG B (CCF).
- **F2 (specimen):** vanilla PINN (tanh MLP, Adam+L-BFGS, FP64), config frozen pre-battery (§5.4). Exists to fail interestingly; no golden gate attaches to it.
- **Out:** 3D/2D claim-bearing work, CAP/interval arithmetic, new-singularity search (G2 = future spec), external parties pre-seal.

## 2. Ledger architecture

### 2.1 Certificate schema (frozen)
```
(ansatz_coords, equation, obstruction_type, dominant_term, scale, exponent,
 instability_order_est, tier_reached, solver_family, precision, seed,
 exhaust_tier, branch_id, cont_step, deflation_count, realization, grid_pair,
 solver_version_hash, run_hash, cert_status)
```
`cert_status ∈ {replicated, bounded, certified}`. **replicated** = multi-check machine-precision agreement (this project's ceiling). **bounded** = a-posteriori mathematical bound (not claimed here). **certified** = interval/formal proof (never claimed; CAP community's "validated numerics" ≈ our "certified" — collision resolved by rename). Vocabulary frozen.

### 2.2 Taxonomy v1 (expansion via §13 only)
{ scaling-supercriticality · spectral-instability(k) · boundary-incompatibility · energy-leakage(scale) · symmetry-breaking · profile-decay-violation · profile-nonexistence · GHOST(mechanism) · UNTYPED }
- GHOST sub-typed by §5.1 mechanisms **plus classical-realization ghost** (maximal-L² strip misread as modes — W2e).
- UNTYPED on a ground-truth case during P4/P5 = taxonomy-failure → HALT. Elsewhere: parks sealed in ledger/untyped/, unread, ships as sealed data.
- profile-nonexistence: both-solver non-convergence at a perturbed parameter per §6.2 rule — a certificate, not waste.

### 2.3 Two-process rule (operational self-honesty, not tamper evidence)
Runner writes results; ledger role (Hermes identity, separate keys) hashes and appends. Same operator ultimately controls both — the rule guards in-the-moment rationalization; the paper says exactly that. If OS-level user separation is unavailable (admin-only host), key separation + chain verification is the accepted fallback, disclosed.

### 2.4 Determinism & archival
F1 (CPU): bit-deterministic, hash-verified twice — replayable. F2 (GPU): seed-hash tested; if nondeterministic, ARCHIVED. LLM extractor: **ARCHIVED, never replayable** — model string pinned, full prompt+response sealed per call, k-sample majority vote per case (k per §14-q), CI computed over cases. Deprecation of pinned model mid-run → HALT + ESC.

### 2.5 Exhaust manifest (hashed at freeze)
- **Tier-E1 (claim-bearing, specimen only):** fields, residual fields, loss curves, λ-funnel, convergence traces. No spectrum, no classical diagnostics, no equation names in any LLM-touched step (automated grep wall).
- **Tier-E2 (ceiling ablation, disclosed):** E1 + linearized spectrum.
- Classical-engine outputs are the answer key; they never enter extractor prompts.

### 2.6 Realization predicate & modulation clause (order claims)
An instability-order entry requires ALL of:
1. Odd-sector basis with origin-H² vanishing imposed (origin regularity matching the collapse point);
2. Essential-spectrum line Re λ = −½ and any maximal-L² strip discarded by stated criterion — noting the strip is the true spectrum of the WRONG realization, not noise;
3. Modulation: two constraint rows N1: Ω_x(0)=const, N2: U(1)+c_l=0 (or Ω_x(1)=0), c_ω=−1 fixed; symmetry modes {0,1} thereby removed;
4. Count stable under resolution doubling AND realization variant (§14-r tolerance).
Negative control (H-B): a deliberately naive maximal-L² run must exhibit the strip; failure of the harness to produce the wrong answer when misconfigured voids the gate. Non-normality caveat ships with every spectrum figure (pseudospectra noted; eigenvalue counts ≠ growth bounds).

Source-verification caveat (carried from ANCHORS): the Xu (2607.19762) §7 exact grid integers, the |c_l(1024)−c_l(2048)| ≲ 5e-4 self-consistency figure, and the §3.2 closed-form eigenfunctions are flagged unverified-from-source in ANCHORS.md. Pre-P0 desk task (free): verify each from the paper. Verified → flag cleared in ANCHORS, logged. Unverifiable → the affected item demotes to soft anchor: it leaves the H-A hard-acceptance set (§14-u), is excluded from the §14-f floor computation, and the demotion ships in the paper's limitations. If P0 runs with any flag unresolved, the first H-A RED triggers the §14-v debug cycle with recipe-check as its mandatory first step.
|Verification completed 2026-09-06; flags cleared with binding annotations in ANCHORS. Demotion path did not fire; H-A hard acceptance stands.

### 2.7 Referent-resolution control (adopted v1.5, standing gate)

Every named equation in the bundle must carry a resolved referent: full author names, year, journal, equation number. Resolution must be verified against the primary source, not secondary literature or acronym convention. Referent resolution is its own gate, distinct from derivation-path verification or identical-if-different-target testing.

**Gap discovered (v1.5):** The CCF misidentification (Córdoba-Córdoba-Fontelos read as Constantin-Lax-Majda) persisted through v1.4 because the identical-if-different-target control tests for circular justification (can a rejection rationale be written without reference to the target?), not referent identity. That control passed and did not catch the error. The two controls test different failure classes and neither substitutes for the other.

**Failure class mapping:**
- Identical-if-different-target: tests for target-fitting in rejection rationales (circular justification)
- Referent-resolution: tests that every named equation maps to the correct primary source (referent identity)

**Implementation:** Every named equation in SPEC.md, RUNBOOK.md, ANCHORS.md, and HANDOFF-CHECKLIST.md must have a resolved referent in ANCHORS.md. Before any freeze, run make referent-audit: grep-ls every equation name, confirm each appears in ANCHORS.md LEG A/LEG B referent tables with primary-source verification status. Missing or unverified referent → RED on referent-audit, do not freeze.

**Control-design lesson (v1.5):** A citation may be invalid as justification while decisive as evidence. The lambda-provenance sentence deleted from rejection #1 (v1.4 amendment log Entry #6: "the published lambda values are from CCF literature...") was correctly removed as circular justification for the identical-if-different-target test, but it was the only in-bundle pointer to the correct CCF referent. Demote, never delete: when a citation fails one control, move it to a different role (evidence) rather than removing it entirely.

## 3. Verdict-validity rule
Every gate verdict = packet {verdict, pos-ctrl, neg-ctrl, contamination caveat, key numbers, hashes, spend}. Either control red → VOID. One postmortem+rerun per phase inside cap; second VOID same phase = TERMINAL-PARK. No external contact on VOID.

## 4. Phase plan (caps are poison-pill lines; runbook §3 governs execution)

LEG A proceeds on existing P0→P2→... sequence. LEG B is NOT STARTED and not in this table.

| Phase | Deliverable | Terminal states | Cap |
|---|---|---|---|
| P0 | F1 skeleton + analytic goldens (H-A) + realization pair (H-B) + resume drill + ledger — LEG A only | GREEN / RED | $20 / 4d |
| P1 | PALC+deflation → gCLM 1st (0.6057337012032) + 2nd (0.4713248638620); orders 0–2 under §2.6; quad re-eval — LEG A only. CCF λ targets are NOT eigenvalues and are not in this scope (move to LEG B). | GOLD-PASS / GOLD-MISS / VOID | $15 / 5d |
| P2 | gCLM α(a) sweep → claim-bearing (λ, order) pairs; §7 variant selection fires — LEG A only | N-PAIRS(n) / SWEEP-FAIL | $40 / 4d |
| P3 | Specimen build + ghost battery 4×25 + CCF §2.3.1 holdout attempt | BATTERY-VALID / INVALID; HOLDOUT-{REPRO, NONREPRO} | $250 / 10d |
| P4 | G0 (§6) | PASS / GRAY / KILL / VOID | $220 / 7d |
| P5 | G1 (§7, selected variant) | PASS / KILL / UNDERPOWERED / VOID | $15 / 3d |
| P6 | Artifact + K0b re-scan + seal | PUBLISHED-SEALED | $15 / 3d |

LEG B — CCF TRANSPORT: NOT STARTED. No engine. Cap and scope UNQUOTED pending its own adjudication. The inherited $40/5d cap from v1.4 P1 is VOID — it was scoped for a different numerical problem (gCLM eigenvalue computation, not CCF self-similar PDE). A new P1 scope for LEG B requires a separate spec and pre-registration. LEG B λ targets (CCF λ₀−λ₃) are recorded in ANCHORS.md LEG B section for reference but are NOT computable by any existing engine.

Global cap $1,000 incl. $300 founder-released reserve. Stable-only ground truth is NOT a valid G0 (auto-VOID).

## 5. Ghost battery

### 5.1 Manufactured species (25 plants each, blind-spiked)
| Mechanism | Manufacture | Anchor |
|---|---|---|
| Gradient-drowning origin artifact | High-gradient config, un-normalized loss | 2511.22819 §2.2 |
| Residual-trivial minima | Fixed collocation, no resampling | 2604.23528 |
| Parameter-poisoning silent failure | Perturbed PDE parameters | 2606.25151 |
| FP32 optimizer stall | FP32 + L-BFGS tolerance stall | 2505.10949 |

### 5.2 Ghost predicate (specimen promotion)
Persistence under: collocation resampling · λ-sweep (granularity from metered unit cost) · CPU quad-precision residual re-evaluation of the converged network (no FP128 retraining) · **F1 cross-solve disagreement check** (classical engine attempts the same profile; disagreement types the run GHOST). 1D-only scope makes the full predicate uniform — no reduced tier needed.

### 5.3 Natural-ghost holdout (replaces 2D module)
CCF §2.3.1 second-stage sign-flip artifact: spurious origin signal, sign flips across random inits; governing second-stage equation fully published (Eq. 9–10). Reproduction attempted ONCE at P3 with the frozen specimen config; hyperparameters underdetermined in source (inherited from 2509.14185) — disclosed. REPRO → holdout scored at P4. NONREPRO → disclosed limitation; C-battery scope = manufactured species + config-gap note; never re-tuned toward reproduction. Catch-rate guarantees extend to manufactured species; natural-ghost evidence is n≤1 — stated in abstract-level limitations.

### 5.4 Specimen config freeze
Architecture, optimizer, precision, collocation policy hashed BEFORE battery tuning (§14-n manifest). Specimen must exhibit all four mechanisms (U4b); any config amendment to achieve this is pre-freeze and logged. Specimen-grade band (must-reach / must-not-exceed residuals) fixed at P3-entry per §14-s; band hash precedes any battery construction.

## 6. G0 — extractor retrodiction

### 6.1 Ground truth (label provenance frozen)
| Case set | Label | Provenance | Role | Leg |
|---|---|---|---|---|
| CCF orders 0–2 | order + λ | Published (2509.14185/2511.22819) | Reported (contamination-suspect) | LEG B — not computable by F1 |
| Perturbed gCLM variants (≥5) | order + λ | **Recomputed by F1; unmemorizable** | **Claim-bearing (C-extract-a)** | LEG A |
| CLM a=0 | type = vortex-stretching blowup; exact profile | Constantin–Lax–Majda 1985; Xu 2026 | C-extract-b positive | LEG A |
| De Gregorio circle | type = advection stabilization (no SS blowup, smooth data) | Chen–Hou–Huang; OSW | C-extract-b negative | LEG A |
| Self-generated failures (≥3) | type | Counterfactual-validated only (§6.3); unvalidated excluded, never guessed | C-extract-b | LEG A |
| Synthetics (≥30) | type + order | True by construction | Floor | LEG A |

### 6.2 Contamination control & existence rule
Published vs perturbed scored side-by-side; published ≫ perturbed = recall signature → §9 cause-separation; caveat ships regardless. Perturbed parameters drawn from a pre-registered sequence inside safe intervals; both-solver non-convergence → profile-nonexistence certificate + next draw (N_max=10 to reach n≥5).

### 6.3 Counterfactual protocol (label factory)
A self-generated failure enters the scored set only if a pre-specified targeted perturbation nullifying the hypothesized obstruction moves the failure as predicted. <3 validated cases → C-extract-b UNDERPOWERED (reported, not gated).

### 6.4 Controls & thresholds
Synthetic floor ≥90% before real cases (fail = VOID). Blinding wall automated (grep). Permutation null 1,000×, p<.05. Leave-one-family-out on the order task. Exact-binomial CIs; n≈10 distinguishes coarse bands only — synthetics carry fine accuracy. **C-extract-a on perturbed set: PASS ≥4/5 · GRAY 3/5 (one extension: same cases, +1 seed batch, per-case majority, n unchanged) · KILL ≤2/5 with green controls.** C-extract-b PASS = CLM + De Gregorio both correct AND ≥2/3 counterfactual cases.

## 7. G1 — α(a)-law discovery (variant selected by P2 pair count; rule frozen)

**Selection rule (W1b):** claim-bearing pairs ≥6 → **(b) cross-family prediction**; 4–5 → **(a) internal holdout**; ≤3 → **(c) reported-not-gated**.
- Common machinery: mechanical wall (PySR/OLS only, audit-logged, no LLM in path); exact knots ENFORCED: α(0)=1, α(1/2)=1/3 (NOT 1/2), α(a_c)=0, and a<0 half-line exact γ̄=1−a (never the odd-symmetric two-scale tables); LSS soft anchors α(2/3)=0.04517094, α(0.8)≈−0.260 as weighted checks; power check on synthetic law+noise at actual n (fail = UNDERPOWERED); shuffle ablation (permuted α must yield no law, else penalty re-tightened, one re-run).
- **(b):** fit on a-grid points, predict a sealed held-out a-point generated AFTER the fit hash (W1d ordering — prediction can never become interpolation). Tolerance: 1.5× fit RMS residual, floor per two-grid self-consistency (§14-f, computed at P2).
- **(a):** same with leave-one-out inside the single family.
- PASS = recovery of knots within tolerance + holdout hit. Recovery-without-prediction = KILL for C-law. **Novelty note (frozen):** an instability-order-vs-a hierarchy for gCLM is literature-silent; any hierarchy found ships as a discovery claim with its own two-grid discipline.

## 8. Pills & escalation
Per runbook §8 failure map; spec-level additions: silent workaround = violation; frontier never adjudicates a gate; UNTYPED-on-ground-truth halts; lineage release mid-run = input (new anchors) never unfreeze (anti-panic clause).

## 9. Inference rules (frozen)
KILL cause-separation signatures: {LLM diagnostic gap, taxonomy misdesign, harness defect, n-too-small, recall-vs-extraction split}; packet must name one. Program updates: numerical-spectral diagnosis is plausibly a HARD LLM domain → G0 KILL updates the wider knowledge-graph program ≈0 (non-transfer statement ships); G0 PASS updates weakly positive and licenses a G2 frontier spec; transfer anywhere else requires its own Stage 0. G1 moves only C-law.

## 10. Artifact, mapping, optionality

**Artifact:** "An Obstruction Ledger for Neural Discovery of Fluid Singularities: A Classical Truth Engine, Failure Taxonomy, and Anti-Spurious Battery." Positioning: systematic classical-truth-engine failure-cataloging methodology (K0b: no precedent; distinguished explicitly from routine per-paper benchmarking). Every number cites a ledger hash; claim grades per §2.1; replay bundle ships.

| Outcome | Ships as | Then |
|---|---|---|
| G0+G1 PASS | Full paper incl. α(a)-law discovery | Contact package ≤1wk post-seal |
| G0 PASS, G1 KILL/UNDERPOWERED | Extraction+battery+engine; law = open problem w/ anchors table | Same |
| G0 KILL (controls green) | Methodology + negative result, signature named | Contact still occurs; §9 updates only |
| 2nd VOID any phase | Internal postmortem only | No contact |

**Optionality note (G0+G1 PASS only):** the architecture instantiates an ungameable co-evolutionary fitness function (classical referee, typed dense reward, parametric difficulty ladder). Licensed consequence: ONE one-page environment-product memo. Not licensed: any build, hub listing, or outreach. Falsifier before any action: one priced conversation clearing the math-transfer objection. (M5 gating language applies.)

**Seal sequence:** repo private → hash repo+paper+ledger → flip public → Software Heritage save-code-now → gist → Zenodo draft → founder publishes. arXiv post-contact (endorsement via the reader/anchor/endorser, one person, approached with the sealed artifact).

**K0b (novelty scan):** frozen query set (automated-PINN-diagnosis; SR-on-λ-law incl. lineage authors; LLM-solver-diagnosis benchmarks; classical-audits-neural methodology), dated log shipped; run at freeze and re-run ≤48h pre-seal. Hit-handling frozen: kill-class hit repositions the affected claim as replication in the abstract; positioning hits get their paragraph pre-P6.

## 11. Launch slot (founder-only blanks)
|- Dependency vs C0/C1 + AIDev states: NONE — independent. C0/C1 complete; AIDev G0 closed (L-C). 2BR publication blocker is administrative, not coupled.
|- Weekly attention budget vs Gate-0 clock (hours, written): ≤2 h/wk. Gate-0 clock outranks all touchpoints except pre-booked T1 hour and one-word approvals. T1 calendar hour booked at launch.
|- No-launch-by date + consequence (re-justify or park): 2026-09-13. Consequence: PARK, freeze hash preserved; relaunch = re-verification only, no re-freeze.
- Slot + architecture-flip provenance logged in omnibus amendment log.

## 12. Freeze procedure
1. Approve §14. 2. Fill §11. 3. P–1 desk fills: exhaust-manifest hash (§14-n), K0b freeze-scan log hash (§14-t). 4. Freeze hash: per-file SHA-256 of SPEC.md, RUNBOOK.md, HANDOFF-CHECKLIST.md, anchors/ANCHORS.md written to MANIFEST.sha256 (sorted paths, LF endings); freeze hash = SHA-256 of MANIFEST.sha256. Publish the hash string (gist; SWH save-code-now unavailable on a private repo — full seal at P6). The env manifest is NOT in the freeze: it is created at scaffold (CHECKLIST §4.5), hashed into STATE, and appended to the amendment log as a launch attestation entry. 5. One-way P0→P6; batteries precede gates; seal precedes contact.

## 13. Amendment log
Dated entries; taxonomy/box/threshold/manifest changes route here; ships with artifact. Long log = weaker experiment; the log is the incentive.

## 14. Open numbers — approve before freeze

Registry scope: this section enumerates gate-bearing thresholds — numbers that decide a terminal state, verdict, or claim. Operational parameters (message caps, reminder rates, warning thresholds, drill targets, cadences) defined in RUNBOOK.md or HANDOFF-CHECKLIST.md are pre-registered by inclusion of those files in the freeze hash (§12) and carry equal force. A number defined in neither the bundle nor this table does not exist; the agent escalates (CHECKLIST §1 missing-threshold rule).

Budget closure note: RUNBOOK §3's $100 misc/telegram/API allocation is the arithmetic remainder of §14-m: $1,000 global − $300 reserve − $600 phase caps.

| # | Number | Proposed |
|---|---|---|
| a | Ghost catch floor | 90% of 100 plants (25×4) |
| b | Synthetic floor | 90% |
| c | C-extract-a PASS/GRAY/KILL (of 5 perturbed) | ≥4 / 3 / ≤2; extension = +1 seed batch, majority per case |
| d | Permutation null | p<.05, 1,000× |
| e | C-extract-b pass | CLM + De Gregorio + ≥2/3 counterfactual |
| f | G1 tolerance | 1.5× fit RMS residual; floor = two-grid self-consistency (filled at P2, pre-fit-hash) |
| g | Perturbed pair target / N_max draws | ≥5 / 10 |
| h | Gray extension count | 1 |
| i | Holdout NONREPRO rule | disclosed limitation, never re-tuned; n≤1 stated |
| j | VOID rerun | 1/phase; 2nd = TERMINAL-PARK |
| k | G1 variant thresholds | ≥6→(b), 4–5→(a), ≤3→(c) |
| l | Stall pill (in-run: no subtask commit/STATE update for the period) | 48h. Distinct from the 48h ESC decision clock (RUNBOOK §6) and from the operator-side watchdog liveness alert (≥6h, Hermes config, outside this freeze; alerts only, never acts) |
| m | Global / reserve | $1,000 / $300 founder-released |
| n | Exhaust + specimen-config manifest hash | 0aa518bfa0d7e052b7300f7ddaaafefb3fe218cd1da47b80f2406b74b4023fee (anchors/exhaust-config-manifest.md); exact specimen hyperparameters hashed at P3-entry with band |
| o | F1 self-verification | anchors + two-grid + realization-variant + quad re-eval; spike runner-up promoted to verification twin IF it reached goldens (else disclosed single-implementation) |
| p | Realization predicate | §2.6 as written |
| q | Extractor votes k | 3 (revisit only if D1e variance probe shows k moot) |
| r | Order-stability tolerance | zero change in count under doubling + realization variant |
| s | Specimen-grade band | filled at P3-entry: frozen-config specimen first-runs on Tier-E1 cases → band (must-reach / must-not-exceed residuals) written + hashed BEFORE any battery construction; hash to ledger + amendment log. If §5.4 config amendment fires (mechanism-exhibition failure, logged), band re-derived ONCE, re-hashed, logged. Inside P3 caps. |
| t | K0b freeze-scan log hash | 72fa73c9cdac05f2683c233c534a4b55b54168d823fd0ba4d23d7c9016539aed (anchors/k0b-freeze-scan-2026-09-06.md) |
| u | H-A acceptance (LEG A): CLM a=0 profile + c_l exact (= 1.0000), a=1/2 α=1/3, γ̄=1−a; gCLM exact-form anchors matched exactly or to stated soft-anchor tolerance. CCF λ targets are NOT in H-A — they belong to LEG B and are not computable by F1. | 8 significant digits; exact-form anchors (α(1/2)=1/3, γ̄=1−a, CLM a=0 profile/c_l) matched exactly or to stated soft-anchor tolerance |
| v | RED-debug allowance (component RED at H-A/H-B class harness, distinct from §3 VOID-rerun) | 1 debug cycle per phase inside cap; second miss = ESC |
| w | ANCHORS.md file hash | c45d5dfdb741267964bed72c62b077e47d0d6cbb247c2cb82bba929d82af3e50 (v1.5 leg-split — companion to §14-n, which remains the exhaust+specimen-config manifest) |

---
*Approved as adjudicated, founder session 2026-09-06 (rows a-w; c,k as proposed; s as amended by §14-s ruling).*
