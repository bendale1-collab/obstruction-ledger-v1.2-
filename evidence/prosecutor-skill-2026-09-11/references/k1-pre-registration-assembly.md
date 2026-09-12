# K1 Pre-Registration Input Assembly

**Domain:** When the founder asks for "K1 pre-registration inputs" — assemble only, author nothing.
**When to use:** Any survey request mapping candidate checks to files, commits, and existing tooling.

## The four-part assembly contract

The founder's standard K1 input request has four parts. Return all four, paths only, no design proposals, no recommendations, no next steps:

- **a. Commit list** — full range `SEAL_COMMIT..HEAD` with full SHA, UTC timestamp, one-line subject.
- **b. Candidate scope** — for each candidate check: exact file paths in scope + where each candidate is currently written (file + commit).
- **c. Existing checker interface** — how checks are invoked, input format, output format. Paths only (Telegram strips code blocks).
- **d. Overlap analysis** — which existing checks overlap the candidates, if any.

## Commit list with UTC conversion (macOS)

`git log --format="%H %ai %s" SEAL_COMMIT..HEAD` prints local-timezone offsets. Convert with Python, not gdate (gdate is not installed on this macOS by default):

```python
import subprocess, datetime, re
out = subprocess.check_output(['git', 'log', '--format=%H %ai %s', 'RANGE'], text=True)
for line in out.strip().split('\n'):
    m = re.match(r'([a-f0-9]{40})\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+([+-]\d{4})\s+(.*)', line)
    sha, dt, tz, msg = m.groups()
    oh, om = int(tz[:3]), int(tz[0] + tz[3:])
    utc = (datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
           - datetime.timedelta(hours=oh, minutes=om)).replace(tzinfo=datetime.timezone.utc)
    print(f'{sha} {utc.strftime("%Y-%m-%dT%H:%M:%SZ")} {msg}')
```

Note: `TZ=UTC gdate` fails — gdate is not installed; the pure-Python conversion is the reliable path.

## K0 checker interface (v0.1, as of 2026-09-10)

- **Invocation:** `python3 work/k0.py --manifest MANIFEST.sha256 --registry-dir registry --extra-corpus-dirs=work <files...>`
- **Input:** one or more report `.md` file paths; reads MANIFEST.sha256 for corpus files, registry/ for control YAMLs. No stdin, no config file.
- **Output:** JSON array on stdout, one element per file:
  `{"file": str, "checks": {"C3": {"total", "matched", "unmatched": [str]}, "C6": [str], "R1": {"registry_count", "matched", "controls_without_verdict": [str]}}}`
- **Validation harness:** `python3 work/k0-test.py` — builds injection set, runs all packets, computes TP/FN/FP/TN per check, prints recall/FP-rate table, acceptance gate recall ≥ 0.9 AND FP ≤ 0.05 per check.

### Implemented vs designed (KNOWN GAP — do not assume)

K0 v0.1 **code** (`work/k0.py`) implements **C3, C6, R1** only. The design reference
(`k0-checker-design.md`) also describes **C1** (prose-table number mismatch) — **not implemented in code.**
No C2, C4, C5, C7, C8, C9, or R2 exist in any spec or code file. When answering
"which checks overlap the candidates," report this mismatch — do not assume the
design doc describes the running tool.

## Candidate-state discipline (pitfall)

The founder may name a count of candidates ("the four K1 candidate checks") that
does not match the ledger. **Re-read the K1 candidate table fresh each session —
the count changes as the founder directs.** Historical notes go stale:
- 2026-09-10 (early): the table held **three** candidates (quote-vs-anchor byte
  check, divergence-declaration check, section-structure stability), while the
  divergence cadence rule was filed as a **standing rule** (rule 7), not a fourth
  candidate.
