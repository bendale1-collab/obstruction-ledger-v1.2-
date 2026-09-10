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

## K1 candidate list

| Candidate | Description | Proposed in | Commit |
|-----------|-------------|-------------|--------|
| 1 | Quote-vs-anchor byte check: verify quoted anchor text is byte-identical to the anchor's current published version | leg-a-closed-2026-09-09.md §4 | 78d961b |
| 2 | Divergence-declaration check: every manifest file differing between seal commit and HEAD must have a declaring ledger entry | leg-a-closed-2026-09-09.md (founder instruction, divergence report) | 78d961b |