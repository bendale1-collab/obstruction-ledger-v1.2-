# Agent Runbook — Long-Horizon Execution with Mechanical Checks

**Purpose:** let an operator agent run the 14-day plan for days at a time with the founder touching only the adjudication queue. Every task is mechanical or it is not assigned to the agent. Every acceptance test is a command with an exit code. Interpretation is a separate queue, read by a human.

**Roles (hard-bound, one profile each, git author set):**
- `operator` — executes task cards. Never authors checks it will run. Never edits the ledger.
- `author-A`, `author-B` — write check code / fixtures in a split; never see each other's work.
- `adjudicator` — founder. Reads `queue/adjudicate/`. Publishes to the gist. Only role with gist scope.

---

## 1. Loop

```
while state.phase != DONE:
    card   = next_ready_card(state)            # dependencies satisfied, budget remaining
    if card is None: halt("NO_READY_CARD")
    nonce  = new_nonce()
    result = run(card, nonce)                  # sandboxed, idempotent
    ok     = accept(card, result)              # exit code of card.accept_cmd
    commit(card, result, nonce)                # message: "[<card.id>] <nonce> <PASS|FAIL|HALT>"
    state  = advance(state, card, ok)
    if card.gate and not ok: enqueue_adjudication(card, result)
    rollup()                                   # regenerates status/ROLLUP.md from state, never typed
```

Rules the loop enforces, not the agent:
- A card whose `accept_cmd` is missing does not run.
- A card that has already produced its output file with matching SHA returns `ALREADY_EXECUTED` and is skipped. That is a success.
- A card that fails `max_attempts` times becomes `HALT` and enters the queue. The agent does not retry, patch, or reinterpret.
- Wall-clock, token, and dollar counters live in `state/budget.json`. Any counter at cap → `HALT_BUDGET`, loop stops.
- Every commit carries the nonce. CI rejects commits without one or from an author not in `manifest.authors`.

---

## 2. Task card schema

```yaml
id:            B1-03
phase:         B1
depends_on:    [B1-02, P0-07]
role:          operator
inputs:                                   # paths + SHAs, nothing else
  - path: data/trace/trajectories.jsonl
    sha:  <64hex>
cmd:           python -m ol.audit run --classes A_weak,A_selfev,A_nonex,A_pad --in data/trace/trajectories.jsonl --out results/B1/trace_audit.json
output:        results/B1/trace_audit.json
accept_cmd:    python -m ol.accept B1-03   # exits 0 iff output exists, schema-valid, denominators present, invocations.log >= case count
gate:          false                      # true = kill-gate; failure routes to adjudicator
max_attempts:  2
budget:        {usd: 5, minutes: 60}
halt_if:                                  # mechanical halt conditions, checked by accept_cmd
  - "canary_fire_rate < 0.8"
  - "invocations < cases"
```

A card with any field missing is rejected at load. There is no free-text "notes" field.

---

## 3. Phase P0 — Setup (day 0–1)

All mechanical. All must pass before any research phase loads.

| Card | Command | Accept |
|---|---|---|
| P0-01 | set per-profile `git config user.{name,email}` for all three profiles; write `manifest.authors` | `git log -3 --format=%ae` per profile matches registry |
| P0-02 | restart gateways; confirm `skills.write_approval: true` live | config dump shows `true` on all three; `chmod -R a-w` on all skill trees; `git status` clean in each |
| P0-03 | install `.pre-commit-config.yaml` (ruff py311, mypy --strict, check-json, check-yaml, detect-secrets, check-ignore audit, radon cc≤10) | `pre-commit run --all-files` exit 0 |
| P0-04 | `uv lock` with pinned 3.11.9; Dockerfile digest-pinned | `docker run <digest> python --version` == 3.11.9 |
| P0-05 | scaffold `inspect_ai` project; register the four audit classes as solvers | `inspect eval --list` shows 4 tasks |
| P0-06 | harness invariant tests (`test_every_check_is_invoked`, `test_fixture_count_nonzero`, `test_check_can_read_its_fixtures`, `test_in_scope`) | `pytest tests/harness -q` exit 0, `--co -q` count ≥ 4 |
| P0-07 | nonce echo: send a nonce to each profile, require it back | `attribution.json` has 3 rows, no gaps |
| P0-08 | publish script reads gist timestamp from GitHub API and writes `ledger/anchor.md` | ledger line matches API response byte-for-byte |
| P0-09 | CI assertion: first code commit time > gist revision time, else auto-label RETRODICTION | CI passes on a test branch with a deliberately early commit → label appears |
| P0-10 | pin datasets: TRACE, Terminal Wrench, flask @ SHA, mathlib4 @ SHA, SWE-bench Verified subset IDs | `manifest.json` has SHA for each; `sha256sum -c` passes |

