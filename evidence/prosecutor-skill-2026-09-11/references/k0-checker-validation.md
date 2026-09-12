# K0 Checker — Injection-Based Report Validation

**Domain:** Quality assurance for quantitative research reports. Verifies that
claims in a report are supported by hashed source artifacts, that threshold
changes are not retro-fitted, and that pre-registered controls carry verdicts.

**When to use:** Before founder review of any report claiming a typed verdict.
Run K0 first; its flags accompany the report. Do not send a report to the
founder without K0 output.

---

## Scope correction (authoritative, 2026-09-10)

Founder-filed: **K0 v0.1 implements C3, C6, R1 only. C1 designed, unbuilt.
C2, C4, C5, C7, C8, C9, R2: names, no spec, no code. The "nine checks"
description is superseded.** The C1 spec below is a design reference, not a
shipped check. Do not describe K0 as having more than three implemented checks.

## Checks (K0 v0.1 implements C3, C6, R1; C1 documented but NOT built)

### C3 — Quote verification

Every quoted string in a report must substring-match a hashed source artifact
in the bundle. No match → FAIL.

**Implementation:**
- Extract all `"..."` strings (≥15 chars) and blockquoted lines (`> ...` with
  content ≥25 chars)
- Compare against a lowercased corpus built from:
  - All files in `MANIFEST.sha256`
  - All `.md` files in the work directory (extra corpus)
- If any extracted string is NOT found in any corpus text, flag as unmatched

**False positive sources:**
- Short common phrases that happen to appear in quotes (`"essential cluster"`)
- Auto-generated text that quotes itself
- The report's own title/headers in quotes  
  → Use `--extra-corpus-dirs=work` so all reports are in the corpus

### C6 — Threshold diff detection

Any proposed change to a test parameter should be applied under both old and
new values. If the verdict flips, flag FITTED-TO-DATA.

**Implementation:**
- Search for "Option (X): Accept ... REJECTED" patterns with numeric thresholds
- Search for explicit "retro-fitting" / "retrofit" text mentions
- A flag means the text CONTAINS retro-fitting language (may be genuine
  discussion, not necessarily a defect — the report itself should explain)

**False positive sources:**
- Genuine `K0 check result: "PASS — no retro-fitting detected"` line in the
  report itself → avoid the word `retro-fitting` in K0's own output, or use
  a different phrasing

### C1 — Prose-table number mismatch

Every numeric value appearing in prose (running text) must correspond to a
numeric value in at least one table cell in the same report. No match → FAIL.

**Implementation:**
- Extract all numeric tokens (decimals `-?\d+\.?\d*`, negatives, scientific
  notation `\d+e[-+]\d+`) from prose paragraphs (running text, not table cells)
- Collect all numbers from all tables in the report (parsed from pipe `|` rows)
- Cross-reference: any prose number NOT found in any table cell is flagged
- Exclude parameter-declaration context (`N=\d+`, `L=\d+`, `δ=\S+`, grid
  parameters like 1024, 2048, 20.0) as these are not result figures

**False positive sources:**
- Grid parameters stated in prose (1024, 2048, 20.0) without appearing in a
  table — handle by either (a) putting grid parameters in a table, or
  (b) maintaining an exclusion list of known grid parameters
- Consecutive numbers in prose that coincidentally match table numbers — these
  are true matches, not FPs; the prose number IS in a table

### R1 — Control checklist

Every pre-registered control must appear in the report with its own pass/fail,
evaluated before any treatment result is interpreted. Missing or unreported
control → REJECTED.

**Implementation:**
- Load all registry `.yaml` files from the registry directory
- For each control, match ONLY its structured registry `id` (e.g. `F-4`, `A1`,
  `OL-MD-001`) as a word-boundary regex: `\b<control_id>\b`
- Do NOT use the control's `name` or `description` fields for matching —
  these contain common English words (`scaling`, `exact`, `stability`) that
  produce false positives in natural-language text
- For each ID found in the report text, check if a verdict keyword
  (`pass`, `fail`, `✅`, `❌`, `correct`, `incorrect`, `present`, `absent`,
  `yes`, `no`, `met`, `not met`, etc.) appears within ±100 chars
- Controls that appear in the text WITHOUT a nearby verdict are flagged

**Important:** Controls not mentioned at all are NOT flagged — only controls
that appear in the text without verdict are flagged. This avoids penalizing
reports that don't mention every control (most don't).

---

## Validation methodology

### Injection set

Generate defects mechanically, 20 per check type:
| Check | Defect type | Method |
|-------|-------------|--------|
| C3 | Swapped quotation | Append a standalone blockquote containing `**FABRICATED_K0_QUOTE_{RANDOM}**_NONEXISTENT_DOES_NOT_APPEAR_ANYWHERE_` |
| C6 | Widened threshold | Append a "**Retro-fitting analysis**" block with Option(A) REJECTED and Option(B) ACCEPTED with wider thresholds |
| C1 | Prose-table number mismatch | Insert a prose sentence containing a numeric value that does NOT appear in any table cell of the clean report. E.g.: `The essential spectrum cluster extended to Re λ = 0.823 under the naive realization.` (0.823 is not in any table) |
| R1 | Deleted control | Replace a verdict-carrying line with `<!-- K0_R1_VERDICT_REMOVED -->` |

