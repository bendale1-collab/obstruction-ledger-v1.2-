# K1a Gate Procedure (G0–G4)

## G0 — Import Smoke Test

**Command:**
```bash
uv run --python 3.11 python -c "
import importlib.util, glob
for f in sorted(glob.glob('work/k1a/*.py')):
    s = importlib.util.spec_from_file_location('m', f)
    m = importlib.util.module_from_spec(s)
    try:
        s.loader.exec_module(m)
        print(f, 'IMPORT-OK')
    except Exception as e:
        print(f, 'IMPORT-FAIL', type(e).__name__, e)
"
```

**Expected:** 7/7 IMPORT-OK

**Then empty-input invocation:**
```bash
for f in work/k1a/*.py; do
  uv run --python 3.11 python "$f"
  echo "exit: $?"
done
```

**Expected:** 7/7 emit `[]` exit 0

**Failure mode (Agent B, 2026-09-11):** k1_3..k1_6 exit 1 with `{"error": "Usage: ..."}` instead of `[]` exit 0. They require positional arguments and fail when none are provided rather than returning an empty result set. This is a code defect, not an import failure.

**Fix pattern (rev 2):** Add early-return branch at top of `main()`:
```python
if len(sys.argv) < 2:
    json.dump([], sys.stdout)
    sys.exit(0)
```
Place BEFORE any `len(sys.argv) != N` check. The empty-input branch produces `[]` exit 0; the argument-count branch produces error object exit 1.

**Halt condition:** Any IMPORT-FAIL halts K1a before the run; the failure is filed and K1a does not proceed that day. Empty-input failures are filed but do not halt (they are code defects, not import defects).

## G1 — Static Syntax (ruff FA,UP)

**Command:**
```bash
uvx ruff check --select FA,UP work/k1a/
```

**Expected:** All checks passed!

**Halt condition:** Any finding halts K1a; the failure is filed and K1a does not proceed that day.

## G2 — pytest collect-only

**Command:**
```bash
uv run --python 3.11 pytest work/k1a-test.py --collect-only -q
```

**Expected:** All 7 checks listed in the collection output.

**Halt condition:** Any missing check halts K1a; the failure is filed and K1a does not proceed that day.

## G3 — Clean Tree

**Command:**
```bash
git status --porcelain | grep -E "^ M|^M " | wc -l
```

**Expected:** 0 (no modified tracked files)

**Halt condition:** Any modified tracked file halts K1a; the failure is filed and K1a does not proceed that day.

## G4 — Divergence Report

**Command:**
```bash
# For each manifest path, diff seal-commit vs HEAD
# Report SAME or DIFFERS with nature = APPEND / EDIT / RENUMBER / DELETE
# Every DIFFERS must cite a declaring ledger entry outside the diverging file
```

**Expected:** Clean or fully declared (every DIFFERS has a declaring ledger entry).

**Halt condition:** Any undeclared divergence halts K1a; the failure is filed and K1a does not proceed that day.

## Gate Output Publication

All five gate outputs are published with the run, pass or fail. Committed as `work/k1a-gates-2026-09-11.txt` (or similar).

## Pitfalls

### Gate must be run fresh, not cited from prior gate output

When a gate (especially G4) is specified as "7d4aad7 vs HEAD", the
comparison must be **executed** against the current HEAD — not cited
from a previous gate output file. A prior G4 may have compared against
a different HEAD (e.g. an earlier commit in the same session). Citing
the prior output instead of running the comparison is the same class
of defect as citing a stale measurement: the gate did not run.

**Violation example (2026-09-11):** The ace2daf commit included a G4
output (work/r41-g4-divergence-7d4aad7-vs-591d638-2026-09-11.txt) that
cited the prior gate output instead of running the comparison against
HEAD=ace2daf. The f2eaf8a commit re-ran G4 and recorded both files —
the stale one preserved in history, the fresh one as the authoritative
gate output.

**Rule:** Each gate invocation runs the comparison fresh. Prior gate
outputs are historical artifacts, not current results.

### No conditional gate outcomes

A gate either PASSes or FAILs. There is no "CONDITIONAL PASS" or
"PASS pending commit" outcome in the spec (§3.1). If a gate cannot
pass (e.g. modified tracked files exist), it FAILs — commit the
artifacts and re-run.

**Violation example (2026-09-11):** G3 reported "CONDITIONAL PASS
(1 modified tracked = harness, pending commit)" at line 117 of
work/k1a-gates-2026-09-11.txt. §3.1 has no conditional outcome.
Recorded in ledger/k1a-k1-3-fixture-defect.md as a procedure defect,
not corrected by editing the gates file (which is a committed artifact).

## Reference

See `work/k1a-gates-2026-09-11.txt` for the 2026-09-11 run output.
