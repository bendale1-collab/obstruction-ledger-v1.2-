# Seal verification protocol (v2)

Domain: verifying that a freeze-hash seal is reproducible from git.
Applies to any project that uses MANIFEST.sha256 + gist publication.

## Core rule — verify against the COMMIT, not the working tree

A working-tree file may differ from the committed version (post-seal
edits, reconstructed files, files that existed only on disk). The
manifest hashes the on-disk working tree at seal time, but the seal
check verifies against git objects:

    for each manifest entry:
      sha256(git show SEAL_COMMIT:path) == entry_hash
    A file that exists on disk but not in the commit is FAIL.

## Seal check v2 procedure

1. Define the file set (paths from MANIFEST.sha256)
2. For each path, compute git object hash:
       git show SEAL_COMMIT:"$file" | shasum -a 256
3. Compare against the stored hash in MANIFEST.sha256
4. Report per-file PASS/FAIL
5. Check: files that exist on disk but not in the commit are FAIL

## Seal check v2 is an attestation, not a monitor

It certifies the bundle at the seal commit and nothing about HEAD.
Once published, it cannot fail — a mismatch between seal commit and
HEAD is not a seal failure. It is expected divergence under the
append-only-after-seal regime.

## History

- v1.5 (2026-09-08): manifest verified on disk only. 5 of 15 files
  were never committed to git; engine/f1.py was modified post-seal.
  The claim "reproducible from git" was FALSE. Filed as SEAL-DETACHED.
- v1.6 (2026-09-09): seal check v2 introduced. All 19 files verified
  against commit 7d4aad7. Published with SUPERSESSION NOTE.

## Typical divergence report

When HEAD moves past the seal commit, run:

    for each manifest path:
      git diff --quiet SEAL_COMMIT HEAD -- path
      → SAME or DIFFERS
      → for each DIFFERS, cite the declaring ledger entry

Undeclared divergence is a finding.