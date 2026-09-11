# K1-2 — divergence-declaration: injection index (Claude-authored)

Fixture convention (git-free): a directory per case with seal/ (files at
the seal commit), head/ (files at HEAD), MANIFEST (one sealed path per
line), and head/ledger/*.md as the candidate declaring entries. A
declaring entry is any head/ledger/*.md file, other than the diverging
path itself, whose text contains the diverging path string. The check
must also run in git mode (seal commit vs HEAD); these fixtures exercise
the logic, not git.

Output rule per sealed §2: full per-path table; SAME or DIFFERS with
nature APPEND / EDIT / RENUMBER / DELETE; every DIFFERS must cite a
declaring entry outside the diverging file. Undeclared divergence or
self-only declaration is a finding.

## Positives (must fire)
| Case | Expected | Rationale | Hard |
|---|---|---|---|
| pos-01 | FINDING a.md APPEND undeclared | no ledger entry | Y |
| pos-02 | FINDING a.md EDIT undeclared | no ledger entry | Y |
| pos-03 | FINDING a.md APPEND self-declared only | declaration is inside a.md | Y |
| pos-04 | FINDING a.md DELETE undeclared | path in manifest, absent at head | Y |
| pos-05 | FINDING b.md APPEND undeclared | a.md declared, b.md not | Y |
| pos-06 | FINDING a.md RENUMBER undeclared | header renumbered, no entry | Y |
| pos-07 | FINDING a.md APPEND undeclared | ledger entry names c.md, not a.md | Y |
| pos-08 | FINDING a.md APPEND undeclared | mention exists but not under ledger/ | Y |
| pos-09 | FINDING ledger/l.md APPEND self-declared only | sealed ledger file declares itself | Y |
| pos-10 | FINDING a.md APPEND undeclared | ledger entry names no path | Y |

## Negatives (must stay silent)
| Case | Expected | Rationale | Hard |
|---|---|---|---|
| neg-01 | SILENT (2 SAME) | no divergence | Y |
| neg-02 | SILENT (a.md DIFFERS/APPEND declared) | ledger/decl.md names a.md | Y |
| neg-03 | SILENT (a.md DIFFERS/EDIT declared) | | Y |
| neg-04 | SILENT (a.md DIFFERS/RENUMBER declared) | | Y |
| neg-05 | SILENT (a.md DIFFERS/DELETE declared) | | Y |
| neg-06 | SILENT (two DIFFERS, both declared) | one entry names both | Y |
| neg-07 | SILENT (ledger/l.md DIFFERS declared by ledger/other.md) | declaration outside the diverging file | Y |
| neg-08 | SILENT (2 SAME) | unsealed file added at head; out of scope | Y |
| neg-09 | SILENT (1 SAME) | single-file manifest | N |
| neg-10 | SILENT (a.md declared) | an unrelated ledger file also present | Y |

Hard-negative count: 9/10.
Note: nature classification correctness is not a finding under the sealed
spec; K1-3 covers renumber detection. pos-06/neg-04 test that RENUMBER is
reported, not that misclassification fires.
