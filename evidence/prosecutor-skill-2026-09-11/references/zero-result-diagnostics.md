# Zero-Result Diagnostics

Emergent from D-33 DIAG1/DIAG2 (2026-08-15): both G-B and G-C passes
suspended pending instrument-density and join-integrity audits.

---

## Reachability Proof Before Recount

**Pattern:** When rebuilding a classifier that produced a zero count
(e.g., 0 BANKRUPTCY from a form-type-only join), assert N known
positives are caught by the rebuilt instrument BEFORE the census rerun.

**Rationale:** A classifier that produces non-zero counts after a fix
may still miss all real cases. Reachability verifies the fix before
the census produces numbers you then cannot un-see.

**Protocol:**
1. Before the recount, enumerate 3+ known-members of the target class.
   Use publicly recognised names from the cohort era that any domain
   expert would agree belong in the category.
2. Assert each is caught by the rebuilt classifier, with source/date.
3. All must HIT. If any MISS, fix before counting — not after.
4. Report the assertion before the recount in the same output that
   carries the new count, so the reader can verify the temporal order.

**Real example (D-33-FIX2):** iHeartMedia (Ch11 2018, CIK 739708),
Sears Holdings (Ch11 2018, CIK 1310067), Claire's Stores (Ch11 2018,
CIK 34115) — all confirmed caught by 8-K Item 1.03 method before the
census re-ran. All three HIT.

**Distinction from mutation testing:** Mutation testing (see
instrument-verification-techniques.md) constructs synthetic items to
test whether the instrument CAN produce a category. Reachability tests
whether it DOES catch known-real members of that category. Both are
required for different purposes: mutation tests the instrument's
ceiling; reachability tests its recall on known cases.

---

## Instrument-Density Coupling Audit

**Pattern:** When a concentration ratio is infinite (∞x) because of a
zero in one group, do not report the ratio as-is. First verify that
both populations are comparably instrumented — otherwise the
concentration claim may be an artifact of differential data density
rather than differential event prevalence.

**Triggers:**
- ∞x ratio (zero in denominator group)
- Any ratio comparing populations with different data-collection depth
- Comparison across death types where one type is systematically
  better-documented (e.g., acquired firms vs forced-out firms)

**Protocol:**
1. Emit median filing-quarters in the primary exposure panel (FSNDS)
   for each population.
2. Emit median event-signal count (e.g., 8-K filings in submissions
   cache) for each population.
3. Compare: if the density ratio (lower/higher) is < 0.5x in either
   instrument, the populations share a data-density parent. The
   concentration claim is UNMEASURED(coupled instruments) — N1a class.
4. If densities are comparable (ratio 0.5-2.0x), report the finite
   concentration ratio using a continuity correction (add 0.5 to both
   numerator and denominator counts). G-B PASSES on the corrected
   ratio.

**Real example (D-33-DIAG1):**
| Metric | Pressured | Unpressured | Ratio |
|--------|-----------|-------------|-------|
| FSNDS quarters | median 1 | median 5 | 0.20x |
| 8-K count | median 44 | median 104 | 0.42x |
→ Both instruments < 0.5x. G-B = UNMEASURED(coupled instruments).

**Note:** The continuity-corrected ratio (311.7x in this case) is
informational but ungateable — the instrument inequality precludes a
typed verdict. Zero-BK-in-acquired *may* be real, but the method
cannot establish it.

---

## Join-Verify-Audit (DIAG2.1)

**Pattern:** Before claiming a population has "zero pre-death data
points," verify the join at raw key level. The most common defect is
a CIK type mismatch (int vs str) that causes the join to silently
produce no matches, not because the data is absent but because no key
equality was possible.

**Protocol:**
1. Check CIK types in both datasets. Emit: x as int, y as int,
   x as str, y as str. If any mismatch exists and the join is
   string-equality, it fails silently on every record.
2. Emit match rate (fraction of classified CIKs that appear in the
   exposure panel). If < 50%, flag as DEFECTIVE — investigate whether
   the join is structurally sound or the data is genuinely absent.
3. Break match rate down by death year AND by death type. A uniform
   deficit is a join bug; a year-gradient (early years lower) is a
   panel-boundary artifact; a type-correlated deficit (one category
   much lower) is a coverage property of the instrument.

**Real example (D-33-DIAG2.1):** All 2,290 classified CIKs were int
and all 9,200 exposure-panel CIKs were int — no type mismatch.
Author's predicted join bug was REJECTED. Match rate was 68.2%:
2015=32% (panel boundary), 2019=82% (full window). Acquired=85%,
VC_dark=40% (instrument coverage, not join defect).

---

## Pre-Death Window Era Audit (DIAG2.2)

**Pattern:** When the pre-death exposure window (t-8..t) is bounded
by panel start date, deaths occurring in the first 1-2 years have
truncated windows by construction. These are UNMEASURED(era) for
those cohorts, not evidence of data absence.

