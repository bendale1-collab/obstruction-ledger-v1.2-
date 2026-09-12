# Manifest Subset Digest Sealing (vs Tree Hash)

**The problem:** `git rev-parse HEAD^{tree}` hashes the entire tree at a commit. This moves on every commit outside the manifest, making it useless as a seal for a subset.

**The solution:** Subset digest — sorted list of (manifest_path, blob_sha_at_commit), sha256-digested.

---

## Pattern

**Freeze the manifest paths** (e.g., 19 files in MANIFEST.sha256).

**At seal commit, for each path:**
```bash
git rev-parse COMMIT:<path>
```
Get the blob hash (40 hex SHA-1).

**Build the digest:**
```bash
printf '%s  %s\n' path blob_hash | sort -k2f | sha256sum
```
(Sorted by path, tab-separated with hash, piped to sha256sum for reproducibility.)

**Falsifier test:** 
- Commit X touches only files *outside* the manifest.
- Commit Y is your seal commit.
- Compute subset digest at both X and Y.
- If they match, the manifest is stable between X and Y (even if X's tree hash differs from Y's).

**Why it works:**
- Tree hash = entire snapshot, moves on any edit anywhere
- Subset digest = only the paths you care about, stable across unrelated edits
- Can be recomputed from any commit with `git show <commit>:<path>` on each frozen path

---

## Falsification example (2026-09-11)

Commits 437c58f and HEAD:
- Tree hash at 437c58f: `e44577671fd59845ce7637e7207d349f9f9f69ef`
- Tree hash at HEAD: `a64bcfdb9126938dc67693c4053cb4d2dbd63ed1`
- **Trees differ** (both touched only ledger/ files outside manifest)

Subset digest (19 manifest paths):
- At 437c58f: `3d9c8dec14e62e78b7afefbbb803dac844fcd52fb1674a8ab292b6160925229b`
- At HEAD: `3d9c8dec14e62e78b7afefbbb803dac844fcd52fb1674a8ab292b6160925229b`
- **Digests identical** → manifest is unchanged

**Verdict:** Tree hash falsified; subset digest is the seal object.

---

## Record in gist/seal packet

Include all three artifacts:
- SUBSET_DIGEST (64 hex)
- BLOB (canonical 40 hex for the single-file case, or list for multi-file)
- GIT_HEAD (commit SHA where subset was verified)

Never use tree hash alone for subset seals. Tree hash is only correct for whole-repo seals.
