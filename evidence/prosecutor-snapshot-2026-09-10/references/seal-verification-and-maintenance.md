# Seal Verification and Maintenance

**Domain:** Verifying the integrity of a frozen-spec research bundle's seal (MANIFEST.sha256) when the working tree may be empty, detached, or modified.

**When to use:** Before founder review, before any compute, when told "verify the working tree against hash X", or when the seal state is unknown.

---

## Problem

A freeze seal consists of a MANIFEST.sha256 file whose own hash is the freeze hash. The manifest lists every hashed file in the bundle. But seal integrity is more complex than "hash matches":

- Files may be in git HEAD but **deleted from the working tree** (still restorable)
- Files may have been **modified** after the seal (hash mismatch against frozen value)
- Files may have been in the working tree at seal time but **never committed** (zero-byte restore from git)
- The MANIFEST.sha256 file itself may match the freeze hash while containing entries for files that don't match HEAD

---

## Detection protocol

**Critical order: SEAL CHECK v2 means verify against `git show HEAD:path`, not the working tree.**

In v1.5 of the Obstruction Ledger, a seal passed because all 15 files existed on disk with matching hashes. But 5 of 15 files were **never committed to git** — they existed only in the working tree at seal time. When the working tree was cleaned, those files were unrecoverable. The working tree check (Step 2) was satisfied; the git-object check (Step 3) was not run at seal time.

**Rule: Steps 2 and 3 must BOTH run at seal time. Step 2 alone is insufficient.** A file on disk with a matching hash means nothing if the file never entered git.

### Step 1 — Freeze hash match

```bash
shasum -a 256 MANIFEST.sha256
# Compare against the stated freeze hash
```

If this fails, the MANIFEST itself was modified — SEAL-BROKEN immediately.

### Step 2 — Per-file existence on disk

```bash
while IFS= read -r line; do
  file=$(echo "$line" | cut -d' ' -f2-)
  if [ -f "$file" ]; then echo "ON-DISK: $file"; else echo "ABSENT: $file"; fi
done < MANIFEST.sha256
```

### Step 3 — Per-file hash against manifest (via git HEAD)

```bash
while IFS= read -r line; do
  mhash=$(echo "$line" | awk '{print $1}')
  file=$(echo "$line" | awk '{$1=""; print $0}' | sed 's/^ //')
  if git show HEAD:"$file" >/dev/null 2>&1; then
    actual=$(git show HEAD:"$file" | shasum -a 256 | awk '{print $1}')
    if [ "$actual" = "$mhash" ]; then
      echo "MATCH: $file"
    else
      echo "MODIFIED: $file (manifest=$mhash, HEAD=$actual)"
    fi
  else
    echo "NEVER-COMMITTED: $file"
  fi
done < MANIFEST.sha256
```

### Result classification

| Result | Meaning | Action |
|--------|---------|--------|
| MATCH | Hash unchanged since seal | ✅ Trustworthy |
| MODIFIED | Changed in a commit after seal | ⚠ Results after the modifying commit are suspect. Check `git log --oneline path` to date the change |
| NEVER-COMMITTED | Was in working tree at seal, never in git | ❌ Lost if working tree was cleaned. File as SEAL-DETACHED |
| ABSENT-FROM-HEAD | Not in git HEAD at all | ❌ Lost. File as SEAL-DETACHED |

### SEAL-DETACHED filing

When SEAL-DETACHED: file an entry with:
- The freeze hash and the last commit where it was intact
- The count of MATCH/MODIFIED/NEVER-COMMITTED per file
- The date of the last verified check
- Which results (commits) fall after the detachment date

---

## Re-seal procedure (when seal is broken or bundle advances)

### Step 0 — SPEC scope rule: decision, not inference

The MANIFEST.sha256 seals the **core bundle only** — files that define the project
state and its governance: SPEC.md, RUNBOOK.md, anchors/, engine/, amendment-log,
HANDOFF-CHECKLIST.md, specs/, all ledger/ entries, and any policy-versioning files
(known-bad-specs/C1-exclusion-list.yaml, etc.).

