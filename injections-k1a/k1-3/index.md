# K1-3 Fixtures — Section-structure stability

Positive fixtures (must fire): 10 cases where header structure diverges between seal and HEAD.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-case-variant | FINDING | Case changed (lowercase at seal → UPPERCASE at HEAD) | Y |
| p-deep-header-changed | FINDING | Level increased (### → ####) | Y |
| p-header-inserted | FINDING | New header inserted (# New header inserted, did not exist at seal) | Y |
| p-header-removed | FINDING | One header removed (was: ## Removed before p-header-removed) | Y |
| p-header-renumbered | FINDING | Original # renamed to ## (# Demoted → ## Demoted) | Y |
| p-header-text-modified | FINDING | Text content changed (different phrase at seal) | Y |
| p-headers-and-content | FINDING | Original header modified + new subsection inserted | Y |
| p-multiple-removed | FINDING | Multiple headers removed | Y |
| p-numbering-reset | FINDING | Numbering restarted (## One appears twice) | Y |
| p-section-three-to-four | FINDING | Level increased (### → ####) | Y |

Negative fixtures (must stay silent): 3 cases where header structure is stable.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-append-only-after-final | SILENT | Original headers unchanged; appended after final original header only (§2 permitted) | Y—same markdown structure type, differs only in headers being identical |
| n-content-modified-headers-same | SILENT | Headers identical to seal; header moves position in file but text and level unchanged | Y—same structure type, differs only in headers being identical (position change is not level/text change) |
| n-identical-unchanged | SILENT | All headers identical to seal; only content changed | Y—same file structure, differs only in headers being identical |

## Properties

**property_no_structure_divergence**: Generates markdown documents where header structure is stable (headers identical at seal and HEAD).
- Minimum 250 examples
- All original headers present with identical text and level
- No renumbering, removal, or modification of original headers
- Append-only changes after final original header permitted per §2

All hand-authored positives derived from ledger/leg-a-closed-2026-09-09.md §3/§4 insertion and renumbering incident at 7d4aad7 → 3763bbb.
