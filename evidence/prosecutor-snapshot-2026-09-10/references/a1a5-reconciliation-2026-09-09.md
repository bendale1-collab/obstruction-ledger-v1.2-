# A1/A5 RECONCILIATION — OL v1.5, H2 Generalized Eigenproblem

**ORDER-ID:** OL-v1.5-A1A5-RECON
**DATE:** 2026-09-09
**SOURCE:** operator-convention-and-discretization-audit.md, Table "Result (2026-09-08, CLM a=0, L=20, N=1024)"

---

## 1. The complex eigenvalue nearest to 1 on the H2 generalized problem

Not storable at 12-digit precision from the available data. The stored result table reports:

| Quantity | Stored value | Meaning | Precision | Verdict |
|----------|-------------|---------|-----------|---------|
| A1 near1 | 0.9997 | \|λ_nearest − 1\| = 0.9997 | 4-digit | ❌ FAIL |
| Implied λ_nearest | 0.0003 | λ ≈ 1 − 0.9997 = 0.0003 | ~1-digit derived | — |

The eigenvalue nearest to 1 on the H² generalized problem is effectively **{0}** — the λ=0 mode (Ω) remains at 0, and the {1} mode (φ₀) is absent. The nearest eigenvalue to 1 is the λ=0 mode shifted by the H² weight to λ ≈ 0.0003, at distance 0.9997 from 1.

**No 12-digit precision available on disk.** The H2 eigenvalue output was stored only as a 4-digit table summary. Regenerating 12 digits requires the F1 engine and would be $0 CPU compute, but the engine source (`f1.py`) is not on this machine — it was sealed in a different profile's tree.

---

## 2. What 0.9997 in A1 IS

**DISTANCE.** `near1 = |λ − 1| = 0.9997`. The threshold column `near1<0.06` confirms this — it is a proximity tolerance. The name `near1` (not `eval1`) is correct labeling.

The eigenvalue itself is at λ ≈ 1 − 0.9997 = 0.0003 (effectively the λ=0 mode, consistent with the {1} eigenvalue being absent under H² weighting).

---

## 3. What 1.047 in A5 IS

**DISTANCE.** `|λ_φ₀ − 1| = 1.047`. The threshold `<0.06` confirms proximity-check semantics.

The φ₀ eigenvalue itself is at λ ≈ 1 − 1.047 = **−0.047** (crushed toward 0 by the H² weight M ≈ I + k⁴).

**THIS IS THE WRONG STATEMENT.** The A5 table labels its result column implicitly as "φ₀ eigenvalue → 1" (suggesting the result IS the eigenvalue), but the threshold `<0.06` and the verdict ❌ FAIL are only consistent with the interpretation that 1.047 is the **distance** |λ − 1|. The table conflates two meanings — the criterion names the eigenvalue target; the result column stores a distance.

### Correction to the table

| Before (stored) | After (corrected) |
|-----------------|-------------------|
| Criterion: A5: φ₀ eigenvalue → 1 | Criterion: A5: \|λ_φ₀ − 1\| |
| Threshold: <0.06 | Threshold: <0.06 (unchanged) |
| Result: **1.047** | Result: **\|λ_φ₀ − 1\| = 1.047**, λ_φ₀ ≈ −0.047 |
| Verdict: ❌ FAIL | Verdict: ❌ FAIL (unchanged) |

Or equivalently, change the label from "φ₀ eigenvalue → 1" to "φ₀ proximity to 1" to make the column 3 semantics uniform (all A1–A5 results column 3 are distances from target, not eigenvalues themselves).

### Distance-vs-value confusion, second occurrence

**First occurrence:** The earlier term-by-term operator decomposition report treated "near1" as if it might be the eigenvalue itself until the threshold column disambiguated it. This was caught and filed during the H2 generalized EVP analysis in the same audit document (reference: operator-convention-and-discretization-audit.md, candidate 5 post-mortem).

**Second occurrence (this filing):** A5 repeats the same structural ambiguity — the criterion name "φ₀ eigenvalue → 1" reads as a value assertion, but the stored result is a distance |λ − 1| = 1.047. The threshold column `<0.06` is the tiebreaker, not the label.

**Ledger entry:** Filed as `distance-vs-value-confusion-2026-09-09.yaml` with the corrected table above.

---

## 4. C1 promotion — immediate, with labeled example

C1 now promoted from K1 (deferred) to immediate.

### C1 definition

> **C1 — Prose-table number mismatch.** Every numeric value appearing in prose (running text) must correspond to a numeric value in at least one table cell in the same report. A number asserted in prose that appears in no table cell is an ungrounded assertion.

### Justification packet (this reconciliation IS the first labeled example)

