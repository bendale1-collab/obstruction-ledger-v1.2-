# Seal Object Definition (Corrected 2026-09-11)

## Problem

Previous approach: use `git rev-parse HEAD^{tree}` to seal a manifest of files.

**Falsified 2026-09-11:** Commits 437c58f and HEAD touched **only files outside the 19-manifest-paths**, yet their tree hashes differ:
- `437c58f^{tree}` → `e44577671fd59845ce7637e7207d349f9f9f69ef`
- `HEAD^{tree}` → `a64bcfdb9126938dc67693c4053cb4d2dbd63ed1`

Subset digest (per-path blob shas) is **identical at both** (`3d9c8dec...`).

**Conclusion:** A whole-repo tree hash moves on every commit in the repo, independent of whether the sealed subset changed. It cannot serve as a manifest seal.

## Solution: Subset Digest Seal Object

**Definition:** Sorted list of `(path, blob_sha)` tuples for the manifest paths, digested with sha256.

### Construction

1. For each path in the manifest (frozen list, sorted order):
   ```
   blob_sha=$(git rev-parse <commit>:<path>)
   ```
2. Build lines: `<blob_sha>  <path>` (two spaces separating)
3. Sort by path (stable, no re-sorting after freeze)
4. Compute digest:
   ```
   printf '%s  %s\n' per line, sorted by path | sha256sum
   ```

### Stability property

- **Stable across outside-manifest edits:** If only files outside the 19 paths change between two commits, the subset digest remains identical (tested: 437c58f → 3763bbb, 17 SAME paths, 2 DIFFERS but identical digest at both).
- **Diverges on manifest path change:** If any of the 19 paths changes, at least one blob_sha changes, and the digest changes.

### Procedure change

1. Every future seal records **both** the manifest hash (SHA256 of manifest file itself) **and** the subset digest.
2. No seal is emitted while `git status --porcelain` shows modified tracked files (must be clean).
3. Seal commit must be published to gist for archival (founder-only).

### Falsification test (from 2026-09-11 session)

**Test commit range:** 437c58f (K1a pre-reg seal prep) → 3763bbb (K1a pre-reg checker added)
**Manifest path changes:** 0 (all 19 SAME)
**Tree hash difference:** YES (e445... ≠ a64bc...)
**Subset digest difference:** NO (both 3d9c8...)

**Verdict:** Subset digest is the correct seal object. Tree hash rejected.

### References

- Seal object decision document: `ledger/seal-object-decision.md` (commit 9deb91f)
- Falsifier evidence: `work/r31-subset-digest-2026-09-11.txt`, `work/r32-manifest-blob-falsifier-2026-09-11.txt`
- K1a gate output: `work/k1a-gate-G4-2026-09-11.txt`
