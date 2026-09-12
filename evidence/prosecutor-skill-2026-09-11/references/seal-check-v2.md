# Seal Check v2 — Commit-Based Verification

**Domain:** Quantitative research project governance — verifying a sealed bundle
against its originating hash.

**When to use:** Every seal-publish operation. Not the same as a working-tree
checksum. Two evolution stages:

## v1 — tree-based (what broke v1.5)

sha256 of each file on disk matches the manifest entry. This PASSES even when
files were never committed to git. At v1.5 seal time, 5 of 15 files existed
only on disk — `git checkout` of the seal commit would not reproduce the
bundle. The seal was **DETACHED** and all 26 subsequent results were produced
against it.

## v2 — commit-based (the control that catches detachment)

```
sha256(git show <seal_commit>:<path>) == manifest_entry
```

Every manifest file must exist as a git object at the seal commit. A file on
disk but not in HEAD → FAIL (the seal is attached to a commit, not a working
tree).

### Procedure

1. Record the seal commit SHA (e.g., `7d4aad7` for v1.6).
2. For each line in MANIFEST.sha256:
   - `actual = $(git show <seal_commit>:<path> | shasum -a 256)`
   - compare against manifest entry.
3. Any file that exists on disk but not in HEAD is a FAIL — it was never
   versioned.
4. Any file whose hash differs from its manifest entry is a MODIFIED — it
   changed after the seal was computed.

### Attestation, not monitor

Seal check v2 attests that every manifest entry matched `git show` at
publication time. It cannot fail after that point — a mismatch between the
seal commit and a later HEAD is expected divergence under the append-only
regime (see `ledger/sealed-file-append-only.md`).

### Composition verification

After a seal is rebuilt, report the composition explicitly:

> 9 unchanged since seal commit, 1 modified, 5 RECONSTRUCTED, + 4 additions.
> v1.6 does not re-certify v1.5. The 5 lost originals remain unrecoverable.

This prevents the new seal from implicitly certifying the old one.