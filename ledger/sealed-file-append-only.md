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