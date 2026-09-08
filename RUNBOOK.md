# Obstruction Ledger — Agent Runbook v1.1

Companion to spec v1.3 (inverted architecture). This file + STATE.yaml + the spec are the agent's ENTIRE context. Nothing in any chat history is authoritative. If this file and the spec conflict, the spec wins; log the conflict.

Operator: cheap model (qwen3-coder-next class) in tmux under watchdog (15-min poll). Frontier calls only at typed escalation points. Founder input arrives ONLY via Telegram replies from the vocabulary in §6.

---

## 0. Prime directives (read every cold start)

1. **Disk is memory.** All state lives in `STATE.yaml`, the ledger, and git. Never rely on conversational context. After every subtask: commit, update STATE (phase, subtask, intent, next_step, spend), then continue.

After each STATE.yaml update, emit the derived digest work/state.json {phase, subtask, next_step, spend, utc} in the same commit. STATE.yaml is authoritative; work/state.json exists solely for the operator watchdog and is never read by the agent.
2. **Verdict-validity.** No PASS/KILL is emitted without positive-control and negative-control status in the same packet. Controls red → VOID, halt, escalate.
3. **Escalate, never improvise.** Ambiguity, gray band, UNTYPED-on-ground-truth, control anomaly, spend within 20% of any cap → HALT + Telegram escalation. Silent workarounds (env edits, tolerance changes, unlogged retries) are spec violations.
4. **Two processes.** Runner writes results; ledger process (separate keys) hashes and appends. Runner never touches `ledger/`.
5. **Budget is physics.** Global cap $1,000. Per-phase caps in §3. Spend logged per run in STATE. Cap breach = poison pill.

## 1. Cold-start / RESUME protocol (context loss & compaction)

Run at session start, after any compaction, restart, or crash:

```
make resume
```
which performs: (1) read RUNBOOK.md §0–§3; (2) read STATE.yaml → {phase, subtask, intent, next_step, spend, open_escalations}; (3) verify ledger hash chain (`make ledger-verify`); (4) verify env manifest hash; (5) if open_escalations nonempty and blocking → idle + re-send Telegram reminder (max 1/24h); else continue at next_step.

**Compaction rule:** before any long tool output or context-heavy operation, write intent + next_step to STATE first. A fresh instance must be able to continue from STATE alone. Never summarize state into the chat — write it to disk.

**Frontier escalation briefs:** when a frontier call is needed, generate `briefs/<id>.md` from STATE + relevant files (self-contained, ≤2k words), call with the brief only. Never paste chat history.

**Resume drill (mandatory P0 test H-K):** watchdog kills the session mid-subtask; fresh session must resume to the correct next_step with zero founder input. Failure = P0 RED.

## 2. Repository layout

```
RUNBOOK.md  SPEC.md(v1.2)  STATE.yaml  LICENSES/
engine/     # F1 classical: Chebyshev/mapped-Fourier + Newton + PALC + deflation + eigensolver (CPU, FP64; mpmath quad path)
specimen/   # F2 vanilla PINN (frozen config; ghost factory)
extract/    # LLM extractor, prompts, blinding filter
harness/    # all tests H-A..H-L, batteries, spike plumbing
ledger/     # append-only certificates, verdict packets, untyped/ (sealed)
briefs/  telegram/  anchors/ANCHORS.md
```

