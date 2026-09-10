# DECISION — sealed-file append-only regime

**Filed:** 2026-09-10  
**Type:** PROCEDURAL-DECISION  

Sealed files (manifest entries at 7d4aad7) are **append-only after seal**.  
Corrections, additions, and annotations live at commits after 7d4aad7.  
The seal certifies the bundle at 7d4aad7 and nothing about HEAD.  

Seal check v2 is an **attestation**, not a monitor. It attests that every  
manifest file matched `git show 7d4aad7:path` at publication time.  
It cannot fail after that point — a mismatch between 7d4aad7 and HEAD  
is not a seal failure; it is expected divergence under the append-only  
regime.  

This decision is filed here. It is not inferred from practice.

## RULE-IN-CLOSED-RECORD (2026-09-10)

The standing rule §3 and K1 candidate §4 were **inserted into** the section
structure of leg-a-closed-2026-09-09.md (a sealed file), not appended at EOF.
Subsequent sections were renumbered (3→5, 4→6, 5→6) to accommodate the
insertion. This occurred in commit 78d961b, the same commit that declared
the sealed-file append-only regime in this ledger entry.

**Do not revert.** The insertion is correct in content and was explicitly
directed by the founder. Record it as: a live standing rule was written into
a closed result document, and a sealed file was edited rather than appended,
in the same commit that declared append-only. Both actions stand; the
contradiction is acknowledged, not resolved by reverting either side.

The rule is now extracted to its canonical address: ledger/standing-rules.md.

### Third instance (2026-09-10)

The blast-radius amendment describing the section-renumbering as "timing, not design" was inserted mid-file into `leg-a-closed-2026-09-09.md` (a sealed closed record) in the same session. The insertion target should have been this RULE-IN-CLOSED-RECORD entry in `ledger/sealed-file-append-only.md`. Not reverted — the content is correct — but recorded as the third instance of a closed-record edit, distinct from the §3/§4 insertion (first instance) and the standing-rules cross-reference insertion that followed (second instance). Standing rule #8 now prohibits all post-seal edits and mid-file insertions to closed result documents; EOF pointers only.

## REFERENT SWEEP — citations of leg-a-closed sections (2026-09-10)

A sweep of ledger/, specs/, work/, harness/ for citations of leg-a-closed
sections (pattern: "leg-a-closed.*§[0-9]" or "leg-a-closed.*section [0-9]")
found hits only in files created after the renumbering:

| File | § ref | Pre-dates 78d961b? | Resolvable? |
|------|-------|-------------------|-------------|
| ledger/standing-rules.md:9 | §5 | No (created 26fb687) | ✅ Refers to OUTPUT-PRECISION POLICY (new §5) |
| ledger/standing-rules.md:10 | §6 | No (created 26fb687) | ✅ Refers to C1 EXCLUSION LIST (new §6) |
| ledger/standing-rules.md:11 | §7 | No (created 26fb687) | ✅ Refers to SPEC SCOPE RULE (new §7) |
| ledger/standing-rules.md:12 | §3 | No (created 26fb687) | ✅ Refers to DERIVED/VERBATIM rule (new §3) |
| ledger/standing-rules.md:13 | §3/§4 | No (created 26fb687) | ✅ Refers to insertion in sealed-file-append-only |
| ledger/standing-rules.md:19 | §4 | No (created 26fb687) | ✅ Refers to K1 candidate 1 (new §4) |
| ledger/standing-rules.md:20 | — | No (created 26fb687) | ✅ No section ref |
| ledger/sealed-file-append-only.md:21 | — | No (created 26fb687) | ✅ No section ref; mentions leg-a-closed as sealed file |

No citations in specs/, work/, or harness/. No citations predate 78d961b.
No unresolvable entries — all refs use the new numbering.