**Gate P0:** all ten PASS. The `state.phase` cannot advance to B1 otherwise. No adjudication needed — this phase has no interpretive content.

---

## 4. Phase B1 — Public trajectory audit (day 1–3)

| Card | What | Accept | Halt |
|---|---|---|---|
| B1-01 | freeze audit class definitions; hash `ol/audit/classes.py` | hash written to manifest; `git show HEAD:ol/audit/classes.py \| sha256sum` matches | — |
| B1-02 | **adjudicator publishes hash to gist** (queue item, human) | P0-08 script confirms revision timestamp | blocks B1-03 until done |
| B1-03 | run four classes on TRACE | schema-valid; `invocations ≥ 517`; canary rate ≥ 0.8 | canary < 0.8 → HALT |
| B1-04 | run four classes on Terminal Wrench | same, `invocations ≥ 3632` | same |
| B1-05 | run four classes on 200 flask PRs (honest set) | same; per-class FPR with Wilson CI | any FPR > 0.05 → **gate**: class retired, adjudicator notified |
| B1-06 | run on 10 benign-test-edit canaries | `A_weak` fires on 0 of 10 | fires → HALT, `A_weak` definition wrong |
| B1-07 | generate `results/B1/confusion.json` + `results/B1/note.md` from script | every number has its producing command inline; no number without one | — |
| B1-08 | **adjudicator** reads note, decides publish | queue | — |

Interpretive content in this phase: zero. The agent never decides whether an FPR is acceptable; the threshold is in the card.

---

## 5. Phase C1 — Necessity base rate (day 2–4, parallel with B1)

| Card | What | Accept | Halt |
|---|---|---|---|
| C1-01 | sample 500 Mathlib theorems by hash of name, seed in manifest | `results/C1/sample.json`, 500 rows, seed recorded | — |
| C1-02 | run `#lint only unusedArguments` over the sample via LeanDojo | per-theorem flag list; `invocations ≥ 500` | LeanDojo error rate > 5% → HALT |
| C1-03 | explicit ablation: for each hypothesis, remove and re-check the given proof → `N_proof` | `N_proof` per (theorem, h); Lean exit codes logged | timeout rate > 10% → HALT |
| C1-04 | counterexample search on `N_proof=0` rows (`slim_check`, 60s) → `N_stmt` | per-row outcome ∈ {found, timeout, none} | — |
| C1-05 | compute rates: `P(N_proof=0)`, `P(N_stmt=0 \| N_proof=0)`, proof-dependence on multi-proof theorems | `results/C1/rates.json` with denominators and CIs | — |
| C1-06 | **gate:** `P(N_proof=0) < 0.05` → natural negative class absent | script emits `KILL_NATURAL_NEG` or `PASS` | KILL → route to C1-07 |
| C1-07 | (conditional) build 200 synthetic redundant-hypothesis mutants; verify each with Lean | 200 rows, all `lean_check == 0`, mutation method recorded per row | verify rate < 0.95 → HALT |

**Gate C1:** either a natural negative class ≥ 5% or a verified synthetic set of 200. Otherwise C2 does not load.

---

## 6. Phase C-pre — Pre-checks that can invalidate C2 (day 4–5)

| Card | What | Accept | Halt |
|---|---|---|---|
| CP-01 (TQ3) | κ between MiniCheck and two disjoint-lineage judges on 200 × 20 perturbations | `results/CP/kappa.json` | `min κ < 0.4` → drop ensemble, single judge; `< 0.6` → adjudicator |
| CP-02 (TQ9) | judge determinism: 100 inputs × 10 reruns, fixed batch, local | `replay_rate == 1.0` | `< 1.0` → CIs mandatory on every Λ |
| CP-03 (TQ2) | Λ stability vs k ∈ {5,10,20,50} on 20 claims, 20 seeds | `k*` written | `k* > 50` → HALT |
| CP-04 (TQ10) | generate 100 template perturbations + 20 deliberately invalid; **adjudicator labels blind** | queue item; `validity ≥ 0.85` | `< 0.85` → all π human-verified; automation off |
| CP-05 (TQ1) | pre-register agreement function = bidirectional strict entailment; other two computed for report only | manifest entry | — |

---

## 7. Phase C2 — Λ separation (day 5–7)

