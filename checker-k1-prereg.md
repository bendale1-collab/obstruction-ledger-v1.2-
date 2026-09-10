# CHECKER K1 — PRE-REGISTRATION v0.3

STATUS: v0.3 FINAL. Founder-adjudicated. Commit unchanged; do not edit. Seal and publish per §6.
R8 locked from git history; K1-5/K1-6 added; operator framing corrected; model census in §0.
AUTHOR: Claude (frontier tier), from Hermes-assembled inputs, commits a8e11c8 → 6b70539.
Hermes did not author this document and must not edit it.
No FOUNDER-FILL markers remain. Any edit to this file after its K1-PREREG hash is
published invalidates the seal; corrections are appended to the gist, never edited in.

## 0. Base state

- Seal: 7d4aad7 / FREEZE_HASH d7043bba…1aee9 (v1.6, 19 files)
- HEAD at drafting: 6b70539 (chain: a8e11c8 → fc08b6f LEDGER-PRESERVE →
  694de3e LEDGER-IGNORED → 4647dd6 .gitignore fix → 6b70539 MULTI-WRITER)
- Operators, from mahamara/state.db sessions table (not from founder notes):
  deepseek/deepseek-v4-flash — session 20260908_072342_c971108e, 09-08 07:23
  to 09-09 23:39 local, produced 66f9b16 through e02e15b: ENGINE-RED, Leg A
  close, v1.6 seal, the full failure catalogue, RENDERING-AS-RECORD, and the
  §3/§4 insertion. Also the 09-06 bootstrap session. qwen/qwen3.7-max —
  session 20260910_084547_3739eed1, this session, from 09-10 08:45.
  Commit a8e11c8 (09-10 06:41) falls between the two: session UNIDENTIFIED.
  "qwen3-coder-next" appears in no session log seen; founder-side documents
  naming it as the operator are superseded by this line. The catalogue was
  produced by one model, correctly named only now.
  Three gateway processes share write access; git author is shared
  (ledger/multi-writer-unattributed.md).
- Model census (state.db, both profiles, 2026-09-10): mahamara has 12
  distinct model strings across six vendors (Anthropic, OpenAI, Google,
  DeepSeek, Qwen, Zhipu), with deepseek-v4-flash recorded under two
  spellings; exec has 4. "Two model families" is superseded: the repo has
  been operated by a rotating pool under one git author.
- a8e11c8 (09-10 06:41 local): UNATTRIBUTED. ~140 sessions carry no end
  timestamp, so activity-at-instant identifies nothing. Nearest-start
  candidate 20260910_054010_4ef0c4f4 is a guess and is not an attribution.
- RUNBOOK.md (sealed, in the 19) names qwen3-coder-next as the operator.
  No session ever ran under that string. The sealed bundle asserts an
  operator identity that was never true, and the text is embedded into
  API requests, so every operating model was told it was a different one.
  Filed as OPERATOR-MISNAMED; Rev C item 7.
- Manifest state: MANIFEST_FILES=19 counts 18 distinct artifacts (one
  byte-identical pair, 09-09 reconstruction defect). 4 of 5 .yaml manifest
  paths do not parse as YAML. Both to be corrected in gist Rev C, append-only.
- K0 v0.1: C3, C6, R1 only (work/k0.py, 144 lines). C1 designed, unbuilt.
  C2, C4, C5, C7, C8, C9, R2: names only. "Nine checks" superseded.
- Standing block: no compute until this document is frozen and its hash published.
- Pre-condition (standing rule 7): divergence report clean-or-declared at freeze commit.

## 1. Scope — seven checks

All mechanical. No LLM in any check. Compute budget $0.

| ID   | Check                          | Source incident                                   | Input                        |
|------|--------------------------------|---------------------------------------------------|------------------------------|
| C1   | Prose–table number mismatch    | A1/A5 distance-vs-value; 42/20 "identical"        | report .md                   |
| K1-1 | Quote-vs-anchor byte match     | Hermes composed anchor block, 09-10               | report .md + raw anchor URL  |
| K1-2 | Divergence-declaration         | seal-detached append, leg-a-closed edit           | seal commit, HEAD, ledger/   |
| K1-3 | Section-structure stability    | leg-a-closed §3/§4 renumber, §7 insert            | seal commit, HEAD            |
| K1-4 | Identifier well-formedness     | 31-char gist ID (dropped char) ×5; 10-char ×1     | tracked files at commit      |
| K1-5 | Duplicate hash within manifest | 53ca0569… ×2 in MANIFEST.sha256 @7d4aad7          | MANIFEST.sha256 at commit    |
| K1-6 | Declared extension vs content  | 4 of 5 .yaml manifest paths fail to parse         | manifest paths at commit     |

