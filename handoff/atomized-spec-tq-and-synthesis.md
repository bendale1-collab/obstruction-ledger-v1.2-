# Atomized Spec — Technical Questions and Synthesis Pillars

**Status:** DRAFT. Feeds the K1 pre-registration. Nothing here runs until sealed.

Notation: `c` claim, `P` premises, `h ∈ P`, `c∖h` claim with `h` removed, `π ∈ Π` perturbation, `f` judge, `N(h)` necessity oracle, `Λ(h) = E_π[1 − agree(f(c), f(π(c∖h)))]`, `A_i` audit class verdict, `U_T` reuse at horizon T.

Every item: **equation → oracle/dataset → threshold → falsifier → cost.**

---

## Part I — The nine technical questions

### TQ1 — Agreement function

Three candidates, pre-registered, chosen by test not taste:

```python
agree_label(a, b)  = 1[argmax(a) == argmax(b)]
agree_prob(a, b)   = 1[ |p(a) - p(b)| < τ ]          # τ sealed
agree_biNLI(a, b)  = 1[ entails(a,b) and entails(b,a) ]
```

**Oracle:** `N(h)` from Lean ablation (LeanDojo, mathlib4 @ pinned SHA).
**Dataset:** 200 informalized Mathlib theorems, 100 with `N=1` hypothesis, 100 with `N=0`.
**Threshold:** select `agree* = argmax AUC(Λ_agree, N)`. Require `AUC ≥ 0.7`.
**Falsifier:** if the three candidates disagree on ranking by more than 0.1 AUC, Λ is agreement-function-dependent — report all three, never one.
**Cost:** CPU + judge calls, <$5.

### TQ2 — Perturbation family size

```python
sd_Λ(k) = std over 20 seeds of Λ_k(h), where Λ_k uses k perturbations
k* = min{ k : sd_Λ(k) / mean(Λ_k) < 0.10 }
```

**Oracle:** none — internal stability.
**Dataset:** 20 claims, `k ∈ {5, 10, 20, 50, 100, 200}`.
**Threshold:** `k* ≤ 50`.
**Falsifier:** `k* > 200` → Λ is too noisy at affordable `|Π|`; instrument dead on cost.
**Cost:** <$3.

### TQ3 — Judge agreement

```python
κ_ij = cohen_kappa(f_i(x), f_j(x)) for all pairs in {MiniCheck, judge_B, judge_C}
```

**Oracle:** none — inter-rater.
**Dataset:** the same 200 × k perturbations.
**Threshold:** `min κ_ij ≥ 0.6`; majority vote only if met.
**Falsifier:** `min κ < 0.4` → vote is noise; Λ measures judge variance. Replace neural judge with symbolic (`Lean`) where available and restrict scope to where symbolic exists.
**Cost:** $0 beyond TQ1.

### TQ4 — Proof-necessity vs statement-necessity

```python
N_proof(h)  = 1[ lean_check(P \ {h} ⊢ c, proof_p) fails ]        # ablate in given proof
N_stmt(h)   = 1[ counterexample_search(P \ {h}, ¬c) finds one ]  # theorem false without h
```

**Oracle:** Lean 4 kernel + `slim_check` / `decide` / `nlinarith` counterexample search, time-boxed 60s.
**Dataset:** 500 Mathlib theorems (C1 in the plan).
**Report:** `P(N_proof=1)`, `P(N_stmt=1)`, `P(N_stmt=0 | N_proof=1)` — the contaminated stratum.
**Threshold:** contaminated stratum `< 0.15` of positives.
**Falsifier:** `> 0.30` → labels are polluted; run C2 on `N_stmt` only and report the smaller `n`.
**Cost:** CPU, hours.

### TQ5 — `A_pad` disambiguation

```python
Λ_pad(span)        = Λ with x = padding span
Λ_pad_ctrl(span)   = Λ with x = matched-length random non-padding span
verdict = "hidden premise" if Λ_pad > Λ_pad_ctrl + δ
        = "mislabel"       if Λ_pad ≈ Λ_pad_ctrl
        = "true padding"   if Λ_pad < ε
```

