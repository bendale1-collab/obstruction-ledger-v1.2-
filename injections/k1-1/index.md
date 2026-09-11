# K1-1 — quote-vs-anchor byte match: injection index (Claude-authored)

Fixture convention: a directory per case with anchor.txt (the anchored
text, standing in for the raw gist fetch at a stated revision) and
report.md. A quoted block is a fenced ``` block immediately preceded by a
line beginning `QUOTE-OF: <anchor>`; the block content must equal the
anchor byte-for-byte, trailing newline and line endings included. A
`DERIVED <rev>` line preceding the QUOTE-OF line exempts the block.
`VERBATIM FROM <anchor>` is treated as QUOTE-OF (a claim of verbatim).
Fenced blocks not preceded by a QUOTE-OF/VERBATIM line are not checked.

## Positives (must report MISMATCH)
| Case | Expected | Rationale | Hard |
|---|---|---|---|
| pos-01 | MISMATCH | continuation indentation flattened (Rev D incident) | Y |
| pos-02 | MISMATCH | trailing newline dropped (Rev E incident) | Y |
| pos-03 | MISMATCH | one line omitted (MANIFEST_FILES) | Y |
| pos-04 | MISMATCH | condensed rendering (RENDERING-AS-RECORD incident) | Y |
| pos-05 | MISMATCH | CRLF line endings vs LF anchor | Y |
| pos-06 | MISMATCH | single character changed in GIT_HEAD | Y |
| pos-07 | MISMATCH | extra line appended inside the quote (stray-line incident) | Y |
| pos-08 | MISMATCH | lines reordered, content otherwise identical | Y |
| pos-09 | MISMATCH | double spaces collapsed to single | Y |
| pos-10 | MISMATCH | block matches nothing: claims VERBATIM, anchor revision differs | Y |

## Negatives (must report MATCH or skip)
| Case | Expected | Rationale | Hard |
|---|---|---|---|
| neg-01 | MATCH | exact | Y |
| neg-02 | MATCH | exact, surrounded by noisy prose containing the same tokens | Y |
| neg-03 | DERIVED (skip) | flattened, but DERIVED header present | Y |
| neg-04 | DERIVED (skip) | condensed, but DERIVED header present | Y |
| neg-05 | MATCH ×2 | two exact quotes of the same anchor | Y |
| neg-06 | SILENT | no quoted block | N |
| neg-07 | MATCH | exact including trailing newline | Y |
| neg-08 | MATCH | both sides lack trailing newline | Y |
| neg-09 | MATCH | both sides CRLF | Y |
| neg-10 | MATCH | an unrelated fenced block exists but carries no QUOTE-OF; the quoted one is exact | Y |

Hard-negative count: 9/10.
