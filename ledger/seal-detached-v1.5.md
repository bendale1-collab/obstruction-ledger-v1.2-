# SEAL-DETACHED-v1.5 — Founder-Attributed Correction
# Type: SEAL-DETACHED
# Filed: 2026-09-09
# Attribution: This entry carries the founder's voice per explicit instruction
# (SEAL RECOVERY prompt, 2026-09-09): "I wrote the false line. It gets
# corrected under my name in the ledger entry, not silently."

## GIST CORRECTION — text for founder to append to gist 6b6d2d42651ffe5b63ab6a54a603ca05
## (new revision; never edit prior text)

> **v1.5 SUPERSESSION NOTE (2026-09-09):**
> manifest verified on disk only. 5 of 15 files were never committed
> to git and are unrecoverable as sealed originals; engine/f1.py was
> modified post-seal. The claim "reproducible from git" is FALSE for
> v1.5. All results 66f9b16..526f7a5 were produced against a detached
> seal. See ledger/seal-detached-v1.5. I wrote the false line. It gets
> corrected under my name in the ledger entry, not silently.
> — bendale1-collab (founder), 2026-09-09

## Origin of the false line

ledger/0000-genesis.yaml (v1.3 gap entry, filed 2026-09-08) contains:

> "The v1.5 hash c6a73ae82f2e8bda1cdac2f348d6a2342ce5c07e5d43ae97516db05d178c00a4
> is the FIRST hash in this chain that is both reproducible from git
> (MANIFEST.sha256 committed at 159412e/5a6d9c8, all 15 entries verified
> against disk) and externally anchored"

The clause "all 15 entries verified against disk" is TRUE (verified
against the working tree at seal time). The clause "reproducible from
git" is FALSE: 5 of 15 entries were never committed to git, so no
git checkout can reproduce the sealed originals. The manifest hashes
the on-disk working tree, not git objects.

## Facts established by SEAL CHECK v2 (2026-09-09)

| Manifest entry | Seal-time status |
|----------------|------------------|
| amendment-log-v1.4.txt | committed at 5a6d9c8, hash matches |
| anchors/ANCHORS.md | committed at 5a6d9c8, hash matches |
| engine/f1.py | committed at 5a6d9c8, hash CHANGED post-seal |
| HANDOFF-CHECKLIST.md | committed at 5a6d9c8, hash matches |
| ledger/chebyshev-mapping-rejection-2026-09-07.yaml | NEVER committed |
| ledger/chebyshev-mapping-rejection.md | committed at 5a6d9c8, hash matches |
| ledger/conv-flag-diagnosis-2026-09-07.yaml | NEVER committed |
| ledger/conv-flag-diagnosis.md | committed at 5a6d9c8, hash matches |
| ledger/fourier-diff-tolerance-2026-09-07.yaml | NEVER committed |
| ledger/fourier-diff-tolerance.md | committed at 5a6d9c8, hash matches |
| ledger/misidentification-by-acronym-collision-2026-09-08.yaml | NEVER committed (sealed empty) |
| ledger/misidentification-by-acronym-collision.md | NEVER committed (sealed empty) |
| RUNBOOK.md | committed at 5a6d9c8, hash matches |
| SPEC.md | committed at 5a6d9c8, hash matches |
| specs/leg-a-p1-pre-registration-v1.5.txt | committed at 5a6d9c8, hash matches |

## Results produced against the detached seal (66f9b16..526f7a5)

P1 ENGINE-RED (66f9b16), V0 kill test (cc88716, 1d3c312), rescope
(62a8933, ed1e5b6, ae2f1cd), L-sweep v2 (67a97e0), Defect A
(f349725), adjudication packet (57eb8d8), control repairs
(2f88c62, c5dd05b), TERM-BY-TERM (370043e), convention audit
(063c04c), HALF-DOMAIN (cf218e8), STRIP CHARACTERIZATION (49f05cc),
ORIGIN-SCOPE (3e05597), K0 injection+validation (b4b1442..9250f09),
B0/B1/B2 registry (b81174a), H2 REALIZATION TEST (526f7a5).

None of these can claim reproducibility from a git checkout of the
sealed v1.5 tree. They are reconstructions under the current seal
recovery and stand on their own evidence files where those exist.

## Recovery status (2026-09-09)

- 5 lost files RECONSTRUCTED from surviving sources (.md twins,
  v1.5-supersession-report). Each carries the header:
  "RECONSTRUCTED 2026-09-09 from <source>; NOT the sealed original."
- Reconstructed files are NOT sealed originals and are not represented
  as such.
- engine/f1.py ENGINE-MODIFICATION entry filed separately.