# Obstruction Ledger

Sealed, replayable records of what an AI agent did, why its attempts failed, and which mechanical rule was in force when each failure appeared — with the rules published before the results exist.

**Status (2026-09-13):** research program with a public ledger. No customers, no revenue. One working check, three half-working, three broken, four instrument designs falsified. Standing block on compute until pre-registration for the next run has a gist revision timestamp.

---

## What this is, in one paragraph

Agents fail interpretively at a constant rate regardless of reward, humans catch those failures at the most expensive tier without deciding to, and the only durable asset is a dated record of which rule was in force when each failure appeared. So: build the cheapest check that fires on the most failures per line of code, seal it before the run, and let the sequence of sealed rules and the exploits that followed each one become the thing people cite.

## What this is not

- Not an observability product. Braintrust, Langfuse, LangSmith, Arize log after the fact and do it well.
- Not a new detector. The core operator (Λ, perturbation-based necessity) is ERASER comprehensiveness (DeYoung et al. 2020) under a different name.
- Not a reward function. `R_T = U_T · A` is a usefulness scorer times an audit; the scalar is table stakes, the sealed tuple is the product.
- Not proven to generalize. One operator, one domain, n small, frameworks derived from their own instances.

---

## Document map

Read in this order.

| # | File | What it is | Read when |
|---|---|---|---|
| 1 | `ol-session-summary-2026-09-10.md` | The research run: primitives, chronology, the 15-failure catalogue, SEAL-DETACHED, standing rules | First. Everything else assumes it. |
| 2 | `ol-postmortem-2026-09-10-to-12.md` | K1/K1a: what was attempted, what broke, per-check verdicts, own errors filed | Second. It's the honest state of the checks. |
| 3 | `obstruction-ledger-program-summary.md` | The thesis after three research passes: what died, what replaced it, the reformulated reward, incumbents, references | For the argument and the citations. |
| 4 | `grounding-prefalsification-Q1-Q17.md` | Prior-art verdicts on the reformulated reward `R_T = U_T · A` | Before touching the reward design. |
| 5 | `prose-to-table-feasibility.md` | Why C1 (prose↔table numeric check) is an open problem, not a feature | Before rebuilding C1. |
| 6 | `operating-plan-14-days.md` | Three tracks, seven gates, under $50 | To decide what runs next. |
| 7 | `prereg-K1-five-experiments-v0.1.md` | Draft pre-registration for X1–X5 | Before sealing anything. |
| 8 | `atomized-spec-tq-and-synthesis.md` | Ten technical questions and six synthesis pillars as equation → oracle → threshold → falsifier | When writing a card. |
| 9 | `operational-standards.md` | Harness, negative controls, retrodiction/OOS, execution-failure mitigations, twelve lessons from K1a | Before building infrastructure. |
| 10 | `agent-runbook.md` | Loop, task cards, phases P0→C2, roles, desktop steps, dataset/tool audit, OpenRouter picks, test discipline | To run it. |

Files 1–5 are the record. Files 6–10 are the plan. The plan cites the record by hash; the record never cites the plan.

---

## Current state, by thread

### The run (Thread A)
- Leg A closed as a typed obstruction: four methods impose parity, one imposes a metric, none imposes the domain. Converging instrument, error ∝ 1/L.
- v1.6 sealed, 19 files, anchored: gist `bendale1-collab/6b6d2d42651ffe5b63ab6a54a603ca05`, Rev H latest. Rev I (K1a RED) pending founder acceptance.
- Root cause of SEAL-DETACHED: two defects, not one — files never committed (`.gitignore:3` ignored `ledger/`) *and* verification against disk instead of `git show <commit>:<path>`.
- K1a is a **retrodiction, not a pre-registration**: Rev H postdated the code by three hours. State this in Rev I.

### The checks (Thread B, built)
| Check | State |
|---|---|
| K1-2 divergence-declaration | GREEN, all phases |
| K1-3/5/6 structure, dup-hash, extension | GREEN on artifacts; fixtures unusable |
| K1-1 quote-vs-anchor | RED — no revision scoping. CiteCheck/CiteTracer exist; don't rebuild. |
| K1-4 identifier | RED — label detection dead code |
| C1 prose-vs-table | RED — every-number-vs-every-number. Open research problem (file 5). MiniCheck covers the entailment case. |
| VERIFIER v0.1 | GREEN, $0; RB-05 caught a fabricated claim on its own author |

### The instruments (Thread B, falsified)
Four designs died the same death — plausible mechanism, confounded measurement:
1. **Cross-lingual compressibility** — codelength is near-invariant across languages (Coupé 2019, Bentz 2017); tokenizer fertility dominates (Petrov 2023); gzip+kNN was contaminated (Schutte 2023).
2. **Spectral-tail subspace** — one unreviewed preprint with a self-flagged subtraction artifact, null cross-lingual transport, missing code; tail eigenvectors are the least stable directions.
3. **Attention-alignment / translation heritage** — MI estimation barred by the ln(N) bound at claim length; single-head ablation confounded by the hydra effect; cross-lingual signal reduces to vocabulary overlap.
4. **Λ (perturbation necessity)** — alive, but it is ERASER comprehensiveness; the Lean negative class is ~1% natural and must be synthesized; the value is the Lean-verified ground truth, not the operator.

