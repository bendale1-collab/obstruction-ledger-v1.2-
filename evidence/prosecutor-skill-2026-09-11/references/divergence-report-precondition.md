# Divergence Report as Precondition

**When to use:** Before any seal, freeze, or gate authorization. Standing rule 7: divergence report runs at every gate and is a pre-condition of authorizing compute. Clean or fully declared, or no compute.

## Procedure

1. **Identify base commit and HEAD:**
   ```bash
   BASE=7d4aad7  # or whatever the seal commit is
   HEAD=$(git rev-parse HEAD)
   ```

2. **For each manifest path, diff and classify:**
   ```bash
   for f in $(awk '{print $2}' MANIFEST.sha256); do
     diff_out=$(git diff $BASE..HEAD -- "$f")
     if [ -z "$diff_out" ]; then
       echo "SAME | $f"
     else
       ins=$(echo "$diff_out" | grep -c '^+[^+]')
       del=$(echo "$diff_out" | grep -c '^-[^-]')
       echo "DIFFERS | $f | +$ins -$del"
     fi
   done
   ```

3. **For every DIFFERS, classify nature:**
   - **APPEND:** Only insertions, no deletions; new content added after original EOF
   - **EDIT:** Both insertions and deletions within existing content
   - **RENUMBER:** Section headers changed (## 3 → ## 4); count lines matching `^[-+]#+ `
   - **DELETE:** Only deletions, no insertions

4. **For every DIFFERS, cite a declaring entry:**
   - Must be in a ledger file **outside the diverging file itself**
   - Self-reference is a finding: if `leg-a-closed.md` diverges and the only declaration is in `leg-a-closed.md`, that's undeclared
   - Acceptable: `ledger/rendering-as-record.md` declares changes to `ledger/seal-detached-v1.5.md`
   - Acceptable: `ledger/sealed-file-append-only.md` RULE-IN-CLOSED-RECORD acknowledges insertions into `leg-a-closed.md`

5. **Output format (full table, every row):**

```
path | status | diff nature | declaring entry
---|---|---|---
amendment-log-v1.4.txt | SAME | — | —
anchors/ANCHORS.md | SAME | — | —
...
ledger/seal-detached-v1.5.md | DIFFERS | append | rendering-as-record.md (78d961b); publication-delegation-failed.md (fe8a1e9)
leg-a-closed-2026-09-09.md | DIFFERS | append+renumber+edit | sealed-file-append-only.md RULE-IN-CLOSED-RECORD (26fb687, a8e11c8)
...
```

**Count-only output is a failed report.** Every manifest path must appear as a row.

## Gate result

- **Clean:** All SAME, no DIFFERS
- **Fully declared:** Some DIFFERS, all have declaring entries
- **Undeclared:** Any DIFFERS without a declaring entry → finding, halt

## Example from this project

2026-09-10, 7d4aad7 vs 8541919: 17 SAME, 2 DIFFERS (seal-detached append, leg-a-closed append+renumber+edit). Both fully declared. Gate: clean or fully declared. Compute authorized for K1 run.

## Standing rule cross-reference

`ledger/standing-rules.md` rule 7: "The divergence report runs at every gate and is a pre-condition of authorizing compute. Clean or fully declared, or no compute."
