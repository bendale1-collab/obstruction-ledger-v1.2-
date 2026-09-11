# Ledger Entry — VERBATIM-CLAIM-UNVERIFIED
# Filed: 2026-09-10
# Type: MECHANISM-FINDING

## Finding

The K1-PREREG publication verification (work/r21-gist-verification-2026-09-10.txt)
reported the gist block as "verbatim, no reflow" and the prior text as
"character-for-character identical." The comparison was performed with
`diff` on extracted text lines, which compares logical content (line by line,
newline-terminated), not raw bytes. Continuation-line indentation — the
whitespace alignment of the MANIFEST_FILES / GIT_HEAD / SPEC_VERSION lines
under FREEZE_HASH — may have been flattened by the mobile editor used to
publish Rev E, and diff would not detect this.

## K1-1 target

K1-1 (quote-vs-anchor byte match) must compare bytes including whitespace.
A content-level diff that passes while whitespace diverges is a false PASS.
This finding is recorded as a live target for the K1-1 retrodiction run:
any check that claims "verbatim" must prove it byte-for-byte, including
indentation and trailing whitespace. The r21 report's "verbatim" claim
does not meet that standard and is retracted to "content-match only;
whitespace not verified."

## Correction to r21

r21-gist-verification-2026-09-10.txt stated:
> No reflow. Exact character match against the prepared block.

This is superseded. The comparison was `diff` on extracted text, which
strips trailing-whitespace differences and does not prove byte identity.
A byte-level comparison (sha256 of the K1-PREREG block bytes from gist
vs. the prepared block) is required before K1-1 can score this row.

Filed 2026-09-10. No edits to the gist or to r21.