`anchors/ANCHORS.md` (frozen, from research 2026-09-06; v1.5 leg-split 2026-09-08):
- LEG A (CLM SPECTRAL, gCLM a=0): a=0 → α=1, profile Ω(y)=−y/(y²+¼), spectrum {0,1}, gap ½ after modulation. a=1/2 → α=1/3 EXACTLY (not 1/2). a_c=0.6890665337007457 → α=0, c_l sign change. a<0 half-line → γ̄=1−a exact (do NOT use odd-symmetric two-scale tables for this check). a=1 → α=−1, compact support. Numeric soft anchors (LSS): α(2/3)=0.04517094, α(0.8)≈−0.260.
- LEG B (CCF TRANSPORT, Córdoba-Córdoba-Fontelos): λ₀=1.1807776628998, λ₁=0.6057337012032, λ₂=0.4713248638620 (2509 table) / 0.47132422 (2511 refined), λ₃=0.2415604743989. NOT computable by F1. See ANCHORS.md for precision notes.
- c_ω=−1 fixed across the standard family; the fitted law is for the SPATIAL exponent α(a).
- Modulation rows (frozen): N1: Ω_x(0)=const · N2: U(1)+c_l=0 (or Ω_x(1)=0). Two constraint rows in the Newton Jacobian.
- Realization predicate: odd basis + origin-H² vanishing; discard Re λ=−½ line; expect naive maximal-L² run to show a strip (that strip is the wrong realization's TRUE spectrum, not noise).
- Perturbation safety: sweep a inside (0, a_c) and a<0 intervals; never across a_c blind.

## 3. Phases, caps, terminal states

| Phase | Work | Terminal states | Cap ($ / days) |
|---|---|---|---|
| P0 | Env pin + F1 skeleton + analytic goldens H-A + realization pair H-B + resume drill H-K + ledger H-L — LEG A only | GREEN / RED(component) | 20 / 4 |
| P1 | PALC continuation + deflation → gCLM 1st+2nd (H-E); eigensolver orders 0–2 under H-B/H-D; quad re-eval — LEG A only. CCF λ targets NOT in scope (move to LEG B) | GOLD-PASS / GOLD-MISS / VOID | 15 / 5 |
| P2 | gCLM α(a) sweep → (λ,order) pairs; W1b selection rule fires G1 variant; anchors cross-check — LEG A only | N-PAIRS(count)→variant / SWEEP-FAIL | 40 / 4 |
| P3 | Specimen PINN (frozen config) + ghost battery 4×25 (H-G) + CCF §2.3.1 sign-flip holdout attempt | BATTERY-VALID / INVALID; HOLDOUT-{REPRO,NONREPRO} | 250 / 10 |
| P4 | G0 extractor: synthetic floor, blinding H-H, contamination pair (published vs perturbed), permutation null, k=3 vote | PASS / GRAY / KILL / VOID | 220 / 7 |
| P5 | G1 per selected variant: PySR mechanical path, power check, shuffle ablation, holdout | PASS / KILL / UNDERPOWERED / VOID | 15 / 3 |
| P6 | Artifact assembly, seal (SHA-256 → gist + SWH + Zenodo) | PUBLISHED-SEALED | 15 / 3 |

LEG B — CCF TRANSPORT: NOT STARTED. No engine. Cap and scope UNQUOTED pending its own adjudication. The inherited $40/5d cap from v1.4 is VOID.

Budget: phases 600 + reserve 300 (released only by founder EXTEND) + misc/telegram/api overhead 100 = **$1,000 hard**. Wall clock ≈ 6 wk. VOID-rerun: one per phase inside cap; second VOID same phase = TERMINAL-PARK.

**Auto-advance rule:** P0→P1→P2 and P4→P5 advance automatically on clean terminal states (Telegram PHASE notice, no reply needed). **Blocking founder gates:** P2→P3 requires T1 battery-design APPROVE; P3→P4 requires APPROVE (battery validity is judgment-adjacent); any GRAY/VOID/UNTYPED-on-ground-truth blocks.

## 4. Harness register (all must exist and pass before their gate)

- **H-A Analytic goldens (positive controls, free):** engine reproduces CLM a=0 exact profile + c_l=1; a=1/2 α=1/3; γ̄=1−a at a∈{−1,−0.5,−0.1}; CCF stable λ to 8 digits. Any miss → engine RED.
- **H-B Realization pair (negative control for the truth engine):** naive maximal-L² eigensolve MUST show the strip; origin-H² MUST show clean {0,1}+line. Both behaviors required — an eigensolver that can't produce the wrong answer when misconfigured proves nothing.
- **H-C Modulation rows:** with N1/N2, Newton converges, c_l matches anchor; with rows removed, rank-deficiency detected and reported (expected-failure test).
- **H-D Order-claim stability:** every instability-order entry requires resolution doubling + realization-variant agreement. Encoded as a certificate-write precondition, not a manual step.
- **H-E Deflation recovery:** stable→1st→2nd CCF via deflated Newton; λ digits logged per stage.
- **H-F Determinism:** CPU engine bit-identical (hash of outputs, 2 runs). Specimen GPU: seed-hash test; if nondeterministic, outputs are ARCHIVED (never claimed replayable) — pre-decided.
- **H-G Ghost battery:** 4 mechanisms × 25 plants, blind spike rate known only to ledger process; ≥90% catch, monitored continuously; drop <90% mid-run = poison pill. CCF §2.3.1 holdout scored ONCE; NONREPRO → disclosed limitation per spec W3c, never re-tuned.
- **H-H Extractor wall:** automated grep of every LLM prompt for forbidden fields (equation names, classical diagnostics, spectrum data, λ truth); any hit = VOID. Synthetic floor ≥90% before real cases. k=3 majority vote; full prompt+response archived to ledger.
- **H-I Spend meter:** every run appends $ to STATE; cap checks before launch of any job.
- **H-J Telegram conformance:** all outbound messages pass template check ≤3,500 chars; logs NEVER sent — hashes + digests only.
- **H-K Resume drill** (§1). **H-L Ledger verify** every cycle.

## 5. Certificate & packet formats (compaction-safe)

Certificate (one line JSON in ledger): per spec §2.1 + classical provenance {branch_id, cont_step, deflation_count, realization, grid_pair}. Verdict packet: {phase, verdict, pos_ctrl, neg_ctrl, contamination_caveat, key_numbers(≤6), hashes, spend}. Packets are the ONLY thing summarized to Telegram.

## 6. Operator-channel protocol (output-limited; currently the authenticated Hermes chat — all "Telegram" references in this bundle mean this channel)

Message classes (templates in `telegram/`):
- `HB` daily heartbeat, 1 line: `HB P3 d4/10 spend 412/1000 ok`
- `PHASE` terminal state, ≤10 lines: state, 3 key numbers, packet hash, next action. No reply needed unless flagged.
- `ESC` blocking escalation, ≤15 lines: what, why, options, default-on-timeout, reply menu.
- `PILL` poison pill fired: cause, state preserved at commit <hash>, awaiting reply.

Reply vocabulary (anything else → agent asks once, then HOLDs): `APPROVE` · `HOLD` · `ABORT` · `EXTEND <$>` (releases reserve) · `INFO <topic>` (agent replies with ≤1 message digest; full detail goes to a file, path given).

Timeout defaults (pre-agreed): ESC unanswered 48h → HOLD (idle, HB continues). PILL unanswered → stay parked. Nothing ever auto-ABORTs or auto-spends reserve.

## 7. Founder touchpoints (total ≈ 3 h + 2 min/day)

| # | When | What | Cost |
|---|---|---|---|
| T0 | Before launch | Approve spec §14, fill §11 blanks, hash spec+runbook+env manifest, publish | 30 min |
| T1 | P2→P3 | Battery design review (the one non-delegable hour): plant list, spike plumbing, holdout seal | 60 min |
| T2 | P3→P4 | APPROVE on battery packet | 1 word |
| T3 | P4 verdict | APPROVE advance / adjudicate GRAY | 1 word–15 min |
| — | Daily | Read HB | 2 min |

Everything else is agent-autonomous or timeout-defaulted.

## 8. Failure map (pre-registered responses; no mid-run judgment)

| Event | Response |
|---|---|
| H-A miss | P0/P1 RED → one debug cycle inside cap (§14-v); if any ANCHORS unverified-from-source flag is unresolved, recipe-check per SPEC §2.6 caveat runs first → second miss = ESC |
| Strip appears in origin-H² run | Realization rows insufficient → strengthen origin-vanishing order per spec W2 predicate → re-run once → still → VOID |
| Perturbed gCLM point non-convergent both grids | Apply spec D3 rule: draw next parameter from pre-registered sequence; log profile-nonexistence certificate; N_max=10 draws |
| Published λ hit, perturbed missed (extractor) | Recall signature → logged into §9 cause-separation; counts AGAINST C-extract-a |
| Ghost catch <90% mid-run | PILL |
| UNTYPED on ground-truth case | HALT + ESC (taxonomy-failure signature) |
| DeepMind lineage posts CCF CAP or NS candidate mid-run | INPUT not unfreeze: log, continue; intro reframe deferred to P6; notify via PHASE-note |
| Spend cap 80% | ESC with projection before any further job |
| Stall pill: no subtask commit/STATE update >48h (§14-l) | PILL. (Operator watchdog alerts at ≥6h liveness silence; alert ≠ pill.) |

## 9. Seal & handback (P6)

1. Assemble artifact per spec §10 mapping (all four outcome branches pre-written; agent selects by verdict, edits nothing else).
2. `make seal-prepare` (agent): hash repo+paper+ledger; write SEAL-PACKET.md {hashes, gist body text, Zenodo draft metadata, SWH request URL}. Founder then: flip repo public → trigger SWH save-code-now → post gist → create+publish Zenodo record. All publication credentials remain founder-only; the agent publishes nothing.
3. Handback packet to founder: verdicts, packet hashes, spend total, contact-package draft (paper DOI + 10-certificate replay bundle + endorsement ask), and the K0b re-scan log (48h-pre-seal novelty check, queries frozen in spec).
4. Park. No external contact by the agent, ever.
