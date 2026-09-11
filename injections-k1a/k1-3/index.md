# K1-3 Fixtures — Section-structure stability

Positive fixtures (must fire): 10 cases where header structure diverges between seal and HEAD.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-header-removed | FINDING | Original header removed at HEAD | Y |
| p-header-inserted | FINDING | New header inserted after seal headers | Y |
| p-header-renumbered | FINDING | Headers renumbered (## became #, ### remained) | Y |
| p-section-three-to-four | FINDING | Header jumped from level to level (### to ####) | Y |
| p-deep-header-changed | FINDING | Subsection renumbered deeper (### to ####) | Y |
| p-header-text-modified | FINDING | Header text content changed | Y |
| p-inserted-after-last | FINDING | New header appended after final original header (violates §2 rule) | Y |
| p-multiple-headers-removed | FINDING | Several headers removed between seal and HEAD | Y |
| p-header-case-changed | FINDING | Header case altered (lowercase to UPPERCASE) | Y |
| p-numbering-reset | FINDING | Section numbering restarted (## One, then # Second, then ## One again) | Y |

Negative fixtures (must stay silent): 3 cases where header structure is stable.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-identical-structure | SILENT | Same header structure seal to HEAD, content only changes | N |
| n-append-only | SILENT | Original headers unchanged, new headers appended only after final | N |
| n-content-only-change | SILENT | Header lines identical, body content modified | N |

## Properties

**property_no_structure_divergence**: Generates markdown with stable header structure. Minimum 200 examples.
- Headers present at seal remain at HEAD with identical text and level
- No renumbering, removal, or modification of original headers
- Append-only changes after final original header permitted
- Markdown must be well-formed UTF-8

All hand-authored positives trace to ledger/leg-a-closed-2026-09-09.md §3/§4 insertion and renumbering incident.
