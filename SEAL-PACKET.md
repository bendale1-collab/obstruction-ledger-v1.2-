# SEAL PACKET — v1.6

## TIMELINE
- v1.0: CCF PDE closure (boot)
- v1.4: gCLM a=0, Elgindi-Jeong corroboration
- v1.5: Leg split, CCF misidentification corrected, engine seal
- v1.5 (DETACHED): P1 ENGINE-RED, K0, H2 realization test, fork adjudication
- **v1.6: SEAL RECOVERED** — obstruction typed with JSON provenance, A1/A5 reconciliation, C1 promoted, output-precision policy, seal-detached entry

## v1.6 CONTENTS (19 files)
- amendment-log-v1.4.txt, anchors/ANCHORS.md, engine/f1.py, HANDOFF-CHECKLIST.md
- RUNBOOK.md, SPEC.md, specs/leg-a-p1-pre-registration-v1.5.txt
- ledger/ (14 entries: 10 original + 5 reconstructed + 2 new + seal-detached)
- known-bad-specs/C1-exclusion-list.yaml
- leg-a-closed-2026-09-09.md

## SEAL RECOVERY NOTES
- v1.5 seal DETACHED: 5/15 files never committed; engine/f1.py modified post-seal
- All 5 lost files reconstructed from .md twins and supersession report
- Each reconstructed file carries RECONSTRUCTED header; NOT sealed originals
- ENGINE-MODIFICATION entry filed for f1.py odd_basis rewrite
- SEAL CHECK v2 (commit-based, not tree-based) now verifies all 19 files
- Gist correction appended: v1.5 SUPERSESSION NOTE (founder-attributed)

## v1.6 FREEZE HASH
6d45b0fdc3b14bee9e130c19070480c3d66c7f071321dc43d09ab6d4e4b08b4b

## PUBLISHED TO GIST
Gist ID: 6b6d2d42651ffe5b63ab6a54a603ca05
Founder must append SUPERSESSION NOTE from ledger/seal-detached-v1.5.md
before publishing this freeze hash as a new revision.