| Card | What | Accept | Halt |
|---|---|---|---|
| C2-01 | informalize 200 Lean theorems (100 `N=1`, 100 `N=0` from C1) → NL claims | 200 rows; informalizer model ≠ any judge; hashes recorded | — |
| C2-02 | perturbation family per hypothesis, `k = k*` from CP-03, templates from CP-04 | `results/C2/perturbations.jsonl`, `≥ 200 × k*` rows | — |
| C2-03 | run judges; compute Λ per hypothesis | `invocations == rows`; Λ ∈ [0,1] | — |
| C2-04 | AUC(Λ, N) with length + overlap controls; bootstrap CI | `results/C2/auc.json` | — |
| C2-05 | **gate:** AUC ≥ 0.7 PASS; < 0.6 KILL; between → adjudicator | script emits verdict | KILL → instrument line closed; phase → S6 write-up |
| C2-06 | holdout: 50 founder-authored claims, structurally validated pre-seal, revealed now | `holdout_structural.json` all runnable; AUC on holdout | gap vs C2-04 > 0.3 → overfit flag |

---

## 8. Adjudication queue

`queue/adjudicate/<card>-<nonce>.md`, generated by script, one per gate event. Contents: the card, the result file path + SHA, the threshold, the measured value, the three admissible decisions (`ACCEPT` / `OVERRULE` / `RERUN`), and nothing else. No narrative from the agent.

The adjudicator's decision is a file: `queue/decided/<card>-<nonce>.md` with one word and a signature line. The loop reads it. Anything in the queue older than 24h with no decision → `HALT_AWAITING_ADJUDICATION`; the agent moves to the next independent card if one exists, else stops.

Interpretive questions the agent may not answer, routed to the queue automatically by keyword in the result: "cause," "because," "known," "no closed form," "cannot be," "likely," "should." Any of these in an agent-written field → that field is blanked and the card is flagged.

---

## 9. Rollup

`status/ROLLUP.md` regenerated after every commit by `python -m ol.rollup`. It contains: phase, cards by state (READY / RUNNING / PASS / FAIL / HALT / SKIPPED), budget consumed vs cap, queue depth, last three commits with nonces. **The agent does not write status prose.** If the founder wants a sentence, the sentence comes from a template filled by numbers.

---

## 10. Halt taxonomy

| Code | Meaning | Who resolves |
|---|---|---|
| `HALT_ACCEPT` | accept_cmd failed after max_attempts | adjudicator |
| `HALT_BUDGET` | a counter hit cap | founder raises cap or ends run |
| `HALT_CANARY` | check missed sealed canaries | author of that check |
| `HALT_ATTRIBUTION` | nonce missing or author unregistered | founder |
| `HALT_SKILLS_DIFF` | a skill tree changed during the run | founder; diff in ledger |
| `HALT_AWAITING_ADJUDICATION` | queue item > 24h | adjudicator |
| `NO_READY_CARD` | dependency graph blocked | founder |

`HALT` is a valid end state for a card and for a run. It is filed, not fixed in place.

---

## 11. What the founder does

Per day, in order:
1. Read `status/ROLLUP.md` (numbers only, one screen).
2. Clear `queue/adjudicate/` — each item is one decision, pre-formatted.
3. Publish any hashes queued for the gist (B1-02 and the C2 pre-reg) with the publish script.
4. Label CP-04 when it arrives (one afternoon, once).
5. Nothing else. No reading agent prose, no reading tables from chat, no re-deriving numbers.

If step 1 takes more than five minutes, the rollup is wrong and that is a bug in `ol.rollup`, not a reason to read more.

---

## 12. Frontier share

`state/frontier_share.json` counts founder decisions and any frontier-model calls against total card executions. Reported in the rollup. If it exceeds 0.30 over any 48-hour window, the runbook has failed its own premise; that is filed as a ledger entry (S2) and the phase halts for redesign — not for the founder to work harder.

---

## 13. Agent assignment — decided

Postmortem constraints that bind this: three Hermes profiles under launchd (`mahamara`, `exec`, `default`), models varied across sessions, one git author for all three, the sealed RUNBOOK named a model that never ran, Cowork has Mac shell but no GitHub credentials and no TTY, gateway restart needs a terminal.

| Role | Agent | Why | Hard limits |
|---|---|---|---|
| `operator` | Hermes **`mahamara`** | Only profile with skills tree already `chmod -R a-w`; highest observed correct-refusal rate under mechanical prompts | Never authors a check it runs. Never writes ledger/. Model pinned by **reading the profile config into the manifest** (P0-11), not by asserting a name. |
| `author-A` | Hermes **`exec`** | Was one of the two code-author sessions in K1a | Writes check code only. Never sees author-B's fixtures or code. |
| `author-B` | Hermes **`default`** | The other code-author session | Same, mirrored. |
| harness + fixtures-A + holdout | **Claude Code** (desktop) | Claude rewrote the K1a harness after three Hermes versions that never invoked checks; Claude authored the holdout and fixtures for C1/K1-1/K1-2 | Harness is infrastructure — tested by the P0-06 invariants, not trusted by role. Fixtures-A go to author-A's checks, never author-B's. Claude Code has no gist scope. |
| Mac-side file ops, secret scan, local git | **Cowork** | Already did this in K1a; flagged its own scope five times unprompted | No push. No gist. No gateway restart. No skill-tree edits. |
| `adjudicator`, gist, push, restart | **Founder** | Only holder of gist scope and a terminal | Reads `status/ROLLUP.md` and `queue/adjudicate/` only. |

