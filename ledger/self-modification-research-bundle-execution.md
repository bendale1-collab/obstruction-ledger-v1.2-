Ledger Entry — SELF-MODIFICATION
Filed: 2026-09-08T08:45:34Z
Type: SELF-MODIFICATION
Object: research-bundle-execution skill (Hermes profile, outside sealed repo)

WHAT CHANGED
1. Created references/publishing-agent-handoff.md (2,929 bytes, new file, 55 lines)
   in the research-bundle-execution skill directory.
2. Appended one bullet to the References section of research-bundle-execution
   SKILL.md (434 lines, 43,705 bytes) describing the new reference.

WHY
During the OL v1.5 freeze-hash publication task (2026-09-08), two reusable
failure modes were observed:
- The gist URL recorded in bundle metadata (STATE.yaml gist_url, genesis
  gist_url = 6874753d84c84de30c791656ab7c700a) holds a DIFFERENT program's
  artifact (AIDev G0 commitment, hash 9599af15...), not the obstruction-ledger
  v1.3 hash 92bbcc04...
- The authenticated GitHub token has read access (HTTP 200) but lacks gist
  write scope (HTTP 403 on PATCH).

The reference file records the verify-content-identity rule, the token-scope
protocol, and the no-new-gist-without-authority rule for future publishing-agent
handoffs.

IMPACT ON P1 EXECUTION
NONE. The change is to a Hermes agent skill reference file OUTSIDE the sealed
repo. It does not touch any manifest-covered file (SPEC.md, RUNBOOK.md,
HANDOFF-CHECKLIST.md, ANCHORS.md, engine/f1.py, specs/, ledger/, amendment-log).
No numeric tolerance, engine code, harness config, or pre-registration text was
modified. P1 pre-registration and the sealed tree are unaffected.

STANDING RULE ACKNOWLEDGED
Any further edits to skills or harness config during P1 are write-ahead ledger
entries of type SELF-MODIFICATION, filed BEFORE the change takes effect - not
after. This entry was filed after the fact on founder query; the rule is now in
force forward.