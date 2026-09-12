# Execution Output Discipline — Standing Rules

Compiled from NSB-G0-series rulings (D-53, D-43, D-50, D-57) and the
battery methodology from G0-5/G0-6.

## 1. File Manifest (D-53 standing rule, permanent)

Every return lists ALL output files produced during execution — hashed,
full 64-char SHA256 — whether or not they support the narrative. An
executed run that goes unreported is defect class D-53 by name.

Format:
```
File                                       SHA256 (full 64)                       Bytes
────────────────────────────────────────────────────────────────────────────────────────
output.json                                abcdef1234567890abcdef1234567890abcde...  12,345
report.txt                                 fedcba0987654321fedcba0987654321fedc...   8,419
```

Rules:
- Every file, every time. No placeholder strings like "(new)" or "(re-run script)".
- Includes scripts that produced the output, not just the output itself.
- Include files that contradict the narrative, not just supporting ones.
- Hash the bytes as read from disk at report time.

## 2. Full 64-char Digests (D-43, D-50, D-57)

All SHA256 hashes are full 64-character hex strings. Truncated prefixes
(20-char, 16-char, etc.) are assertions, not digests, and replaced with
full digests on first occurrence.

## 3. Typed-Denominator Battery Methodology

When testing a classifier's accuracy against ground truth:

### Truth-label validity
- A battery row whose honest truth is TYPE-UNPARSED (deficiency genuinely
  uncited and undescribed in the source text) is VALID for exchange/coverage
  recall testing but EXCLUDED from the type accuracy denominator.
- State this exclusion per row.
- If exclusions drop the type denominator below the minimum threshold,
  extend the seed sequence (next items in the seeded random order) until
  enough typed rows exist.

### Thresholds
- Labeler LICENSED only when BOTH fields pass:
  - EXCH pass ≥ (n − 1)/n (typically ≥ 14/15)
  - TYPE pass ≥ (n_typed − 1)/n_typed at n_typed ≥ minimum (typically 12)
- On STOP: emit every miss with the raw quote vs the labeler's output.
  No local phrase-list patching to pass — that's tuning on the test set.

## 4. Decision Map Pattern

Every measurement threshold uses a three-branch decision map:

```
LICENSED  → threshold fully met. Proceed to next stage.
REPORTED  → within middle band. Operator weighs evidence; may proceed
            or require supplementary data source.
STOP      → threshold failed. Operator decides whether to redesign the
            instrument or accept the result as-is.
```

Branches must be registered BEFORE any number exists. The threshold
values are frozen; the operator decides which branch fired.

## 5. Population Filter vs Taxonomy Edit

A population filter (e.g., voluntary-delisting filter) is evaluated FIRST,
before exchange/rule/language classification. It is NOT a taxonomy edit —
the frozen type map and phrase lists remain untouched.

Precedence: voluntary filter → exchange → rule citation → deficiency
language → UNPARSED.

When a document matches both a population filter AND a deficiency rule,
the result is CONFLICT-{filter} (e.g., CONFLICT-VD): counted, listed,
not resolved. The first-notice document decides the episode's entry label.

## 6. Hash Verification

When a previously-malformed hash is flagged (D-43 class recurring):
- Re-compute and re-emit the full 64-char digest.
- Verify the digest by re-reading the file from disk and re-computing.
- State the hash and the file's byte count.