**Protocol:**
1. Compute pre-death quarter count per matched CIK.
2. Report by death year: median pre-death quarters, fraction with ≥1,
   fraction with ≥N (where N is the registered pre-death window).
3. Flag early-cohort years explicitly: "Death year YYYY: 0/N with
   ≥N pre-death quarters is a panel-boundary artifact — the panel
   starts in YYYY+1, so no 8-quarter window is possible."
4. Report pre-death coverage by death type to check whether the
   deficit is uniform or category-specific.

**Decision rules:**
- 0% in panel-start year: UNMEASURED(era) — panel too young
- ≥90% with ≥1 quarter in mid-late years: data is present, era check
  passes
- < 50% with ≥1 quarter in late years: structural data absence
- A category with lower coverage despite adequate years: instrument
  coverage gap (reported as property, not defect)

**Real example (D-33-DIAG2.2):**
| Death year | ≥8 quarters | Verdict |
|------------|-------------|---------|
| 2015 | 0/157 (0%) | panel-boundary (FSNDS starts 2015Q1) |
| 2016 | 0/399 (0%) | panel-boundary (needs 2014Q1 data) |
| 2017 | 14/366 (3.8%) | transitional |
| 2018 | 60/319 (18.8%) | data present |
| 2019 | 59/321 (18.4%) | data present |

Cat-4 BK CIKs had similar profile (med_pre=4, ≥8q=11/194=5.7%),
consistent with the overall pattern — no additional defect specific
to BK.

---

## Denominator Re-Audit (DIAG2.3)

**Pattern:** The AM2 power census must run on the correct denominator:
CIKs with VALID lagged exposure (≥N pre-death quarters), not CIKs
with any form data. Using the wrong denominator (form-data n instead
of exposure n) produces a false PASS for AM2.

**Protocol:**
1. Define "valid lagged exposure": CIKs with at least N pre-death
   quarters in the exposure panel (N = registered pre-death window).
2. Compute valid n per category.
3. Re-evaluate AM2 thresholds on valid n:
   - pressured dead with valid lagged exposure ≥ 150
   - cat-1 (acquired) ≥ 20
   - cat-4 (bankruptcy) ≥ 20
4. If valid n < threshold, the verdict is UNMEASURED(underpowered at
   pole) — as registered in the protocol.

**Terminal-window secondary (fallback):** If the primary AM2 fails
because most deaths lack an 8-quarter pre-death window, the
terminal-window secondary (t-3..t, any exposure data at all) may
still run. CIKs with ≥1 pre-death quarter are the feasible
denominator. This terminal-window test is labeled TERMINAL SIGNATURE
per AM1 — never pooled with or promoted to lagged exposure.

**Real example (D-33-DIAG2.3):**
| Threshold | Valid n | Result |
|-----------|---------|--------|
| Pressured ≥ 150 | 46 | FAIL |
| Cat-1 ≥ 20 | 87 | PASS |
| Cat-4 ≥ 20 | 11 | FAIL |
→ G-C primary = UNMEASURED(underpowered at pole) as registered.
Terminal-window secondary feasible: 200/246 BK CIKs with ≥1
pre-death quarter.

---

## G-C vs G-C: Blocked vs Deferred — The Distinction

A gate that cannot run on its primary substrate is **blocked**, not
deferred:

- **DEFERRED** = substrate exists but hasn't arrived yet (forward
  panel not yet mature, data collection in progress). The test WILL
  run when the substrate is ready.
- **BLOCKED** = the substrate exists on disk but the pre-conditions
  (join verification, era coverage, denominator adequacy) have not
  been proven. The test CANNOT run until the audit clears.

A test that returns UNMEASURED(underpowered) after the audit is not
blocked — it has a verdict. The audit was the test. The verdict is
"this question cannot be answered with the available data."

**Real example:** G-C was initially reported as DEFERRED because
EOD data wasn't available for dead CIKs. The correct status was
BLOCKED(exposure join unverified) — the FSNDS panel existed on disk;
what hadn't been checked was whether the join and pre-death window
were sound. After the DIAG2 audit, G-C's true verdict was
UNMEASURED(underpowered at pole), with a terminal-window secondary
identified as still feasible.

---

## Author-Prediction Comparison

After completing each diagnostic, compare the outcome to the
author's pre-registered prediction. The comparison is part of the
record:

| Prediction | Actual | Verdict |
|------------|--------|---------|
| Join bug (CIK type mismatch) | No mismatch, 68.2% match | REJECTED |
| Cat-4 lagged-n 60-120 | 11 | REJECTED |
| The tables adjudicate | The tables adjudicate | STANDING |

Report rejected predictions dispassionately. A correct fix that
disproves the author's prediction is still a correct fix — the
prediction was the hypothesis under test.