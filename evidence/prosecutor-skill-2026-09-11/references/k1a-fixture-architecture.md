# K1a Fixture Architecture (Pre-registration falsification bundles)

**Context:** K1a is a successor run to K1 (which was RED due to environment, harness, and fixture contamination). K1a fixtures are authorship-split, sealed before code, and structured to prevent the three failure modes.

---

## Per-check structure

```
injections-k1a/k1-N/
├── index.md                    # Case table (expected, rationale, hard Y/N) + property statements
├── properties.py               # Hypothesis generators for negative space
├── positive/
│   ├── p-case-one.md          # 10 incident-derived fixtures
│   ├── p-case-two.md
│   └── ... (no numerals in content; case id in filename only)
└── negative/
    ├── n-valid-case-one.md    # 3 hand-authored hard negatives
    ├── n-valid-case-two.md
    └── n-valid-case-three.md
```

---

## Constraints that prevent K1 contamination

### 1. No numerals in parsed content
- Removes the "-01" → −1 parsing bug (K1 C1 defect)
- Case identity lives **in filename only** and **in index.md only**
- No `# packet <case>` headers; no `# case` line
- Fixtures are raw content the check parses, no labels embedded

### 2. Three hard negatives per check (K1a decision)
- Hypothesis properties are published *before* code exists
- A wrong property + hand negatives expose each other (disagreement is a finding)
- Hard negatives are incident-derived, author-split (same as positives)
- Properties stay silent on them; any exception is a property defect

### 3. Positive fixtures are incident-derived
- Trace to specific ledger entries or sealed incidents
- Record the source in index.md under each fixture's rationale
- Example: K1-3 positives trace to `ledger/leg-a-closed-2026-09-09.md §3/§4`

### 4. properties.py: 200+ examples minimum per property
- Hypothesis strategies generate the negative space (inputs that MUST NOT fire)
- Declared from §2 definitions alone (no import of check code)
- Generated cases have no author-supplied labels (prevent label-parsing regressions)

### 5. index.md structure
```
# K1-N Fixtures — [Title]

Positive fixtures (must fire): [N] cases where [check fires]

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-... | FINDING  | ...incident ref... | Y |

Negative fixtures (must stay silent): [N] cases where [check silent]

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-... | SILENT   | ...structure... | N |

## Properties

**property_name**: Generates [what]. Minimum [N] examples.
- Requirement 1
- Requirement 2
- Property must be written from §2 definition alone

[Optional: source incident, design note, related checks]
```

---

## Authorship split (K1a procedure)

- Fixture author does NOT write the check code for that check
- Code author does NOT read the other author's fixtures (read §2 definitions only)
- Both agents read the sealed checker-k1a-prereg.md document (definitions locked, single source)
- Contamination is bounded to definitions, not implementations or fixtures

---

## Session example

**K1a INJECTIONS (Hermes half): K1-3..K1-6** — 2026-09-11
- 62 total files (17 K1-3, 15 each for K1-4/K1-5/K1-6)
- 40 fixtures (10+3 per check × 4 checks)
- 4 properties.py files with Hypothesis strategies
- 4 index.md tables with full case documentation
- Committed before any check code exists (seal blocker)

All positive fixtures trace to sealed incidents:
- K1-3: ledger/leg-a-closed §3/§4 insertion and renumbering
- K1-4: work/r8-grep-2026-09-10.txt (31-char gist ID dropped, 65-char SHA truncation, etc.)
- K1-5: MANIFEST.sha256 @7d4aad7 duplicate hash (53ca0569…)
- K1-6: .yaml/.json parse failures in manifest paths
