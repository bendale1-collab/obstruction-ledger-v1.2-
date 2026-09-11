# K1-5 Fixtures — Duplicate hash within manifest

Positive fixtures (must fire): 10 cases where MANIFEST.sha256 contains duplicate hashes (sha256 format: 64-char hex).

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-two-paths-same-hash | FINDING | One hash at two paths; other hashes unique | Y—same manifest format and structure, differs only in hash uniqueness |
| p-triple-dup-one-hash | FINDING | One hash at three paths; others unique | Y—same format (hash + path pairs), differs only in having a triplicate |
| p-two-duplicate-pairs | FINDING | Two distinct hashes, each appearing twice | Y—same structure, differs only in duplicate count |
| p-mix-of-duplicates | FINDING | Five hashes with two pairs duplicated | Y—same manifest format, differs only in having duplicates |
| p-all-three-same | FINDING | All entries share identical hash | Y—same structure (hash + path), differs only in all being identical |
| p-dup-at-manifest-end | FINDING | Duplicate hash at end of list (late detection) | Y—same format, differs only in duplicate position |
| p-dup-mid-manifest | FINDING | Duplicate hash in middle of manifest | Y—same structure, differs only in duplicate location |
| p-many-unique-then-dup | FINDING | Five unique hashes, then one repeated in sixth entry | Y—same manifest format, differs only in final entry duplicating an earlier hash |
| p-consecutive-dups | FINDING | Duplicate hashes on adjacent lines | Y—same format (hash + path pairs), differs only in adjacency |
| p-unsorted-dupes | FINDING | Duplicates in non-sorted order (z, a, a) | Y—same manifest structure, differs only in duplicate positions not sorted |

Negative fixtures (must stay silent): 3 cases where all hashes in MANIFEST are unique (sha256 format).

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-five-all-unique | SILENT | Five distinct hashes, all unique; manifest structure identical to positives | Y—same manifest file type and format (hash + path), differs only in all hashes being unique |
| n-eight-distinct-hashes | SILENT | Eight distinct hashes in longer manifest; structure same as positives | Y—same format (hash + path pairs), differs only in all hashes being distinct across longer set |
| n-single-entry | SILENT | Single manifest entry (trivially unique); structure same type as positives | Y—same format (hash + path), differs only in having no duplicates possible |

## Properties

**property_all_hashes_distinct**: Generates manifest entries (MANIFEST.sha256 format) where all hashes are unique.
- Minimum 250 examples
- Each hash exactly 64-character hex string (sha256sum format)
- All hashes unique across entries
- All paths unique
- At least one entry

Source incident: MANIFEST.sha256 at 7d4aad7 contains byte-identical defect: 53ca0569… appears twice (misidentification-by-acronym-collision.md and -2026-09-08.yaml), defect from 2026-09-09 reconstruction.