**Model pinning rule (new card P0-11):** for each profile, `cat ~/.hermes/profiles/<p>/config.yaml | grep model` is written verbatim into `manifest.models` by Cowork. The RUNBOOK cites the manifest. No model name is typed by anyone.

**Author disjointness:** `manifest.authors` maps profile → git identity → model. CI rejects a commit from author-A touching `fixtures/B/` or `checks/B/`, and vice versa. Claude Code's commits are rejected outside `harness/`, `fixtures/A/`, `holdout/`.

---

## 14. Desktop / Cowork steps — reviewed

Every P0 card was checked against who can actually execute it on the Mac.

| Card | Needs | Executor | Notes |
|---|---|---|---|
| P0-01 git authors | file edit in 3 profile dirs + launchd env | **Cowork** writes; **Founder** restarts | Config change is a file; it takes effect on restart. |
| P0-02 gateway restart, `write_approval`, `chmod` | terminal, launchd | **Founder** (restart); **Cowork** (`chmod`, `git init` in skill trees, config check) | Restart cannot be delegated. Do it once, verify with Cowork reading the live config dump. |
| P0-03 pre-commit | file write + `pre-commit install` | **Cowork** | `pre-commit run --all-files` output is the accept artifact. |
| P0-04 uv lock, Dockerfile | Docker Desktop on Mac | **Cowork** builds; `docker run <digest> python --version` is the accept | If Docker Desktop is not installed, this is a founder step. |
| P0-05 inspect_ai scaffold | pip, file writes | **Claude Code** | Harness territory. |
| P0-06 harness invariants | pytest | **Claude Code** writes; **Cowork** runs and commits the output | Separation: author ≠ runner. |
| P0-07 nonce echo | messages to 3 profiles | **Founder** sends (Telegram); **Cowork** collects and writes `attribution.json` | Cannot be automated until the profiles have a non-chat inbox. |
| P0-08 publish script | GitHub API read (public, no auth) | **Cowork** | Reading the gist needs no credential. Writing does — founder only. |
| P0-09 CI timestamp assertion | GitHub Actions | **Claude Code** writes the workflow; **Founder** pushes | Cowork cannot push. |
| P0-10 dataset pinning | network, disk | **Cowork** downloads, hashes; `sha256sum -c` is the accept | See §15 for what to pin. |
| P0-11 model pin | read profile configs | **Cowork** | New. |
| B1-02, C2 pre-reg publish | gist write | **Founder** | Mobile desktop-site mode worked last time; the script generates the block, founder pastes. |
| CP-04 blind labeling | human | **Founder** | One afternoon. Labels sealed before Λ is computed. |
| Every `git push` | GitHub credential | **Founder** | Cowork commits locally; founder pushes in a batch. This is the relay's replacement: one push, not sixty prompts. |

**Sequencing on the Mac:** Cowork does P0-01/02(file parts)/03/04/08/10/11 in one session, commits locally. Founder restarts gateways, runs P0-07, pushes. Claude Code does P0-05/06/09 on the pushed tree. Founder pushes again. P0 gate evaluates on that commit.

---

## 15. Dataset and tool audit

Checked against primary sources on 2026-09-13. **Verified** = confirmed this session. **Unverified** = not confirmed; treat as a P0-10 sub-task before pinning.

### Datasets

| Asset | What it actually is | Size | License | Status | Correction to earlier docs |
|---|---|---|---|---|---|
| **Terminal Wrench** | github.com/few-sh/terminal-wrench; arXiv 2604.17596 | 331 unique tasks, 957 task/model entries; **3,632 confirmed hacks + 1,216 legitimate attacker solves + 1,441 no-reward attempts + 2,352 non-adversarial baseline trajectories** | not shown in README excerpt — **unverified** | Repo and counts verified | Earlier docs said "3,632 exploit trajectories" and implied no negatives. **It has ~5,000 non-hack trajectories** — that's the negative class for recall/FPR, use it. Also: hacks were **elicited** by a prompt appended to the task. Recall on TW measures detection of *induced* hacks; it overstates recall on natural ones. Say so in B1's note. |
| **TRACE** | HF `PatronusAI/trace-dataset`; arXiv 2601.20103; Patronus AI | 517 trajectories, avg 26 turns, 54 subcategories in 10 categories, 37+ domains | not shown — **unverified** | Verified on HF | Trajectories are **synthetic, generated with Claude Code (opus-4-5) and human-verified**, not observed in the wild. Multilabel. The paper ablates benign:hack ratio, so benign trajectories exist in the release — confirm count at pin time. Patronus is an eval vendor in the incumbent table; using their benchmark is fine, citing them as neutral is not. |
| **SWE-bench Verified** | OpenAI/Princeton curated 500-task subset | 500 tasks; ~28.5% Docker-verified hackable (arXiv 2606.16062) | repo MIT — **verify at pin** | Task IDs by hash of instance ID, seed in manifest | The 28.5% is from a third-party audit; pin that paper's task list if you want the hackable subset, not the whole 500. |
| **pallets/flask** | honest-PR corpus | 200 PRs sampled | BSD-3 | Verified | — |
| **mathlib4** | Lean library | ~232k theorems | Apache 2.0 | Verified | Pin one commit for C1/C2/X4 and five for X5 snapshots. `docs/100.yaml` is the Freek-100 importance label file — verify path at pin. |
| **LeanDojo Benchmark 4** | traced mathlib4 | 122,517 theorems | CC BY 2.0 | Verified (prior pass) | Its mathlib commit may differ from your pin; trace fresh or accept theirs, not both. |

