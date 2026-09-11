# K1a K1-3 Fixture Defect

## Defect type

Injection defect (§4). Fixture structure does not match check interface.

## Check interface

K1-3 (section-structure stability) compares two states:
  before_file after_file before_commit after_commit

The check extracts ATX headings from both files and reports any header
that was inserted, removed, renumbered, or modified between them.

## Sealed fixture set (at 7b887de)

All 13 K1-3 fixtures are single `.md` files:
  10 positives in injections-k1a/k1-3/positive/
   3 negatives in injections-k1a/k1-3/negative/

No fixture contains a before/after pair. Each positive file is a single
markdown document whose content *describes* a header change (e.g. a file
with a header that "did not exist at seal"), but it is not paired with
the seal state it diverges from.

## Consequence

No before_file exists in the sealed set. The check cannot be invoked
against these fixtures with a valid before state. The fixtures are
structurally untestable by the sealed interface.

## Authorship

Mahamara session authored the K1-3..K1-6 fixtures (commits 3cebd19,
898c566). The 591d638 harness patch (negatives as before==after,
positives as needs-pair) was written by the same author who wrote the
fixtures. That patch is withdrawn as a scoring path: it was authored by
the fixture author to work around the fixture author's defect.

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

injections-k1a/k1-3/ contains no `properties.py` file. The negative-space
property was not delivered for this check.
