# Ledger Entry — ANCHOR-POSTDATES-ARTIFACT
# Filed: 2026-09-11
# Type: PROCEDURE-FINDING

## Finding

The K1a-RUN public anchor (Rev H) was published after code commits c3e7e19 and 163f11b.
The repo record holds; the public-before-code claim does not for K1a.

## Timestamps

- **c3e7e19** (Agent A: C1, K1-1, K1-2): 2026-09-11T18:50:50Z (13:50:50 -0500)
- **163f11b** (Agent B: K1-3..K1-6): 2026-09-11T18:55:38Z (13:55:38 -0500)
- **Rev H** (gist revision a948002653d0): 2026-09-11T22:10:53Z

## Gap

- Rev H minus c3e7e19: **3 hours 20 minutes 3 seconds**
- Rev H minus 163f11b: **3 hours 15 minutes 15 seconds**

## Attribution

Founder-attributed. Stated on the gist itself (Rev H timestamp from API).

## Context

Seal commit 7b887de (2026-09-11T14:12:09Z) predates both code commits.
The repo record (git log, seals) holds the correct ordering.
The public-before-code claim (fixtures published, then code written) does not
hold for K1a: the public gist anchor was updated after the code was committed.

This is a procedure finding, not a disqualification. The code was written
after the seal commit and after the fixtures were committed to the repo,
but before the public gist anchor was updated to Rev H.

Filed 2026-09-11. No edits to code or fixtures.
