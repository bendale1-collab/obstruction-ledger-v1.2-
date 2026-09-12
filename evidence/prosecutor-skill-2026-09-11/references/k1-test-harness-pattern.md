# K1 Test Harness Pattern

**When to use:** Running the K1 check suite against injection fixtures and retrodiction corpus after both code commits are in.

## Output contract (three sections, in order)

1. **INJECTION TABLE** — one row per fixture: `check | case | expected | got | PASS/FAIL`. All 140 cases. No summary substitutes for the table.
2. **Per-check recall and false-positive rate** — for each check: `recall=X/Y (X/Y), FPR=Z/Y (Z/Y false positives)`.
3. **RETRODICTION TABLE** — 14 rows R1–R14 from §3: `row | check | expected | got | PASS/FAIL`. All 14 rows.

A count-only report is a failed report.

## Two-harness split (K1a pattern, 2026-09-12)

When the run includes both injection testing and retrodiction against
real commits, split into two harness files to isolate failure domains:

- **`work/k1a_run.py`** — injection fixtures + properties.py hypothesis tests.
  Reads `injections-k1a/` only. Outputs JSON (machine-readable) and TXT
  (human-readable). Commit message: `"K1a RUN (injections + properties):
  harness by Claude, executed by operator. Verdicts unadjudicated."`

- **`work/k1a_retro.py`** — retrodiction rows R1–R14 + RA-1..RA-5.
  Reads real commits via `git show` and real files. Does NOT touch
  `injections-k1a/`. Commit message: `"K1a RETRODICTION (R1-R14, RA-1..RA-5):
  harness by Claude, executed by operator. Verdicts unadjudicated."`

Each harness is placed at repo root by Cowork, sha256sum-verified by
operator, moved to `work/`, then run. Neither harness is edited by the
operator — if a hash mismatch occurs, stop.

**Execution order:** injections first (k1a_run.py), then retrodiction
(k1a_retro.py). Holdout is NOT run — it has not been revealed.

## Harness structure

```python
# Two harness files (injections + retrodiction split)
# work/k1a_run.py — imports each check as a subprocess, runs against fixtures
# work/k1a_retro.py — runs retrodiction rows against real commits
# Neither is edited by the operator
```

## Key patterns

### Index.md parsing

Extract `(case, expected)` pairs from the markdown tables in each check's `index.md`. The expected column contains values like `FINDING`, `SILENT`, `MATCH`, `MISMATCH`, `DERIVED (skip)`, or qualified forms like `FINDING a.md APPEND undeclared` or `SILENT (2 SAME)`.

### Evaluation logic

- **FINDING expected** → check returned non-empty JSON array → PASS
- **SILENT expected** → check returned empty array `[]` → PASS
- **MATCH expected** → check returned findings with `status: MATCH` → PASS
- **MISMATCH expected** → check returned findings with `status: MISMATCH` → PASS
- **DERIVED expected** → check returned findings with `status: DERIVED` or no findings (block skipped) → PASS
- **Error** → check crashed or returned non-JSON → record error as result, continue

### Checks without code

If Agent B hasn't written K1-3 through K1-6 code yet, those retrodiction rows return `NO_CODE` as the verdict. This is not a failure — it's a pre-stated dependency. Report it explicitly.

### Fixture-structure gaps → UNTESTABLE-FIXTURE-DEFECT

When a check's CLI interface doesn't match the fixture layout (e.g.,
check needs 4 args but fixtures are single files), the harness must
emit **UNTESTABLE-FIXTURE-DEFECT** for all affected injection cases.

**Do NOT attempt workarounds** such as:
- Negatives as before=after (the fixture author writing the workaround
  is the same contamination as the fixture author modifying code)
- Positives as "needs-pair" errors (skipping is not scoring)

The fixture author cannot fix their own defect. The harness must
report the defect, not mask it. Score all affected rows as
UNTESTABLE-FIXTURE-DEFECT — not PASS, not FAIL, not SKIP.

```python
elif stem == "k1-3":
    return [{"verdict": "UNTESTABLE-FIXTURE-DEFECT", "fixture": str(fixture_path)}], -1
```

In the test function, skip with reason (not assertion failure):

```python
if findings and isinstance(findings, list) and len(findings) == 1:
    if isinstance(findings[0], dict) and findings[0].get("verdict") == "UNTESTABLE-FIXTURE-DEFECT":
        pytest.skip("UNTESTABLE-FIXTURE-DEFECT (see ledger/<check>-fixture-defect.md)")
```

