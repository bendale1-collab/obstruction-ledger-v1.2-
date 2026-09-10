# Ledger Entry — OPERATOR-MISNAMED
# Filed: 2026-09-10
# Type: MECHANISM-FINDING

## Finding

`RUNBOOK.md` (sealed, one of the 19 manifest paths) names `qwen3-coder-next` as
the operator model:

> Operator: cheap model (qwen3-coder-next class) in tmux under watchdog (15-min poll).
> — RUNBOOK.md line 5

No session in either Hermes profile's `state.db` (`mahamara` or `exec`) ever ran
under that model string. The `model` column in the `sessions` table was queried
with `LIKE '%qwen3-coder-next%'` across both profiles: zero rows.

## Recorded operators

| What produced what | Session ID | Model string | Profile |
|---|---|---|---|
| Commits 66f9b16..e02e15b | 20260908_072342_c971108e | deepseek/deepseek-v4-flash | mahamara |
| Current session (r8-grep onward) | 20260910_084547_3739eed1 | qwen/qwen3.7-max | mahamara |
| Commit a8e11c8 (2026-09-10 06:41:28 -0500) | UNATTRIBUTED | — | — |

Commit a8e11c8 is unattributable because ~140 sessions in both profiles carry no
`ended_at` timestamp, making activity-at-instant identification unreliable — too
many zombie sessions match the time window.

## Mechanism

The RUNBOOK text is embedded into API request payloads as system-prompt content
(confirmed in session request dumps under
`~/.hermes/profiles/mahamara/sessions/request_dump_*`). Every operating model
received RUNBOOK text telling it that the operator is a different model. The
asserted operator (`qwen3-coder-next`) and the recorded operator
(`deepseek/deepseek-v4-flash`, `qwen/qwen3.7-max`) diverge without any signal
that the divergence has occurred.

## Correction to earlier model-census claim

The earlier census (r14-gitignore-provenance-audit-2026-09-10.txt) stated "at
least two models have operated this repo." The census covered all sessions in
each profile, not this repo specifically. Repo-local evidence establishes two
models by session-to-commit timestamp matching (deepseek-v4-flash for 66f9b16..
e02e15b; qwen3.7-max for current session). More models are possible and
unattributable under the shared git author `bendale1-collab` — the shared author
precludes commit-level model attribution.

## K-candidate status

Asserted-operator vs recorded-operator divergence is a **K2 candidate** (design
for future checker implementation). K1 scope is locked at seven checks (R8b, R8c,
C3, C6, R1, and the four standing-rule candidates); this finding does not expand
K1.

Filed 2026-09-10. RUNBOOK.md NOT edited — it is sealed and the finding lives
here.
