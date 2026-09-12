# Resolution controls — referent verification and class audit

## Referent resolution (pre-registered control — derived from CCF↔CLM acronym collision)

Every named equation, constant, model, or object in a frozen bundle MUST carry a
resolved referent:

  Full author names · Year · Journal · Equation number

Verified against the PRIMARY SOURCE, not against secondary literature or
acronym convention.

### Rationale

The acronym "CCF" resolved to "Constantin-Lax-Majda" in a prior session
instead of the correct "Córdoba-Córdoba-Fontelos." Both are 1D Hilbert-transform
fluid surrogates in adjacent citation neighborhoods. The identical-if-different-target
control (below) could not catch this because it tests circular justification,
not referent resolution.

### Execution

When a named equation enters the spec:
1. Identify the canonical primary source (usually the first paper that named
   the equation).
2. Open the primary source (PDF via arXiv or journal).
3. Extract the governing PDE, not the surrounding prose description. If only
   the abstract is accessible, note the limitation and tag the equation
   REFERENT-PARTIAL.
4. Quote the equation text verbatim from the source, with equation number.
5. Confirm the equation matches the spec's usage. If it does not, the spec
   usage is either (a) misidentified or (b) a different convention. File
   as MISIDENTIFICATION or CONVENTION-IMPLICIT.

### Acronym collision risk

Risk factors for acronym collision:
- Same domain (fluid PDEs, singularity formation, numerical methods)
- Same mathematical signature (Hilbert transform, scalar 1D, nonlocal)
- Adjacent citation neighborhoods in the literature
- Named after different authors sharing initials (CCF = CLM in this case)

When an acronym has known collisions, the spec must state the full name and the
collision it resolves.

### Tagging

- REFERENT-VERIFIED — checked against primary source, equation confirmed
- REFERENT-PARTIAL — only abstract/meta available; equation assumed
- MISIDENTIFIED — wrong equation was attributed to the name

---

## Class audit — derivation-path verification

Every numeric target, anchor, or golden value in a frozen spec must be
audited for its derivation path.

### Execution

For each numeric value in the spec (including §14 tables, RUNBOOK thresholds,
ANCHORS constants, and test tolerances):

1. Can the value be computed from the governing equations in the bundle?
   → Y = DERIVABLE
   → N = ASSERTED-UNDERIVABLE (has a source but no in-bundle derivation path)
   → N + no source cited = ASSERTED-UNSOURCED

2. Depth: does the source itself explain the derivation, or just state the number?
   - Paper-derived: paper states the value and its method → ASSERTED-UNDERIVABLE
   - Paper approximate: paper gives ≈ value → extend beyond paper precision → ASSERTED-UNDERIVABLE
   - No source: no primary source named → ASSERTED-UNSOURCED

3. Mark each tag in the spec or anchors file. Never silently fix them.

### Tags

Tag         | Meaning                                    | Action
------------|--------------------------------------------|-------------------------
DERIVABLE   | In-bundle equation can compute it         | Engine must reproduce it
ASSERTED-UNDERIVABLE | Source exists but no in-bundle path | Report as limitation
ASSERTED-UNSOURCED   | No source cited                  | Report as gap; can block

---

## Identical-if-different-target test

A rejection rationale (why alternative X is rejected) MUST be writable
verbatim-identical had the acceptance targets been different numbers.

### Purpose

Detects circular justification: "we rejected X because its published λ
values are from Y literature" consults the very targets the rationale
is supposed to be independent of.

### Execution

1. Write the rejection rationale.
2. Replace every numeric acceptance target with a different number.
3. If the rationale still holds (it was about family hierarchy, equation
   structure, or naming convention, not about specific numbers), it passes.
4. If the rationale mentions the targets themselves, rewrite to remove
   the target reference or escalate.

Separates two failure modes the same test:
- TARGET-FITTING (rationale depends on the specific numbers) → fails test
- REFERENT-MISRESOLUTION (wrong equation identified) → passes test;
  caught by referent-resolution control, not by this test

Document which control failed when filing the defect.