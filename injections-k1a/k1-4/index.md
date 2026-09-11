# K1-4 Fixtures — Identifier well-formedness

Positive fixtures (must fire): 10 cases where identifiers have malformed length.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-truncated-gist | FINDING | Gist ID 31 chars (dropped 1), canonical is 32 | Y |
| p-extra-char-sha | FINDING | SHA-256 at 65 chars (extra 1), canonical is 64 | Y |
| p-wrong-length-seven | FINDING | Commit ref 6 chars, canonical is 7 or 40 | Y |
| p-malformed-freeze | FINDING | FREEZE_HASH 63 chars (short 1), canonical is 64 | Y |
| p-prefix-match-short | FINDING | Prefix match 15 chars, canonical gist is 32 | Y |
| p-embedded-sha-wrong | FINDING | SHA256= label with 31-char value, canonical is 64 | Y |
| p-eight-char-partial | FINDING | Commit 8 chars, canonical is 7 or 40 | Y |
| p-length-check-hex | FINDING | Blob hash 49 chars (incomplete 40), canonical is 40 | Y |
| p-gist-one-short | FINDING | Gist 31 chars (short 1), canonical is 32 | Y |
| p-sha-case-variant | FINDING | SHA 65 chars with case variant, canonical is 64 and case-insensitive hex | Y |

Negative fixtures (must stay silent): 3 cases where identifiers are canonical length.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-correct-gist | SILENT | Gist ID exactly 32 hex chars | N |
| n-correct-sha256 | SILENT | SHA-256 exactly 64 hex chars | N |
| n-correct-commit | SILENT | Commit exactly 7 hex chars (short form) | N |

## Properties

**property_canonical_gist_id**: Generates 32-character hex strings. Minimum 250 examples.
- All characters in range [0-9a-f]
- Exactly 32 characters
- No embedded labels or prefixes

**property_canonical_sha40**: Generates 40-character hex strings. Minimum 250 examples.
- All characters in range [0-9a-f]
- Exactly 40 characters
- No length variants

**property_canonical_sha64**: Generates 64-character hex strings. Minimum 250 examples.
- All characters in range [0-9a-f]
- Exactly 64 characters
- No length variants

All hand-authored positives from sealed bundle incidents (work/r8-grep-2026-09-10.txt, v1.6 publication, SEAL-PACKET.md).