- 2026-09-10 (later): the founder directed **K1 candidate 4 — file identifier-length
  check**: every hash, SHA, and gist ID in a report must match its canonical length
  (64 hex SHA-256 / 40 hex SHA-1 / 32 hex gist ID) and, where an anchor exists, its
  canonical value. Source: three truncated gist-ID occurrences, 2026-09-10.

Correct behavior: report what exists NOW, flag any mismatch, and do NOT invent
candidates. If the founder's count exceeds the table, say so and list what is missing.

## Sealed closed-record rule (standing rule 8)

Closed result documents (e.g. `leg-a-closed-2026-09-09.md`) receive **no edits and
no insertions after seal**. Corrections and commentary live in the ledger. EOF
pointers only. The mid-file blast-radius insertion (2026-09-10) was the third
instance of such an edit; it was NOT reverted but filed in RULE-IN-CLOSED-RECORD
(third instance) in `ledger/sealed-file-append-only.md`. Rule 8 was then filed in
the standing-rules index.

## K0 checker scope correction (authoritative, 2026-09-10)

Founder-filed correction appended to `work/k0-results.json` (commit a8e11c8):

**K0 v0.1 implements C3, C6, R1 only. C1 designed, unbuilt. C2, C4, C5, C7, C8,
C9, R2: names, no spec, no code. The "nine checks" description is superseded.**

When describing K0 capability, use this exact scope. The design doc
(`k0-checker-design.md`) describing C1 as a fourth check is a DESIGN doc, not the
running tool — code implements C3/C6/R1 only.

## Identifier-length audit procedure (K1 candidate 4 technique)

When auditing a hash/SHA/gist-ID for length correctness across git history, use pickaxe + per-commit grep:

```
# Step 1: find every commit where the substring count changed
git log -p -S <SUBSTRING> --all --format='%h %cI %s'

# Step 2: for each commit returned, grep all occurrences
for c in <commits>; do
  echo "=== $c ==="
  git grep -n <SUBSTRING> $c 2>&1 || echo "NO_HITS"
done
```

**Table output format** — never counts-only, every row:

```
commit | path | line | full line text | truncated? (chars)
-------|------|------|---------------|-------------------
```

**Key distinctions when classifying:**
- **Full ID in URL** (e.g. embedded in `https://gist.github.com/.../FULL_ID`) → NOT truncated (the URL wouldn't work otherwise). The pickaxe `-S` catches it because the substring changed, but the value in the URL context is the full ID.
- **Truncated ID in prose** (e.g. `Gist ID: TRUNCATED_ID`, `(...TRUNCATED_ID...)`) → flagged. Compare against canonical length (64 hex SHA-256 / 40 hex SHA-1 / 32 hex gist ID).
- ANCHORS.md MUST record the canonical gist ID. If it doesn't, that's a gap — the file is an anchor registry but has no anchor reference.
- Untracked files are invisible to `git log -S`. If a file exists on disk but is untracked/never committed, the pickaxe won't find it — audit separately with `grep -n <SUBSTRING> <untracked_file>`.

**Tracking corrections:** use `git diff <truncated_commit> <correcting_commit> -- <file>` to confirm what changed. Report a corrections table:

```
File | Truncated at | Correcting commit | Original | Corrected to
```

## Replay-limitation awareness

A replay from a bundle commit (e.g. d7043bba) yields only the sealed copy of files
at that commit. Corrections, divergence declarations, and later standing rules live
in unsealed files (e.g. `ledger/rendering-as-record.md`, `ledger/standing-rules.md`)
and are NOT reconstructed by bundle replay alone. When a survey asks where a rule is
"currently written," check both the sealed file AND the unsealed ledger — the latest
statement may be in the unsealed one.

## Divergence-report staleness

The divergence report compares SEAL_COMMIT vs a HEAD snapshot. If commits exist past
that snapshot, the report is stale — say so and file the cadence rule (runs at every
gate, pre-condition of authorizing compute) rather than re-running. Re-running a
stale report without authorization violates the standing block.
