# V0 Kill Test Table (verbatim from terminal)

$ cd /Users/brukendale/ol-run/obstruction-ledger-v1.2 && python3 kill_test.py 2>&1

======================================================================
V0 KILL TEST — ARBITER OVER RB-01..05
======================================================================

──────────────────────────────────────────────────────────────────────
✅ RB-01
  Expected: UNRESOLVED
  Detail:   1 record(s) with no extractions, status UNRESOLVED

──────────────────────────────────────────────────────────────────────
✅ RB-02
  Expected: HALT-REFERENT
  Detail:   extraction disagreement detected:

──────────────────────────────────────────────────────────────────────
✅ (correct miss) RB-03
  Expected: NOT CAUGHT
  Actual:   RESOLVED
  Detail:   test spec passes syntactic check (arbiter has no test-semantic validation in V0)

──────────────────────────────────────────────────────────────────────
✅ (correct miss) RB-04
  Expected: NOT CAUGHT
  Actual:   RESOLVED
  Detail:   test spec passes syntactic check (arbiter has no test-semantic validation in V0)

──────────────────────────────────────────────────────────────────────
✅ RB-05
  Expected: HALT-REFERENT
  Detail:   parity disagreement:

======================================================================
SCORE: 3/3 on RB-01/02/05
✅ V0-GREEN — arbiter caught 3/3 prescribed cases

======================================================================
TERMINAL: V0-GREEN