# Ledger Entry — MULTI-WRITER-UNATTRIBUTED
# Filed: 2026-09-10
# Type: MECHANISM-FINDING

## Finding

Three Hermes gateway processes share UID `brukendale` and have full write access
to this repo, `ledger/`, `MANIFEST.sha256`, and all 19 manifest paths:

| PID | Profile | Started | Command |
|---|---|---|---|
| 92273 | mahamara | 2026-08-13 11:53:45 local | hermes_cli.main --profile mahamara gateway run --replace |
| 93765 | exec | 2026-08-13 12:11:53 local | hermes_cli.main gateway run --profile exec |
| 15651 | (unflagged) | 2026-08-28 01:47:43 local | hermes_cli.main gateway run --replace |

All three run as the same OS user. Filesystem permissions are `-rw-r--r--` /
`drwxr-x---` with owner `brukendale` throughout; no ACLs, no immutable flags,
no process-level isolation. Any of the three (plus any interactive shell taken
as `brukendale`) can write to any file in the repo.

At least two distinct model families have operated this repo: `deepseek-v4-flash`
(session 20260906_112638_5611f71d, 2026-09-06) and `qwen/qwen3.7-max` (current
session, 2026-09-10). The `exec` profile's model is not visible in this scan but
its gateway process has been running since 2026-08-13.

## Attribution gap

Git author identity is `bendale1-collab`, set globally in
`/Users/brukendale/.gitconfig`. All three gateway processes commit under this
same author name. Commits cannot be attributed to a specific session or profile
from git metadata alone — the author name, email, and committer name are
identical across all three processes.

## Credential-separation scope

Credential separation is enforced for gist publication only (the founder
publishes freeze hashes manually; the agent never has gist credentials). Within
the repo, single-writer discipline is procedural — it depends on which session
is instructed to touch what, not on any OS-enforced boundary. The "single-admin
host" control referenced in `SPEC.md §2.3` and `ledger/seal-detached-v1.5.md`
is a procedural/organizational control, not an isolation mechanism.

## Consequence

Any commit in this repo's history could have been authored by any of the three
gateway processes or any interactive shell session. The agent session that
produced a given commit is recoverable only from Hermes session logs (external
to git), not from the repo itself. This is an unattributed-multi-writer regime
operating under a single-author identity.

Filed 2026-09-10, confirmed from `ps aux`, `git config --show-origin`, and
filesystem permissions audit.