**Oracle:** hand-label 50 high-`Λ_pad` spans as hidden-premise vs mislabel (founder, blind to Λ).
**Dataset:** padding spans from the K1 fixture set + 50 synthetic insertions.
**Threshold:** verdict rule agrees with hand label `≥ 0.8`.
**Falsifier:** `< 0.6` → the class can't distinguish; drop `A_pad` from the product `A` and record it only.
**Cost:** two hours labeling.

### TQ6 — `A_weak` needs a pre-registered baseline

```python
A_weak = 0 if diff(test_original, test_final) relaxes any assertion
where test_original := sealed test at manifest time  (fresh runs)
                     := merged-PR base commit          (retrospective)
```

**Oracle:** the sealed test file hash.
**Dataset:** X3's 200 human PRs (retrospective) + 50 SWE-bench Verified tasks (fresh; tests sealed in manifest).
**Threshold:** class runs in both modes with `FPR ≤ 0.05`.
**Falsifier:** fresh-run mode has no sealed baseline → `A_weak` is retrospective-only. State that scope.
**Cost:** $0 beyond X1/X3.

### TQ7 — Code reuse metric

Pre-register **one** before any code task:

```python
U_dep(Δ)   = |{ functions calling any symbol introduced in Δ }|   at T
U_test(Δ)  = |{ tests exercising lines in Δ }|                    at T
U_surv(Δ)  = |lines of Δ surviving unreverted at T| / |lines of Δ|
```

**Oracle:** reviewer-rated PR value (1–5), 50 PRs, two raters, κ reported.
**Dataset:** `pallets/flask` merged PRs, 90-day window already elapsed.
**Threshold:** pick `argmax ρ(U_k, rating)`; require `ρ ≥ 0.3`.
**Falsifier:** all three `< 0.3` → reuse doesn't transfer to code; buyer-side Δ needs a different base.
**Cost:** 4 hours rating.

### TQ8 — Reuse-at-seal vs reuse-at-horizon

```python
U_seal(c)    = uses(c) computed on G @ manifest SHA
U_horizon(c) = uses(c) computed on G @ (manifest SHA + T days)
Δ_U          = U_horizon − U_seal
```

**Oracle:** mathlib4 git history — both snapshots exist.
**Dataset:** 200 lemmas merged 90+ days before manifest SHA.
**Threshold:** reward on `U_horizon`; require `Spearman(U_seal, U_horizon) ≥ 0.6` to justify `U_seal` as a proxy.
**Falsifier:** `< 0.4` → seal-time reuse predicts nothing; only the deferred number is valid.
**Cost:** CPU.

### TQ9 — Judge determinism

```python
replay_rate = P( f(x) identical across 10 re-runs )
```

**Oracle:** exact-match on judge output.
**Dataset:** 100 perturbations, judged 10× each, on (a) hosted API, (b) self-hosted with batch-invariant kernels (`thinking-machines-lab/batch_invariant_ops`).
**Threshold:** (b) `replay_rate = 1.0`; (a) reported, not required.
**Falsifier:** (b) `< 1.0` → the deterministic stack isn't; Λ is stochastic everywhere and every Λ carries a CI.
**Cost:** ~$2.

### TQ10 — Perturber identity (carried, still open)

```python
for π_gen in {template, llm_A, llm_B}:
    validity(π_gen) = P( π(c) is a valid perturbation | K=3 independent judges agree )
```

**Oracle:** K≥3 judge agreement on validity, none sharing weights with `π_gen`.
**Dataset:** 100 claims × 3 generators.
**Threshold:** `validity(template) ≥ 0.9`; LLM generators used only if `validity ≥ 0.85` and judged by disjoint models.
**Falsifier:** template `< 0.8` → even the safe path is unreliable; the perturbation family needs hand curation.
**Cost:** <$5.

---

## Part II — Synthesis pillars as falsifiers

### S1 — Failures are model-class, not operator-class

```python
rate_i(model) = P(A_i = 0 | model, no reward, 50 tasks)
```

**Oracle:** the four audit classes at their measured FPR.
**Dataset:** 50 SWE-bench Verified tasks × {qwen2.5-coder-7b, a frontier reasoning model}.
**Threshold:** both models show `Σ_i rate_i > 0.02`.
**Falsifier:** frontier model `≈ 0` on all classes → the catalogue is a cheap-operator artifact; scope it as such.
**Cost:** ~$30.

