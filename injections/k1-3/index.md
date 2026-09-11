# K1-3 — Section-structure stability: injection index

10 positive (must fire) + 10 negative (must stay silent).
Each fixture is a file pair: seal.md (before) and head.md (after).
Check compares header text and numbering between the two.

## Positives (must fire)

| Case | Expected | Rationale | Hard-neg |
|------|----------|-----------|----------|
| pos-01 | FINDING | "## 2.5 Inserted" added between existing ## 2 and ## 3 | N |
| pos-02 | FINDING | "## 2. Beta" removed, gap in numbering | N |
| pos-03 | FINDING | "## 3. Gamma" renumbered to "## 4. Gamma" | N |
| pos-04 | FINDING | "## 2. Beta" changed to "### 2. Beta" (level change) | N |
| pos-05 | FINDING | "## 2. Beta" changed to "## 2. Delta" (text change) | N |
| pos-06 | FINDING | "## 1. New" inserted at top, cascade renumber ## 2→## 3 | N |
| pos-07 | FINDING | "## 3. Gamma" removed from 4-section file | N |
| pos-08 | FINDING | Sub-header "### 1.2" renumbered to "### 1.3" | N |
| pos-09 | FINDING | "## 2. Inserted" added + renumber cascade ## 2→## 3, ## 3→## 4 | N |
| pos-10 | FINDING | "## 3. Gamma" removed and replaced with "## 4. Delta" | N |

## Negatives (must stay silent)

| Case | Expected | Rationale | Hard-neg |
|------|----------|-----------|----------|
| neg-01 | SILENT | "## 3. Gamma" appended after "## 2. Beta"; originals unchanged | Y |
| neg-02 | SILENT | "## 2. Beta" and "## 3. Gamma" both appended after "## 1. Alpha"; originals unchanged | Y |
| neg-03 | SILENT | Prose paragraph added under existing "## 2. Beta"; no header change | Y |
| neg-04 | SILENT | Multiple prose paragraphs added under "## 1. Alpha"; no header change | Y |
| neg-05 | SILENT | seal.md and head.md byte-identical; no diff at all | Y |
| neg-06 | SILENT | Both files empty; no headers to compare | N |
| neg-07 | SILENT | Plain text both sides, no headers at all; prose appended | N |
| neg-08 | SILENT | "# Title" (h1 only) both sides; body text added, no header change | N |
| neg-09 | SILENT | "## 1. Alpha" both sides; code block added under it, not a header | N |
| neg-10 | SILENT | "## 1. Alpha" both sides; horizontal rule and prose added, not a header | N |

Hard-negative count: 5/10 (neg-01 through neg-05).
