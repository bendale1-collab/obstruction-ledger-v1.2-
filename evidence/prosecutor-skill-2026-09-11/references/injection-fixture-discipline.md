# Injection Fixture Discipline

**When to use:** Designing test cases for adversarial validation checks (K1, K0, or any checker that needs positive/negative injection sets).

## Core rules

### Hard-negative requirement (5/10 minimum)

At least 5 of every 10 negatives **must share file type, identifiers, and structure with the positives** and differ only in the checked property. A blank file or unrelated content counts as a negative but does NOT count toward the five.

**Why:** Easy negatives (empty files, completely different formats) prove the check runs, not that it discriminates. Hard negatives prove the check isolates the exact defect.

### Write-before-code ordering

Injections must be committed **before any check code exists**. This prevents the temptation to sketch the check first and choose cases it passes. The git log order is the proof: `git log --oneline` must show the injection commit before any code commit for that check.

### Class-level organization

Organize fixtures by check ID, not by session or task:
```
injections/
  k1-3/
    pos-01/ (seal.md, head.md)
    neg-01/ (seal.md, head.md)
    index.md
  k1-4/
    pos-01.md, neg-01.md, ...
    index.md
```

Each check gets:
- 10 positive fixtures (must fire the check)
- 10 negative fixtures (must stay silent)
- One `index.md` with a table: case | expected | rationale | hard-negative Y/N

### Index.md format

```markdown
## Positives (must fire)
| Case | Expected | Rationale | Hard-neg |
|------|----------|-----------|----------|
| pos-01 | FINDING | 31-char gist ID (dropped "1" at pos 11) | N |
...

## Negatives (must stay silent)
| Case | Expected | Rationale | Hard-neg |
|------|----------|-----------|----------|
| neg-01 | SILENT | Correct 32-char gist ID after label | Y |
...

Hard-negative count: 5/10 (neg-01 through neg-05).
```

### Thresholds (pre-stated)

- **Recall = 1.0** on 10 positives (all must fire)
- **FP = 0.0** on 10 negatives (all must stay silent)
- Deterministic code on predefined cases has no tolerance. A single miss halts the run for that check; the miss is filed and adjudicated (injection defect vs code defect), never silently re-run.

## Fixture design patterns

### K1-3 (section-structure stability)

- **Positives:** Insert header, remove header, renumber header, change header level, change header text, cascade renumber
- **Negatives (hard):** Append new headers after originals (originals unchanged), add prose paragraphs under existing headers (no header change), byte-identical seal/head pair
- **Negatives (easy):** Empty files, plain text with no headers, code blocks added under headers (not headers themselves)

### K1-4 (identifier well-formedness)

- **Positives:** Truncated (31 chars), inserted (33 chars), wrong length (63/65 chars), value mismatch (correct length, wrong value)
- **Negatives (hard):** Correct-length identifiers under labels, correct short SHA (7 chars), correct 40-char git SHA
- **Negatives (easy):** QUOTED/DERIVED header blocks (skipped by check), non-hex strings, empty files

### K1-5 (duplicate hash)

- **Positives:** 2-line dup, 3-way dup, 2 separate pairs, manifest mirroring real structure with 1 dup
- **Negatives (hard):** 19-entry manifest all unique, 10-entry all unique, mixed extensions all unique, last-hex-char-differ (same path, hashes differ only in final char)
- **Negatives (easy):** Empty file, 1-entry, blank lines between entries

**Last-hex-char-differ pattern:** Two manifest lines with identical paths, hashes differing only in final hex char (e.g. `a1b2c3...a1b2  file.md` vs `a1b2c3...a1b3  file.md`). Expected SILENT because hashes are distinct. Hard-negative because it shares file type, structure, and path format with positives. Tests that the check correctly identifies distinct hashes as non-duplicates even when they're near-identical.

### K1-6 (extension vs content)

