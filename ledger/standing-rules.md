# Standing Rules Index

**Canonical address for all live standing rules.**
Rules are listed with the file and commit where they were first filed.
Rules in sealed files are not moved; they are indexed here by reference.

| # | Rule | First filed in | Commit | Notes |
|---|------|---------------|--------|-------|
| 1 | **Output-precision policy** — eigenvalues/residuals at ≥12 significant digits in machine-readable JSON | leg-a-closed-2026-09-09.md §5 | 7d4aad7 | Sealed file. |
| 2 | **C1 exclusion list** — versioned in repo; additions are ledger entries | leg-a-closed-2026-09-09.md §6, known-bad-specs/C1-exclusion-list.yaml | 7d4aad7 | Sealed file + versioned data. |
| 3 | **SPEC scope rule** — manifest seals core bundle only; work/, registry/, harness/, arbiter/, env/, SEAL-PACKET.md, known-bad-specs/RB-*.yaml are tracked but unsealed | leg-a-closed-2026-09-09.md §7 | 78d961b | Decision, not inference. |
| 4 | **DERIVED vs VERBATIM anchor representation** — any text presented as content of an anchored file must be byte-identical or carry DERIVED header with source revision SHA | leg-a-closed-2026-09-09.md §3 | 78d961b | Applies to all ledger entries, reports, chat output. Violation = RENDERING-AS-RECORD defect. |
| 5 | **Sealed-file append-only regime** — sealed files are append-only after seal. Corrections live at commits after seal commit. Seal certifies the bundle at seal commit and nothing about HEAD. | ledger/sealed-file-append-only.md | 78d961b | Incorporated: RULE-IN-CLOSED-RECORD (leg-a-closed §3/§4 insertion acknowledged). |
| 6 | **Replay limitation** — replay from d7043bba yields the sealed (pre-correction) copy of `ledger/seal-detached-v1.5.md`; the correction, and both divergence declarations, live in `ledger/rendering-as-record.md`, which is unsealed. The d7043bba bundle alone does not reconstruct the complete incident record. | leg-a-closed-2026-09-09.md (RULE-IN-CLOSED-RECORD: section-renumbering blast radius) | current | Cross-reference: `ledger/rendering-as-record.md`. |
| 7 | **Divergence-report cadence** — the divergence report runs at every gate and is a pre-condition of authorizing compute. Clean or fully declared, or no compute. | leg-a-closed-2026-09-09.md (RULE-IN-CLOSED-RECORD: section-renumbering blast radius) | current | Replaces ad-hoc divergence runs. |
| 8 | **Closed-result-document immutability** — closed result documents (e.g. leg-a-closed-2026-09-09.md) receive no edits and no insertions after seal. Corrections and commentary about them live in the ledger. EOF pointers only. | ledger/sealed-file-append-only.md (RULE-IN-CLOSED-RECORD, third instance) | current | Supersedes the prior practice of editing sealed closed records. Cited: RULE-IN-CLOSED-RECORD first, second, third instances. |
| 9 | **Per-profile git author attribution** — each Hermes profile commits under a distinct `GIT_AUTHOR_NAME` and `GIT_COMMITTER_NAME` (mahamara / exec / <third>), set per gateway. This is attribution, not isolation — it records which profile authored a commit but does not enforce single-writer discipline (OS-level isolation is absent; see ledger/multi-writer-unattributed.md). Current state: all three profiles share the global author `bendale1-collab` from `~/.gitconfig`; per-profile overrides are not yet set. | ledger/standing-rules.md (founder instruction) | current | Founder sets git config; agent reports but does not change it. |

## K1 candidate list

| Candidate | Description | Proposed in | Commit |
|-----------|-------------|-------------|--------|
| 1 | Quote-vs-anchor byte check: verify quoted anchor text is byte-identical to the anchor's current published version | leg-a-closed-2026-09-09.md §4 | 78d961b |
| 2 | Divergence-declaration check: every manifest file differing between seal commit and HEAD must have a declaring ledger entry | leg-a-closed-2026-09-09.md (founder instruction, divergence report) | 78d961b |
| 3 | **Section-structure stability** — for each sealed file, header text and numbering at HEAD must match the seal commit. Note: K1 candidate 2 (divergence-declaration check) passed on leg-a-closed while a renumbering (originally §3→§5, §4→§6, §5→§6) hid inside a declared diff. Divergence output must report diff **nature** (append / edit / renumber), not just SAME/DIFFERS. | leg-a-closed-2026-09-09.md (founder instruction, divergence report) | 78d961b |
| 4 | **File identifier-length check** — every hash, SHA, and gist ID in a report must match its canonical length (64 hex for SHA-256, 40 hex for SHA-1, 32 hex for gist ID) and, where an anchor exists, its canonical value. Source: three truncated gist-ID occurrences observed 2026-09-10. | ledger/standing-rules.md (founder instruction) | current | K1 candidate 4. |

K1-4 label scope — §2 lists labels illustratively. Whether hash: and similar unlisted labels trigger the check is undefined in the sealed spec, identified pre-code at injection k1-4/neg-08. Disagreement between code and fixture will be adjudicated under §4, not resolved by editing either.

K1-6 fixtures are labelled by running yaml.safe_load / json.load; for this check that is the only possible labelling method.