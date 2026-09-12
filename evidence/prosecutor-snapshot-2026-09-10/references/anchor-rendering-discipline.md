# Anchor Rendering Discipline — DERIVED vs VERBATIM

**Domain:** Any report or ledger entry that quotes or summarizes an anchored
artifact (gist, published hash, manifest file, GitHub revision).

**Rule:** Any text presented as the content of an anchored file must be either:
(a) **byte-identical** to the anchor (proven by hash or diff), OR
(b) **explicitly identified as DERIVED** with the source revision SHA cited
    and a note that the text is condensed/paraphrased.

A file that carries the anchor's content without either property is a
**RENDERING-AS-RECORD** defect.

## Two failure modes

| Mode | Detection | Example |
|------|-----------|---------|
| Condensed-as-verbatim | Partial gist content in a report, missing lines, dropped `Published:` stamps | v1.6-gist-publish.txt — omitted "Seal check v2: 19/19 PASS", full composition line, timestamps replaced with `GitHub revision:` |
| Table-as-record | SHAs and timestamps extracted to a table, full gist text omitted | seal-detached-v1.5.md — revision table without the actual freeze-hash content |

## Correction pattern (from 2026-09-10)

When a RENDERING-AS-RECORD is discovered:
1. File the defect as a ledger entry (type RENDERING-AS-RECORD).
2. Append a correction with the verbatim text, noting the original was
   condensed.
3. Do NOT replace the original — it is evidence.
4. Note the cross-reference: mechanical hash checks (V1-class) pass while
   surrounding prose degrades unchecked.

## K1 candidate

Quote-vs-anchor byte check (to be pre-registered): extract all quoted blocks
attributed to a gist or published hash, fetch raw text from the anchor URL
at the stated revision SHA, diff against the quoted text. Flag any difference
as VERBATIM-MISMATCH.