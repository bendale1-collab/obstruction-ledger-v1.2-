# Mechanical Grep-Report Contract

**When to use:** Founder gives a frozen list of sections + exact commands (pickaxe,
git grep, tracked/untracked, plain grep) and demands raw output written to a file,
with an exact 2-3 line reply and "nothing else."

## Section-completeness rule

Every section header in the spec must end in EITHER data rows OR the literal
placeholder word the spec names (`NONE`, `PICKAXE ZERO (label)`, etc.). A header
with nothing under it is a failed report — never leave a section silently empty.
If a command legitimately returns zero hits, write the exact placeholder text
given in the spec, not a paraphrase ("no results found").

## Tracked vs untracked classification

`grep -rn <pattern> . --exclude-dir=.git` walks the whole working tree, including
files git has never seen. Classify every hit:

```
git ls-files --error-unmatch <path>   # exit 0 + prints path => tracked
                                       # exit 1 "did not match any file(s)" => untracked
```

Do this per-path, not per-repo — a working tree commonly has both tracked and
untracked files matching the same pattern (e.g. a corrected value lives in a
tracked file while a stray audit-note draft with the old truncated value sits
untracked). Report both, labelled.

### Untracked is not the whole story — check .gitignore before calling something "untracked"

Plain `git status --porcelain` only lists tracked-modified (` M`) and
untracked-not-ignored (`??`) entries. A path that matches a `.gitignore` rule
(e.g. a directory rule like `ledger/`) is SILENTLY OMITTED from that default
output — it will not show as `??` and it will not show as tracked. Before
reporting a file as "untracked" or asserting it's absent from porcelain output,
run `git check-ignore -v <path>` on it. If it returns a matching rule (exit 0),
the correct classification is **ignored**, not untracked, and it only appears
under `git status --porcelain --ignored` as `!!`. Conflating "not in default
porcelain" with "does not exist" or "untracked" is a live error class — a
founder asking "why doesn't X show in git status" is often hitting a
`.gitignore` rule, not a git bug.

### Verify exact filenames before running ls-files / check-ignore

A spec-given filename may not match the actual file on disk verbatim (e.g. spec
says `ledger/anchor-gap-v1.3.yaml`, actual file on disk is
`ledger/anchor-gap-v1.3-2026-09-08.yaml`). Always `ls` or `search_files` the
directory first to confirm the exact name before running `git ls-files
--error-unmatch` or `git check-ignore` — a typo'd path returns a clean "did not
match any files" which looks identical to a real untracked/ignored result but
means something different (the path is simply wrong, not a git state fact).

## Pickaxe + per-commit grep (recap, canonical form)

```
git log -S <PATTERN> --all --format='%h %cI %s'      # commits that touch PATTERN
for c in <hashes>; do
  git grep -n <PATTERN> $c                            # occurrences AT that commit
done
```

