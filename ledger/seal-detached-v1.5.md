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

## Gist revision history (external anchor, added 2026-09-10)

| Revision | Description | SHA | UTC Timestamp |
|----------|-------------|-----|---------------|
| Original v1.5 | First freeze hash published | f4e3a19333bea12ec5459e28180da3dcfc16675c | 2026-09-08T13:57:07Z |
| Rev A | v1.5 SUPERSESSION NOTE appended (seal-detached correction) | 05c96bd0aa15e646ddac1cfa1e2ed816d85cc67a | 2026-09-10T03:08:39Z |
| Rev B | v1.6 block (seal recovered, leg a closed) | 862219a34fdca397ced5e3260e4c044ceff5383c | 2026-09-10T03:11:25Z |

Gist ID: 6b6d2d42651ffe5b63ab6a54a603ca05
Repository: https://gist.github.com/bendale1-collab/6b6d2d42651ffe5b63ab6a54a603ca05

## Correction (2026-09-10) — condensed rendering replaced with verbatim anchor

The revision history table above is a **condensed** rendering of the gist content,
not verbatim text. It records only the revision SHAs and timestamps, omitting the
full gist text. The RENDERING-AS-RECORD ledger entry (filed 2026-09-10) covers
this class of defect.

Verbatim gist text follows, fetched 2026-09-10T04:01:06Z from:
  https://gist.githubusercontent.com/bendale1-collab/6b6d2d42651ffe5b63ab6a54a603ca05/raw/ol-freeze-hashes.txt

```
OBSTRUCTION LEDGER — FREEZE HASH CHAIN

v1.3  92bbcc04984cac1fb3fa333f497da003dd2357883aa0cb54c4b32b24f3287536
      Frozen 2026-09-06. RETROACTIVE, ASSERTED-ONLY:
      (a) not externally published at freeze time — agent
          publication failed on credentials;
      (b) the v1.3 MANIFEST.sha256 was never committed to git;
          this value is recorded in ledger/0000-genesis.yaml and
          STATE.yaml at v1.3 commits, but cannot be reproduced
          from the v1.3 tree. First manifest in git is at v1.4
          (87671c8).
      P0 GREEN (2026-09-07) ran against this asserted hash.
      Recorded here 2026-09-08 for chain continuity only.

v1.4  ee189ec49945fde81e18c842996a7ddd265c32d0dbfe3d22557f134ff034ebb2
      Unpublished, superseded (CCF misidentification).

v1.5  FREEZE_HASH=c6a73ae82f2e8bda1cdac2f348d6a2342ce5c07e5d43ae97516db05d178c00a4
      MANIFEST_FILES=15
      GIT_HEAD=5a6d9c8
      SPEC_VERSION=v1.5
      TIMESTAMP=2026-09-08T12:30:00Z
      Published: 2026-09-08T12:58:00Z
      First hash in this chain that is both reproducible from
      git and externally anchored.
v1.5 SUPERSESSION NOTE (work dated 2026-09-09 local)
      Manifest was verified on disk only. 5 of 15 files were never
      committed to git and are unrecoverable as sealed originals;
      engine/f1.py was modified post-seal. The claim above,
      "reproducible from git," is FALSE for v1.5. All results in
      commits 66f9b16..526f7a5 were produced against a detached
      seal. Founder-attributed. See ledger/seal-detached-v1.5.
      Published: 2026-09-10T03:08Z
v1.6  FREEZE_HASH=d7043bba1eda9996da2575dba81d2bdc38456ca66dfbd2124d570a915bf1aee9
      MANIFEST_FILES=19
      GIT_HEAD=7d4aad7
      SPEC_VERSION=v1.6
      Verified against commit (git show), not working tree.
      Seal check v2: 19/19 PASS.
      Composition: 15 files carried forward from the v1.5 manifest
      (9 unchanged since 5a6d9c8, 1 modified, 5 RECONSTRUCTED and
      marked in-file) + 4 v1.6 additions. v1.6 does not restore
      v1.5; the 5 lost originals remain unrecoverable.
      Published: 2026-09-10T03:11Z
      NOTE: all Published timestamps in this file are UTC. Ledger
      entry dates are local (America/New_York). The v1.6 work is
      dated 2026-09-09 local = 2026-09-10 UTC.
```