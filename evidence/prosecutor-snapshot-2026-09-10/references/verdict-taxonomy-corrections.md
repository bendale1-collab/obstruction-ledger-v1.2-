# Verdict Taxonomy Corrections — Learned 2026-07-19

These corrections were surfaced during the Phase 0 canary retest (OMNIBUS C2/C6) and are not yet embedded in the main SKILL.md (which is at the 100K char limit). Patch into the main body when room opens.

## 1. BLOCKED ≠ FAILED (verdict taxonomy)

A data-access limitation that prevents a test from running is **BLOCKED**, not a structural failure.

| Category | Meaning | Response |
|----------|---------|----------|
| **BLOCKED** | Test couldn't run due to data-access limitation (trial truncation, free-tier window, coverage gap, credential missing) | State blocker cause explicitly. Recommend fix. Do NOT collapse into a verdict. |
| **REAL FAIL** (structural) | Test ran on correct data with sufficient depth; threshold was missed. The signal is genuine. | Kill for this canary. This IS a thesis signal. |
| **UNTESTED** | No attempt was made because a prerequisite failed first (e.g., C5 cannot proceed because C2 didn't produce pairs) | State the prerequisite gap. Do not call it a pass or fail. |

**BLOCKED can become REAL FAIL** after the blocker is fixed. Do not assume BLOCKED is temporary. In this session: C2 was initially BLOCKED (Shovels trial truncation), then retested on Cleveland open data with correct 13-year window and became REAL FAIL (0 residential pairs).

## 2. Measurement axis must match model axis

A negative finding is only valid if the measured quantity is the same quantity the model uses.

**Example from this session:** C6 initially measured cross-county annual degree-days (CV = 0.011) and reported "NEO too uniform." But the model axis is **cumulative DD-since-install per home** — a different quantity that varies by install year and lifespan duration, not just by geography. The finding was invalid.

**Rule:** Before reporting any negative result, ask: does the quantity I measured correspond to the model's covariate? (a) ≠ (b) is not evidence about (b).

## 3. Verdict must be internally consistent

The headline verdict must match the evidence body. A KILL headline followed by "bounded pivot is the only path forward" in the final paragraph is a contradiction. Three valid pairings:

| Headline | When | Body evidence must show |
|----------|------|------------------------|
| **KILL** | Structural failure confirmed on correct data | Specific canary that failed, threshold missed, data was correct/window sufficient |
| **EXPAND-THEN-RETEST** | Data-access limits caused the shortfall; a bounded fix exists | Specific blocker, specific fix (deeper data, wider geography, different variable), retest plan |
| **AMBIGUOUS** | Test ran but couldn't resolve (thin cells, CI overlapping zero) | Result is "can't tell," not "it's dead" or "it works" |
| **GO** | All gates passed on correct data | Every canary cleared its threshold |

A headline that contradicts the body's evidence is a framing error, not a finding.
