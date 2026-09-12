# WRITE-FILE DESTRUCTION — 2026-09-11
# Type: INSTRUMENTATION-DEFECT
# Filed: 2026-09-12

## Discovery

On 2026-09-11, `ledger/verbatim-claim-unverified.md` was destroyed when
`write_file` leaked placeholder content and overwrote the entire file.
Recovered from commit 3d92e6b via `git show`.

The prosecutor skill documents this event at section
"write_file destroys content when placeholder leaks in" (SKILL.md lines 186-195).
Quoted verbatim below:

### Verbatim quote from `research/prosecutor/SKILL.md`

```
### write_file destroys content when placeholder leaks in

When using `write_file` to append to an existing file, if the tool's
auto-generated placeholder content (e.g., "[truncated]") leaks into the
file, it **destroys the original content**. The tool replaces the entire
file, not appends. If you see a truncated placeholder in a write_file
response, immediately check the file with `cat` or `head` and recover
from git history if needed:

git show HEAD~1:<path> > /tmp/recovered.md
# Then re-do the append correctly

Better approach: use `patch` tool for appends, or read the file first,
then use write_file with the full content (original + new). Never trust
that write_file will preserve existing content if you don't provide it
in full. (2026-09-11: verbatim-claim-unverified.md was destroyed when
write_file leaked placeholder; recovered from 3d92e6b.)
```

## Status of the recovered file

`ledger/verbatim-claim-unverified.md` is **reconstructed**, not
continuously appended. Instances filed before the destruction (i.e.,
before the `write_file` overwrite erased them) are recovered text from
git history (3d92e6b), not original append-order witnesses. The
current content at HEAD is the git-recovered version plus whatever
appends followed the recovery.

## Cross-reference: same class as v1.5 RECONSTRUCTED files

The five v1.5 RECONSTRUCTED files share the same structural defect:
the file was destroyed (or never committed) and subsequently
reconstructed from surviving sources. In both cases the current file
is not a continuously-appended original.

The five v1.5 RECONSTRUCTED files (per `ledger/seal-detached-v1.5.md`):

| File | Seal-time status | Source for reconstruction |
|------|------------------|---------------------------|
| ledger/chebyshev-mapping-rejection-2026-09-07.yaml | NEVER committed | .md twin |
| ledger/conv-flag-diagnosis-2026-09-07.yaml | NEVER committed | .md twin |
| ledger/fourier-diff-tolerance-2026-09-07.yaml | NEVER committed | .md twin |
| ledger/misidentification-by-acronym-collision-2026-09-08.yaml | NEVER committed (sealed empty) | v1.5-supersession-report |
| ledger/misidentification-by-acronym-collision.md | NEVER committed (sealed empty) | v1.5-supersession-report |

These files were reconstructed from surviving sources (`.md` twins,
v1.5-supersession-report) and carry the header
`# RECONSTRUCTED 2026-09-09 from <source>; NOT the sealed original.`

The write_file-destroyed verbatim-claim-unverified.md was reconstructed
from git commit 3d92e6b and does NOT carry a RECONSTRUCTED header — this
is an outstanding protocol gap: instrumented recovery from git history
is still a reconstruction of a destroyed original and should be marked
as such.

Both classes share the same finding: **the current file is not a
continuously-appended original. Text filed before the destruction point
is recovered, not primary.**