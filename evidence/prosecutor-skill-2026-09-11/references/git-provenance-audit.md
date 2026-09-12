# Git provenance audit

Techniques for auditing a git repo's commit provenance: force-adds past
`.gitignore`, multi-writer attribution, manifest integrity.

## The `git check-ignore --no-index` pitfall

`git check-ignore -v <path>` (without `--no-index`) silently skips files
already tracked in the index — returning exit 1 and no output for any
tracked file, regardless of whether `.gitignore` matches it. This makes
force-added files (tracked despite an ignore rule) appear as if they are
not ignored.

**Always use `--no-index` when auditing ignore-rule coverage:**

```
git check-ignore -v --no-index <path>
```

This returns the matching `.gitignore` rule even for tracked files. Without
it, a repo with `ledger/` in `.gitignore` and 21 force-added ledger files
will report all 21 as "not ignored" — a false negative that hides the
entire force-add history.

## Force-add detection workflow

1. Enumerate all files under the directory of interest: `find <dir> -type f | sort`
2. For each file, check tracked status: `git ls-files --error-unmatch <path>`
3. Check ignore-rule match with `--no-index`: `git check-ignore -v --no-index <path>`
4. A file that is BOTH tracked AND matched by an ignore rule was force-added.
5. Find the add-commit: `git log --diff-filter=A --format='%h %cI %s' -- <path>`
6. Verify the ignore rule was active at that commit: `git show <commit>:.gitignore`

## QUOTED header convention

When an audit file reproduces sensitive identifiers (gist IDs, freeze hashes,
commit SHAs) as evidence rather than asserting them as current state, prepend:

```
QUOTED: identifiers below are reproduced as evidence, not asserted
```

This distinguishes reproduction from assertion — the file documents what
was found, not what the author claims. Particularly important for truncated
or variant identifiers that appear in the evidence (e.g., a 31-char gist
ID found in one commit vs the canonical 32-char form).

## Multi-writer attribution audit

When multiple processes share UID and write access to a repo:

1. `ps aux | grep <harness>` to enumerate running gateway/agent processes.
2. Record PID, start time, and profile/command for each.
3. `git config user.name` + `git config --show-origin user.name` to check
   whether author identity is global or repo-local.
4. If all processes share the same `user.name`, commits cannot be attributed
   to a specific session from git metadata alone.
5. File as MULTI-WRITER-UNATTRIBUTED with all PIDs, start times, and the
   consequence stated plainly.

Per-profile git author attribution (standing rule 9) sets distinct
`GIT_AUTHOR_NAME` / `GIT_COMMITTER_NAME` per gateway. This is attribution,
not isolation — it records which profile authored a commit but does not
prevent other profiles from writing to the same paths.

## Session attribution from Hermes state DB

Model strings and timestamps for a session are stored in:
`~/.hermes/profiles/<profile>/state.db` → table `sessions`

```sql
SELECT id, model, model_config, started_at, ended_at, title
FROM sessions WHERE id = '<session_id>';
```

Session IDs follow the format `YYYYMMDD_HHMMSS_<short_hash>`. The `session_search`
tool returns `session_id` in discovery results; use it to look up the producing
session for any commit range.

## Manifest duplicate-hash scan

```
awk '{print $1}' MANIFEST.sha256 | sort | uniq -d
```

For each duplicate hash, show paths: `grep "^<hash>" MANIFEST.sha256`. A
byte-identical `.md`/`.yaml` pair in a manifest is a reconstruction defect
(both twins generated from the same source in the same pass), not a
formatting convention. Pre-reconstruction twins should have distinct hashes.

## .yaml extension is not a format guarantee

A `.yaml`-named file may be prose with `#`-commented headers, not parseable
YAML. Verify with `python3 -c "import sys,yaml; yaml.safe_load(sys.stdin)"`
piped from `git show <commit>:<path>`. Report exit code per file.

## OPERATOR-MISNAMED error class (asserted-operator vs recorded-operator)

When a sealed spec document (e.g. RUNBOOK.md) names a specific model as the
"operator" model, but no session in any profile's `state.db` ever ran under
that model string, the spec and reality diverge silently. The operating model
receives the spec text embedded in its system prompt and is told it is a
different model — without any signal that this has occurred.

**Audit pattern:**
1. `grep -r "<model-string>" ~/.hermes/` — find ALL occurrences (routing code,
   model catalogs, request dumps, skill references).
2. `SELECT DISTINCT model FROM sessions` per profile — enumerate actually-used models.
3. Cross-reference: if the string appears in routing code and catalogs but NEVER
   as a session model, the spec names a model that was never used.
4. File as a ledger entry with the correction. Do NOT edit the sealed spec.

**K-candidate status:** asserted-operator vs recorded-operator divergence is a
K2 candidate (design for future checker). K1 scope is locked at seven checks;
this finding does not expand K1.

## Zombie sessions and activity-at-instant attribution

When querying `sessions` for "which session was active at timestamp T," many
sessions carry no `ended_at` value (NULL). This makes the query
`WHERE started_at <= T AND (ended_at IS NULL OR ended_at >= T)` return hundreds
of results — most of which are zombie sessions that were never formally closed.
Activity-at-instant attribution is unreliable when zombie counts are high. Report
the count and the most recently started match, but label the result UNATTRIBUTED
when the zombie set is too large to narrow.

## Model-census scope correction

When reporting "at least N models have operated this repo," distinguish:
- **Profile-level census** (all sessions in `state.db`) — covers the profile, not the repo.
- **Repo-local evidence** (session-to-commit timestamp matching) — covers only what you can attribute.

A profile census finding of 12 distinct models does not mean 12 models wrote to
the repo. Repo-local evidence may establish only 2 by timestamp matching; more
are possible and unattributable under a shared git author. State the scope of
each claim explicitly — never conflate profile coverage with repo coverage.