### S2 — Scarce resource is interpretive attention

```python
frontier_share = (frontier-tier actions in loop) / (all loop actions)
```

**Oracle:** the ledger's own action log, per run.
**Dataset:** the last two runs (Leg A, K1a), reconstructed from commits and chat.
**Threshold:** 2BR premise says `< 0.30`.
**Falsifier:** `> 0.30` on both → premise is violated for interpretive workloads; either revise the threshold or file the premise as failed for this class. Both are ledger entries; one must be chosen.
**Cost:** two hours counting.

### S3 — Catch-rate per line of code

```python
yield(check) = catches(check) / LOC(check)
```

**Oracle:** the catalogue of ~15 + K1a's 40 ledger entries, hand-assigned to the check that would have caught each.
**Dataset:** the checks: reference-correlation gate (1 line), substring matcher, criterion-diff, C1 (~300 lines), K1-1..6.
**Threshold:** rank by yield; build in that order.
**Falsifier:** C1 ranks in the top half → the cheap-first principle is wrong for this catalogue.
**Cost:** one hour.

### S4 — The gate beats the subtraction

Already grounded (safe-RL, composite indicators). One check:

```python
inversions = |{ (c1,c2) honest, Δ(c1)>Δ(c2), R(c1)<R(c2) }| / |pairs|
```

**Oracle:** `N=1` on both claims.
**Dataset:** 200 honest claim pairs.
**Threshold:** `inversions ≤ 0.10`.
**Falsifier:** `> 0.10` → the product form inverts honest rankings; add `m_floor > 0` per term.

### S5 — Citability precedes standing

```python
external_refs(t) = count of external documents citing a ledger entry by hash, at time t
```

**Oracle:** search + inbound-link log.
**Dataset:** the gist, the mirror, B1's published confusion matrices.
**Threshold:** `external_refs(90d) ≥ 1` from a benchmark author, lab, or standards body.
**Falsifier:** `= 0` at 90 days after B1 publication → the citability route is slower than the runway; prioritize the eval-data sale.
**Cost:** $0.

### S6 — The four-instrument pattern is itself the finding

```python
for instrument in {compressibility, subspace, alignment, Λ}:
    record (mechanism_plausible, measurement_confounded_by, date_killed, hash_of_prereg)
```

**Oracle:** the ledger.
**Threshold:** none — this is a record, not a test.
**Falsifier:** Λ survives C2 and C3 → the pattern breaks at n=4, and that's the result. If Λ dies, the pattern holds at n=4 and the write-up is the negative result.

---

## Dependency graph

```
TQ4 ──► TQ1 ──► TQ2 ──► C2 (AUC test)
TQ3 ──┘              │
TQ9 ─────────────────┘
TQ10 ─────────────── C3 (non-math transfer)
TQ5, TQ6 ──────────► B1 (public trajectory audit)
TQ7, TQ8 ──────────► reward definition, deferred
S1, S2, S3 ────────► Rev I of the postmortem
S4 ────────────────► reward form
S5 ────────────────► go/no-go on the citability route at 90d
```

**Run first:** TQ4, TQ3, TQ9 — all three can invalidate C2 before it runs and none costs more than $5. S2 and S3 are two hours of counting and both change the postmortem.

---

## Oracle and dataset registry

| Oracle | Source | License | Pinned |
|---|---|---|---|
| `N_proof`, `N_stmt` | Lean 4 kernel via LeanDojo, mathlib4 | Apache 2.0 | SHA in manifest |
| Entailment judge 1 | MiniCheck-FT5 770M | permissive | HF revision |
| Entailment judge 2, 3 | two open-weight models, disjoint lineage | Apache 2.0 | HF revisions |
| Reviewer rating | founder + one rater, κ reported | — | — |
| Test-suite pass/fail | pytest on pinned repo | BSD-3 (flask) | SHA |
| Public trajectories | TRACE (517), Terminal Wrench (3,632) | check each | SHA |
| Deterministic inference | batch_invariant_ops | check | commit |
| Padding hand-labels | founder, blind | — | sealed before Λ computed |

Anything not in this table is not an oracle and cannot be cited as one.
