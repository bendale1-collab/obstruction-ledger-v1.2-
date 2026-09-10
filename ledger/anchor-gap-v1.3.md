Ledger Entry — ANCHOR-GAP-V1.3
Filed: 2026-09-08 (pre-P1, on founder direction)
Type: ANCHOR-GAP-V1.3

The v1.3 freeze hash 92bbcc04984cac1fb3fa333f497da003dd2357883aa0cb54c4b32b24f3287536
is asserted in ledger/0000-genesis.yaml (bundle_hash field) and STATE.yaml at the
v1.3 commits (cca4d0b P0 GREEN, c6f6b46 SMOKE). It was never externally published
at freeze time (agent publication failed on credentials), and the v1.3
MANIFEST.sha256 itself was never committed to git — the first manifest in git
appears at the v1.4 SHIP commit 87671c8.

Consequence: P0 GREEN (2026-09-07) ran against an unverifiable seal. The v1.3
hash cannot be reproduced from the v1.3 tree; it exists only as an asserted
value in genesis/STATE.

The v1.5 hash c6a73ae82f2e8bda1cdac2f348d6a2342ce5c07e5d43ae97516db05d178c00a4
is the FIRST hash in this chain that is both reproducible from git (MANIFEST.sha256
committed at 159412e/5a6d9c8, all 15 entries verified against disk) and externally
anchored (published to gist 6b6d2d42651ffe5b63ab6a54a603ca05, revision
f4e3a19333bea12ec5459e28180da3dcfc16675c, 2026-09-08T12:58:00Z).

Recorded here for chain continuity. The gap is acknowledged; it does not affect
the v1.5 seal validity.