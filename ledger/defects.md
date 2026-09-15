# Defects

## 2026-09-14

- MARKER-OUT-OF-ORDER — `queue/decided/P0.md` written 2026-09-14T15:35:58Z,
  after Phase C ran; the gate was issued verbally beforehand.
- RESULTS-PREVIEWED-BEFORE-ANCHOR — split A was run before the anchor;
  adjudicator-caused. Recorded in `prereg/K1-five-experiments-v0.2.md`
  under "Amendment — measurement split"; the measurement moved to split B.
- SKILLS-LOCKDOWN-POROUS — `.usage.json` written despite `chmod a-w` on the
  skill trees.
- HYPOTHESIS-DB-PARTIAL-TRACKING — `.hypothesis/` is only partly tracked;
  entries generated after the P0-17 commit remain untracked.
- NO-RUN-START-TIMESTAMP — result files carried no run start or finish time.
  Fixed in B1-01n: `started_at` and `finished_at` required by
  `schemas/result.schema.json` and written by `ol.audit`.
- SEAL-INDEX-NOT-WORKTREE — `scripts/seal_digest.py` hashes blob shas from
  the git index rather than the worktree. No commit B1-01o exists on any
  branch in this repository, so no fix is recorded here.
- INTERPRETATION-AMBIGUITY — the sealed interpretation bands did not state
  whether recall is computed over retained classes only. Adjudicated
  2026-09-14 in `ledger/B1-verdict.md`: retired classes do not count.
  Future pre-registrations must state it.
