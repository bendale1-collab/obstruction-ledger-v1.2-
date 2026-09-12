# Multi-Arm Baseline Integrity Protocol

## The Mistake (worked example from join-test, 2026-07-23)

In a 4-arm join-selection experiment (A=containment, B=frontier, C=hybrid, D=random), Arm A crashed on 3 of 4 base tables because CatBoost received only numeric features after `select_dtypes(include=[np.number])` filtered out all string columns. YADL Binary lake has 49/70 tables with only string columns.

**What went wrong:** The crash was recorded as `None`, which the summary code treated as "B beats A" since B produced a real score. The bug was structural (wrong preprocessing), not a genuine comparison. The report claimed B outperformed A when in reality A was broken.

## Rules

### R1 — Do not score a cell where any arm errored

An error (exception, None, NaN, crash, OOM, timeout) is MISSING DATA, not a finding. Do NOT:
- Score an error as a win or loss for any other arm
- Include the cell in summary counts ("B beats A: X/Y")
- Claim a comparative finding from an incomplete comparison

**Verdict for that cell:** `HARNESS_BREAKAGE` or `DATA_WALL`. Report the error, exclude the cell.

### R2 — Reproduce the published baseline before adding experimental arms

Before running any experimental arm (frontier, hybrid, etc.), the published reference configuration must produce valid scores on every cell it should. If the reference configuration crashes anywhere:
- Stop. Investigate the crash
- Fix the preprocessing, not the claim
- Do NOT proceed to experimental arms on broken infrastructure

**Gate:** "Can I reproduce Table/Figure N of the paper?" If no, stop.

### R3 — Prefer calling the published code over reimplementing

Reimplementations introduce subtle bugs:
- Different categorical handling (one-hot vs native CatBoost)
- Different aggregation semantics (group_by + first vs unique + keep=any)
- Different null handling (fillna vs dropna vs skipna)
- Different split logic (GroupShuffle vs Shuffle vs KFold)

When reimplementation is unavoidable (API changes, missing dependencies):
- Diff EVERY preprocessing step against the original
- Run a positive control (known-answer test) on each step
- Do NOT assume the reimplementation matches — measure it

### R4 — Report repair as repair, not as a separate arm

If Arm A crashes and you fix the bug, re-run everything from scratch. Do NOT:
- Report "Arm A (after fix): X" alongside "Arm B: Y" — this biases toward B
- Keep B's results from the broken run — B was evaluated on different infrastructure
- Record B's choice from the broken run — the model was ranking a different candidate pool

**Correct:** Re-run all arms on the fixed infrastructure. Report one clean table.

### R5 — D (Random) is not optional

Any multi-arm experiment with a selection mechanism must include a random-selection baseline:
- Random picks from the same candidate pool, replicated 5+ times
- If the mechanism doesn't beat random, report that FIRST — the mechanism is broken, not tested
- Arm D is not "noise" — it's the first gate. Fail here → mechanism does not work as specified

## Detection

**Before trusting a comparison, check for:**
1. Are all arms reporting scores for the same cells? If not, which are missing?
2. Of the missing cells: how many are errors vs genuine data walls?
3. Would removing missing cells change the headline (e.g., "B beats A on 2/3" vs "B beats A on 2/5")?
4. Is the error pattern structural (same arm always crashes) or random?

A structural error pattern (one arm crashes on a specific data type) is the strongest signal of a harness bug, not a finding about the other arm.
