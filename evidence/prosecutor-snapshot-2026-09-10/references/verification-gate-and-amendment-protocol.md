# Verification Gate & Pre-Registration Amendment Protocol

**Added:** 2026-07-09 (after BYND C8 false positive)
**Source:** SETUP_VERIFICATION_GATE + BYND_AMENDMENT directive

## R5 Verification Gate

Before any deadline event enters the scored ledger, the filing must be verified against the extracted text:

### Requirements
- **(a) Accession** — exact accession number (adsh) from EFTS
- **(b) Phrase** — matched sentence containing BOTH the trigger keyword AND an explicit date, quoted verbatim from the filing text
- **(c) Item-code check** — for C8 warrant events: item 3.02 alone = ISSUANCE, auto-reject (carries "No Right of Redemption" clause). Legitimate redemption calls carry item 8.01, 3.03, or a notice exhibit with explicit redemption date.

### Consequences
- Missing any of (a)-(c) → **SETUP_UNVERIFIED** — cannot enter scored ledger
- The gate is permanent. It was added because the BYND 2026-06-25 8-K (item 3.02) was initially classified as a C8 warrant redemption when it was actually a warrant issuance with Section 4 "No Right of Redemption by the Company."

## Pre-Registration Amendment Protocol

When a frozen-spec SETUP declaration is subsequently found to be based on an incorrect filing classification:

1. **Amendment is logged**, not suppressed. Log: `type=PRE_REG_AMENDMENT`, timestamp, ticker, original_status, revised_status, verbatim justification citing the specific filing text that disproves the original classification.
2. **Rule definition is unchanged.** Only the specific application is voided. A rule that produced a false positive needs a methodology fix (new verification step), not a rule edit.
3. **The verification fix is permanent.** The gate that would have caught the error becomes a permanent part of the methodology.
4. **The amended entry remains in the ledger** with both statuses preserved (original and revised), so the error trail is auditable.

## Hash-Chained Scoring Ledger Pattern

For append-only scoring of calendar events under a frozen rule:
- Each entry carries: ticker, deadline, type (HISTORICAL/PROSPECTIVE), setup_status (SETUP/NON_SETUP/SETUP_UNVERIFIED), outcome (once scored), plus any verification fields.
- Hash chain: each entry includes `prev_hash` of the previous entry and an `entry_hash = SHA256(entry_content + prev_hash)[:16]` of its own.
- Chain tip is recomputed on every append. The `total_entries` counter and `chain_tip` hash are the integrity check.
- Amendments add entries, they do not mutate existing ones (exception: when the original entry's status field is wrong due to an input error, it may be updated with a `p1_amendment` subfield that documents the correction; the hash changes but the audit trail is preserved in the amendment subfield).

## C8 False Positive: BYND Case Study

| Field | Value |
|---|---|
| Original classification | C8 warrant redemption, deadline 2026-07-25 |
| Cited filing | 8-K 2026-06-25, accession 0001655210-26-000046, item 3.02 |
| Actual content | Warrant issuance to Big Geyser, Inc. |
| Smoking gun | Exhibit 4.1, Section 4: "No Right of Redemption by the Company" |
| Correction | Reclassified NON_SETUP. Rule unchanged. R5 verification gate added. |
| Lesson | Item 3.02 alone = warrant issuance. Redemption requires 8.01/3.03 or notice exhibit with explicit redemption date. Verify the verbatim text, not just the item code. |