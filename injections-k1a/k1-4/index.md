# K1-4 Fixtures — Identifier well-formedness (in-scope, canonical length)

Positive fixtures (must fire): 10 cases where in-scope identifiers have non-canonical length.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-gist-truncated-one-short | FINDING | Gist ID after label, 31 chars; canonical 32 | Y—same context (label + hex string), differs only in length |
| p-sha256-extra-one-char | FINDING | SHA after label, 65 chars; canonical 64 | Y—same format (label + hex), differs only in length |
| p-commit-six-chars-short | FINDING | commit label, 6 chars; canonical 7 or 40 | Y—same context (commit label + hex), differs only in length |
| p-freeze-hash-one-short | FINDING | FREEZE_HASH= label, 63 chars; canonical 64 | Y—same format (label + hex), differs only in length |
| p-prefix-gist-incomplete | FINDING | Prefix of known gist, 15 chars; canonical 32 | Y—matches gist ID structure, but incomplete canonical form |
| p-label-embedded-wrong-length | FINDING | SHA256= label with 31-char value; canonical 64 | Y—same label context, differs only in length |
| p-commit-eight-invalid | FINDING | commit label, 8 chars; canonical 7 or 40 | Y—same context (commit label + hex), differs only in length |
| p-blob-incomplete-forty | FINDING | Blob hash 49 chars; within 40-char canonical form range but incomplete | Y—hex string format, wrong length for canonical 40 |
| p-gist-exactly-short | FINDING | Gist ID, 31 chars; canonical 32 | Y—same gist context, one char short of canonical |
| p-sha-wrong-length-fiftyfive | FINDING | SHA label, 65 chars; canonical 64 | Y—same SHA format, differs only in length |

Negative fixtures (must stay silent): 3 cases where in-scope identifiers are canonical length.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-canonical-gist-32 | SILENT | Gist ID with label, exactly 32 hex chars | Y—same label and hex format, correct canonical length |
| n-canonical-sha256-64 | SILENT | SHA with label, exactly 64 hex chars | Y—same label and hex format, correct canonical length |
| n-canonical-commit-40 | SILENT | commit label, exactly 40 hex chars (full form) | Y—same commit context and hex format, correct canonical length |

## Properties

**property_canonical_gist_id_32**: Generates 32-character hex strings following Gist ID labels (Gist ID:, FREEZE_HASH=).
- Minimum 250 examples
- All characters [0-9a-f]
- Exactly 32 characters
- No embedded labels

**property_canonical_sha40**: Generates 40-character hex strings following commit labels or GIT_HEAD= tags.
- Minimum 250 examples
- All characters [0-9a-f]
- Exactly 40 characters (full form)
- No length variants

**property_canonical_sha64**: Generates 64-character hex strings following SHA256=, FREEZE_HASH=, or BLOB= labels.
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
