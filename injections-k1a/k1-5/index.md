# K1-5 Fixtures — Duplicate hash within manifest

## MEASUREMENTS

file | line count | unique hash count
---|---|---
p-all-three-same | 3 | 1
p-consecutive-dups | 3 | 2
p-dup-at-manifest-end | 4 | 3
p-dup-mid-manifest | 4 | 3
p-many-unique-then-dup | 6 | 5
p-mix-of-duplicates | 5 | 3
p-triple-dup-one-hash | 4 | 2
p-two-duplicate-pairs | 4 | 2
p-two-paths-same-hash | 3 | 2
p-unsorted-dupes | 3 | 2
n-eight-distinct-hashes | 8 | 8
n-five-all-unique | 5 | 5
n-single-entry | 1 | 1

Positive fixtures (must fire): 10 cases where MANIFEST.sha256 contains duplicate hashes (sha256 format: 64-char hex).

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-all-three-same | FINDING | 3 lines, 1 unique hash (all entries identical) | Y—same manifest format and structure, differs only in hash uniqueness |
| p-consecutive-dups | FINDING | 3 lines, 2 unique hashes (duplicates adjacent) | Y—same format (hash + path pairs), differs only in adjacency |
| p-dup-at-manifest-end | FINDING | 4 lines, 3 unique hashes (duplicate at end) | Y—same format, differs only in duplicate position |
| p-dup-mid-manifest | FINDING | 4 lines, 3 unique hashes (duplicate in middle) | Y—same structure, differs only in duplicate location |
| p-many-unique-then-dup | FINDING | 6 lines, 5 unique hashes (final entry duplicates earlier) | Y—same manifest format, differs only in final entry duplicating an earlier hash |
| p-mix-of-duplicates | FINDING | 5 lines, 3 unique hashes (two pairs duplicated) | Y—same manifest format, differs only in having duplicates |
| p-triple-dup-one-hash | FINDING | 4 lines, 2 unique hashes (one hash at three paths) | Y—same format (hash + path pairs), differs only in having a triplicate |
| p-two-duplicate-pairs | FINDING | 4 lines, 2 unique hashes (two distinct hashes, each twice) | Y—same structure, differs only in duplicate count |
| p-two-paths-same-hash | FINDING | 3 lines, 2 unique hashes (one hash at two paths) | Y—same manifest format and structure, differs only in hash uniqueness |
| p-unsorted-dupes | FINDING | 3 lines, 2 unique hashes (duplicates in non-sorted order) | Y—same manifest structure, differs only in duplicate positions not sorted |

Negative fixtures (must stay silent): 3 cases where all hashes in MANIFEST are unique (sha256 format).

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-eight-distinct-hashes | SILENT | 8 lines, 8 unique hashes; structure same as positives | Y—same format (hash + path pairs), differs only in all hashes being distinct across longer set |
| n-five-all-unique | SILENT | 5 lines, 5 unique hashes; manifest structure identical to positives | Y—same manifest file type and format (hash + path), differs only in all hashes being unique |
| n-single-entry | SILENT | 1 line, 1 unique hash (trivially unique); structure same type as positives | Y—same format (hash + path), differs only in having no duplicates possible |

## Properties

**property_all_hashes_distinct**: Generates manifest entries (MANIFEST.sha256 format) where all hashes are unique.
- Minimum 250 examples
- Each hash exactly 64-character hex string (sha256sum format)
- All hashes unique across entries
- All paths unique
- At least one entry

Source incident: MANIFEST.sha256 at 7d4aad7 contains byte-identical defect: 53ca0569… appears twice (misidentification-by-acronym-collision.md and -2026-09-08.yaml), defect from 2026-09-09 reconstruction.
