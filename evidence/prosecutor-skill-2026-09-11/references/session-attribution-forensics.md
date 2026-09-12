# Session attribution forensics

When verifying which session/model produced a specific commit, query the
Hermes state DB directly. The user's claim ("session X committed Y") may be
wrong — the database is authoritative.

## Schema

**Locations:**
- `~/.hermes/state.db` — default profile
- `~/.hermes/profiles/<profile>/state.db` — named profiles

**Tables:**
- `sessions` — id, source, model, started_at, ended_at, title
- `messages` — session_id, role, content, timestamp

**Timestamps:** Unix epoch (seconds since 1970-01-01 00:00:00 UTC).

## Query pattern

### Step 1 — Find sessions mentioning the commit or task

```sql
SELECT DISTINCT session_id
FROM messages
WHERE content LIKE '%<commit_sha>%'
   OR content LIKE '%<task_keyword>%';
```

### Step 2 — Get session metadata

```sql
SELECT id, source, model, title,
       datetime(started_at, 'unixepoch') AS started,
       datetime(ended_at, 'unixepoch') AS ended
FROM sessions
WHERE id IN (SELECT DISTINCT session_id FROM messages
             WHERE content LIKE '%<commit_sha>%');
```

### Step 3 — Verify the commit timestamp

```bash
git log --format='%H %ai' <commit_sha> -1
# Convert to UTC epoch
python3 -c "from datetime import datetime; print(int(datetime(<Y>,<M>,<D>,<H>,<M>,<S>).timestamp()))"
```

### Step 4 — Find sessions active at that instant

```sql
SELECT id, source, model, title
FROM sessions
WHERE started_at <= <epoch>
  AND (ended_at IS NULL OR ended_at >= <epoch>);
```

**Caveat:** Many sessions have `ended_at IS NULL` (zombie sessions). If the
zombie count is high (>50), activity-at-instant attribution is unreliable. Report
the count and label UNATTRIBUTED when the zombie set is too large.

### Step 5 — Cross-reference message timestamps

```sql
SELECT session_id, role, substr(content, 1, 200),
       datetime(timestamp, 'unixepoch') AS msg_time
FROM messages
WHERE session_id = '<candidate_session>'
  AND timestamp BETWEEN <epoch_minus_3600> AND <epoch_plus_3600>
ORDER BY timestamp;
```

Look for the user's prompt and the agent's commit message near the commit
timestamp.

## Common misattribution patterns

1. **User told session X committed it, but session Y actually did.** The user
   may have received a report from session X claiming success, but the actual
   commit was produced by session Y running in parallel or sequentially after.

2. **Multiple sessions received the same prompt.** If the user sent the same
   instruction to multiple sessions (e.g., testing different models), all
   sessions will have the prompt in their message history. Only the one with
   the tool output showing the actual `git commit` command produced the commit.

3. **Timestamp mismatch.** The commit timestamp (from git) and the message
   timestamp (from state DB) may differ by seconds to minutes due to network
   latency or agent processing time. Use a ±5-minute window for matching.

4. **Split-breach detection.** When a project uses split-authorship guards
   (fixtures by one author, code by another), verify that the fixture author
   and code author are in different sessions AND different profiles. If the
   same session/profile produced both fixtures and code, the split is breached
   even if the commits are different. Query both the fixture commit and the
   code commit against the state DB; if they resolve to the same session or
   same profile, the guard failed. (2026-09-11 K1a: fixtures at 3cebd19/898c566
   and code rev 2 at 0511785 were both from mahamara session 20260911_124250_f1624c
   running qwen/qwen3.7-max — split breached for K1-3..K1-6.)

## Reporting format

| Field | Value |
|---|---|
| Commit SHA | `<full_40_char_sha>` |
| Commit time (UTC) | `<YYYY-MM-DD HH:MM:SS>` |
| Session ID | `<session_id>` |
| Profile | `<profile_name>` |
| Model | `<model_string>` |
| Title | `<session_title>` |
| Prompt received | `<YYYY-MM-DD HH:MM:SS>` |

**Same session?** Yes/No. Different sessions, different profiles, different models.

## Example (2026-09-11, K1a CODE)

User claimed session `20260909_215809_aa334cf1` (default, z-ai/glm-5.3) committed
`163f11b`. Database showed:

- Session `20260909_215809_aa334cf1` received the prompt at 18:49:54 UTC but
  produced no output (no tool calls, no commit message).
- Session `20260911_135145_ea67cb91` (default, deepseek/deepseek-v4-flash)
  received the prompt at 18:51:50 UTC and committed at 18:55:38 UTC.

The glm-5.3 session was told to commit but failed silently; the deepseek session
ran 2 minutes later and actually executed the write + commit.

**Rule:** When the user asks "which session committed X," query the database.
Do not trust the user's premise or your own prior claim without verification.
