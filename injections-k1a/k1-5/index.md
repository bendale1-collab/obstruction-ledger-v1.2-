# K1-5 Fixtures — Duplicate hash within manifest

Positive fixtures (must fire): 10 cases where MANIFEST.sha256 contains duplicate hashes.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-double-hash | FINDING | One hash at two paths | Y |
| p-triple-duplicate | FINDING | One hash at three paths, plus unique hash | Y |
| p-two-pairs | FINDING | Two distinct hashes, each at two paths | Y |
| p-mixed-duplicates | FINDING | Five hashes, three unique, two pairs duplicated | Y |
| p-all-same | FINDING | All three entries share same hash | Y |
| p-duplicate-at-end | FINDING | Duplicate hash at end of manifest (late detection) | Y |
| p-duplicate-mid | FINDING | Duplicate hash in middle of manifest | Y |
| p-many-unique-one-dup | FINDING | Five unique hashes, then one repeated (sixth entry) | Y |
| p-adjacent-duplicates | FINDING | Duplicate hashes on consecutive lines | Y |
| p-nondeterministic-order | FINDING | Duplicates in non-sorted order (zulu, alpha, alpha) | Y |

Negative fixtures (must stay silent): 3 cases where all hashes in MANIFEST are unique.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-all-unique | SILENT | Five distinct hashes, all unique | N |
| n-long-unique-list | SILENT | Eight distinct hashes in longer manifest | N |
| n-single-file | SILENT | Single entry (trivially unique) | N |

## Properties

**property_all_hashes_unique**: Generates manifest entries where all hashes are distinct. Minimum 250 examples.
- Each manifest entry has unique hash (32 hex chars)
- No duplicates across the set
- Path names are distinct valid identifiers
- At least one entry present

Source incident: MANIFEST.sha256 at 7d4aad7 records 53ca0569… twice (misidentification-by-acronym-collision.md and -2026-09-08.yaml, byte-identical defect from 2026-09-09 reconstruction).
