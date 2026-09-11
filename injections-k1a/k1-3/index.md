# K1-3 Fixtures — Section-structure stability

Positive fixtures (must fire): 10 cases where header structure diverges between seal and HEAD.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-header-removed | FINDING | One original header removed; seal had "## Removed" | Y |
| p-header-inserted | FINDING | New header inserted at HEAD that did not exist at seal ("# New header inserted") | Y |
| p-header-renumbered | FINDING | Original "# Demoted" renumbered to "##" at HEAD | Y |
| p-section-three-to-four | FINDING | Original header at level ### renumbered to #### | Y |
| p-deep-header-changed | FINDING | Original "###" renumbered to "####" | Y |
| p-header-text-modified | FINDING | Header text changed (was different phrase at seal) | Y |
| p-headers-and-content | FINDING | Original header modified AND new subsection inserted (§2 violation: not append-only) | Y |
| p-multiple-removed | FINDING | Several original headers removed between seal and HEAD | Y |
| p-case-variant | FINDING | Headers changed case (lowercase at seal, UPPERCASE at HEAD) | Y |
| p-numbering-reset | FINDING | Section numbering pattern restarted ("## One" appears twice in different ## contexts) | Y |

Negative fixtures (must stay silent): 3 cases where header structure is stable (headers unchanged seal to HEAD).

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-identical-unchanged | SILENT | All headers identical to seal; only content changed | Y—same file type and structure as positives, differs only in headers being identical |
| n-append-only-after-final | SILENT | Original headers ("# Section one", "## Subsection", "# Final") unchanged; only appended headers after final | Y—same structure type, appends after final original (§2 permitted), identical headers prove no divergence |
| n-content-modified-headers-same | SILENT | Headers identical to seal ("# Section one", "## Subsection", "# Final"); content text completely changed | Y—same file structure, headers are the difference, headers are identical |

## Properties

**property_no_structure_divergence**: Generates markdown documents with stable header structure (headers identical at seal and HEAD).
- Minimum 250 examples
- All original headers present with identical text and level
- No renumbering, removal, or modification of original headers
- Append-only changes after final original header permitted

All hand-authored positives derived from ledger/leg-a-closed-2026-09-09.md §3/§4 insertion and renumbering incident at 7d4aad7 → 3763bbb.
