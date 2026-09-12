# Tarball Handoff Pattern (Multi-Agent Fixture Delivery)

## Purpose

When multiple agents author fixtures in parallel (e.g., Agent A writes C1/K1-1/K1-2, Agent B writes K1-3..K1-6), the fixtures are delivered via tarball to preserve authorship separation and prevent contamination.

## Procedure

1. **Receiving agent** places tarball at repo root (e.g., `k1ainjectionsclaudehalf.tar.gz`)
2. **Filename may lose hyphens in transit** — match on size (e.g., 16505 bytes) if name is mangled
3. **Hash-verify before extraction:**
   ```bash
   sha256sum k1ainjectionsclaudehalf.tar.gz
   ```
   Must equal expected hash (e.g., `e530c2848fb33caef04ede8da5c42dd27b1387a5d8e51e4f1d27c9f333291420`). On MISMATCH, stop.
4. **Extract at repo root:**
   ```bash
   tar xzf k1ainjectionsclaudehalf.tar.gz
   ```
5. **Count entries (mechanically, without opening/reading contents):**
   ```bash
   find injections-k1a/c1 -type f | wc -l
   find injections-k1a/k1-1 -type f | wc -l
   find injections-k1a/k1-2 -type f | wc -l
   ```
   Expected: 16 each (10 positives + 3 negatives + 1 index.md + 1 MEASUREMENTS.txt + 1 properties.py)
6. **Remove tarball:**
   ```bash
   rm k1ainjectionsclaudehalf.tar.gz
   ```
7. **Commit with provenance message:**
   ```bash
   git add injections-k1a/
   git commit -m "K1a-INJECTIONS (Claude half): C1, K1-1, K1-2. Placed by Cowork, hash-verified, not read by the committing agent."
   ```

## Constraints

- **Do not cat, open, view, or grep anything under the delivered directories.** The committing agent must not read the other agent's fixtures.
- **Report SHA, entry count under each directory, and git status --porcelain modified-tracked lines only.**
- **Confirm no `__pycache__` or `.pyc` files were shipped.** If present, they should be ignored by `.gitignore` (line 6: `__pycache__/`, line 7: `*.pyc`). Verify with `git ls-tree -r <sha> --name-only | grep -i pycache` — expect no output.

## Reference

See commit `283eec6` (2026-09-11) for an example of the tarball variant.

## Single-file variant (harness delivery, 2026-09-12)

When a single file (not a tarball) is placed at repo root by Cowork
(e.g., `k1a_run.py`, `k1a_retro.py`), the same verification pattern applies:

1. **sha256sum at repo root:**
   ```bash
   sha256sum k1a_run.py
   ```
   Must equal expected hash. On MISMATCH, stop. Report both strings.

2. **Move to work/:**
   ```bash
   mv k1a_run.py work/k1a_run.py
   ```
   Do not edit.

3. **Commit with provenance:**
   ```bash
   git add work/k1a_run.py
   git commit -m "K1a RUN: harness by Claude, executed by operator. Verdicts unadjudicated."
   ```

The operator verifies the hash, moves the file, runs it, and commits
the outputs. The operator does NOT edit the harness.

See commit `0565013` (2026-09-12) for an example of the injection
harness variant, and the subsequent retrodiction commit for the
retrodiction variant.
