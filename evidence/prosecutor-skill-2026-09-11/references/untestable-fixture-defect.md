# UNTESTABLE-FIXTURE-DEFECT

**Verdict type:** Fixture structure does not match check interface.

## Definition

When a check requires multiple inputs (e.g. before/after pairs) but the sealed
fixture set contains only single files with no derived state, the fixtures are
structurally untestable. Score all affected injection rows as
**UNTESTABLE-FIXTURE-DEFECT** — not PASS, not FAIL, not SKIP.

## Pattern

- Check interface: `check(before_file, after_file, before_commit, after_commit)`
- Fixture set: single `.md` files, no before state, no paired directories
- Harness cannot invoke the check without fabricating the missing state
- Fabricating state = fixture author writing code = split-authorship breach

## Filing procedure

Document in `ledger/<check>-fixture-defect.md`:

1. **Defect type:** Injection defect (§4)
2. **Check interface:** what the check requires
3. **Sealed fixture set:** what exists (file count, layout, structure)
4. **Consequence:** no valid invocation exists
5. **Authorship:** who wrote fixtures, who wrote harness patches
6. **Verdict:** UNTESTABLE-FIXTURE-DEFECT for all affected rows
7. **Remaining evaluation surface:** real commits (R5/R6/R7), holdout row
8. **Harness update:** emit `{"verdict": "UNTESTABLE-FIXTURE-DEFECT", "fixture": "<path>"}` with exit -1; test function skips with reason

## Harness implementation

```python
elif stem == "k1-3":
    # K1-3 fixtures are single files; the check needs before/after pairs.
    # No before state exists in the sealed set.
    return [{"verdict": "UNTESTABLE-FIXTURE-DEFECT", "fixture": str(fixture_path)}], -1
```

In the test function:

```python
if findings and isinstance(findings, list) and len(findings) == 1:
    if isinstance(findings[0], dict) and findings[0].get("verdict") == "UNTESTABLE-FIXTURE-DEFECT":
        pytest.skip("UNTESTABLE-FIXTURE-DEFECT (see ledger/k1a-k1-3-fixture-defect.md)")
```

## Example (2026-09-11 K1a K1-3)

All 13 K1-3 injection fixtures were single `.md` files in `positive/` and
`negative/` subdirectories. The check `k1_3.py` requires four arguments:
`before_file after_file before_commit after_commit`.

The 591d638 harness patch attempted to work around this:
- Negatives: `before = after` (identical file, no header change)
- Positives: returned `k1-3-positive-needs-pair` error

This patch was **withdrawn as a scoring path** because it was written by the
fixture author (mahamara session 20260911_124250_f1624c). The fixture author
writing the harness patch is the same contamination class as the fixture
author modifying code under test.

Filed in `ledger/k1a-k1-3-fixture-defect.md`. K1-3 still evaluated on:
- R5, R6, R7 (real commits in repository history)
- Seven-row holdout (authored by no code author, unseen by any)

## Missing properties.py

When `properties.py` is absent from a check directory, the negative-space
property was not delivered. This is a delivery defect, separate from the
fixture-structure defect. Report both in the same filing or in a completeness
audit.

**Example (2026-09-11 K1a):** k1-3 and k1-6 had no `properties.py`. Both
checks missing the §2-mandated negative-space property generator (minimum
200 examples). Reported in fixture-defect filings.

## Key principle

**The fixture author cannot fix their own defect.** A harness patch written
by the fixture author to work around the fixture author's structural defect
is not a valid scoring path. The defect must be filed, the rows scored as
UNTESTABLE, and evaluation deferred to uncontaminated surfaces (real commits,
holdout).
