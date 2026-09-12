# Quarantine Execution — Blind-Experiment Isolation Procedure

**Origin:** PROSECUTOR session-isolation protocol, battle-tested during RC-0 Session A→B quarantine (2026-08-24).
**Purpose:** Mechanically remove all traces of a blinded experiment from a Hermes profile so a fresh conversation can serve as a blinded session.
**Key correction from field use:** Pass 1 is never enough. Expect to discover residual contamination in paths you didn't quarantine the first time. Treat the user's review of Pass 1 as a free audit and plan for it.

---

## When to apply

Any partitioned blind experiment where one agent context has seen the gold-standard (incident registry, ground-truth labels, known-change timelines) and a fresh blinded context must be provisioned on the same Hermes profile.

**Rule:** A context that has seen the incident register is permanently disqualified from the blinded evaluation session. Contamination is not partial — there is no "partial blindness."

---

## Procedure

### Step 0 — Declare operator/auditor status

Before starting, the executing agent must self-report whether it can serve as the blinded session. If it has seen the incident registry, it must disqualify itself and designate itself operator/auditor. The operator executes quarantine; a different (fresh) conversation serves the blinded session.

### Step 1 — Map every auto-loaded and tool-readable path

A fresh conversation on a Hermes profile **auto-loads** these files into every turn's prompt context:

| Path | Content |
|------|---------|
| `SOUL.md` | System prompt / soul definition |
| `memories/MEMORY.md` | Persistent agent memory |
| `memories/USER.md` | User profile / preferences |

A fresh conversation **can read** (via `skill_view`, `read_file`, `search_files`, `session_search`, `terminal`):