### Tools

| Tool | Role | License | Status | Note |
|---|---|---|---|---|
| `inspect_ai` (UK AISI) | eval harness | MIT | High confidence, verify at install | EvilGenie's harness (`JonathanGabor/evilgenie_inspect`) runs on it — reuse its holdout-test pattern. |
| **LeanDojo** | Lean interaction, ablation | MIT | Verified | — |
| **`plausible`** (was `slim_check`) | counterexample search, TQ4 `N_stmt` | Apache 2.0 | **Correction:** Mathlib's `slim_check` was extracted to a standalone library `leanprover-community/plausible` in late 2024; the tactic is now `plausible`. Cards C1-04 and TQ4 say `slim_check` — **change to `plausible`** and verify it is present on the pinned mathlib commit. | — |
| `#lint only unusedArguments` | TQ4 `N_proof` proxy | Batteries (Apache 2.0) | Verified (prior pass) | Syntactic: flags unused *arguments*; explicit ablation (C1-03) is still required for the semantic label. |
| **MiniCheck-FT5** | entailment judge | repo `Liyan06/MiniCheck` — license **verify at install** (believed MIT) | Numbers verified | Deterministic at fixed batch, local. |
| `batch_invariant_ops` | deterministic inference, TQ9 only | **unverified** license | Repo verified (prior pass) | Only needed if a decoder judge is used. With MiniCheck local at fixed batch, skip it. |
| `ruff`, `uv`, `radon`, `detect-secrets`, `pre-commit` | hooks | MIT / Apache | Standard | `vermin` **falsified** in K1a — do not use. |
| `git check-ignore` | ignore audit | — | Standard | The one-liner that would have caught `.gitignore:3`. |

### Models

| Model | Role | License | Status | Note |
|---|---|---|---|---|
| `Qwen/Qwen2.5-Coder-7B-Instruct` | X1 code agent | Apache 2.0 | Verified | — |
| `deepseek-ai/deepseek-coder-6.7b-instruct` | proposed independent prover/judge | **DeepSeek License, not Apache** | **Correction:** earlier docs listed this as an Apache-clean pair. It is not. If license matters, replace. | Disjoint-lineage judge set that is clean: **MiniCheck-FT5 (T5) + `mistralai/Mistral-7B-Instruct-v0.3` (Apache 2.0) + `meta-llama/Llama-3.1-8B-Instruct` (Llama Community License)**. Three families, no shared weights. |
| `ReProver`, `LeanHammer` | X2 provers | MIT / check | Prior pass | ReProver is a LeanDojo model; LeanHammer is separate lineage. Confirm neither shares a base with the informalizer used in C2-01. |
| Hermes profile models | operator / authors | — | **Read from config (P0-11)** | The sealed K1 RUNBOOK named `qwen3-coder-next`; the postmortem found it never ran. Do not repeat that. |

### Corrections carried into the cards

1. C1-04 and the atomized spec TQ4: `slim_check` → `plausible`; verify presence on pinned commit.
2. B1-03/04: Terminal Wrench has ~5,000 non-hack trajectories; use them as the FPR set for B1 alongside flask. Report recall on TW as "recall on elicited hacks."
3. B1-03: TRACE is synthetic; report recall as "recall on synthetic, human-verified hacks."
4. Judge set for CP-01/C2: replace `deepseek-coder-6.7b` with Mistral-7B-Instruct-v0.3 and Llama-3.1-8B-Instruct.
5. P0-10: licenses for Terminal Wrench, TRACE, MiniCheck, batch_invariant_ops are sub-tasks with their own accept (`LICENSE` file hash in manifest), not assumptions.
6. P0-11 added: model names come from config reads, never from prose.

---