Ordering by self-enforcement (most mechanical first): K1-5, K1-6, K1-3, K1-4, K1-2, K1-1, C1.
K1-5 and K1-6 catch defects that K1-2 and K1-3 pass by construction: a
duplicated file is SAME against the seal and has identical headers.

## 2. Check definitions

### C1 — prose–table number mismatch
Every number in prose that also appears in a table or JSON in the same
packet must agree in value and unit. A distance reported as a value, or
two differing values called "identical," is a finding.
Output: list of (prose location, table location, prose value, table value).
Tolerance (DECIDED): exact match after rounding both values to the fewer
significant digits of the pair. Rounding via Python `decimal` with
ROUND_HALF_UP on the string representation, never on binary floats.
Integers compare exactly. Units must match literally.

### K1-1 — quote-vs-anchor
Any block presented as quoting an anchored file (gist, sealed path) must
byte-match the anchor at the stated revision, or carry the header
`DERIVED <revision-sha>`. Unlabeled non-matching text is a finding.
Output: (block location, anchor, revision, MATCH / DERIVED / MISMATCH).
Network: one fetch per anchor, raw URL, cached per run.

### K1-2 — divergence-declaration
For each manifest path: diff seal-commit vs HEAD. Report SAME or
DIFFERS with nature = APPEND / EDIT / RENUMBER / DELETE. Every DIFFERS
must cite a declaring ledger entry outside the diverging file.
Undeclared divergence, or declaration only by self-reference, is a finding.
Output: full 19-row table. Count-only output is itself a finding.

### K1-3 — section-structure stability
For each sealed file: header text and numbering at HEAD must equal the
seal commit. Any inserted, removed, or renumbered header is a finding.
Appended headers after the original final header are permitted only if
the original headers are unchanged.
Output: (path, header diff).

### K1-4 — identifier well-formedness
Any hex string that is a prefix-match (≥10 chars) of a canonical anchor
value, or sits after a label (Gist ID:, FREEZE_HASH=, SHA, commit), must
be exactly canonical length: SHA-256 = 64, git SHA = 40 or 7, gist ID = 32.
Any other length is a finding — including 31 (dropped character), 10
(truncation), or 65 (inserted character). Where a canonical value is
recorded in the bundle (STATE.yaml, SEAL-PACKET.md, seal-detached-v1.5.md),
the full string must match it. Malformation, not only truncation.
Scope: tracked files at the stated commit. Blocks under a `QUOTED` or
`DERIVED` header (same convention as K1-1) are skipped — audit files that
document malformed identifiers must carry the header or they fire.
Output: (location, identifier, expected length, found length, anchor match).

### K1-5 — duplicate hash within manifest
Every hash in MANIFEST.sha256 must be unique. Two paths with one hash is
a finding, reported with both paths. Distinct-artifact count is reported
alongside the line count.
Output: (hash, [paths]); MANIFEST_LINES vs DISTINCT_ARTIFACTS.

### K1-6 — declared extension vs content
Every manifest path with a machine-readable extension (.yaml, .yml, .json)
must parse under that format at the stated commit (yaml.safe_load /
json.load). Parse failure is a finding, reported with the parser error.
Output: (path, extension, PARSE / FAIL + error).

## 3. Retrodiction corpus and pre-stated outcomes

Fixed before freeze. A run passes only if every row matches exactly.

