# K1-4 Fixtures — Identifier well-formedness (in-scope, canonical length)

## MEASUREMENTS

file | label preceding | hex length
---|---|---
p-blob-39 | BLOB= | 39
p-commit-6 | commit: | 6
p-commit-8 | commit: | 8
p-freeze-hash-63 | FREEZE_HASH= | 63
p-gist-31 | Gist ID: | 31
p-gist-33 | Gist ID: | 33
p-gist-prefix-14 | Referenced: | 14
p-sha256-31 | SHA256= | 31
p-sha256-63 | (no label) | 63
p-sha256-65 | SHA256= | 65
n-commit-40 | commit: | 40
n-gist-32 | Gist ID: | 32
n-sha256-64 | SHA256= | 64

Positive fixtures (must fire): 10 cases where in-scope identifiers have non-canonical length.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-blob-39 | FINDING | BLOB= label, 39 chars; canonical 40 | Y—same format (label + hex), differs only in length |
| p-commit-6 | FINDING | commit: label, 6 chars; canonical 40 | Y—same context (commit label + hex), differs only in length |
| p-commit-8 | FINDING | commit: label, 8 chars; canonical 40 | Y—same context (commit label + hex), differs only in length |
| p-freeze-hash-63 | FINDING | FREEZE_HASH= label, 63 chars; canonical 64 | Y—same format (label + hex), differs only in length |
| p-gist-31 | FINDING | Gist ID: label, 31 chars; canonical 32 | Y—same context (label + hex), differs only in length |
| p-gist-33 | FINDING | Gist ID: label, 33 chars; canonical 32 | Y—same context (label + hex), differs only in length |
| p-gist-prefix-14 | FINDING | Referenced: label, 14 chars; gist canonical 32 | Y—matches gist ID structure, but incomplete canonical form |
| p-sha256-31 | FINDING | SHA256= label, 31 chars; canonical 64 | Y—same label context, differs only in length |
| p-sha256-63 | FINDING | SHA label, 63 chars; canonical 64 | Y—same SHA format, differs only in length |
| p-sha256-65 | FINDING | SHA256= label, 65 chars; canonical 64 | Y—same format (label + hex), differs only in length |

Negative fixtures (must stay silent): 3 cases where in-scope identifiers are canonical length.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-commit-40 | SILENT | commit: label, exactly 40 hex chars (full form) | Y—same commit context and hex format, correct canonical length |
| n-gist-32 | SILENT | Gist ID: label, exactly 32 hex chars | Y—same label and hex format, correct canonical length |
| n-sha256-64 | SILENT | SHA256= label, exactly 64 hex chars | Y—same label and hex format, correct canonical length |

## Properties

**property_canonical_gist_id_32**: Generates 32-character hex strings following Gist ID: labels only.
- Minimum 250 examples
- All characters [0-9a-f]
- Exactly 32 characters
- No embedded labels

**property_canonical_sha40**: Generates 40-character hex strings following commit labels or GIT_HEAD= tags.
- Minimum 250 examples
- All characters [0-9a-f]
- Exactly 40 characters (full form)
- No length variants

**property_canonical_sha64**: Generates 64-character hex strings following SHA256=, BLOB=, or unlabeled SHA occurrences.
- Minimum 250 examples
- All characters [0-9a-f]
- Exactly 64 characters
- No length variants

**property_canonical_sha7_short_form**: Generates 7-character hex strings following commit labels (short form).
- Minimum 100 examples
- All characters [0-9a-f]
- Exactly 7 characters
- No full-form variants

All hand-authored positives from sealed bundle incidents: work/r8-grep-2026-09-10.txt (v1.6 publication), SEAL-PACKET.md, 7d4aad7 anchors/ANCHORS.md and MANIFEST.sha256 blob identifiers.
