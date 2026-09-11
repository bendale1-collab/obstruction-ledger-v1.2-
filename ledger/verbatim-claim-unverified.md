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

---

## Instance 3 — 2026-09-10, K1-RUN publication report

The report presented the published K1-RUN block as
"verbatim from gist" with continuation-line indentation
intact. The founder's editor diff shows the published
text has flattened continuation lines. The quoted block
was therefore reconstructed or re-indented, not
byte-fetched. Same defect as instance 1 (Rev D) and
gist correction item 10. The gist is not edited; the
flattened text stands as evidence. This is a live
target for K1-1 at the run.

Filed 2026-09-10. No edits to the gist.

---

## Instance 4 — 2026-09-10, Claude (frontier) session-identity inference

Claude (frontier) read Agent B's self-label "Agent B (Hermes, this session)"
as evidence that A and B were the same session, and halted the run. Session
state showed otherwise: B is 20260909_215809_aa334cf1, default profile,
z-ai/glm-5.3; A is mahamara, qwen/qwen3.7-max. The claim was an inference
from a naming convention, not from the record. Same class as instances 1-3,
frontier tier, committed while auditing for that class.

Filed 2026-09-10.

---

## Instance 5 — 2026-09-11, K1a-PREREG RevG verification report

The report (no file name stored; verbal output) stated: "Prior line
differences (byte-level, whitespace included): NONE (no prior Rev F
fetch exists in repo to compare against; gist revG is first commit
of this fetch)". The verdict "NONE" implies the comparison was
performed. The preamble "(no prior Rev F fetch exists...)" indicates
no baseline existed. A verdict was emitted for a comparison that was
not run. When the baseline was later found (work/r27-k1-run-publication-verify-2026-09-10.txt),
the diff showed lines 1-34 (K1-RUN PUBLICATION VERIFICATION header
and state checks) are absent from the revG fetch. The gist revG is
a raw fetch; r27 is a report wrapping that fetch. The comparison
should have been deferred or stated as not-performed. Same class as
instances 1-4: a judgment reported as a measurement.

Filed 2026-09-11.