| Row | Packet / commit                                    | Check | Expected     |
|-----|----------------------------------------------------|-------|--------------|
| R1  | Hermes anchor block (rendering-as-record instance) | K1-1  | MISMATCH ×2 blocks (v1.5, v1.6) |
| R2  | seal-detached-v1.5.md verbatim correction @78d961b | K1-1  | MATCH        |
| R3  | 7d4aad7 vs fe8a1e9                                 | K1-2  | leg-a-closed DIFFERS/EDIT, UNDECLARED (no entry existed) |
| R4  | 7d4aad7 vs a8e11c8                                 | K1-2  | 17 SAME; seal-detached DIFFERS/APPEND declared; leg-a-closed DIFFERS/RENUMBER declared. Note: the leg-a-closed declaration (RULE-IN-CLOSED-RECORD) is an acknowledgement of a standing-rule-8 violation, not an authorization. K1-2 passing here while K1-3 fires on the same file (R5/R6) is the intended behaviour. |
| R5  | leg-a-closed @fe8a1e9                              | K1-3  | FINDING (§7 inserted) |
| R6  | leg-a-closed @78d961b                              | K1-3  | FINDING (§3/§4 inserted, §3–§5 renumbered) |
| R7  | 18 other sealed files @a8e11c8                     | K1-3  | 18 × SILENT  |
| R8  | LOCKED, history (below)                            | K1-4  | FINDING ×5, exactly at locked coordinates, nowhere else in those commits |
| R8b | v1.6-publication-confirmation-2026-09-10.txt:35    | K1-4  | FINDING ×1 (10-char anchor ref) |
| R8c | gist-id-audit-2026-09-10.txt; work/r8-grep-2026-09-10.txt | K1-4 | SILENT (QUOTED header present) |
| R9  | anchors/ANCHORS.md @6b70539                        | K1-4  | SILENT       |
| R10 | A1/A5 reconciliation packet                        | C1    | FINDING (distance reported as eigenvalue) |
| R11 | K0 H2 report (K0 PASS packet)                      | C1    | SILENT (bet; adjudication branch below) |
| R12 | MANIFEST.sha256 @7d4aad7                           | K1-5  | FINDING ×1: 53ca0569… at misidentification-by-acronym-collision{.md, -2026-09-08.yaml}; 19 lines / 18 distinct |
| R13 | 5 .yaml manifest paths @7d4aad7                    | K1-6  | FAIL ×4 (chebyshev, conv-flag, fourier-diff, misidentification); PARSE ×1 (C1-exclusion-list) |
| R14 | K1-MANIFEST.sha256 at K1-PREREG seal               | K1-5  | SILENT       |

R8 — LOCKED (from work/r8-grep-2026-09-10.txt, git history, 2026-09-10).
The defect is not truncation. The variant is 6b6d2d4265ffe5b63ab6a54a603ca05,
31 chars, "1" dropped at position 11. Five occurrences, two coordinates,
three commits, all pre-seal, all corrected during seal recovery:
  5f49023  SEAL-PACKET.md:20
  5f49023  leg-a-closed-2026-09-09.md:161
  9123787  SEAL-PACKET.md:20
  9123787  leg-a-closed-2026-09-09.md:161
  e7b2261  leg-a-closed-2026-09-09.md:161
N = 5. K1-4 run at each of those three commits must fire at exactly the
listed coordinates for that commit. No tracked file at HEAD carries the
variant (confirmed: git grep at HEAD, exit 1). The founder-side record's
"three occurrences" was wrong in count and kind; locked from data.

R8b/R8c — freeze blocker. Before freeze, Hermes commits unchanged:
v1.6-publication-confirmation-2026-09-10.txt (line 35 carries the 10-char
ref; K1-4 must fire there, once). And commits gist-id-audit-2026-09-10.txt
and work/r8-grep-2026-09-10.txt each with one line prepended:
`QUOTED: identifiers below are reproduced as evidence, not asserted`.
K1-4 must be SILENT on both. The commit SHA is recorded here at lock:
  R8b/R8c commit: 0c32940 (2026-09-10)

R11 — adjudication branch (DECIDED). Expected SILENT. Note: K0 PASS
attests C3/C6/R1 only; C1 was never in K0, so K0 PASS is no evidence
about prose–table agreement in H2. SILENT is a prediction, not an
implication. If C1 fires on H2, the founder adjudicates each output
tuple before any other action:
  - TRUE-MISMATCH: H2 contains a real prose–table defect. File it as a
    finding on H2. C1 is correct; row R11 scores PASS-WITH-FINDING.
  - FALSE-POSITIVE: values agree under §2 tolerance. C1 RED.
