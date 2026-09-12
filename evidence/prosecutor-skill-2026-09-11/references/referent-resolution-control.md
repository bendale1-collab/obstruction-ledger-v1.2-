# Referent-Resolution Control (v1.5 OL, 2026-09-08)

## When to use

Every named equation, theorem, model, or technical term in a research bundle must carry a resolved referent: full author names, year, journal, equation number, verified against the primary source, not secondary literature or acronym convention.

Use this control whenever:
- The bundle uses acronyms for equations, theorems, or models (CCF, CLM, gCLM, OSW, LSS, etc.)
- A single acronym could resolve to multiple distinct entities in adjacent subfields
- The identical-if-different-target test (circular-justification check) has already passed — referent resolution tests a DIFFERENT failure class
- A citation or reference is being removed from one role (e.g. justification)

## Protocol

1. **Enumerate all named equations/terms** in every spec file (SPEC.md, RUNBOOK.md, ANCHORS.md, CHECKLIST.md).
2. **Resolve each to its primary source:** full author names, year, journal, equation number.
3. **Verify against the primary source** — do not accept secondary literature, later reviews, or convention knowledge. Read the actual paper.
4. **Check for acronym collision:** is there more than one entity with the same acronym? (CCF = Constantin-Lax-Majda AND Córdoba-Córdoba-Fontelos are two different equations.) If yes, flag HIGH.
5. **Record verification status:** VERIFIED / REFERENT-UNVERIFIED / REFERENT-OUT-OF-SCOPE.
6. **Gate:** Missing or unverified referent → RED on referent audit, do not freeze.

## Failure class distinction

Referent-resolution control tests a DIFFERENT failure class from the identical-if-different-target control:

| Control | Tests | Failure class | Example failure |
|---------|-------|---------------|-----------------|
| Identical-if-different-target | Can a rejection rationale be written without reference to the target? | Circular justification | "λ from CCF literature" as sole rationale |
| Referent-resolution | Does every named equation map to the correct primary source? | Referent identity | CCF = Constantin-Lax-Majda (wrong) vs Córdoba-Córdoba-Fontelos (correct) |

**Neither substitutes for the other.** A spec that passes identical-if-different-target may still have misidentified referents, and a spec with correct referents may still have circular justifications.

## The "Demote, never delete" principle

A citation may be invalid as justification while decisive as evidence. When a piece of evidence fails ONE control, move it to a different role rather than removing it entirely.

**Real example (OL v1.4→v1.5):**
- The lambda-provenance sentence "the published lambda values are from CCF literature" was deleted from rejection #1 because it was circular justification (it referenced the target λ values in a test meant to be self-consistent).
- But that sentence was the ONLY in-bundle pointer to the correct CCF referent (Córdoba-Córdoba-Fontelos, not Constantin-Lax-Majda).
- Correct handling: demote it from "justification" to "evidence" — keep it as a referent pointer in ANCHORS.md or a control-audit table, even though it no longer serves as a rejection rationale.

**Generalized rule:** Before removing a citation or piece of evidence from the bundle, ask:
1. Does it fail the control it currently serves? → Potentially remove from that role.
2. Does it still serve a DIFFERENT control? → Keep it in the bundle in a different role.
3. Is it the ONLY pointer to a correct referent? → Never remove — assign a new role.

**Operational implementation:** When a citation is removed from a justification or rejection rationale, file it in EVIDENCE-ONLY table in ANCHORS.md or a dedicated references file, with a note stating what role it failed and what role it retains.

## Acronym-collision hazard

Acronyms that resolve to multiple entities in adjacent subfields are a high-severity defect carrier. The risk profile:

- **Same magnitude range + same domain:** Two entities produce quantities with similar names (both "λ values") and similar magnitude (~0.4–1.2), but the quantities mean different things (eigenvalues vs blow-up scaling rates). The error persists because the numbers look plausible.
- **Both are cited in the same paper's bibliography:** The paper mentions both CCF (Córdoba-Córdoba-Fontelos as the studied equation) and CLM (as a related model). A reader who resolves "CCF" to "Constantin-Lax-Majda" will find supporting citations.
- **Correcting the referent changes the numerical problem entirely:** Eigenvalue computation vs self-similar PDE continuation are different numerical tasks requiring different engines.

**Detection pattern:** For every acronym in the bundle, ask: is there another entity with the same string in any subfield that appears in the paper's bibliography? If yes, tag the referent as HIGH ACRONYM-RISK and verify against the primary source.

## Related: Precision-verification referents

The same referent-discipline applies to numerical values stated as "from paper X." Every value must carry:
- The exact precision stated in the source (e.g., "13 digits from 2509.14185 table, line 194")
- Any value that exceeds source-stated precision → UNSOURCED-PRECISION (file separately, don't silently truncate)
- Any prose/table conflict within a single source → UNRESOLVED-SOURCE-DISCREPANCY (do not assert a resolution without evidence)
- Any subset of published targets without documented exclusion → SELECTION-UNRECORDED (silent subsetting is its own defect class)