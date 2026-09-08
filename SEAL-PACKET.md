# Obstruction Ledger — SEAL-PACKET v1.5

**Date:** 2026-09-08
**Phase:** GATE 1 (pre-GATE 2 authorization)
**Status:** SEAL-PREPARED — awaiting founder gist publication + P1 AUTHORIZED

---

## Freeze hash

`c6a73ae82f2e8bda1cdac2f348d6a2342ce5c07e5d43ae97516db05d178c00a4`

## Manifest (      15 files)

- `amendment-log-v1.4.txt`: `693ee708303a245bdca997f6b16b3aee3106d80f73cfd34268975bf276e2dddf`
- `anchors/ANCHORS.md`: `c45d5dfdb741267964bed72c62b077e47d0d6cbb247c2cb82bba929d82af3e50`
- `engine/f1.py`: `78f0abd6660f53dcc0b4f0c19cd1d1f3493e1118a1c8989c52d178f0167fd2b6`
- `HANDOFF-CHECKLIST.md`: `7ca4fcfe7ebc9dc2143a0829c6e7008d6774bd6f57b190e1eeff2e52f2e6f9a1`
- `ledger/chebyshev-mapping-rejection-2026-09-07.yaml`: `7f031e147dc0693221a5dfb2fd0b8035d0b2c7cee549df7f3979c3f4ae49113a`
- `ledger/chebyshev-mapping-rejection.md`: `5c89483a40f6adc5fee6d0e783b46e37b91777146e788024f0362ef9eda2f99f`
- `ledger/conv-flag-diagnosis-2026-09-07.yaml`: `6a8ea5e6262dec6ab86c4269d4d0c51969ebe35f48840c98d3cf959ed5d709a6`
- `ledger/conv-flag-diagnosis.md`: `476e6c68926d568370970e35dc930861ef68eba4ee7f0ef573cd88b6ddabef2e`
- `ledger/fourier-diff-tolerance-2026-09-07.yaml`: `1d59231626b8da517b00dc60068311db8fe061982bda46a50e2970a6c89a9546`
- `ledger/fourier-diff-tolerance.md`: `7e12262e16af1f4ca1a5050ecd8266fe0d4422c50fd46cd4b7d51893377f3368`
- `ledger/misidentification-by-acronym-collision-2026-09-08.yaml`: `1a70944c8a339ea759509c3d0567dee438710fcb1f4e60ee431877a9c1f030d6`
- `ledger/misidentification-by-acronym-collision.md`: `540c2e882a92cd5dc4574ead259df34fb5737dde1935f83ef8f7f18a2363ff03`
- `RUNBOOK.md`: `65281acf80fec05ed13df4c497851e80438f533822d09498e27a119b2b5b160b`
- `SPEC.md`: `1e7c2dfac2fe41542e7acc7e934e9682d08f68761fe0f6707d68f50194fab877`
- `specs/leg-a-p1-pre-registration-v1.5.txt`: `a90e9373be326bdc4635f2da94a20e31beca1130e113b2e52a221c2e58bf4eaa`

## Ledger

- Entries:        4 non-genesis certificates
- Ledger chain hash: `257bc8b1e81361930a0f570f3d14a7f0faf193ff3ea90af03a8084a0d8da3350`
- Note: chain verification FAILED — non-genesis entries lack prev_hash fields (pre-existing, introduced v1.4). Corrective action deferred to P6 seal.

## Gist body text (founder publishes)

```
OL v1.5 seal — Leg split, precision correction, referent-resolution control, P1 pre-registration

Freeze hash: c6a73ae82f2e8bda1cdac2f348d6a2342ce5c07e5d43ae97516db05d178c00a4
Contains:
- LEG A (CLM Spectral, gCLM a=0) — P0 GREEN, P1 pre-registered
- LEG B (CCF Transport) — NOT STARTED, cap and scope UNQUOTED
- Precision correction: lambda targets truncated to source-stated precision
- UNSOURCED-PRECISION, UNRESOLVED-SOURCE-DISCREPANCY, SELECTION-UNRECORDED registries
- Referent-resolution control (§2.7 standing gate)
- LSS (Lushnikov-Silantyev-Siegel) and Eggers-Fontelos referents verified from primary sources
- LEG A P1 falsification battery pre-registered (F-4 first, then F-1/F-2/F-3/F-5)
- FLOOR = -1/2 + 3e-3 single spectral boundary
- Cap: 5/5d (derived from marginal-cost estimate)
```

## Zenodo draft metadata

```yaml
title: "Obstruction Ledger — v1.5: Leg-Split, Precision Correction, and P1 Pre-Registration for CLM Spectral Continuation"
description: >
  Sealed research bundle for the Obstruction Ledger project. v1.5 corrects
  the CCF misidentification (Córdoba-Córdoba-Fontelos ≠ Constantin-Lax-Majda),
  splits the bundle into LEG A (CLM Spectral, gCLM a=0) and LEG B (CCF Transport),
  files precision corrections and source-discrepancy registries, adopts a
  referent-resolution control, and pre-registers the LEG A P1 falsification
  battery with a single spectral boundary (FLOOR = -1/2 + 3e-3).
creators:
  - name: [Founder name]
  - name: [Researcher name]
access_right: restricted
version: v1.5
```

## SWH request

```
Save-code-now URL: https://archive.softwareheritage.org/save/#origin=[REPO_URL]
Scheduled at P6 seal (repo currently private; SWH requires public repo)
```

## GATE 1 status

- [x] spec/ directory created: specs/
- [x] Pre-registration moved into sealed tree: specs/leg-a-p1-pre-registration-v1.5.txt
- [x] ANCHORS.md: leg split, referent resolutions, precision tags, UNRESOLVED-SOURCE-DISCREPANCY, SELECTION-UNRECORDED
- [x] Referent-resolution control: SPEC §2.7
- [x] SPEC §4 cap: $15/5d
- [x] RUNBOOK §3 cap: 15/5
- [x] Amendment log: through Entry #8 (v1.5 supersession)
- [x] Ledger entries: Chebyshev, Fourier-tol, conv-flag, MISIDENTIFICATION-BY-ACRONYM-COLLISION
- [ ] Founder publishes freeze hash to gist
- [ ] Founder issues P1 AUTHORIZED

Awaits: GATE 2 (founder gist publication + "P1 AUTHORIZED").
