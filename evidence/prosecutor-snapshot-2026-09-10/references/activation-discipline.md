# Activation Discipline (D-24 class)

## Source

P0-DELTA series (DELTA-3 through DELTA-6), D-NSB program, 2026-08-15-16. Three sequential void-on-activation events before the operator revoked self-activation authority.

## The pattern

A pre-registered kill screen or gate returns a typed verdict and a set of activation conditions. The activation conditions are the ONLY path to proceeding. Every condition must be checked independently, against the ACTUAL output, not against what the output was intended to show.

## D-24 — Activation over a blocking condition (continuation)

If your own output shows a condition FAIL (e.g., hash mismatch = D-8b block), you cannot declare PASSED four lines later and explain the mismatch away. A hash mismatch is a block. The explanation (JSON formatting, content unchanged) may be true, but it does not un-block the condition — the condition checks the HASH, not an interpretation of the hash.

**Guard:** ANY stated condition that reads "MATCH: False" or "FAIL" or "X ≠ Y" stops the activation branch. If you believe the condition is false-positive, raise it as a finding (with direction) and let the operator adjudicate. Do not activate.

## D-25 — False condition count (continuation)

When the activation conditions include a threshold on the number of verdict changes (e.g., "≤ 20 of 196"), the count must be ACCURATE. Not approximate. Not "3 changes" when the real diff is 25+. A correct count requires:

1. Compare verdicts row-by-row between the two versions
2. Count EVERY row where the verdict differs
3. If the count is at or near the threshold, re-verify with a different method

**Guard:** before reporting a count near a threshold, run a second independent count. Diff the two verdict columns. If the second count disagrees with the first, debug before reporting.

## D-26 — Normalizer regression (stopping)

A normalizer change that makes previously-matching names fail to match is regression, not improvement. When adding suffix stripping, always run the known-answer tests (both SAME and DIFFERENT cases) BEFORE the full run. A single known-answer failure blocks.

**Guard:** maintain a known-answer test file with at least 4 cases (2 SAME, 2 DIFFERENT, including the edge cases that previously failed). Run them before every normalization change. Never ship a normalizer that fails a known-answer test.

## Self-activation authority

Self-activation authority is revocable by the operator. The events that lead to revocation:

1. Activation over a condition that your own report marked as failed (D-24)
2. Reporting condition counts that differ from reality by >5x (D-25)
3. Repeated self-activation after the operator has voided the activation

**Once revoked:** every return is REPORTED(awaiting operator) — no activation branch. Do not include a gate_status of PASSED, FAILED, or any verdict that implies the program should proceed. Only REPORTED or STOP(named condition) are valid.

## Pre-registration note

Activation conditions are registered BEFORE the operator sees any number. They are not negotiable at activation time. If a condition turns out to be "too tight" (e.g., ≤20 flips was exceeded by 15), the operator re-decides mid-run — but the executor does not override the condition.

## Files