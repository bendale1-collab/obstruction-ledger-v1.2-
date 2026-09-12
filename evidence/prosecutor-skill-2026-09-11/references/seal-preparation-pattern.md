# Seal Preparation Pattern

**When to use:** Preparing a K1, K1-RUN, or any separate seal (not a v1.7 main seal). Two-stage because scripts/injections don't exist at freeze time.

## Stage 1: Pre-registration seal (freeze the spec)

1. **Write the manifest file** (e.g., `K1-MANIFEST.sha256`) with exactly the files to be sealed:
   ```bash
   sha256sum checker-k1-prereg.md > K1-MANIFEST.sha256
   ```
   One line per file: `<hash>  <path>` (two-space separator per sha256sum convention).

2. **Commit the manifest:**
   ```bash
   git add K1-MANIFEST.sha256
   git commit -m "K1-PREREG SEAL: manifest for checker-k1-prereg.md, one entry"
   ```
   Report the commit SHA.

3. **Seal check v2** (commit-based verification):
   ```bash
   git show <sha>:checker-k1-prereg.md | sha256sum
   ```
   Must match the manifest line exactly. Report MATCH or MISMATCH with both strings in full.

4. **Print gist block** (ready to paste, not published by agent):
   ```
   K1-PREREG  FREEZE_HASH=<hash>
              MANIFEST_FILES=1
              GIT_HEAD=<sha>
              SPEC_VERSION=K1-prereg-v0.3
              Verified against commit (seal check v2).
              Separate seal; base v1.6 (7d4aad7 / d7043bba) unchanged.
              Seven checks, fourteen retrodiction rows, outcomes stated before any run.
   ```

5. **Founder publishes** the gist block as a new revision. Agent does not publish.

## Stage 2: Run seal (freeze spec + injections + holdout)

After injections are written (per injection-fixture-discipline.md):

**K1a-RUN variant (subset digest, 2026-09-11):** Uses git blob references
instead of sha256sum of file contents. The manifest lines are
`<path>  <git rev-parse HEAD:path>` (git blob sha, two-space separator),
not `<sha256sum>  <path>`. The SUBSET_DIGEST is sha256 of the manifest
file itself. This is the corrected procedure per subset-digest-sealing.md —
whole-repo tree hashes were falsified as seal objects.