Files in work/, registry/, harness/, arbiter/, env/, telegram/, SEAL-PACKET.md,
and known-bad-specs/RB-*.yaml are tracked in git but **unsealed**. They are not
in the manifest and are not verified by seal checks. The K0 injection set and all
work products belong outside the seal boundary.

This is a decision recorded in the bundle, not an inference from practice.
If a future version changes the scope, the change is a ledger entry.

### Step 1 — Restore manifest files from git HEAD

```bash
while IFS= read -r line; do
  file=$(echo "$line" | awk '{$1=""; print $0}' | sed 's/^ //')
  dir=$(dirname "$file")
  mkdir -p "$dir"
  git show HEAD:"$file" > "$file"
done < MANIFEST.sha256
```

### Step 2 — Restore content files that were never committed

Files that were NEVER-COMMITTED are **zero-byte restores** — they have no content in git. Their actual content is lost unless there is a backup or the working tree already has them. This case must be documented.

### Step 3 — Add new files to the manifest

```bash
NEW_FILES=(
  "new-report.md"
  "known-bad-specs/new-exclusion-list.yaml"
)
TMP=$(mktemp)
for f in "${OLD_FILES[@]}"; do shasum -a 256 "$f" >> "$TMP"; done
for f in "${NEW_FILES[@]}"; do shasum -a 256 "$f" >> "$TMP"; done
sort -k2f "$TMP" > MANIFEST.sha256
rm "$TMP"
```

The sort `-k2f` is critical — it produces the canonical file-order that defines the freeze hash.

### Step 4 — Compute the new freeze hash

```bash
shasum -a 256 MANIFEST.sha256
```

### Step 5 — Update SEAL-PACKET and commit

```bash
# Update SEAL-PACKET.md with new hash and timeline
git add MANIFEST.sha256 SEAL-PACKET.md <new-files>
git commit -m "vX.Y SEAL: <short description>"
```

### Step 6 — Publish freeze hash

The new freeze hash must be published to the existing gist (or agreed publication channel) before any compute uses the new seal.

---

## Pitfalls

- **The MANIFEST.sha256 file on disk defines the freeze hash.** The `MANIFEST.sha256` stored file's byte order (after `sort -k2f`) defines the freeze hash. NEVER regenerate the manifest by re-sorting after freeze. Verify by hashing the STORED file.
- **Zero-byte YAML files in git** — A YAML ledger entry created at seal time but never committed restores as an empty file (hash `e3b0c44298fc1c...`). The tooling must handle this gracefully (e.g., skip YAML parse on empty files).
- **Seal-detached does not invalidate results.** Results produced against a detached seal may still be correct — the detachment is a metrology issue, not an automatic invalidation. File the status and proceed.
- **Per-file baseline at HEAD** — Always check against `git show HEAD:path` not the on-disk file, because on-disk may be stale or absent.
- **.gitignore can silently exclude ledger files from commits.** If `.gitignore` contains `ledger/` (common for projects that keep ledger files ephemeral), files added to the working tree at seal time will never be committed. `git add -f` is required to force-track them. Without force-adding, the seal passes Steps 1-2 (hash + on-disk) but files are absent from git — and "reproducible from git" is FALSE. Detection: Step 3 (git objects check) catches this because `git show HEAD:path` fails for such files.
- **RECONSTRUCTED header protocol.** When files that were never committed need to be reconstructed from surviving sources (.md twins, reports, chat), each reconstructed file MUST carry a header line: `# RECONSTRUCTED YYYY-MM-DD from <source>; NOT the sealed original.` The file is never represented otherwise. This prevents the reconstructed file from being mistaken for the sealed original, which could lead to circular verification in future seal checks.
- **ENGINE-MODIFICATION ledger entry.** When a compute-critical file (engine source, operator code) changes after the seal, file a ledger entry: what changed, which commit introduced the change, which subsequent results depend on it. This prevents results from claiming reproducibility from the sealed tree.
- **Founder-attributed gist correction.** A false claim in seal documentation (e.g. "reproducible from git" when files were never committed) must be corrected under the founder's name in the ledger entry, and the correction appended to the gist as a new revision (never edit prior text). The correction text should be: `I wrote the false line. It gets corrected under my name in the ledger entry, not silently.`

