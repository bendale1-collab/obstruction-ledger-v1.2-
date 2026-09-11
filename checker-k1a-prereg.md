# CHECKER K1a — PRE-REGISTRATION v0.3

STATUS: v0.3 FINAL. Founder-adjudicated 2026-09-11. Commit unchanged; do not edit.
Any edit after the K1a-PREREG hash is published invalidates the seal; corrections
are appended to the gist, never edited in. Not yet sealed. Not yet published.
AUTHOR: Claude (frontier tier). Hermes did not author this document and must not edit it.
SUPERSEDES: nothing. K1 (FREEZE_HASH 34f06514…7dacd, K1-RUN 61459091…844e) stands
as published, RED, and is not amended. This is a successor run, not a repair.

## 0. Why K1a exists

K1 ran at d00f75f and was adjudicated RED (ledger/k1-red-2026-09-11.md, 893b7a1).
Three independent causes, none of which was a check being wrong:

1. ENVIRONMENT — K1-1 and K1-2 use PEP 604 `X | None`; the interpreter was
   Python 3.9.6. Both failed at import. 40 fixtures and 4 retrodiction rows
   produced no result. Workflow defect, Claude-attributed.
2. HARNESS — work/k1-test.py hardcoded three scripts (lines 165–192), no
   discovery loop, no evaluators for K1-3..K1-6. Agent B's four checks were
   committed at 2042bf2 and never called. Workflow defect.
3. INJECTION — every Claude-authored C1 fixture opened `# packet <case>`; the
   prose-number extractor read `-01` as −1 and compared it to every table value.
   9 of 10 negatives false-fired. C1's rounding logic was demonstrably correct
   (neg-04 computed 0.985 vs 0.970 accurately). Injection defect, Claude-attributed.

K1 measured nothing about whether the checks work. It measured that the process
around them holds: the fixtures were public before any code existed, so all three
causes are attributable and none can be argued away after the fact.

K1a re-runs the same seven check definitions, unchanged, under gates that make
each of those three causes impossible rather than merely unlikely.

## 1. Carried forward unchanged

- The seven check definitions in checker-k1-prereg.md §2. Not edited. K1a cites
  them by the K1-PREREG hash 34f06514…7dacd; that document remains the spec.
- The 14 retrodiction rows R1–R14 of §3, with the same expected outcomes.
- The authorship split: whoever writes a check's fixtures does not write its code.
- The holdout: 7 rows, founder-held, hash
  fd2d6faa9b06d8fc6e108eac70583b889ab6e2424eea0f2b4891fe3c9dc8c8e1, published at
  K1-RUN and NEVER REVEALED. It carries into K1a intact. The RED cost no holdout
  value.
- Adjudication under §4/§5 of the K1 pre-reg: a failing expected outcome is
  filed, never edited to match the result.

## 2. What changes, and why each change is forced by a named K1 cause

### 2.1 Interpreter (cause 1)
- `.python-version` = 3.11, `requires-python = ">=3.10"` in pyproject.toml.
- `uv run` is the ONLY entrypoint. Direct `python3 foo.py` invocation is a
  procedure violation, not a result.
- Verified by experiment 2026-09-11: uv 0.12.13 installed and refuses a
  non-conforming interpreter.

### 2.2 Gate 0 — import smoke test (cause 1)
Before any fixture runs, every check module is imported and invoked with empty
input. Expected: 7/7 IMPORT-OK and `[]` from each. A single IMPORT-FAIL halts
K1a before the run; the failure is filed and K1a does not proceed that day.

Verified against the known defect 2026-09-11: the smoke loop returned
IMPORT-FAIL for exactly k1_1.py and k1_2.py and IMPORT-OK for the other five —
the precise partition of RED cause 1. Five lines of shell, no dependency.

### 2.3 Gate 1 — static syntax gate (cause 1, complement)
`uvx ruff check --select FA,UP work/k1a/` must be clean at the declared target.
Verified 2026-09-11: ruff 0.16.7 flagged FA102 at k1_1.py:44 and k1_2.py:26,
39, 77 — the exact failing lines.

REJECTED: vermin. Falsified 2026-09-11. `uvx vermin -t=3.9 --violations work/k1/`
reported "Minimum required versions: 3.7" for code that cannot import on 3.9,
and did not flag the PEP 604 annotations. `X | None` is valid 3.9 *syntax*; the
failure is a runtime TypeError on annotation evaluation, which an AST scan does
not see. A research report recommended vermin for exactly this bug; the report
was tested before adoption and was wrong. Recorded so the recommendation is not
re-adopted from the same source.

### 2.4 Harness (cause 2)
- pytest with `pytest_generate_tests` enumerating work/k1a/ at collection time.
  One parametrized test over every check script found on disk. A hardcoded list
  is a procedure violation.
- `pytest --collect-only` output is published with the run: it must show all
  seven checks before any assertion runs.
- coverage.py with `--cov-branch --cov-fail-under` over work/k1a/. A committed
  check that is never exercised FAILS. "NO_CODE" is not a permissible outcome
  for a check whose file exists at HEAD.

### 2.5 Fixtures (cause 3)
K1 fixtures are sealed, published, and NOT edited. K1a uses a new fixture set,
separately sealed. The K1 set stands as the record of what was tested and why
it failed.

Changes to the new set:
- No numerals anywhere in content the check parses. Case identity lives in the
  filename and in index.md only. For markdown fixtures, no `# packet <case>`
  header — no header at all unless the check under test requires one.
