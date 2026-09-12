# Split-Authorship Protocol for Check Code

**When to use:** Two agents write code for different checks in a sealed pre-registration. Prevents contamination between code authors.

## Protocol

### Authorship split

- **Agent A** writes code for checks C1, K1-1, K1-2.
- **Agent B** writes code for checks K1-3, K1-4, K1-5, K1-6.
- Each agent reads **§2 only** — the sealed spec text. No other repo files for intent.
- Neither agent reads the other's code or fixtures before committing.

### Contamination boundary

Both agents read all seven check definitions (because §2 is one sealed document containing all seven). Contamination is therefore bounded to **definitions only**:

- Agent A knows what K1-3 through K1-6 are supposed to do (from §2).
- Agent B knows what C1, K1-1, K1-2 are supposed to do (from §2).
- Neither knows HOW the other implemented their checks.
- Neither has seen the other's fixtures.

This is acceptable because definitions are frozen at seal time. The risk is not definition leakage but implementation leakage — and the split prevents that.

### Constraints per agent

Each code author MUST NOT:
- Open, list, cat, grep, or glob anything under `injections/` for checks they don't own.
- Read `ledger/`, `work/r*`, or any session report.
- Create or edit files outside `work/k1/`.
- Run checks against anything (code-only phase).

Each code author MUST:
- Read only `checker-k1-prereg.md §2` for specification.
- Implement exactly the checks assigned to them.
- Commit all assigned checks in one commit.
- State explicitly in the commit report whether they opened any file under `injections/`.

### Commit discipline

- Agent A commit: `"K1-CODE (A): C1, K1-1, K1-2"`
- Agent B commit: `"K1-CODE (B): K1-3, K1-4, K1-5, K1-6"`
- Injections commit must precede both code commits in `git log`.
- Neither code commit may precede the other's injection commit.

### Pre-run statement

Before the run begins, the standing rules should include:

> Spec-scope note — checker-k1-prereg.md §2 defines all seven checks in one sealed document, so each code author read all seven definitions. Contamination is bounded to definitions; neither author read the other's code or fixtures. Stated pre-run.

This is filed in `ledger/standing-rules.md` under the K1 section before either code commit.

## Why this matters

The §4 adjudication rule requires that injection defects vs code defects can be distinguished. If one agent wrote both the code AND the fixtures for a check, a failure could be masked by adjusting either side. The split ensures:

1. **Fixture author** knows what the check should detect but not how it's implemented.
2. **Code author** knows what the check should detect but has never seen the specific test cases.
3. **Adjudication** can independently blame fixture or code when a case misbehaves.

## Cross-reference

- `references/injection-fixture-discipline.md` — multi-agent blind-split protocol for fixtures (tarball hash-verify, extract without reading).
- `references/seal-preparation-pattern.md` — two-stage seal (pre-reg + run), holdout binding, publication verification.
- `references/session-attribution-forensics.md` — state.db queries for session attribution; zombie session caveat.

## Split-breach detection

### Wrong-invariant verdict

When an attribution or isolation test passes, verify it tested the
**correct invariant**. A test confirming "different sessions produced
the commits" may pass while the actual guard ("fixture author did not
modify code under test") fails — the test measured session identity,
not authorship contamination.

**Pattern:** Before reporting a pass, ask: "What invariant was this
test designed to verify? Does the test actually measure that invariant,
or does it measure a proxy that can pass while the invariant fails?"
If the test measures a proxy, report it as a **wrong-invariant
verdict** — the test passed but the guard it was supposed to enforce
is still breached.

**Example (2026-09-11 K1a):** The session attribution report confirmed
that 0511785 and 163f11b were produced by different sessions/profiles/models
and reported "split holds." But the split-authorship guard requires that
the fixture author not modify code under test. Both the fixtures
(3cebd19/898c566) and the code revision (0511785) were from the same
mahamara session (20260911_124250_f1624c, qwen/qwen3.7-max). The test
verified session identity between Agent A and Agent B, not fixture-vs-code
authorship. Filed as wrong-invariant verdict in
`ledger/split-breach-2026-09-11.md`.

### State.db verification for session attribution

To verify which Hermes session produced a commit, query the session
databases across all profiles:

```bash
# Find all state.db files
find ~/.hermes -name 'state.db' -type f | sort

# Search for commit SHA or message text in messages table
for db in ~/.hermes/state.db ~/.hermes/profiles/*/state.db; do
  echo "=== $db ==="
  sqlite3 "$db" "SELECT s.id, s.source, s.model, s.title,
    datetime(s.started_at, 'unixepoch') as started
    FROM sessions s WHERE s.id IN (
      SELECT DISTINCT session_id FROM messages
      WHERE content LIKE '%COMMIT_SHA%' OR content LIKE '%MESSAGE_TEXT%'
    ) ORDER BY s.started_at;"
done
```

**Key tables:**
- `sessions`: id, source, model, title, started_at, ended_at
- `messages`: session_id, role, content, timestamp

**Common misattribution patterns:**
- User claims session X produced commit Y, but database shows session Z
- Session received prompt but ended without output; prompt re-issued to
  different session (unreported)
- Zombie sessions (ended_at IS NULL) appear in "active at commit time"
  queries

**Verification:** Cross-reference message timestamps with commit
timestamps. A session that received the prompt at 18:49:54 but ended
at 18:51:45 did not produce a commit at 18:55:38 — the prompt was
re-issued.

### Split-breach filing

When fixture author and code author share the same session/profile,
the split-authorship guard is breached regardless of risk level
(9 insertions / 10 deletions, empty-input branch only — risk low,
breach absolute). File in ledger as `split-breach-<date>.md` with:

1. Session ID, profile, model
2. Commit SHAs (fixtures + code)
3. Diff size and scope
4. Risk assessment
5. Breach classification (absolute)
6. Remaining guard (holdout row)
7. Routing attribution (who re-issued the prompt, unreported)
8. Claude-attributed label-based inferences that preceded record consultation