| Path | Access mechanism |
|------|------------------|
| `skills/` (entire tree) | `skills_list`, `skill_view` |
| `.skills_prompt_snapshot.json` | auto-listed at startup |
| `skills/.bundled_manifest` | file tools |
| `config.yaml` | startup |
| `cache/` | file tools |
| `cron/` | cron tool |
| `scripts/` | terminal |
| `sessions/` | file tools |
| `state.db*` | session_search |
| `logs/` | file tools |
| `data/`, `projects/`, `sandboxes/`, `workspace/`, `plans/` | file tools |
| `audio_cache/`, `image_cache/`, `lsp/`, `bin/`, `home/`, `hooks/`, `pairing/`, `state/`, `skins/` | file tools |
| `state/rich_sent_index.json` | file tools (runtime generated — may contain this session's work) |

The quarantine directory MUST be outside the profile root — e.g. `~/.hermes/<name>-quarantine/` (sibling to `profiles/`, not inside it).

### Step 2 — Multi-pass move

**Pass 1: Obvious files.** Move cache directories (experiment data, registry, plant record, seal, operator tool, corpus interface), skill references that contain experiment names/incident details, session dumps that reference the experiment.

**Pass 2: Residual contamination.** After Pass 1, run a content search across ALL non-excluded paths for every experiment identifier (codename, vendor-incident IDs, artifact names). Any hit outside accepted-residual paths must be quarantined. Common pass-2 targets:
- State/index files (`state/rich_sent_index.json` — runtime generated, may contain this session's quarantine output)
- Skill `.usage.json` — contains skill-name keys; evaluate whether the key itself leaks (skill name that IS the experiment codename → move; generic project name referenced from a skill tag → evaluate)
- Reference files in sibling skill directories that mention the experiment by name
- Competing-session skill references (`pre-registered-research-executor`, `measurement-discipline` etc.)
- The umbrella skill's own SKILL.md if it contains experiment-specific reference pointers

**Pass 3: Reference pointer neutralization.** After moving files, remaining skills may still have reference pointers (`*(ref:quarantined-file.md)*`) that dangle. Replace them with a neutral placeholder. Also check main profile files (SOUL.md, MEMORY.md, USER.md) for any reference to the experiment or its codename.

### Step 3 — Hash discipline

Before moving ANY file, compute and record its SHA-256. After the move, recompute and verify. Report both in the relocation manifest.

**Seal file integrity rule:** The seal file contains committed hashes of experiment artifacts. Verify every hash inside the seal matches the post-move computed value — these are the invariant. The seal file's OWN hash is NOT committed anywhere and its value is irrelevant. Do NOT claim the seal file's hash "changed on relocation" or attribute it to "filesystem metadata." Content hashes are deterministic: the same bytes produce the same hash regardless of path. If you did not record the pre-move hash, say so — do not fabricate an explanation.

### Step 4 — Exhaustive clean-profile content search

Search every auto-loaded and tool-readable path (excluding quarantine, live logs, state.db, sessions) for every experiment identifier:

- Experiment codename and abbreviations (`rc-0`, `RC-0`, `retrocanary`, `rc0`)
- Skill/program names that reference the experiment (`cn-omnibus`, `conformance-oracle`)
- Vendor-incident IDs (`ANTH-2025-*`, `ANTH-2026-*`, `OPENAI-2025-*`, `OPENAI-2026-*`, `GOOG-2026-*`)
- Artifact names (`plant-record`, `quiet-ledger`, `seal`, `registry`, `corpus-interface`, `superseded-hashes`, `op-tool`)

Use `find` with content grep (not `search_files` — it has FTS5 output limits that can miss hits in large files). Exclude accepted residuals.

**Target: zero content hits outside accepted-residual paths.**

### Step 5 — Memory and profile cleanup

- `memories/MEMORY.md`: remove or neutralize any line referencing the experiment name, program name, or skill that contained incident data. Replace with a dated placeholder recording the removal. Log exact before/after text.
- `memories/USER.md`: check for experiment-specific preferences or work references.
- `SOUL.md`: check for any experiment-specific clauses, codenames, or skill-loading instructions.

### Step 6 — Handle accepted string-level residuals

These paths will always contain term matches after quarantine and are accepted:

| Path | Reason | Risk |
|------|--------|------|
| `logs/*.log*` | Historical log entries, not auto-loaded | None — not in prompt context |
| `state.db*` | Session database backing `session_search`; not in prompt context | Low — but `session_search` can be called on a clean profile after quarantine, so ensure the experiment's dedicated session dump is also quarantined |
| `skills/.usage.json` | Usage metadata with skill-name keys only; no incident content | None |
| XML schemas in `powerpoint/`, pyright stubs in `lsp/node_modules/` | Unrelated `conformance` attribute in XML/infer stubs | None |

Report these explicitly in the search results as "accepted residuals" so the operator can evaluate the risk.

### Step 7 — Deliver

Deliver exactly: (1) the auto-load/exhaustive-read path list, (2) the relocation manifest with hash confirmations and seal integrity statement, (3) the clean-profile search results verbatim. Do not narrate, summarise, or add observations beyond these three items.

---

## Pitfalls (earned in RC-0 quarantine)

- **Pass 2 is mandatory, not optional.** The user's review of Pass 1 is a free audit — treat it as routine, not failure.
- **Seal file hash trap:** Do not claim the seal file's own hash changed on relocation. Content hashes are deterministic. If you didn't compute pre-move, say so. The seal's invariant is the six hashes *inside* it.
- **State index contamination:** `state/rich_sent_index.json` is a runtime FTS5 index that captures this session's text. It will contain quarantine terminology. Must be moved before the profile is clean.
- **Sibling skill references:** A reference file in `pre-registered-research-executor/references/` may reference the experiment by name even though it belongs to a different skill family. Search ALL skill directories, not just the experiment's own.
- **Dangling ref pointers:** After moving a skill reference file, check whether the parent SKILL.md still points to it. Replace with a neutral placeholder.
- **Two copies of same file:** Some files exist in both `skills/` and `cache/` (e.g. `cn-audit-annex.md`). Move both copies independently.
- **Conformance-oracle empties:** After moving `skills/research/conformance-oracle/SKILL.md` and its references, `rmdir` the empty directories so the profile no longer lists them.
- **Usage.json metadata:** `skills/.usage.json` records skill names as keys. If the skill name itself is the experiment codename, the key leaks it. Accepted as residual only when the key is a generic project name, not the experiment itself.