## 16. Model classes on OpenRouter — decided

Checked against OpenRouter listings 2026-09-13. Slugs and prices change; the manifest pins the slug **and the provider**, read from `GET /api/v1/models` at P0-11, never typed.

**Standing OpenRouter rules**
- `provider: {order: [<one provider>], allow_fallbacks: false}` on every call. OpenRouter routes across providers with different quantizations; a fallback mid-run changes the model without changing the slug. Log the `x-openrouter-provider` response header per call into `attribution.json`.
- No judge runs through OpenRouter. Hosted inference is batch-nondeterministic; judges are local (MiniCheck at fixed batch, or a local open-weight at fixed batch).
- No publication through OpenRouter. The 403 is the control; it stays.
- Every role's model is a different lineage from every judge and from the informalizer.

| Role | Class | Pick | Why | Cost |
|---|---|---|---|---|
| `operator` (mahamara) | cheap open-weight MoE coding agent, tool use, high refusal under mechanical prompts | **`qwen/qwen3-coder-next`** (80B MoE, 3B active, Apache 2.0) | This is the model the K1 RUNBOOK *named*; the postmortem found it never actually ran. Run it for real now, pinned by config read. $0.07/$0.30 per M — the cheapest always-on agent class on the router. | ~$2/day at card volume |
| `author-A` (exec) | open-weight, strong long-horizon coding | **`z-ai/glm-5.2`** (or `glm-5.3` if that's what the profile config says — read it) | OpenRouter's June note calls GLM the open-weight quality leader for planning and long-horizon coding. Was one of the K1a author sessions. | low |
| `author-B` (default) | open-weight, disjoint from A, SWE-bench-class | **`deepseek/deepseek-v4-flash`** (MIT, 79.0% SWE-bench Verified, 1M ctx) | Disjoint lineage from Qwen and GLM. Was the other K1a author session. MIT license is clean for anything you ship. | low |
| X1 code agent (the subject of the reward-delta experiment) | **must be open-weight and local** — it's the thing being audited; you need weights fixed and trajectories replayable | `Qwen/Qwen2.5-Coder-7B-Instruct` local, **not via OpenRouter** | Fixed weights, fixed batch, sandbox with git history present. The audit's subject can't be a moving target. | GPU hours, ~$25 |
| S1 frontier reasoning comparison | closed frontier reasoning | **`openai/gpt-5.6`** via OpenRouter, *or* `anthropic/claude-*` — one, pinned | The only role where a closed model is correct: the question is whether the failure classes persist at the frontier. 20 tasks, once. | ~$30 |
| Informalizer (C2-01, Lean → NL) | open-weight, disjoint from all three judges | **`mistralai/devstral`** or `mistralai/mistral-small-3.1` (Apache 2.0) | Mistral lineage; not T5, not Llama, not Qwen. | trivial |
| Judges (CP-01, C2-03) | local, deterministic, three disjoint lineages | **MiniCheck-FT5** (T5) + **Llama-3.1-8B-Instruct** + **Qwen2.5-7B-Instruct** — all local | Removes Mistral from the judge set because Mistral is now the informalizer. Three families, no shared base, none on the router. | local GPU |
| Perturbation generator (TQ10, if automated) | open-weight, disjoint from judges and informalizer | **`deepseek/deepseek-v4-flash`** | Same slug as author-B is fine — perturbation generation is not check authorship. Validity still hand-labeled at CP-04. | trivial |

**Lineage matrix (must have no shared base across any row pair marked ✕):**

```
                 operator  authA  authB  X1-agent  informalizer  judge1  judge2  judge3
operator  Qwen3      —      ✕      ✕      (Qwen)       ✕           ✕       ✕     (Qwen)
authA     GLM               —      ✕       ✕           ✕           ✕       ✕       ✕
authB     DeepSeek                 —       ✕           ✕           ✕       ✕       ✕
X1-agent  Qwen2.5                          —           ✕           ✕       ✕     (Qwen)
informal  Mistral                                      —           ✕       ✕       ✕
judge1    T5                                                       —       ✕       ✕
judge2    Llama                                                            —       ✕
judge3    Qwen2.5                                                                  —
```

Two Qwen overlaps are flagged in parentheses: operator/judge3 and X1-agent/judge3. The operator never judges, so the first is harmless. The second is not — **judge3 must not be Qwen if the X1 agent is Qwen.** Replace judge3 with `google/gemma-2-9b-it` (Gemma terms) or `microsoft/phi-4` (MIT), local. Decision: **Phi-4**, MIT, disjoint from everything.

**Final judge set:** MiniCheck-FT5, Llama-3.1-8B-Instruct, Phi-4. All local, fixed batch.

**What is deliberately not on this list**
- Any "auto" or "free" router slug. Routing changes the model; the manifest can't pin it.
- Any Hermes profile model that isn't read from its config. The RUNBOOK error does not recur.
- A closed model as operator or author. The catalogue's provenance claim is "open-weight, replayable"; a closed operator breaks it.

**P0-11 accept, extended:** `manifest.models` has, for every role, `{slug, provider, lineage_family, license, retrieved_at, source: "config"|"api"}`. CI fails if any two roles marked ✕ share `lineage_family`.

---

## 17. Test discipline — smoke, lint, and failing-first

Industry norms, applied. The K1a postmortem is a catalogue of what happens without them: three harnesses reporting PASS on zero tests, syntax that didn't run on the target interpreter, fixtures the checks couldn't read, a property that would only pass on wrong code. Every one is caught by a stage below.

### 17a. Pipeline stages (CI, in order; each stage blocks the next)

```
stage 0  lint         ruff check + ruff format --check + mypy --strict + radon cc
stage 1  smoke        import every module; run every check CLI with --help; run 1 fixture per check; exit 0
stage 2  unit         pytest tests/unit -q --cov=ol --cov-fail-under=80 --cov-branch
stage 3  contract     schema validation of every fixture, result file, manifest, card
stage 4  property     hypothesis-based tests, min 200 examples per property, deadline=None
stage 5  integration  full harness on all fixtures; invariants (§1) must pass
stage 6  mutation     mutmut run --paths-to-mutate ol/checks; kill rate ≥ 0.7 on check code
stage 7  seal-check   manifest vs git show; timestamp assertion; lineage matrix
```

Stage 0 runs on every commit via pre-commit. Stages 0–3 run on every push. Stages 4–7 run before any seal and before any card marked `gate: true`.

Failing any stage sets the run to `RED` in `status/ROLLUP.md` with the stage name. There is no `YELLOW`.

### 17b. Lint — configuration, sealed in the manifest

```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 100
select = ["E","F","W","I","N","UP","B","A","C4","SIM","ARG","PTH","ERA","PL","RUF"]
ignore = []                      # no blanket ignores; per-line noqa requires a reason comment
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["PLR2004"]          # magic numbers allowed in tests

[tool.mypy]
strict = true
warn_unreachable = true
disallow_any_generics = true

[tool.radon]
cc_min = "B"                     # any function graded C or worse fails
```

Rules:
- `# noqa` without a trailing reason is a lint failure (`ruff` `PGH004` / custom hook).
- `ERA` (commented-out code) is an error, not a warning. Dead code is where the placeholder leak came from.
- `ARG` (unused arguments) is an error in `ol/` — the Python analogue of Lean's `unusedArguments`.
- No `type: ignore` without an issue number.

### 17c. Smoke tests — the five-second gate

`tests/smoke/test_smoke.py`, runs first, must finish in < 5s:

```python
def test_imports():
    import ol, ol.audit, ol.checks, ol.harness, ol.rollup, ol.accept   # any ImportError = RED

def test_every_check_has_cli():
    for name, check in CHECK_REGISTRY.items():
        r = subprocess.run([sys.executable, "-m", f"ol.checks.{name}", "--help"], capture_output=True)
        assert r.returncode == 0, name

def test_one_fixture_per_check_runs():
    for name, check in CHECK_REGISTRY.items():
        f = first_fixture(name)
        r = subprocess.run([sys.executable, "-m", f"ol.checks.{name}", str(f)], capture_output=True)
        assert r.returncode in (0, 1), (name, r.stderr)   # 0 = silent, 1 = finding; anything else = crash

def test_interpreter():
    assert sys.version_info[:2] == (3, 11)                # the PEP 604 class, caught in 5s

def test_manifest_loads():
    m = load_manifest(); assert m.freeze_hash and m.authors and m.models
```

The smoke suite is the first thing the operator runs at the top of every session (card `SMOKE-00`, `depends_on: []`). A red smoke suite halts the loop before any research card loads.

### 17d. Failing-first — tests are written red, before code, and the red is committed

This is TDD applied to the pre-registration discipline. The order is enforced by git history, which CI reads:

1. **Author writes the test.** It fails because the code doesn't exist. Commit: `[<check>] red: <test name>`. CI asserts the test fails on this commit.
2. **Author writes the code.** The test passes. Commit: `[<check>] green: <test name>`. CI asserts the test passes and no other test changed state.
3. **Refactor** under green. Commit: `[<check>] refactor`. CI asserts the test set is identical and still green.

A `green` commit with no preceding `red` commit for the same test is rejected. That is the mechanical form of "public before code": the test's existence and its failure are on record before the implementation.

**Expected failures are declared, never silent:**
```python
@pytest.mark.xfail(reason="K1-1 revision scoping not implemented; issue #47", strict=True)
def test_k1_1_scopes_to_revision(): ...
```
`strict=True` is mandatory: an xfail that unexpectedly passes is a failure. That is exactly the K1-4 property case — "if the property passes, the code is wrong" — turned into a test attribute. `xfail` without `strict=True` or without an issue reference is a lint error.

**Skips need a reason and an owner.** `pytest.mark.skip` without `reason=` is a lint error. A skip older than 14 days (by git blame) is a CI warning; older than 30 is a failure.

### 17e. Negative tests — every check has more negatives than positives

Per check, the fixture set must satisfy `|negatives| ≥ |positives|`, and negatives must include:
- **hard negatives**: inputs that look like the positive but aren't (K1a's `n-identical-unchanged` class, deduped by content hash per §7d)
- **canaries**: sealed, position-randomized (§2 of operational-standards)
- **out-of-scope**: inputs the check must ignore, asserted `in_scope() == False` and no finding
- **adversarial**: the null-model class — a constant/empty input must not score as a finding