1a. **Write K1a-RUN-MANIFEST.txt** (subset-digest variant):
   ```bash
   git ls-files checker-k1a-prereg.md injections-k1a/ | sort | while read path; do
     blob=$(git rev-parse "HEAD:$path")
     echo "$path  $blob"
   done > K1a-RUN-MANIFEST.txt
   echo "holdout.txt  <founder-published-sha256>" >> K1a-RUN-MANIFEST.txt
   ```
   SUBSET_DIGEST = `sha256sum K1a-RUN-MANIFEST.txt` (the file's own hash).

**K1-RUN variant (sha256sum, 2026-09-10):** Uses sha256sum of file contents.

1b. **Write K1-RUN-MANIFEST.sha256** with spec + all injection leaf files + holdout:
   ```bash
   (sha256sum checker-k1-prereg.md; find injections/ -type f | sort | while read f; do sha256sum "$f"; done) > K1-RUN-MANIFEST.sha256
   echo "<founder-published-hash>  holdout.txt" >> K1-RUN-MANIFEST.sha256
   ```
   **Pitfall — fixture count ≠ manifest line count.** "140 fixtures" does NOT
   mean 140 manifest lines. Multi-file fixtures (k1-1: 2 files/case, k1-2:
   seal/head/MANIFEST subdirs, k1-3: seal.md/head.md pairs) expand to more
   leaf files. Use `find injections/ -type f | wc -l` to get the actual line
   count, not the fixture count. The K1-RUN manifest at `32d23b2` has 281
   repo lines (280 injection leaf files + 1 pre-reg) + 1 holdout = 282 total.

2. **Commit:**
   ```bash
   git add K1-RUN-MANIFEST.sha256
   git commit -m "K1-RUN SEAL: pre-reg + <N> fixtures + holdout hash"
   ```

3. **Seal check v2** — for every line except holdout.txt:
   ```bash
   git show <sha>:<path> | sha256sum
   ```
   Must match the manifest line. Report `N/N` pass or failing paths.

4. **Print gist block** (ready to paste):
   ```
   K1-RUN  FREEZE_HASH=<sha256 of K1-RUN-MANIFEST.sha256>
           MANIFEST_FILES=<repo-line-count> (+1 founder-held holdout)
           GIT_HEAD=<commit-sha>
           HOLDOUT=<founder-published-hash>
           Fixtures split by author; neither author has read the other's.
           Holdout: 7 rows, founder-held, revealed after both code commits.
           No check code exists at this commit.
   ```

5. **Founder publishes.** Agent does not publish.

## Holdout pattern

A holdout is a founder-held file NOT in the repo, whose hash is appended as
the final manifest line. It binds the founder's private test set to the seal
without revealing it. The holdout hash is founder-published alongside the
FREEZE_HASH and revealed only after both code commits are done.

- The holdout line uses the same `sha256sum` two-space format as repo lines.
- `MANIFEST_FILES` count uses `+1` notation: `<repo-count> (+1 founder-held holdout)`.
- Seal check v2 skips the holdout line (file doesn't exist in the commit).
- The holdout filename is `holdout.txt` by convention.

## Publication verification

After founder publishes, verify:

1. **Fetch raw gist** — `curl -s <gist-raw-url>`
2. **Block present?** — Grep for the seal label (e.g. `K1-RUN`). Quote verbatim.
3. **FREEZE_HASH byte-compare** — published value vs `sha256sum K1-RUN-MANIFEST.sha256`. Both strings in full. MATCH or MISMATCH.
4. **HOLDOUT byte-compare** — published value vs founder-specified holdout hash. Both strings in full. MATCH or MISMATCH.
5. **No check code at HEAD** — confirm `work/k1/` does not exist and no check implementations (C1, K1-1 through K1-6) are committed. Report any `.py`/`.sh` files under check directories.
6. **Diff from prior revision** — report any prior line that differs from the previous fetch. Include whitespace differences; content-match is not verbatim.

## Key rules

- **Separate seals, never fold into main manifest.** Folding K1 into `MANIFEST.sha256` would alter the base state (7d4aad7) that K1-2 and K1-3 measure against.
- **Seal check v2, not v1.** Compare `git show <sha>:<path>` against manifest entry, not working-tree hash. Working tree can drift; commit is frozen.
- **Founder-only publication.** Agent prepares the block; founder pastes it to gist. Credential separation: agent never has gist write access.
- **Append-only gist.** New revisions append; prior text never edited. Gist provides third-party-witnessed ordering via GitHub's revision clock, but is not proof of time (no timestamp authority).

## Examples from this project

K1-PREREG seal (2026-09-10):
- Manifest: `K1-MANIFEST.sha256` (1 line: `34f06514...  checker-k1-prereg.md`)
- Commit: `51c22340b9030282430b3a83062045b813323c06`
- Seal check v2: MATCH (both strings `34f06514419c660174e6ae0c3b4e828595681d72c31e355cf366a634bae7dacd`)
- Founder published as gist Rev D at 2026-09-10T22:15Z

K1-RUN seal (2026-09-10):
- Manifest: `K1-RUN-MANIFEST.sha256` (282 lines: 281 repo + 1 holdout)
- Commit: `32d23b2`
- FREEZE_HASH: `61459091e98aa11ed9fcabc7a4964b55dd5e8f49bcb4752bc5c7882f4eaf844e`
- Seal check v2: 281/281 PASS
- HOLDOUT: `fd2d6faa9b06d8fc6e108eac70583b889ab6e2424eea0f2b4891fe3c9dc8c8e1`
- Fixtures: 280 injection leaf files across c1/k1-1/k1-2 (Claude) + k1-3/k1-4/k1-5/k1-6 (Hermes)
- Founder published to gist at 2026-09-10T22:45Z
- Publication verified: FREEZE_HASH MATCH, HOLDOUT MATCH, no check code at HEAD

K1a-RUN seal (2026-09-11):
- Manifest: `K1a-RUN-MANIFEST.txt` (188 lines: 187 repo + 1 holdout)
- Commit: `7b887ded5990e1c428fad114dc9b56de00c7928c`
- SUBSET_DIGEST: `81361728f34190eafb9b08e25de7c4df5d2e5ca85147dbc8609f72baf15c8e9e`
- Format: `<path>  <git rev-parse HEAD:path>` (blob sha, not sha256sum)
- HOLDOUT: `fd2d6faa9b06d8fc6e108eac70583b889ab6e2424eea0f2b4891fe3c9dc8c8e1`
- Fixtures: 187 tracked files across c1/k1-1/k1-2 (Claude half, tarball-placed, hash-verified, not read by committing agent) + k1-3/k1-4/k1-5/k1-6 (Hermes half, measurements-driven)
- Every index carries a MEASUREMENTS table generated by running §2-mandated parsers, not asserting
- Two properties falsified and corrected pre-seal (K1-4 FREEZE_HASH label scoping; C1 rounding ambiguity)
- No check code exists at this commit (work/k1a/ does not exist)
- Gate G3: PASS (0 modified-tracked lines)
- Gate G4: 17 SAME, 2 DIFFERS (both declared by ledger entries)
- Not published (report-and-stop)