File the defect in `ledger/<check>-fixture-defect.md` and evaluate
the check on uncontaminated surfaces (real commits, holdout row).
See `references/untestable-fixture-defect.md` for full procedure.

(2026-09-11 K1a: the initial harness attempted before=after for
negatives and skip-with-error for positives. This was withdrawn as a
scoring path because the harness author was the fixture author.
Corrected to UNTESTABLE-FIXTURE-DEFECT at ace2daf.)

### Retrodiction rows requiring git commits

Some rows (R2, R3, R4) require extracting files at specific commits via `git show <commit>:<path>`. Write to a temp file, run the check, delete the temp file. If the commit doesn't exist in the current repo, record as ERROR.

### Retrodiction rows requiring specific files

Some rows (R10, R11) require finding specific files by name pattern. If the file doesn't exist at the expected location, record as MISSING.

## Execution

```bash
python3 work/k1-test.py > work/k1-run-public-YYYY-MM-DD.txt 2>&1
git add work/k1-test.py work/k1-run-public-YYYY-MM-DD.txt
git commit -m "K1-RUN: public rows — harness + injection/retrodiction output"
```

## properties.py collection and hypothesis tests

Each check directory may contain a `properties.py` file declaring
negative-space properties (generators of inputs that must NEVER produce
a finding, minimum 200 examples per property). The harness must collect
and run these.

### Harness pattern

```python
def discover_properties(check_stem: str) -> Path | None:
    """Find properties.py for a check. Returns path or None."""
    fixture_dir_name = check_stem.replace("_", "-")
    prop_file = FIXTURE_ROOT / fixture_dir_name / "properties.py"
    return prop_file if prop_file.is_file() else None

def pytest_generate_tests(metafunc):
    if "properties_file" in metafunc.fixturenames:
        params = []
        for check_path in discover_checks():
            stem = check_path.stem
            prop = discover_properties(stem)
            if prop:
                params.append(pytest.param(
                    (check_path, prop),
                    id=f"{stem}::properties"
                ))
            else:
                params.append(pytest.param(
                    (check_path, None),
                    id=f"{stem}::no-properties"
                ))
        metafunc.parametrize("properties_file", params)

def test_properties(properties_file):
    check_path, prop_path = properties_file
    if prop_path is None:
        pytest.skip(f"{check_path.stem} has no properties.py")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(prop_path), "-v", "--tb=short"],
        capture_output=True, text=True, timeout=60, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"properties.py produced finding(s).\n"
        f"Check: {check_path.name}\n"
        f"Stdout:\n{result.stdout}\nStderr:\n{result.stderr}"
    )
```

### Completeness check

Verify properties.py exists for each check directory:

```bash
for d in c1 k1-1 k1-2 k1-3 k1-4 k1-5 k1-6; do
  count=$(find "injections-k1a/$d" -name 'properties.py' -type f | wc -l)
  echo "$d: $count"
done
```

**Missing properties.py is a delivery defect.** The negative-space
property is part of the §2 specification; its absence means the check
cannot be evaluated on the property dimension. Report in fixture-defect
filings or completeness audit.

**Example (2026-09-11 K1a):** k1-3 and k1-6 had no properties.py.
Both checks missing the §2-mandated negative-space property generator.
Harness collects 7 property tests (5 present, 2 skip with "no-properties").

## Adjudication

The harness reports results; the founder adjudicates. Common adjudication branches:

- **Injection defect** — fixture is malformed (e.g., expected FINDING but check correctly returns SILENT because the fixture doesn't contain the claimed defect)
- **Code defect** — check has a bug (e.g., expected SILENT but check fires on a valid case)
- **Spec ambiguity** — check definition is unclear (e.g., K1-4 `hash:` label scope, filed in standing rules pre-code)

Never silently re-run. Never edit the expected outcome to match the result.

## Example from this project

K1-RUN public rows at `d00f75f` (2026-09-10):
- 60 injection cases run (C1: 20, K1-1: 20, K1-2: 20)
- C1: 9/10 positives PASS, 1/10 negatives PASS (9 false positives — C1 code defect, fires on all numbers in file not just row-label-linked pairs)
- K1-1: 0/20 run (all ERROR — Python 3.9 `str | None` syntax crash, code defect)
- K1-2: 0/20 run (all ERROR — same Python 3.9 crash)
- K1-3 through K1-6: NO_CODE (Agent B not yet committed)
- Retrodiction: R11 PASS (C1 silent on K0 H2), R2–R4 ERROR (K1-1/K1-2 crash), R5–R9/R12–R14 NO_CODE
- Founder adjudication pending on C1 false-positive rate and K1-1/K1-2 syntax errors
