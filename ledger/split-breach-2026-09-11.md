# Split Breach — 2026-09-11

## K1-3..K1-6: fixture author modified code under test

| Item | Value |
|------|-------|
| Fixtures author | mahamara session `20260911_123521_113d3a` (anthropic/claude-haiku-4.5) |
| Fixture commits | `3cebd19d` (round 3), `898c566e` (round 4 rewrite) |
| Code rev 2 author | mahamara session `20260911_124250_f1624c` (qwen/qwen3.7-max) |
| Code rev 2 commit | `05117855add8c0d7796d05b533eb10f3df868722` |
| Checks affected | K1-3, K1-4, K1-5, K1-6 |
| Diff size | 9 insertions, 10 deletions |
| Scope | Empty-input branch only |
| Risk | Low |
| Breach | Absolute |

The fixture author and the code author shared the same Hermes profile and
filesystem. The split-authorship guard (fixtures by one author who writes no
code for those checks; code author reads no fixtures) was breached: the
qwen3.7-max session that wrote fixtures at 3cebd19/898c566 also wrote the
code revision at 0511785.

## K1a Agent B (163f11b): unreported session re-issue

| Item | Value |
|------|-------|
| Original session | `20260909_215809_aa334cf1` (default profile, z-ai/glm-5.3) |
| Original session ended | 2026-09-11 18:51:45 UTC — no output |
| Re-issued to | `20260911_135145_ea67cb91` (default profile, deepseek/deepseek-v4-flash) |
| Re-issue time | 2026-09-11 18:51:50 UTC |
| Commit 163f11b | 2026-09-11 18:55:38 UTC |
| Operator | deepseek/deepseek-v4-flash (original run's operator) |

K1a pre-reg §6 "different models" is false as stated. The Agent B code was
produced by deepseek/deepseek-v4-flash, the same model that operated the
original run. This entry is the correction; spec not edited.

## Rev 2 postdates Rev H

| Item | Value |
|------|-------|
| Rev 2 commit (0511785) | 2026-09-11 22:40:57 UTC |
| Rev H (gist publication) | 2026-09-11 22:10:53 UTC |
| Gap | 30 minutes 4 seconds (rev 2 AFTER Rev H) |

The attribution report's "split holds" verdict tested session identity
(different sessions, different profiles, different models), not
fixture-vs-code authorship. Filed as a wrong-invariant verdict: the report
tested the wrong split.

## Routing attribution

Founder-attributed routing: the prompt was re-issued from glm-5.3 to
deepseek-v4-flash without reporting the switch.

Claude-attributed for two label-based inferences (bot name → session) in
opposite directions before the record was consulted:
1. "Claude" label on Agent B fixtures → inferred same session as code (false)
2. "Agent B" label on deepseek session → inferred glm-5.3 produced 163f11b (false)

## Remaining guard for K1-3..K1-6

The seven-row holdout: authored by no code author, unseen by any code
author, sealed before any check existed. This is the only uncontaminated
test surface remaining for these four checks.
