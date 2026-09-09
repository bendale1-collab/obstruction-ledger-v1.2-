# Ledger Entry — MISIDENTIFICATION-BY-ACRONYM-COLLISION
# RECONSTRUCTED 2026-09-09 from v1.5-supersession-report-2026-09-07.txt (TASK 2 section)
# NOT the sealed original. File existed only on disk at seal time (never committed; sealed as empty).
# Type: MISIDENTIFICATION-BY-ACRONYM-COLLISION
# Filed: 2026-09-08

The acronym "CCF" was resolved to "Constantin-Lax-Majda" instead of
the correct "Córdoba-Córdoba-Fontelos." Both are:
  - 1D scalar PDEs on ℝ with Hilbert transform nonlocality
  - Describing singularity formation in finite time
  - Adjacent citation neighborhoods in the fluid-singularity literature
  - Both producing self-similar profiles with discrete admissible λ

The identical-if-different-target control (introduced in v1.4:
rejection rationale must be writable without reference to the targets)
PASSED and did not catch this error. As designed, the control tests
for circular justification (target-fitting), not referent resolution.
The error persisted because:
  1. "CCF" resolves to two distinct PDEs in adjacent subfields
  2. Both produce "λ values" (different quantities: one eigenvalue,
     one blow-up scaling rate)
  3. The λ values happen to share similar magnitude ranges (~0.4-1.2)
  4. The ANCHORS value 1.1807776628998 appears in Wang 2509.14185's
     table labeled "CCF Stable" — but that IS the correct CCF stable
     λ, just under the wrong equation attribution

The lambda-provenance sentence deleted from rejection #1 ("the published
lambda values are from CCF literature...") was circular as justification
(for a control that tests self-consistency) but CORRECT as evidence.
Deletion removed the only in-bundle pointer to the correct referent.

GENERALIZED CONTROL (to pre-register):
  Every named equation in the bundle must carry a resolved referent:
  (full author names, year, journal, equation number) verified against
  the primary source, not secondary literature or acronym convention.
  Referent resolution is its own gate, distinct from derivation-path
  verification.

Consequence: this error propagated into v1.4 P1 scope (P1-SCOPE-OK
adjudication voided), the $40/5d cap derivation (scoped for wrong
equation), and all λ anchors (moved to LEG B in v1.5 leg split).