# Closed-Record Discipline — sealed files, closed result docs, replay limits

**Domain:** Obstruction-ledger (ol-run/obstruction-ledger-v1.2) and any pre-registered
research project with a sealed manifest + ledger. Load alongside seal-check-v2.md.

## Durable rules (filed in ledger/standing-rules.md in the active project)

1. **Closed-result-document immutability (rule 8).** Closed result documents
   (e.g. `leg-a-closed-2026-09-09.md`) receive NO edits and NO mid-file insertions
   after seal. Corrections and commentary about them live in the ledger. EOF
   pointers only — an EOF pointer may note that commentary exists elsewhere, but
   the body of the closed record never changes.
2. **Sealed-file append-only regime.** Corrections live at commits after the
   seal commit. The seal certifies the bundle AT the seal commit and nothing
   about HEAD. Seal check v2 is an attestation, not a monitor.
3. **Replay limitation.** A replay from the seal commit (e.g. d7043bba) yields
   the pre-correction copy of files corrected later; the corrections and
   divergence declarations live in unsealed ledger entries (e.g.
   rendering-as-record.md). The sealed bundle alone does NOT reconstruct the
   complete incident record — state this, don't imply replay is a full recovery.
4. **Divergence-report cadence.** The divergence report (seal commit vs HEAD)
   runs at EVERY gate and is a precondition for authorizing compute. Clean or
   fully declared, or no compute. Divergence output must report diff NATURE
   (append / edit / renumber), not just SAME/DIFFERS — a renumbering can hide
   inside a declared diff (K1 candidate 2/3 lesson).

## Divergence-report execution (how to produce the full table)

For each of the 19 manifest paths:

```
for f in $(awk '{print $2}' MANIFEST.sha256); do
  diff_out=$(git diff <seal_commit>..HEAD -- "$f")
  if [ -z "$diff_out" ]; then
    echo "SAME | $f"
  else
    ins=$(echo "$diff_out" | grep -c '^+[^+]')
    del=$(echo "$diff_out" | grep -c '^-[^-]')
    renumber=$(echo "$diff_out" | grep '^[-+]' | grep -cE '^[-+]#+ ')
    echo "DIFFERS | $f | +$ins -$del | renumber_lines=$renumber"
  fi
done
```

Output format: one row per manifest path, four columns:
- `path` — the manifest path
- `status` — SAME or DIFFERS
- `diff nature` — append (insertions only) / edit (insertions+deletions) / renumber (section headers changed) / delete
- `declaring ledger entry` — for every DIFFERS, name the ledger entry that declares it (e.g. `ledger/rendering-as-record.md`)

Count-only output is a failed report. Every row must be present. Gate result:
"clean or fully declared" when all DIFFERS have declaring entries; otherwise
the gate fails.

## Instance taxonomy (classifying closed-record edits)

Classify by CHRONOLOGY vs the moment the append-only rule was declared, not by
the file touched:
- **pre-rule:** committed before the rule existed — not violations.
- **post-rule:** committed after — violations; record, never revert (do-not-revert is the pattern).
- **EOF pointers:** NOT instances (explicitly permitted).
Observed 2026-09-10: two of three real insertions were post-rule; a misclassified
EOF-pointer entry had to be corrected with a classification table.

## Operational pitfalls (obstruction-ledger repo)

- `ledger/` is in `.gitignore` but its files ARE tracked. `git add ledger/x`
  refuses with "ignored by your .gitignore files"; use `git add -f ledger/x`.
  Verify tracked status with `git ls-files --error-unmatch ledger/x`.
- Commit timestamps: use `git log --format='%h %cI %s'` for authoritative dates
  (strict ISO 8601 WITH offset). `%cI` carries the committing machine's LOCAL
  offset — -05:00 in September is CDT (America/Chicago), NOT -04:00 EDT
  (America/New_York). When asked about timezone, report `git config --get
  log.date`, `date +%Z`, and `readlink /etc/localtime`; never change config and
  never silently convert. For UTC conversion do python datetime arithmetic
  (offset is sign-aware hours:minutes), not guesswork — gdate may be absent.