**Critical:** For C3, the fabricated quote must be a STANDALONE blockquote
(`> "...") not an inline replacement, to avoid quote-pairing ambiguity
with adjacent quotation marks.

**Commit the injection set before the first validation run.** The commit hash
freezes the ground truth so metric computation is auditable.

### Metric computation (per packet, not aggregate)

| Metric | Definition |
|--------|-----------|
| TP | injected file → check detected the defect |
| FN | injected file → check did NOT detect |
| FP | clean file → check detected a defect (false alarm) |
| TN | clean file → no detection |

**C3 detection:** Fabricated quote contains `fabricated_k0_quote` marker found
in unmatched quotes.

**C6 detection:** C6 findings list is non-empty on the injected file, empty
on clean.

**R1 detection:** Compare the set of `controls_without_verdict` on the
injected file against its source file. If the injected file has a strictly
larger set (new controls lost their verdict), R1 detects a defect.
**Important:** Without this source-baseline diff, R1 recall is ~0 because
most reports already have some controls without verdicts in the baseline.

### Acceptance gate

| Threshold | Value |
|-----------|-------|
| Recall | ≥ 0.90 |
| FP rate | ≤ 0.05 |

Per check. Both must be met for the check to ship. "Design finding" if below
threshold: the check's implementation is the deliverable even if it doesn't
pass the gate, because the methodology exposed the gap.

---

## Running

```bash
# Single report
python3 work/k0.py --manifest MANIFEST.sha256 --registry-dir registry \
  --extra-corpus-dirs=work path/to/report.md

# Validate
python3 work/k0-test.py  # builds injection set, runs checks, computes metrics
```

## Known limitations (2026-09-09)

- **R1 metrology** still requires per-packet source-baseline diff for the injection test (controls_without_verdict on injected vs source), which is only valid when the source file path is stored in the injection set. The current test stores `src` fields for this purpose.
- **R1 common-word collisions eliminated** via ID-only matching — R1 now matches only structured registry IDs (`F-4`, `A1`, `OL-MD-001`) via word-boundary regex, not control name/description fields. This eliminates false positives from generic terms like `scaling`, `exact`, `stability` in natural-language text. The fix was specified in the A1/A5 reconciliation (2026-09-09) and the design reference (k0-checker-design.md) already documents it.
- **C6 threshold detection** is regex-pattern-based and may miss retro-fitting patterns that use different phrasing. Extending the pattern set is straightforward.

## Scope correction (2026-09-10)

K0 v0.1 (`work/k0.py`) implements **C3, C6, R1 only**. The older "Four checks"
wording over-reached:
- **C1 (prose-table number mismatch): designed, NOT built** — no implementation exists.
- **C2, C4, C5, C7, C8, C9, R2: names only — no spec, no code.**
- Any "nine checks" description is superseded. Only C3/C6/R1 have code,
  injection sets, and acceptance metrics (recall >= 0.9, FP <= 0.05).

## K1 candidate list (4, as of 2026-09-10)

| # | Candidate | Description |
|---|-----------|-------------|
| 1 | Quote-vs-anchor byte check | Quoted anchor text in a report must be byte-identical to the anchor's current published version (fetch raw URL at stated revision SHA, diff). |
| 2 | Divergence-declaration check | Every manifest file differing between seal commit and HEAD must have a declaring ledger entry. Undeclared divergence is a finding. |
| 3 | Section-structure stability | Header text + numbering of sealed files at HEAD must match seal commit; divergence output must report diff NATURE (append / edit / renumber), not just SAME/DIFFERS. |
| 4 | File identifier-length check | Every hash, SHA, and gist ID in a report must match its canonical length (SHA-256=64, SHA-1=40, gist ID=32 hex) and, where an anchor exists, its canonical value. Source: three truncated gist-ID occurrences, 2026-09-10. |

## Identifier audit technique (K1-4 tooling pattern)

To find every location of an identifier across history and detect truncation:

```bash
# 1. Which commits touched the string (pickaxe):
git log -p -S <id-prefix> --all --format='%h %cI %s'
# 2. For each commit returned, grep the tree at that commit:
git grep -n <id-prefix> <commit>
# 3. Check each hit's char count vs canonical length (64/40/32 hex).
# 4. When a truncated occurrence exists in an older commit, find the
#    correcting commit by diffing the same path between commits:
git diff <old> <new> -- <path>
```

Truncation signature observed: gist ID `6b6d2d42651ffe5b63ab6a54a603ca05` written
with a dropped char at position 11 (`6b6d2d4265ffe5...`, 31 chars) in
SEAL-PACKET.md and leg-a-closed at commits e7b2261/9123787/5f49023, corrected at
fe8a1e9. The pickaxe `-S` with the truncated prefix catches both forms; a bare
substring grep in the working tree misses corrections already committed.