That pattern, sealed and dated, is publishable (Insights from Negative Results in NLP; ReScience C).

### The thesis (Thread B, standing)
- Exploits are model defaults (METR, RHB, Cursor) and reward pressure adds to them (0.6%→13.9% under RL). The audit is exogenous *and* corrective.
- Never expose the audit rule under optimization (Baker et al. 2025 — obfuscated hacking). Seal, hash, reveal after.
- Usefulness = realized reuse by independent provers (Kaliszyk–Urban Q₂, PageRank). Deferred like citations.
- Gate, don't subtract. Zero on failure, never negative. Selection only, never training, until the audit has drifted measurably.
- Bit-for-bit replay on hosted APIs is impossible (batch-size nondeterminism). Promise it only on a self-hosted fixed-batch stack.
- IISE ~46% Exit-class was scored on the *old* thesis. Rescore against the reformulation before using the number.

---

## What runs next

From `operating-plan-14-days.md`, in order:

1. **Five phone calls** — is anyone being asked for EU AI Act Art. 12 logs since 2 August? If 0 of 5, the demand leg is aspirational. One afternoon.
2. **Rescore IISE** against `R_T = U_T · A`. Two hours.
3. **Rev I edits** — split SEAL-DETACHED into two defects, mark K1a as retrodiction, add denominators to §4b, strike "traceable to an author" until per-profile git identity exists.
4. **P0** — 17 mechanical setup cards (`agent-runbook.md` §3, §17j). One to two days. Nothing loads until all pass.
5. **B1** — run the four audit classes on Terminal Wrench and TRACE, publish confusion matrices with definitions hashed beforehand. First numbers on data you didn't generate. A weekend.
6. **C1** — Mathlib necessity base rate. Decides natural vs synthetic negatives.
7. **CP / C2** — pre-checks, then Λ at AUC ≥ 0.7 or the instrument line closes for good.

Kill gates: A1 0/5 → demand leg downgraded. C1 < 5% → synthesize negatives. C2 AUC < 0.6 → instrument line closed, write the negative result.

---

## Roles

| Role | Who | Can | Cannot |
|---|---|---|---|
| operator | Hermes `mahamara` (`qwen/qwen3-coder-next`, pinned by config read) | run cards | author checks it runs; write `ledger/` |
| author-A / author-B | Hermes `exec` (GLM 5.2) / `default` (DeepSeek V4 Flash) | write check code in their own dir | see each other's work |
| harness, fixtures-A, holdout | Claude Code | infrastructure | gist, push |
| Mac-side ops | Cowork | files, local git, secret scan | push, gist, gateway restart, skill edits |
| adjudicator | founder | gist, push, restart, decisions | read agent prose (read the rollup and the queue only) |

Model names come from config reads into the manifest. The K1 RUNBOOK named a model that never ran; that doesn't recur.

---

## Standing rules

From the session summary and postmortem, in force for every run:

- Seal verification is against the **commit**, never the working tree.
- Publication is founder-only; the 403 is the control.
- Correct by **appending**, never editing or deleting. Botched attempts stay visible.
- GitHub revision timestamps are authoritative; `Published:` lines are founder assertions.
- Every count carries its denominator. Every number carries its producing command.
- A test parameter may not be chosen by looking at which cases it excludes.
- Demote, never delete: a citation may be invalid as justification while decisive as evidence.
- Hermes channel strips code blocks — request file paths, not content. "Verbatim" is banned; SHAs are not.
- Any conclusion naming a cause ("truncation," "known property," "no closed form") routes to a second family or arbiter before it ships.
- Watch the direction of proposed fixes. A threshold that moves, a zone that widens, a criterion that relaxes — that's the pattern, not a fix.
- The framework explaining the 15 failures was derived from those 15 failures. n=2 out-of-sample. Say so.

---

## Where things live

```
gist   https://gist.github.com/bendale1-collab/6b6d2d42651ffe5b63ab6a54a603ca05   (anchors; founder-only)
mirror github.com/bendale1-collab/obstruction-ledger-v1.2-                          (public, read outputs from raw URLs)
local  three Hermes profiles under launchd; skill trees read-only and under git
```

Anything not in the mirror at a commit that postdates the gist revision is not a result.

---

## How to read a result

A file under `results/<run>/` is citable only if the run's `verdict.md` says `PASS` or `KILL` (not `INCOMPLETE`, not `HALT`), the definition-of-done files in `operational-standards.md` §8 all exist, and the manifest hash it cites is in a gist revision that predates the first code commit. If any of those fail, the number is an observation, not a result.
