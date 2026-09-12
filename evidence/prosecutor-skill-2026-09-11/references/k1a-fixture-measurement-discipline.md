# K1a Fixture Measurement Discipline — Operationalizing Planted Controls

**Session:** 2026-09-11 (K1a-INJECTIONS round 3)  
**Correction source:** User required measurements-driven index construction after fixtures were written.

## Problem

When writing 13 fixtures (10 positives + 3 negatives) for a check, the agent wrote index.md rationales based on assertion ("this fixture should diverge in X way") rather than measurement. When rationales did not match fixture reality, the defect went undetected until review.

## Solution: Measure Before Writing Index

For each check (K1-3 through K1-6), generate MEASUREMENTS.txt by running code on actual fixtures:

### K1-3 (section-structure stability)
For each fixture pair (seal version vs head version):
```bash
diff <(grep '^#' seal.md) <(grep '^#' head.md)
```
Output: nature of change (header removed, inserted, renumbered, text modified, etc.)  
**Index rationale must match the diff output character-for-character.**

### K1-4 (identifier well-formedness)
For each fixture:
```python
python3 -c "
import re
content = open(fixture).read()
for match in re.finditer(r'([a-fA-F0-9]{6,})', content):
    hex_str = match.group(1)
    pos = match.start()
    preceding = content[:pos].split()[-1] if pos > 0 else '(no label)'
    print(f'{fixture} | {preceding} | {len(hex_str)}')"
```
Output: `file | label preceding | hex length` (3 columns)  
**Index rationale states "X chars; canonical Y" and measurement must show the exact hex length.**

### K1-5 (duplicate hash within manifest)
For each fixture:
```bash
wc -l fixture  # line count
awk '{print $1}' fixture | sort -u | wc -l  # unique hash count
```
Output: `file | line count | unique hash count`  
**Index must declare both line and unique-hash counts.**

### K1-6 (declared extension vs content)

**Do NOT use a try-yaml-then-json fallback chain.** §2 mandates the parser
by declared extension, not a universal parser guess. YAML's grammar is
permissive enough to accept most malformed JSON as a scalar or bare mapping,
so a yaml-first fallback will silently mask JSON parse failures — this
produced a real defect (round 3, 2026-09-11): six fixtures intended to FAIL
(comments, NaN, trailing commas, single quotes, unquoted keys, duplicate
keys) instead measured YAML_OK, contradicting their own expected column.

Use the exact §2 parser per fixture's intended type:
```bash
# .json fixtures:
python3 -c "import json,sys; json.load(open(sys.argv[1]))" fixture.txt; echo "exit: $?"
# .yaml/.yml fixtures:
python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" fixture.txt; echo "exit: $?"
```
Output: `file | parser | exit code` (parser is `json.load` or `yaml.safe_load`,
never a guess) — 3 columns, not 2.
**Index positive cases must all show exit code 1 under their declared
parser; negatives must all show exit code 0.** If any positive shows exit 0,
the fixture is wrong (make it actually invalid under that specific parser),
not the expectation — YAML's duplicate-key and permissive-scalar tolerance
in particular defeats naive "make it look wrong" fixture writing. Verify
each candidate fixture against the real parser before adding it, not after.

## Workflow

1. **Write fixtures with exact lengths.** For K1-4, use hex strings of exact canonical length (32, 40, 64, 7 chars). For K1-5, generate manifests with known duplicate patterns.
2. **Run measurements scripts against all fixtures.** Capture output to `injections-k1a/k1-<N>/MEASUREMENTS.txt`.
3. **Write index.md rationales matching measurements exactly.** If MEASUREMENTS.txt shows 31 chars, rationale says "31 chars; canonical 32" — not "one char short" or approximation.
4. **Commit MEASUREMENTS.txt alongside index.md.** Future agents can diff MEASUREMENTS.txt if fixtures are modified.

## Hard negative discipline

- All 3 negatives must differ from each other structurally (not just from positives).
- Each negative must state its hard-negative property (`Y—same X structure, differs only in Y`).
- Check hard-negative counts: K1-3/K1-4/K1-5/K1-6 each have 3. If any negative duplicates another structurally, replace it with a distinct variant.

## Property file discipline

When writing `properties.py`, verify that each property's label list matches §2 of the pre-registration:
- **K1-4:** `Gist ID:` label only (NOT `FREEZE_HASH=`, which takes 64-char sha256).
- **K1-5:** All labels permitted in §2 for hash fields (FREEZE_HASH=, SHA256=, BLOB=, commit, GIT_HEAD=).
- **K1-6:** Test both YAML and JSON separately, since both .yaml and .json paths exist in MANIFEST.

## Rationale matching rule

Every fixture rationale in the index must be independently verifiable by running the measurement code on that fixture. If measurement says "65 chars" and rationale says "64 chars" or "one over," the defect is caught before code review.

Rationales for negatives must also follow: if n-five-all-unique has 5 lines and 5 unique hashes (not 4), the index must state both numbers.

## Source-incident paragraph verification

When an index.md cites specific filenames from a sealed manifest (e.g., "four .yaml paths fail to parse"), verify every filename exists in the manifest before commit. A "phantom filename" defect — listing a name that doesn't exist in the manifest — is the same class as a measurement-vs-expectation contradiction: a claim without verification.

**Pattern (K1a round 3, 2026-09-11):** The K1-6 source-incident paragraph listed four undated `.yaml` names (`chebyshev-mapping-rejection.yaml`, `conv-flag-diagnosis.yaml`, `fourier-diff-tolerance.yaml`, `misidentification-by-acronym-collision.yaml`) that do not exist in `MANIFEST.sha256`. The actual undated twins are `.md` files. The four dated `.yaml` paths (`-2026-09-07.yaml`, `-2026-09-08.yaml`) do exist and do fail to parse. Corrected at round 4 by naming only the dated `.yaml` paths that exist, with the `.md` twins named as `.md`.

**Rule:** Before committing a source-incident paragraph, grep the manifest for every filename cited. If any filename returns zero matches, the paragraph is wrong and must be corrected or the filename removed. Do not rely on memory of what the manifest contains; verify mechanically.

## Tag

Applies to: K1a-INJECTIONS (Hermes half), K1a-INJECTIONS (founder half), any pre-reg check with 10+ fixtures.