This branch is stated before the run and is not an edit of the expected
outcome.

## 4. Injection validation

Harness: extend work/k0-test.py. Per check (DECIDED): 10 positive,
10 negative injections. Injections written before code, by a party who
does not write the check code. Hermes may write injections OR check code,
not both for the same check.

Thresholds, pre-stated (DECIDED): recall = 1.0, FP = 0.0 per check on
its 20 injections. Deterministic code on predefined cases has no
tolerance to claim. A single miss halts the run for that check; the miss
is filed and adjudicated (injection defect vs code defect), never
silently re-run.
Note: 20 cases at 1.0/0.0 is evidence the code handles those 20 cases.
It is no evidence about generalization (§7).
Retrodiction rows: exact match, no tolerance.

## 5. Pass / kill

- K1 GREEN: all seven checks meet injection thresholds AND all retrodiction rows match.
- K1 RED on a check: that check's retrodiction row(s) fail. Other checks
  may still be GREEN individually; K1 as a set is not GREEN.
- A failing expected outcome is filed, never edited to match the result.
- No injection or threshold may be chosen by looking at which cases it excludes.

## 6. Procedure

Seal location (DECIDED): separate K1 seals, never v1.7. Folding K1 into
the base manifest would alter the 7d4aad7 base state that K1-2 and K1-3
measure against. Two stages, because scripts do not exist at freeze:

1. R8b/R8c commit made and its SHA recorded in §3; founder confirms the
   operator model string in §0. No other blocker remains.
1a. Gist Rev C published (v1.5 timestamp; 9/1/5 line; 19 lines / 18 distinct;
   4 of 5 .yaml paths not YAML). Not a K1 gate, but it must precede the K1
   block on the same gist so the corrections appear before new claims.
2. Run divergence report at the intended freeze commit. Must be clean-or-declared.
3. K1-PREREG seal: hash this document alone (K1-MANIFEST.sha256, one entry).
   Publish hash to gist as a K1 block. Founder-only.
4. Injections written per §4 split. Then K1-RUN seal: hash injection set
   + this document (K1-RUN-MANIFEST.sha256). Publish. Founder-only.
   Check code is written only after the K1-RUN hash is published.
5. Run injection harness. Report per-check table, full, JSON to stdout, paths not inline.
6. Run retrodiction rows. Report full table, every row, no counts-only.
7. Founder adjudicates GREEN/RED per row, and R11 branch if triggered.
Both K1 seals are verified against commit (seal check v2) and are
attestations, not monitors; divergence report applies to them at every
subsequent gate.

## 7. Known limitations, stated in advance

- One repo, one domain. NOT one operator: at least two model families and
  three gateway processes have had write access, under one shared git
  author. Every "one operator, one run" statement in founder-side documents
  (session summaries, omnibus handoff, venture framing) is superseded by
  this line. Generalization across domains unproven; generalization across
  operators is weakly supported by the two-family catalogue, not tested.
- Repo integrity is procedural. The seal proves what the bundle was at
  7d4aad7; it does not and never claimed to prove who changed it
  (SPEC.md §2.3 says so). Per-profile git author (standing rule 9) is a
  label, not a control.
- K1-2 and K1-3 are blind to duplicated or misnamed files by construction;
  K1-5/K1-6 exist for that reason and were added after the fact, from
  incidents.
- Retrodiction rows were selected from incidents already known; recall on
  unknown defect types is not measured here.
- K1-1 requires network; offline runs skip it and must say so.
- Timezone (DECIDED): recorded as an instrument property. Committing
  machine is America/Chicago (-05:00); founder convention remains
  America/New_York. All commit stamps from 7d4aad7 onward carry the
  machine offset. Nothing historical is edited. No K1 check reads
  timestamps; GitHub revision UTC remains the authoritative anchor time.

## 8. After K1

Run all seven checks on one packet from an unrelated domain. Cheaper than
Leg B; answers the buyer's generalization question.

K2 candidate, not in K1 scope (scope is locked at seven): asserted-operator
vs recorded-operator — for each commit, the model string asserted in
RUNBOOK/SPEC must equal the model string in the session log for the
producing session. Fires on every commit in this repo to date.