`%cI` is the committer-date ISO-8601 (already includes the UTC offset) — no
manual timezone math needed for this format string, unlike the plain `%ai` used
elsewhere (see `k1-pre-registration-assembly.md` for the `%ai`→UTC conversion
when the format string doesn't carry `I`).

Run the SAME two-step procedure separately for a truncated substring and its
full canonical form when both are in play (e.g. a 31-char vs 32-char ID) — a
substring pickaxe hit does not tell you which length variant fired, only that
the count of some occurrence changed. Only the per-commit `git grep` disambiguates.

### `git check-ignore` silently skips already-tracked files — use `--no-index` for "was this force-added" questions

Plain `git check-ignore -v <path>` (or `-q`) returns **exit 1, no output** for any
path git already has in its index, even when a `.gitignore` rule would match it.
This looks identical to "not ignored" but means something different: the file
*is* matched by an ignore rule and was only ever added via `git add -f`. Do not
conclude "tracked, therefore not ignored" from a bare `check-ignore` exit code.

To classify a file as **tracked / ignored / BOTH** correctly:

```
git ls-files --error-unmatch <path>        # exit 0 => tracked
git check-ignore -v --no-index <path>      # exit 0 + rule shown => matched by an ignore rule,
                                            #   regardless of tracked status (bypasses the skip)
```

A file that is both tracked AND matched by an ignore rule is **BOTH** — it was
force-added past the ignore at some point. This is common in ledger-style repos
where a blanket directory rule (`ledger/`) is deliberately overridden per-file
for sealed/committed entries while sibling scratch files in the same directory
stay genuinely ignored.

### Detecting force-adds past `.gitignore`

To confirm a tracked file was force-added rather than added before the ignore
rule existed:

```
git log --diff-filter=A --format='%h %cI' -- <path>   # the add-commit
git show <add-commit>:.gitignore                       # .gitignore content AT that commit
```

If the ignore rule was already present in `.gitignore` at the add-commit, the
add was necessarily a `git add -f` (or equivalent force-stage). Do this per-file
when the founder asks "was file X force-added past the ignore" — don't infer it
from the current `.gitignore` alone, since the rule could have been added later.

## Anchor-registry negative check

When a section asks "does anchor file X record canonical ID Y," running
`grep -rn "gist" anchors/*.md` and getting unrelated hits (e.g. matches on the
substring "digits") is NOT evidence of recording — verify by eye that none of
the returned lines contain the actual ID substring, then write the spec's
exact ANCHOR-UNRECORDED (or equivalent) placeholder. Do not infer "found" from
a keyword match on an unrelated word.

## Exact-reply-contract override

When the task specifies the literal reply format ("Reply with exactly two lines:
FILE: <path> LINES: <n>", "print the file path and its line count. Nothing
else."), that literal template is the entire reply. This overrides the general
"attach as MEDIA + one-line verdict" habit from `telegram-delivery-format.md` —
do not attach the file, do not add a verdict line, do not add commentary. Count
lines with `wc -l` on the actual written file and report that number, not an
estimate.

## Duplicate-content hash confirmation (manifest dedup check)

When two manifest entries share an identical hash and the founder asks to
"confirm" the duplicate: run `sha256sum` on both files on disk AND on both
files at the specific commit named (`git show <commit>:<path> | sha256sum`).
Report all four hashes plus `head -N` of each at that commit — do not just
assert "they match," show the four independent computations so the founder can
verify without re-running anything. A reconstructed-file duplicate (two paths,
one content, because a `.md` and a `.yaml` sibling were filed from the same
source) is a legitimate manifest state, not a bug — the report's job is to
confirm the byte-identity mechanically, not to judge whether it should exist.

## Founder-stated expected counts are a check, not a target

When the spec says "N expected" (e.g. "Fourteen expected") for an enumeration,
run the enumeration independently (two ways if possible — e.g. `git status
--porcelain --ignored | grep '^!!'` AND a `find` + per-file `git ls-files`
walk) and report the actual measured count even when it disagrees with the
stated expectation. Do not pad, drop, or reclassify an item to make the count
match. State the discrepancy plainly (e.g. "13 found, not 14 expected — both
enumeration methods agree") and move on. The founder's stated number is a
sanity check for THEM to catch a bad enumeration, not a target for the report
to hit.

## Blocked-item pattern (founder says "I will place files" but they don't exist yet)

When a multi-item task includes "commit both unchanged" for files the founder
says they will place but haven't yet, and you check and the files are absent:
report BLOCKED for that item and proceed with the remaining items. Do not
fabricate, do not wait, do not skip silently. The blocked item gets a one-line
"BLOCKED — file not found at <path>" and the rest of the task executes normally.

## Full duplicate-hash scan (not just confirming a known pair)

To find EVERY duplicate hash in a manifest, not just confirm one already
suspected pair:

```
awk '{print $1}' MANIFEST.sha256 | sort | uniq -d      # any hash appearing >1×
for h in $(awk '{print $1}' MANIFEST.sha256 | sort | uniq -d); do
  grep "^$h" MANIFEST.sha256                            # show all paths sharing it
done
```

Report `NONE` if `uniq -d` returns nothing. This generalizes the
duplicate-content confirmation above (which assumes the pair is already known)
to an open-ended "are there others" question.

## YAML/JSON parse-check at a specific commit

When asked whether files at a given commit are valid YAML/JSON despite a
`.yaml`/`.json` extension:

```
git show <commit>:<path> | python3 -c "import sys,yaml; yaml.safe_load(sys.stdin)"
git show <commit>:<path> | python3 -c "import sys,json; json.load(sys.stdin)"
```

Report the command and exit code per file — do not infer parseability from
the extension alone. A `.yaml`-named file can be plain commented prose (e.g. a
ledger entry with a `#`-comment header) that fails `yaml.safe_load` with a
`ScannerError`; the extension is a naming convention in this project, not a
format guarantee. Only one of several `.yaml` manifest entries may actually be
structured YAML — check each independently.

## Recovery-narrative verification (not just hash confirmation)

When a reconstructed/recovered file claims a specific recovery source (e.g. a
header comment "RECONSTRUCTED from <source>"), verify the claim against the
literal source text, not just the resulting hash:

1. `grep -n "<specific-claim-string>" <claimed-source-file>` — confirm the
   source actually contains what the header claims it was reconstructed from
   (e.g. does the source mention the specific filename, or only prose content
   that was later given a filename during reconstruction).
2. `git log --all --format='%h %cI %s' -- <path>` — walk the FULL commit
   history for that exact path to confirm no earlier, different-content
   version ever existed. A single add-commit with no prior history supports
   "never existed before this reconstruction"; report the commit list, don't
   assert from memory.
3. If the recovery narrative references an intermediate commit by message
   only (e.g. a commit message mentioning the ledger entry type before the
   file was reconstructed), inspect that commit's diff directly
   (`git show <commit> -- '<path-glob>'`) to confirm it did NOT touch the
   path in question — a commit message mentioning a topic is not evidence the
   commit touched the specific file being audited.

## Source

r8-grep report, 2026-09-10: gist-ID truncation forensics (5 sections: truncated-ID
history, full-ID history, working-tree grep w/ tracked flag, anchor-registry
negative check, environment snapshot). Read-only task, single output file,
exact 2-line reply contract.

r10/r11 follow-on audits, 2026-09-10: .gitignore full-file enumeration,
tracked/ignored/BOTH classification via --no-index, force-add detection,
duplicate-hash confirmation and full-scan, YAML/JSON parse-checking at a
commit, and recovery-narrative verification against claimed source text.

## Zero-match search: report the gap, do not expand

When a founder-specified phrase or section name returns zero matches across
all tracked files (`git grep -n "<exact phrase>" -- $(git ls-files)` returns
nothing), report "not found in any tracked file" and stop. Do not escalate
to broader variants, untracked files, or regex relaxations in the same turn
unless the founder explicitly asks for a broader search. A 5-turn escalating
search that ends at "not found" is a failed interaction — the user has to
watch the agent fail repeatedly instead of getting a quick answer. The correct
response to zero matches is one line stating the gap, then ask the founder to
clarify the target.

## Verbatim verification: `diff` is not byte comparison

When comparing two text sources for "verbatim" identity, `diff` on extracted
text compares logical lines (newline-delimited). It is blind to:
- Continuation-line indentation changes (e.g., mobile editor flattening whitespace)
- Trailing whitespace on lines
- Line-ending differences (LF vs CRLF)
- Leading/trailing blank lines at file boundaries

For a true "verbatim" claim, use byte-level comparison:
```
sha256sum <file1> <file2>            # compare hash of entire files
# or for a section extracted from a larger file:
<extract section> | sha256sum        # hash the exact bytes
```
A `diff` exit 0 proves content-match, not verbatim-match. Any report that
claims "verbatim" or "no reflow" based solely on `diff` should be retracted
to "content-match only; whitespace not verified" until byte comparison confirms.
