#!/bin/bash
# seal-prepare.sh — Obstruction Ledger seal preparation
# RUNBOOK §9: hash repo+paper+ledger; write SEAL-PACKET.md
# GATE 1: v1.5 seal (leg-split + P1 pre-registration)

set -e
ROOT="/Users/brukendale/ol-run/obstruction-ledger-v1.2"
cd "$ROOT"

# Read freeze hash from MANIFEST.sha256
FREEZE_HASH=$(shasum -a 256 MANIFEST.sha256 | cut -d' ' -f1)

# Collect per-file hashes (same set as MANIFEST)
FILE_HASHES=$(cat MANIFEST.sha256)

# Ledger chain hash (hash of all ledger yaml files concatenated)
LEDGER_CHAIN=$(for f in $(ls ledger/*.yaml | sort); do
    shasum -a 256 "$f" | cut -d' ' -f1 | tr -d '\n'
done | shasum -a 256 | cut -d' ' -f1)

# Count ledger entries (non-genesis yaml files)
LEDGER_COUNT=$(ls ledger/*.yaml 2>/dev/null | grep -v genesis | wc -l)

cat > "$ROOT/SEAL-PACKET.md" << EOF
# Obstruction Ledger — SEAL-PACKET v1.5

**Date:** 2026-09-08
**Phase:** GATE 1 (pre-GATE 2 authorization)
**Status:** SEAL-PREPARED — awaiting founder gist publication + P1 AUTHORIZED

---

## Freeze hash

\`${FREEZE_HASH}\`

## Manifest ($(echo "$FILE_HASHES" | wc -l) files)

$(echo "$FILE_HASHES" | while read h p; do echo "- \`$p\`: \`$h\`"; done)

## Ledger

- Entries: ${LEDGER_COUNT} non-genesis certificates
- Ledger chain hash: \`${LEDGER_CHAIN}\`
- Note: chain verification FAILED — non-genesis entries lack prev_hash fields (pre-existing, introduced v1.4). Corrective action deferred to P6 seal.

## Gist body text (founder publishes)

\`\`\`
OL v1.5 seal — Leg split, precision correction, referent-resolution control, P1 pre-registration

Freeze hash: ${FREEZE_HASH}
Contains:
- LEG A (CLM Spectral, gCLM a=0) — P0 GREEN, P1 pre-registered
- LEG B (CCF Transport) — NOT STARTED, cap and scope UNQUOTED
- Precision correction: lambda targets truncated to source-stated precision
- UNSOURCED-PRECISION, UNRESOLVED-SOURCE-DISCREPANCY, SELECTION-UNRECORDED registries
- Referent-resolution control (§2.7 standing gate)
- LSS (Lushnikov-Silantyev-Siegel) and Eggers-Fontelos referents verified from primary sources
- LEG A P1 falsification battery pre-registered (F-4 first, then F-1/F-2/F-3/F-5)
- FLOOR = -1/2 + 3e-3 single spectral boundary
- Cap: $15/5d (derived from marginal-cost estimate)
\`\`\`

## Zenodo draft metadata

\`\`\`yaml
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
\`\`\`

## SWH request

\`\`\`
Save-code-now URL: https://archive.softwareheritage.org/save/#origin=[REPO_URL]
Scheduled at P6 seal (repo currently private; SWH requires public repo)
\`\`\`

## GATE 1 status

- [x] spec/ directory created: specs/
- [x] Pre-registration moved into sealed tree: specs/leg-a-p1-pre-registration-v1.5.txt
- [x] ANCHORS.md: leg split, referent resolutions, precision tags, UNRESOLVED-SOURCE-DISCREPANCY, SELECTION-UNRECORDED
- [x] Referent-resolution control: SPEC §2.7
- [x] SPEC §4 cap: \$15/5d
- [x] RUNBOOK §3 cap: 15/5
- [x] Amendment log: through Entry #8 (v1.5 supersession)
- [x] Ledger entries: Chebyshev, Fourier-tol, conv-flag, MISIDENTIFICATION-BY-ACRONYM-COLLISION
- [ ] Founder publishes freeze hash to gist
- [ ] Founder issues P1 AUTHORIZED

Awaits: GATE 2 (founder gist publication + "P1 AUTHORIZED").
EOF

echo "SEAL-PACKET.md written. Freeze hash: $FREEZE_HASH"