---

## Post-publication discipline

### RENDERING-AS-RECORD defect class

When presenting the content of an anchored artifact (gist, gist revision, manifest file, published block) in a report, ledger entry, or chat response:

- The text must be **byte-identical** to the anchor (proven by hash or diff from the raw URL)
- OR carry the header: `DERIVED from <source_revision_SHA> — condensed rendering`
- A file/presentation that carries the anchor's content without either property is a **RENDERING-AS-RECORD** defect

This applies to:
- Gist freeze-hash blocks presented in chat or ledger entries
- Quoted gist text in any report
- Summaries of gist content that rephrase or condense lines
- Revision-history tables that omit the full gist text

**Detection:** The v1.5→v1.6 publication (2026-09-10) produced a condensed block that omitted several `Published:`, `TIMESTAMP=`, and composition lines that existed in the actual gist. The condensed block passed the mechanical hash check (MANIFEST matches) but the surrounding prose degraded. The hash check is necessary but not sufficient — the quoted text must also be checked against the raw URL.

**First instance filed:** `ledger/rendering-as-record.md` (2026-09-10).

### Standing rule: DERIVED vs VERBATIM

Any text presented as the content of an anchored file must be either:
  (a) **byte-identical** to the anchor (proven by hash or diff), or
  (b) **explicitly identified as DERIVED** with the source revision SHA
      cited and a note that the text is condensed/paraphrased.

This applies to all ledger entries, reports, and chat output.

### K1 candidate — quote-vs-anchor byte check

New K1 check: verify that quoted anchor text in a report is byte-identical to the anchor's current published version.

  1. Extract all quoted blocks attributed to a gist or published hash
  2. Fetch the raw text from the anchor URL at the stated revision SHA
  3. Diff the quoted text against the fetched raw bytes
  4. Flag any difference as VERBATIM-MISMATCH

Raw URL pattern: `https://gist.githubusercontent.com/{user}/{gist_id}/raw/{rev_sha}/{filename}`

### Timestamp authority

**"Published:" lines in gist blocks are founder assertions and are NOT authoritative.**
The authoritative timestamp for any gist revision is the GitHub API revision record's
`committed_at` field. When fetching gist content for verification:

1. Query the gist API for revision history (`history[].committed_at`)
2. Compare the `committed_at` against any local "Published:" values
3. If they differ, the API timestamp wins — file a timestamp correction

Example (v1.5, 2026-09-10):
- Gist block said `Published: 2026-09-08T12:58:00Z`
- GitHub revision `f4e3a193` recorded `2026-09-08T13:57:07Z`
- Difference: ~59 min. The API timestamp is authoritative.

The same rule applies to all three revisions in the chain (Rev A, Rev B).
Correction is filed as a ledger entry; the gist is not re-edited (never edit prior text).

### Composition disclosure

When advancing from one seal version to the next, the composition line must state:
  - **X unchanged** (hash identical to prior seal commit)
  - **Y modified** (hash changed post-seal, with ENGINE-MODIFICATION entry)
  - **Z RECONSTRUCTED** (never committed at prior seal; reconstructed from surviving sources with RECONSTRUCTED header)
  - **W added** (new in this version)
  - **vX.Y does not re-certify vX.(Y-1)** — explicitly state that the prior seal's status (lost originals, modified files) is not retroactively fixed

Bad: "15 v1.5 originals — all present and hash-verified"
Good: "15 files carried forward from the v1.5 manifest (9 unchanged, 1 modified, 5 RECONSTRUCTED) + 4 v1.6 additions. v1.6 does not restore v1.5."