CI counts them. A check with fewer negatives than positives cannot be sealed.

### 17f. Mutation testing — does the test suite actually constrain the code?

```
mutmut run --paths-to-mutate ol/checks --tests-dir tests/unit --runner "pytest -x -q"
mutmut results  → kill rate per file
```

Threshold: **kill rate ≥ 0.70** on `ol/checks/`; surviving mutants listed in `results/<run>/mutants.txt`. A surviving mutant in a comparison operator or a threshold constant is a `HALT` for that check — it means the tests wouldn't notice the check being wrong by one. This is the mechanical answer to "three harnesses reported PASS on nothing": mutation testing fails a suite that can't fail.

### 17g. Property tests — with the K1a lesson built in

```python
from hypothesis import given, settings, strategies as st

@settings(max_examples=200, deadline=None, derandomize=True)   # derandomize: seed from test name → replayable
@given(st.from_regex(r"[0-9a-f]{64}", fullmatch=True))
def test_k1_4_accepts_valid_sha(hexstr):
    assert k1_4.check_id(f"FREEZE_HASH={hexstr}") == []      # silent on valid input

@settings(max_examples=200, deadline=None, derandomize=True)
@given(st.from_regex(r"[0-9a-f]{1,63}|[0-9a-f]{65,80}", fullmatch=True))
def test_k1_4_rejects_wrong_length(hexstr):
    assert k1_4.check_id(f"FREEZE_HASH={hexstr}") != []      # fires on invalid input
```

