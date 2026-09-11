SEAL OBJECT — decided 2026-09-11.

The seal object is the sorted list of (manifest path, blob SHA at the seal commit), digested with sha256. Obtained per path by git rev-parse <commit>:<path>. Subset digest at 7d4aad7: 020bb559e6f712892dec0c91439cfcbe895ae1b8aa2edb5a63787e10150f5639

REJECTED: git rev-parse HEAD^{tree} as the seal object. Falsified 2026-09-11: commits 437c58f and HEAD touched only files outside the 19 manifest paths, yet the tree hashes differ (e44577671fd59845ce7637e7207d349f9f9f69ef vs a64bcfdb9126938dc67693c4053cb4d2dbd63ed1) while the subset digest is identical at both (3d9c8dec14e62e78b7afefbbb803dac844fcd52fb1674a8ab292b6160925229b). A whole-repo tree hash moves on every commit, sealed paths or not, so it cannot serve as a seal for a subset manifest. Recommendation taken from a research report and tested before adoption; the report was correct for whole-repo sealing, wrong for this case.

Procedure change: every future seal records the subset digest alongside the manifest hash, and no seal is emitted while git status --porcelain is non-empty for tracked files.

Corroboration: the per-path blob comparison at 7d4aad7 vs HEAD independently reproduces the divergence report (17 SAME, 2 DIFFERS: ledger/seal-detached-v1.5.md and leg-a-closed-2026-09-09.md) by a different mechanism. Both misidentification-by-acronym-collision paths share blob 64ced0c258eb677ea30eb12bfd23b523624fb18e, git's own confirmation of gist correction item 3.
