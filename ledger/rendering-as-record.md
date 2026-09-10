# Ledger Entry — RENDERING-AS-RECORD
# Type: RENDERING-AS-RECORD
# Filed: 2026-09-10

A derived, condensed rendering of an anchored artifact was presented
(and partially recorded) as if it were the anchor's content.

## Instance 1: gist publish text (2026-09-10)

The file `v1.6-gist-publish.txt` was composed as a condensed summary
of the gist `ol-freeze-hashes.txt`, interleaving revision metadata
from the GitHub API. It was delivered as text for the founder to
publish. It was NOT a verbatim fetch of the gist, nor was it
identified as DERIVED.

Differences between the composed block and the published gist:
- v1.5 block: omitted `TIMESTAMP=2026-09-08T12:30:00Z`, `Published:
  2026-09-08T12:58:00Z`, and the `First hash... externally anchored`
  claim line
- v1.5 timestamps replaced with `GitHub revision:` (SHA @ UTC)
- v1.6 block: omitted `Seal check v2: 19/19 PASS`, full composition
  parenthetical, `Published: 2026-09-10T03:11Z`, and the UTC/local NOTE
- v1.6 timestamps replaced with `GitHub revision:` (SHA @ UTC)

## Instance 2: external-anchor record in seal-detached.md (2026-09-10)

The revision history table appended to `ledger/seal-detached-v1.5.md`
under the publication message records only SHAs and UTC timestamps as
a condensed table. It does not contain the verbatim gist text. A
correction has been appended: the full verbatim text now follows.

## Cross-reference: frontier-tier instance

The RENDERING-AS-RECORD pattern is structurally related to the
truncated-diff misread already filed (2026-09-09/10), in which a
diff summary was read as the full file content. In both cases:
  1. Mechanical hash checks (V1-class, seal check v2, MANIFEST
     verification) PASSED — the hash comparison tools worked
     correctly.
  2. Prose surrounding the hash checks degraded — a condensed or
     truncated rendering replaced the verbatim artifact.
  3. The defect was caught by human reading, not by any automated
     check.

## Resolution (this file)

The defect is recorded, not retroactively corrected. The gist is
already published. The seal-detached.md entry now carries both
the condensed table (original) and the verbatim gist text
(correction). The v1.6-gist-publish.txt file is available on
disk as evidence of the composed block.