# K1a K1-3 Fixture Defect

## Defect type

Injection defect (§4). Fixture structure does not match check interface.

## Sealed fixture set (at 7b887de)

K1-3 fixtures at 7b887de are 13 single .md files under positive/ and
negative/ (per K1a-RUN-MANIFEST.txt lines for injections-k1a/k1-3/):
  10 positives in injections-k1a/k1-3/positive/
   3 negatives in injections-k1a/k1-3/negative/

## Check interface

K1-3 (section-structure stability) compares two states:
  before_file after_file before_commit after_commit

The check extracts ATX headings from both files and reports any header
that was inserted, removed, renumbered, or modified between them.

## Defect

No before state exists in the sealed set. Each fixture is a single .md
file — there is no paired seal-state file for any of the 13 cases.
The check cannot be invoked against these fixtures with a valid before
state. The fixtures are structurally untestable by the sealed interface.

## Authorship

Mahamara session authored the K1-3..K1-6 fixtures (commits 3cebd19,
898c566).

## 591d638 harness patch withdrawn

The 591d638 harness patch (negatives as before==after, positives as
needs-pair) was written by the fixture author to work around the
fixture author's defect. It is withdrawn as a scoring path.

## Verdict for K1-3 injection rows

All 13 K1-3 injection cases are scored:

  **UNTESTABLE-FIXTURE-DEFECT**

Not PASS. Not FAIL. The test surface is structurally absent.

## K1-3 evaluation surface

K1-3 is still evaluated on:
  - R5, R6, R7 (real commits in the repository history)
  - The seven-row holdout (authored by no code author, unseen by any)

The injection rows do not contribute to the K1-3 score.

## No properties.py

injections-k1a/k1-3/ contains no properties.py file. The negative-space
property was not delivered for this check.

## G3 conditional outcome

Gates file (work/k1a-gates-2026-09-11.txt, line 117) reported G3 as
"CONDITIONAL PASS" with one modified tracked file. checker-k1a-prereg.md
§3.1 has no conditional outcome — gates PASS or FAIL. Recorded here,
not corrected by editing the gates file (which is a committed artifact).