- **Positives:** Comment-header prose in .yaml, unquoted colons, truncated JSON, tab indentation, trailing commas
- **Negatives (hard):** Valid YAML key-value pairs, valid YAML lists, valid JSON objects/arrays, valid nested mappings
- **Negatives (easy):** .md/.txt/.py files (out of scope), empty .yaml (parses as None)

## Multi-agent blind-split protocol (fixtures)

Cross-reference: see also `references/split-authorship-protocol.md` for the code-authorship split (same principle, applied to check implementations rather than fixtures).

When two agents write fixtures for different checks (e.g. Claude writes C1/K1-1/K1-2, Hermes writes K1-3–K1-6), the committing agent MUST NOT read the other agent's fixtures before committing. The protocol:

1. **Hash-verify the tarball** — `sha256sum` the archive against the founder-published hash. MATCH or MISMATCH, both strings in full. On MISMATCH, stop.
2. **Extract at repo root** — `tar xzf`. Do not cat, open, view, or grep anything under the other agent's directories.
3. **Delete the tarball** — `rm` the archive.
4. **Commit unchanged** — `git add injections/.` and commit with a message explicitly stating the committing agent did not read the other agent's fixtures (e.g. "Placed by Cowork, hash-verified, not read by the committing agent").
5. **Report** — SHA, file counts per directory (ls entries, not find -type f), and `git status --porcelain`.

**Why:** The §4 separation rule means the code-writer must not see the fixtures before writing code. If the committing agent reads fixtures for checks it will later write code for, the run is void. The commit message is the audit trail proving the separation held.

**File counts:** Use `ls <dir> | wc -l` for directory entry counts (includes index.md + case files/dirs), not `find -type f | wc -l` which counts leaf files inside subdirectories. The user expects entry counts matching the fixture count + 1 (for index.md). **Exclude `__pycache__`** — a `properties.py` that gets imported (e.g. by a local test run before packaging) leaves a `__pycache__/*.pyc` directory in the tarball; `ls | wc -l` will count it as an extra entry and `find -type f` will count the compiled bytecode as a fixture file. Filter it explicitly: `ls -1 <dir> | grep -v __pycache__ | wc -l`. (Round-4 tarball extraction, 2026-09-11: c1/k1-1/k1-2 each carried a `__pycache__/properties.cpython-312.pyc`; raw `find -type f` counts were 17/30/79 against an expected 16/16/16 until pycache was excluded.)

## Adjudication branch (for ambiguous cases)

If a fixture fires when expected silent, or stays silent when expected to fire:
- **Injection defect:** The fixture is malformed. File it, replace with a corrected fixture, re-run.
- **Code defect:** The check has a bug. File it, fix the check, re-run against the same injections.
- **Spec defect:** The check definition is ambiguous. File it, clarify the spec, re-design affected fixtures.

Never silently re-run. Never edit the expected outcome to match the result.

## Example from this project

K1 step 5 (2026-09-10): 80 fixtures for K1-3/K1-4/K1-5/K1-6 committed at `ea7236a`. No check code existed. 104 files (10 pos + 10 neg per check × 4 checks + 4 index.md). Hard-negative count: 5/10 for all four checks. Git log proves injection commit precedes all future code commits.

**Correction at `27a51a1`:** neg-07 was a structural duplicate of neg-03 (both single-entry manifests). Replaced with last-hex-char-differ: two manifest lines with same path, hashes differ only in final hex char (e.g. `...a1b2` vs `...a1b3`). Expected SILENT because hashes are distinct (not duplicates). Hard-negative count raised to 6/10. Lesson: review all 10 negatives against each other before committing.

**Claude-half split-author execution at `a094184` (2026-09-10):** 176 files for C1/K1-1/K1-2 placed via hash-verified tarball (`4b905047...`). Hermes extracted, committed, and did NOT read any fixture content. Entry counts: c1=21, k1-1=21, k1-2=21 (index.md + 20 cases each). K1-1 and K1-2 use per-case subdirectories (anchor.txt + report.md, or seal/head/MANIFEST layout), so leaf file counts are higher: k1-1=41 files, k1-2=114 files. Total across both halves: 280 injection leaf files.
