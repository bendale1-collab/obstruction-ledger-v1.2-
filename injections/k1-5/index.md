# K1-5 — Duplicate hash within manifest: injection index

10 positive (must fire) + 10 negative (must stay silent).
Each fixture is a single .sha256 file in sha256sum format.
Check validates every hash is unique; reports duplicates with paths.

## Positives (must fire)

| Case | Expected | Rationale | Hard-neg |
|------|----------|-----------|----------|
| pos-01 | FINDING | 3 lines, 1 duplicate pair (hash-a ×2 + hash-b ×1); 3 lines / 2 distinct | N |
| pos-02 | FINDING | 3 lines, all same hash (hash-a ×3); 3 lines / 1 distinct | N |
| pos-03 | FINDING | 4 lines, 2 separate duplicate pairs (hash-a ×2 + hash-b ×2); 4 lines / 2 distinct | N |
| pos-04 | FINDING | 4 lines, all same hash (hash-a ×4); 4 lines / 1 distinct | N |
| pos-05 | FINDING | 19-entry manifest mirroring real structure, 1 duplicate pair (hash-dd ×2); 19 lines / 18 distinct | Y |
| pos-06 | FINDING | 5 lines, 1 duplicate pair (hash-a ×2 + 3 unique); 5 lines / 4 distinct | N |
| pos-07 | FINDING | 4 lines with mixed extensions, 1 duplicate pair (hash-a ×2); 4 lines / 3 distinct | N |
| pos-08 | FINDING | 4 lines, 3-way duplicate (hash-a ×3 + hash-b ×1); 4 lines / 2 distinct | N |
| pos-09 | FINDING | 10 lines, 2 separate duplicate pairs; 10 lines / 8 distinct | N |
| pos-10 | FINDING | 2 lines, both same hash; 2 lines / 1 distinct | N |

## Negatives (must stay silent)

| Case | Expected | Rationale | Hard-neg |
|------|----------|-----------|----------|
| neg-01 | SILENT | 19-entry manifest, all unique hashes; 19 lines / 19 distinct | Y |
| neg-02 | SILENT | 5-entry manifest, all unique; 5 lines / 5 distinct | Y |
| neg-03 | SILENT | 1-entry manifest; 1 line / 1 distinct | Y |
| neg-04 | SILENT | 2-entry manifest, different hashes; 2 lines / 2 distinct | Y |
| neg-05 | SILENT | 10-entry manifest, all unique; same format as positives | Y |
| neg-06 | SILENT | Empty file; 0 lines / 0 distinct | N |
| neg-07 | SILENT | Single entry manifest; 1 line / 1 distinct | N |
| neg-08 | SILENT | 3 entries with mixed extensions, all unique | N |
| neg-09 | SILENT | 2 entries with blank line between; all unique | N |
| neg-10 | SILENT | 12-entry manifest, all unique; large but no duplicates | N |

Hard-negative count: 5/10 (neg-01 through neg-05).
