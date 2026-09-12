# Gist-ID Audit — 2026-09-10

**Target:** `6b6d2d4265` (truncated prefix) / `6b6d2d42651ffe5b63ab6a54a603ca05` (canonical 32-char gist ID).

**Audit command:** `git log -p -S 6b6d2d4265 --all --format='%h %cI %s'` then per-commit `git grep -n 6b6d2d4265 <commit>`.

## Results

### Truncated-ID occurrences (31 chars — missing "1" at position 11)

| commit | path | line | line text |
|--------|------|------|-----------|
| e7b2261 | leg-a-closed-2026-09-09.md | 161 | `to the existing gist (6b6d2d4265ffe5b63ab6a54a603ca05) as v1.6.` |
| 9123787 | SEAL-PACKET.md | 20 | `Gist ID: 6b6d2d4265ffe5b63ab6a54a603ca05` |
| 9123787 | leg-a-closed-2026-09-09.md | 161 | (same as e7b2261) |
| 5f49023 | SEAL-PACKET.md | 20 | `Gist ID: 6b6d2d4265ffe5b63ab6a54a603ca05` |
| 5f49023 | leg-a-closed-2026-09-09.md | 161 | (same) |

Corrected in fe8a1e9 (both SEAL-PACKET.md:29 and leg-a-closed:155 updated to full 32-char ID).

### Untracked-file truncation

`v1.6-publication-confirmation-2026-09-10.txt` line 35:
`GIST REVISION HISTORY (anchor: 6b6d2d4265)` — **10 chars only**. Not in any commit (untracked); invisible to pickaxe.

### ANCHORS.md gap

`anchors/ANCHORS.md` does NOT record the canonical gist ID in any commit — the file has no `6b6d2d4265` mention. This is a gap: the anchor registry has no anchor reference for the freeze-hashes gist.

## K1 candidate

The findings demonstrated the need for K1 candidate 4 (filed 2026-09-10):
**File identifier-length check:** every hash, SHA, and gist ID in a report must match its canonical length (64 hex SHA-256 / 40 hex SHA-1 / 32 hex gist ID) and, where an anchor exists, its canonical value.

## Audit method (reusable)

See `k1-pre-registration-assembly.md` § "Identifier-length audit procedure" for the technique (pickaxe + per-commit grep + truncation classification + correction tracking).