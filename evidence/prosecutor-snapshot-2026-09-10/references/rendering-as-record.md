# RENDERING-AS-RECORD — anchor fidelity

Defect class: a derived, condensed, or paraphrased rendering of an
anchored artifact is presented (or recorded) as if it were the
artifact's verbatim content.

## Rule

Any text presented as the content of an anchored file (gist, gist
revision, manifest file, published hash block) must be either:

  (a) **byte-identical** to the anchor (proven by hash or fetch-diff),
      or
  (b) **explicitly identified as DERIVED** with the source revision
      SHA cited and a note that the text is condensed/paraphrased.

A file that carries the anchor's content without either property is a
RENDERING-AS-RECORD defect.

## Key property

The defect class applies even when mechanical hash checks (manifest
comparison, seal check v2, freeze hash verification) pass correctly.
Prose degradation around hash checks is its own failure mode, not
excused by the checks passing. The founder caught the v1.6-gist-publish
condensed rendering by reading — no automated check existed for it.

## Cross-reference

Structurally related to truncated-diff misread (2026-09-09/10), in
which a diff summary was read as the full file content. In both cases:
  - Mechanical hash checks PASSED
  - Prose surrounding the checks degraded
  - The defect was caught by human reading, not by any automated check

## K1 candidates

- quote-vs-anchor byte check: extract quoted blocks attributed to a
  gist or published hash, fetch raw bytes from the anchor URL at the
  stated revision SHA, diff against quoted text.
- divergence-declaration check: every manifest file that differs
  between seal commit and HEAD must have a declaring ledger entry.
  Undeclared divergence is a finding.