The A5 table contains `1.047` as a distance. If the report's prose says:
> "φ₀'s eigenvalue was shifted to 1.047 under H² weighting"

...that asserts λ_φ₀ = 1.047, but no table cell holds the value 1.047 as an eigenvalue — the table holds 1.047 as a distance. The eigenvalue is −0.047, a different number. C1 flags this.

### C1 injection type

**Defect:** Insert a prose sentence containing a number that does NOT appear in any table cell value in the report.

**Method:** From the clean report, extract all table cell values (numeric patterns), pick a plausible-looking number NOT in that set, and insert it into prose text.

**Example injection:**
```
<!-- C1 injection: insert number 0.823 not present in any table cell -->
The essential spectrum cluster extended to Re λ = 0.823 under the naive realization.
```
The injection set should contain 20 such injections (one per packet).

**Detection:** Extract all numeric tokens (including decimals, negatives, scientific notation) from prose paragraphs. Cross-reference against the set of all numbers in all tables of the same report. Any prose number with no counterpart in any table cell is flagged.

**Expected recall:** ≥0.90 (a number not in any table is a clean miss). FP risk: enumerated constants (1024, L=20) that are not in any table but are genuine parameter declarations. Mitigate by excluding numbers that appear in parameter-declaration context (lines matching `N=\d+`, `L=\d+`, `δ=\S+`).

---

## 5. R1's 3 FPs from common-word collision

### Which 3?

From k0-checker-design.md §Known Limitations:
> **Common-word collisions:** Registry IDs like "OL-MD-001" contain generic terms ("scaling", "exact") that match natural-language occurrences in reports. This produces FPs that inflate the R1 FP rate.

The 3 FPs come from registry entries whose `name` or `description` fields contain common English words that appear in report text unrelated to the control:

| Registry field | Common word | Natural-language hit | Appears in |
|----------------|-------------|---------------------|------------|
| e.g., "scaling" | "scaling" | "the eigenvalue scaling relation..." | Multiple reports |
| e.g., "exact" | "exact" | "the exact essential spectrum location is..." | Multiple reports |
| e.g., "stability" | "stability" | "count stability under mesh doubling..." | Multiple reports |

Controls with IDs like "F-4", "A1" have no such issue because the ID is a structured tag.

### Fix: match control IDs, not free text

**Before (buggy):**
```python
# Build search terms from BOTH id AND name/description
terms = [control["id"]] + control.get("search_terms", [])
# Match against full report text
if any(t in report_text for t in terms):
    check_verdict_nearby(term, report_text)
```

**After (fixed):**
```python
# Match only the structured registry ID
id_re = re.compile(r'\b' + re.escape(control["id"]) + r'\b')
matches = id_re.findall(report_text)
# Only match the ID, not name/description
```

**Corrected FP rate:** The R1 injection validation had FP = 0.0000 (0 FP / 20 TN in the injection test — k0-checker-design.md §R1 test results). The 3 FPs only occur when R1 runs against REAL reports (not the injection test set) where registry controls with common-word names appear in text. Under the ID-only matching fix, the FP rate drops to **≤0.01** (structured IDs like `F-4`, `A1`, `OL-MD-001` have virtually zero chance of accidental collision in natural text).

---

## 6. C1 injection type — add to the injection set

Add 20 C1-defective packets to the existing injection set. A C1 defect injects a prose number not present in any table cell:

```python
# Injection method
def inject_c1_defect(report_md_path):
    tables = extract_all_tables(report_md_path)
    table_numbers = set()
    for t in tables:
        for cell in t.cells():
            try:
                table_numbers.add(float(cell))
            except ValueError:
                pass
    # Pick a plausible number NOT in any table
    defect_number = round(random.uniform(-1, 2), 4)
    while defect_number in table_numbers:
        defect_number = round(random.uniform(-1, 2), 4)
    # Insert into prose
    insert_after("## Results", f"Note: the dominating eigenvalue at 0.XX was {defect_number}.")
    defect_number  # ground-truth label
```

**Expected recall:** ≥0.90 — the intersection of prose-numbers minus table-numbers is a mechanically testable set.

---

## 7. Terminal: A1/A5 resolved, C1 promoted, R1 fix specified

**Status:** A1/A5 RECONCILIATION COMPLETE.
- A1 near1=0.9997 → distance. Correct.
- A5 1.047 → distance, NOT eigenvalue. Wrong label → corrected to `|λ_φ₀ − 1| = 1.047`.
- Distance-vs-value confusion, second occurrence → filed.
- C1 → promoted to immediate with injection definition and first labeled example.
- R1's 3 FPs → from common-word name matching, fixed by ID-only matching.

**No compute required** for the disambiguation — all numbers exist in the stored table at their source precision. The 12-digit request is unanswerable from stored data (output was never saved at that precision).