- Negatives are generated by Hypothesis properties for every check where the
  input has a declarable shape. Generated inputs carry no author-supplied
  labels, so the cause-3 class cannot recur in fixture content. It CAN recur in
  a wrongly declared property (see §6). Therefore (DECIDED 2026-09-11) each
  check also carries three hand-authored hard negatives, incident-derived,
  written under the same authorship split as the positives. A property and a
  hand-authored negative that disagree is a finding about the property, filed
  before any code is adjudicated.
- Positives remain hand-authored and incident-derived. That is where their value
  is: each traces to a defect that actually occurred in this run.
- Minimum generated cases per property: 200 (DECIDED 2026-09-11).

### 2.6 Seal object (independent of the three causes)
The seal object is the sorted list of (manifest path, blob SHA at the seal
commit), sha256-digested. Per path via `git rev-parse <commit>:<path>`.
Subset digest at 7d4aad7: 020bb559e6f712892dec0c91439cfcbe895ae1b8aa2edb5a63787e10150f5639

REJECTED: `git rev-parse HEAD^{tree}`. Falsified 2026-09-11: commits 437c58f and
HEAD touched only files outside the 19 manifest paths, yet tree hashes differ
(e44577671fd59845ce7637e7207d349f9f9f69ef vs a64bcfdb9126938dc67693c4053cb4d2dbd63ed1)
while the subset digest is identical at both
(3d9c8dec14e62e78b7afefbbb803dac844fcd52fb1674a8ab292b6160925229b). A whole-repo
tree hash moves on every commit, sealed paths or not.

No seal is emitted while `git status --porcelain` shows any modified tracked file.

## 3. Pre-stated outcomes

### 3.1 Gates (stated before the run, in order)
| Gate | Expected | On failure |
|---|---|---|
| G0 smoke | 7/7 IMPORT-OK, 7/7 emit `[]` on empty input | halt, file, do not run |
| G1 ruff FA,UP | clean | halt, file, do not run |
| G2 collect-only | all 7 checks listed | halt, file, do not run |
| G3 clean tree | no modified tracked files | halt, file, do not run |
| G4 divergence | clean-or-declared at the seal commit | halt, file, do not run |

All five gate outputs are published with the run, pass or fail.

### 3.2 Injection and retrodiction
- Per-check: recall 1.0, FP 0.0, on hand-authored positives and generated negatives.
- The 14 retrodiction rows R1–R14, expected outcomes unchanged from the K1
  pre-reg §3.
- Then, after both code commits and the public run: the 7 holdout rows.

### 3.3 New retrodiction rows, K1a-specific
| Row | Target | Check | Expected |
|---|---|---|---|
| RA-1 | work/k1/k1_1.py, k1_2.py @b21abb0 under py3.9 | G0 smoke | IMPORT-FAIL ×2 |
| RA-2 | work/k1/ (all 7) @d00f75f under py3.9 | G0 smoke | IMPORT-OK ×5, IMPORT-FAIL ×2 |
| RA-3 | work/k1/ @d00f75f | G1 ruff FA102 | FINDING at k1_1.py:44 and k1_2.py:26 |
| RA-4 | work/k1-test.py @d00f75f | G2 collect-only | 3 of 7 checks — the harness defect, reproduced |
| RA-5 | injections/c1/neg-01 @a094184 (K1 set, unedited) | C1 | FINDING — the contamination, reproduced on the sealed fixture |

RA-1 through RA-5 are the gates retrodicting the three RED causes on the sealed
K1 artifacts. If a gate cannot reproduce the failure it was built to prevent,
that gate is not verified and K1a does not rely on it.

## 4. Procedure

1. No open items. §2.5 resolved: Hypothesis negatives plus three hand-authored
   hard negatives per check.
2. Gates G3, G4 run. Clean-or-declared.
3. K1a-PREREG seal: subset digest over this document alone. Publish to gist.
   Founder-only, appended after the K1-RUN block.
4. New fixtures authored per the §1 split. K1a-RUN seal: subset digest over this
   document plus all fixtures plus the unchanged holdout hash. Publish.
5. Code: work/k1a/, written after the K1a-RUN hash is published. Same two-agent
   split, neither agent reading the other's fixtures. Agents do not run the
   checks; gates G0–G2 are run by the harness operator, not the code authors.
6. Gates G0–G2. Published.
7. Injection run, then retrodiction R1–R14 and RA-1–RA-5. Full tables. A
   count-only report is a failed report.
8. Founder reveals the holdout. Seven rows run. Full table.
9. Founder adjudicates GREEN/RED per row.

## 5. Pass / kill
- K1a GREEN: all five gates pass, all injection thresholds met, all retrodiction
  rows match including RA-1..RA-5, and all seven holdout rows match.
- A gate failure is not a check failure. It halts the run and is filed as a
  gate result.
- Any expected outcome that fails is filed. Never edited to match.
- No fixture, threshold, or gate may be chosen by looking at what it excludes.

## 6. Known limits, stated in advance
- Same repo, same domain. Generalization untested; that is the post-K1a step
  (one packet from an unrelated domain).
- Two code agents, different models and profiles, but both read all seven
  definitions from one sealed document. Contamination is bounded to definitions,
  not implementations or fixtures (standing-rules.md, K1 section).
- Hypothesis-generated negatives test the property as declared. A wrongly
  declared property produces confidently wrong negatives, which is the cause-3
  class relocated rather than eliminated. Mitigation: properties are published
  with the fixtures, and three hand-authored hard negatives per check give a
  wrong property something to disagree with. Detectable, not impossible.
- Repo integrity remains procedural, not enforced (ledger/multi-writer-unattributed.md).
- The gist provides third-party-witnessed ordering, not proof of time (gist item 9).