Rules: every property has a **paired inverse** (accept-valid / reject-invalid). A property with no inverse is the K1-4 defect — it can pass on wrong code. `derandomize=True` so a failing example is replayable from the test name alone, no seed hunting. Hypothesis's database is committed (`.hypothesis/`) so found counterexamples persist across runs.

### 17h. Contract tests — fixtures and results are schemas, not conventions

```
schemas/fixture.schema.json     every fixture dir: index.md fields, MEASUREMENTS.txt columns
schemas/result.schema.json      every results/*.json: numerator, denominator, ci_low, ci_high, producing_cmd
schemas/card.schema.json        every card: all fields present, no free text
schemas/manifest.schema.json    authors, models (with source), datasets (with sha + license_sha)
```

`check-jsonschema` in pre-commit on every file under `fixtures/`, `results/`, `cards/`. A result file with a number that lacks `producing_cmd` fails the schema — §7h as a schema constraint, not a rule someone remembers.

### 17i. What "the tests pass" is allowed to mean

A run may report `PASS` only if all of:
- stage 0–7 green on the commit being reported
- `tests_collected > 0` and equals the count in `results/<run>/test_manifest.json`
- `invocations.log` line count ≥ fixture count
- mutation kill rate ≥ 0.70
- no `xfail` flipped to pass, no skip without reason
- coverage ≥ 80% branch on `ol/`

Any of these missing → the run reports `INCOMPLETE`, not `PASS`. `INCOMPLETE` cannot be cited.

### 17j. Cards added to P0

| Card | What | Accept |
|---|---|---|
| P0-12 | `pyproject.toml` lint/mypy/radon config, sealed | `pre-commit run --all-files` exit 0; config hash in manifest |
| P0-13 | smoke suite (`tests/smoke/`) | `pytest tests/smoke -q` exit 0 in < 5s |
| P0-14 | red/green commit-order CI check | test branch with green-before-red is rejected |
| P0-15 | schemas for fixture/result/card/manifest | `check-jsonschema` passes on all existing files |
| P0-16 | mutmut configured; baseline kill rate recorded | `mutmut results` produces a number; threshold in manifest |
| P0-17 | hypothesis database committed; `derandomize` enforced by lint | grep for `@given` without `derandomize=True` → 0 hits |

P0 is now 17 cards. Still one to two days. Still nothing loads until all pass.
