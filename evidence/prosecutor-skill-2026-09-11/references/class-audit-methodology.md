# Class-Audit Methodology (pre-execution derivation-path scan)

**Origin:** OL v1.3→v1.4 amendment sweep (2026-09-07) — 9 spec gaps identified in 38 numeric targets.
**Scope:** Any PROSECUTOR study where numeric targets, anchors, or golden values appear in a frozen bundle.

---

## Principle

Before ANY execution phase that uses a numeric target, enumerate EVERY number in the frozen bundle and check whether its derivation path is specified IN-BUNDLE. A value whose computation path is absent is a **spec gap of the same class as the CCF equation gap** — not a softer defect.

## Method

### Step 1 — Enumerate all numeric targets
Collect from:
- SPEC.md §4 (phase deliverables), §14 (open numbers table), and any phase-specific sections
- RUNBOOK.md §3 (phases), §4 (harness register)
- HANDOFF-CHECKLIST.md §5 (SMOKE tests with pass conditions)
- ANCHORS.md (every anchor value — exact, soft, and stated)

### Step 2 — For each, classify
| Category | Mark | Meaning |
|---|---|---|
| Derivation in-bundle | Y | The spec provides the formula, equation, or protocol that produces this number |
| Published value | N | The value is stated as a reference number from an external source, with no in-bundle computation path |
| Soft anchor | N | The value is stated as approximate or soft, with source cited but no derivation |
| Threshold | Y | The number is a pre-registered pass/fail threshold (SPEC §14) — derivation is the spec itself |

### Step 3 — Same-class-gap test
Every `N` is a spec gap of the same class as the CCF equation gap in OL v1.3:
- The value IS used as a target or gate criterion
- The value CANNOT be recomputed from in-bundle information
- The phase that depends on it is either blocked (if the value gates execution) or requires a pre-registered resolution path

### Step 4 — Resolution paths
1. **Patch the spec** (close the gap by adding the derivation path — e.g. adding the governing PDE)
2. **Mark as external constant** (the value is accepted as-is, no recomputation, explicitly named "published value" in the paper)
3. **Defer** (move the dependent phase to a later phase where the derivation path is introduced)

## Output contract

```
value | location | derivation-specified? | source
------|----------|-----------------------|-------
...   | ...      | Y/N                    | ...
N gaps: <count>
list: ...
```

## Reference implementation
OL v1.3 amendment sweep (2026-09-07): 38 values scanned, 9 N gaps.
Output at `amendment-audit-sweep-report-2026-09-07.txt` and `work/class_audit.py` in that repo.