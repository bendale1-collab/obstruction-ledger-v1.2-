# Former-Names EDGAR Adjudication

**Source:** P0-DELTA-4/5 session (2026-08-16). D-15 rule (token-content-preservation) superseded by EDGAR former-names lookup.

## When to use

Any adjudication step that decides whether two names belong to the same entity, where one name comes from a snapshot/exchange list and the other from an EDGAR CIK. This replaces token-set or token-content-preservation heuristics that over-reject renames (Cenntro Electric Group → Cenntro Inc.) and under-reject absorptions (Cyclacel Pharmaceuticals → GW PHARMACEUTICALS PLC).

## Method

1. Fetch `data.sec.gov/submissions/CIK{n}.json` for each CIK (pad to 10 digits: `cik.zfill(10)`).
2. Build name set: current `"name"` + every entry in `"formerNames"` (each carries `from`/`to` dates).
3. Compare snapshot name against EVERY name in the set whose era covers `snapshot_date ± 90 days`.
4. **Verdict:** SAME-ENTITY iff `token_sort ≥ 95` against any covering name. Else DIFFERENT-ENTITY.

## Normalization pitfalls (identified during P0-DELTA-5)

These were discovered iteratively. Each missing normalization rule caused legitimate same-entity pairs to score < 95:

| Issue | Example | Fix |
|-------|---------|-----|
| Hyphens | `BIO-key` → `BIO KEY` | `re.sub(r'[,\\.;\'\"()\-]', ' ', n)` |
| HTML entities | `&amp;` in Wayback snapshot names | `re.sub(r'&AMP;', '&', n)` BEFORE stripping punctuation |
| Leading "The" | `The Bancorp, Inc.` → `Bancorp, Inc.` | `re.sub(r'^THE\s+', '', n)` |
| Compound suffixes | `ALKALINE WATER CO INC` — after stripping INC, CO remains | Two-pass suffix strip (loop 2x) |
| COMPANY ≠ CO | `Company` vs `Co` | Strip COMPANY alongside CO, CORP, INC, LIMITED, LTD |
| CORPORATION ≠ CORP | `Corporation` vs `CORP` | Strip both CORPORATION and CORP |
| LIMITED ≠ LTD | `Limited` vs `Ltd` | Strip both LIMITED and LTD |
| INCORPORATED ≠ INC | `Incorporated` vs `INC` | Strip both INCORPORATED and INC |

**Canonical suffix set:**
```
INC | CORP | CORPORATION | COMPANY | LLC | LTD | LIMITED | LP | LLP | PLC | NV | SA | AG | AB | OYJ | CO
```

Apply in a loop (2 passes minimum) to handle compound endings like `CO INC`.

## Evidence-column discipline (D-21 fix)

The "301_18mo" column cannot be `Y` without showing `filed_date` and `accession`. These must be read from the **actual EDGAR filing events index** (p0_events.json or equivalent), NOT inferred from a per-CIK cache of "has any 3.01."

Procedure:
```python
def find_best_301(cik_int, snap_date_str):
    """Return the LATEST 3.01 filing in [snap−548d, snap]."""
    sd = parse(snap_date_str)
    ws = sd - timedelta(days=548)
    best = None
    for ev in cik_events[cik_int]:
        if ev matches 3.01 and ws <= ev.date <= sd:
            if best is None or ev.date > best.date: best = ev
    return best  # has .accession and .date

ev = find_best_301(cik_int, snap)
if ev and in_window_548(ev.date, snap):
    row.Y = True; row.accession = ev.accession; row.filed_date = ev.date
else:
    row.Y = False; row.status = "N-UNVERIFIABLE(no evidence)"
```

**Sentinel rows** (two examples named per D-21):
- 2023 BIO-key (CIK 1019034): SAME-ENTITY, Y (accession 0001437749-23-016136, filed 2023-05-30)
- 2024 Anghami (CIK 1810491): DIFFERENT-ENTITY, N-UNVERIFIABLE (no 3.01 in window)

## D-23 Provenance probe

When a CIK assignment is suspected incorrect (e.g. Jupiter/Kairous swap), probe verbatim:
1. Read the cached submissions JSON for the suspect CIK
2. Echo `name` field + `formerNames` array + cache SHA256 as verbatim JSON
3. Compare against the claimed assignment
4. If the JSON confirms the assignment: **REFUTED**
5. If the JSON contradicts: **CONFIRMED** — rebuild CIK column from original delta mapping (token_set run)

## Hash discipline

Hashes must be **shown** (printed as hex), not **asserted**:
```python
# WRONG — asserted without evidence
"input hashes unchanged"

# RIGHT — shown beside expected values
print(f"2015-09-10: {sha256(path)} (DELTA-2 expected: ba75d14...)")
print(f"census: {sha256(path)} (DELTA-2 expected: 786fb61c...)")
print(f"MATCH: {actual == expected}")
```

## Runnable source requirement

Every comparison/adjudication function must be emitted as **runnable code** (a `def` function, not pseudocode), ≤25 lines, as executed. The order explicitly rejected pseudocode date-string comparisons (DELTA-4 defect: "compared date strings to datetime objects — pseudocode; the order required runnable code").

## Key known-answer tests

These must pass before the adjudication is valid:
- Cenntro Electric Group Limited → Cenntro Inc.: **SAME-ENTITY** (via formerName "CENNTRO ELECTRIC GROUP Ltd")
- Cyclacel Pharmaceuticals, Inc. → GW PHARMACEUTICALS PLC: **DIFFERENT-ENTITY** (never that CIK's name)
- Adamis Pharmaceuticals → GW PHARMACEUTICALS PLC: **DIFFERENT-ENTITY**
- BIO-key International, Inc. → BIO KEY INTERNATIONAL INC: **SAME-ENTITY** (hyphen fix required)
- The Bancorp, Inc. → Bancorp, Inc.: **SAME-ENTITY** (leading THE fix required)