# Gate Execution Lessons

Emergent from G0 (VLM ledger-diff budget breach) and M2 (conditioning return rate — video cost wall), 2026-07-25/26.

## Budget discipline (G0 kill cause)

- **Measured prices, not assumed.** Run ONE generation on each model first. Report the observed billed cost with the logged call id. The observed token count for a 720×1280 image on GPT-4o-mini was 36,856 — 17.5× the naive estimate of 2,100. Assumed prices killed G0.
- **Propagate observed numbers into the budget table.** A note acknowledging 36,856 tokens alongside a table using 2,100 is a self-contradiction. The table and the note cannot both stand — the table is wrong.
- **No "well within $X" as a conclusion.** Show the arithmetic: price × arms × n, plus mutation calls, plus sweep settings. If the margin is under 10%, the budget may not cover the run — say so at registration, not at exhaustion.
- **Budget breach at design time is a result, not a failure to avoid.** G0 died at $26.56 on $8 — 3.3× over, before any experiment call. That is the correct outcome. Do not shrink arms, drop arms, downscale images, or substitute substrate to fit — those are post-hoc re-bands (§2.6).

## Substrate declaration (M2 correction)

- **Gate 0 must declare the input modality.** The spec said "video" — I priced "image." Image-to-image reference conditioning is a different, easier, better-studied problem. The substrate switch is what made the price fit.
- **Declaration rule:** State "Modality: [video/image/text/audio]" as the first line of Gate 0. If it differs from the spec, the gate is blocked.
- **The measured price for the WRONG substrate is not a price for the experiment.** It's a budget-measurement call that must be repeated on the correct substrate.

## Sweep requirement for cost-based kills

- **A cost-based verdict from a single path is UNMEASURED(not swept).** This is K2 in cost space — the parameter that moved the result was chosen, not swept. It is the same defect that killed G0 (assumed token count).
- **Minimum sweep:** 3 routes × 2 tiers × 2 clip lengths (for video). Report a table with source URLs and retrieval dates.
- **Route examples:** direct API, platform reseller, subscription credits.
- **Tier examples:** budget, standard, lite.
- **Excluded tiers must have a stated reason** (e.g., "budget tier excluded — reference conditioning unconfirmed"). An excluded tier without a stated reason is an omitted parameter.
- **Verdict rule, fixed at registration:** minimum > $8 → UNTESTABLE(cost). Minimum ≤ $8 → verdict re-evaluated.

## Frozen-threshold discipline (M2 item 2 correction)

- **Thresholds are FROZEN at registration or have a separate calibration protocol.**
- **No "mutation test will calibrate."** Writing a number and then qualifying it with "pending calibration" is a post-hoc re-band (§2.6). Either the number is the threshold (mutation test only verifies operationality), or there is a separate calibration protocol written in full before any measurement runs.
- **Calibration protocol requirements:**
  - What inputs (exact paths or generation parameters)
  - What statistic (mean, median, percentile)
  - What rule maps the statistic to a threshold (e.g., "set threshold at median of canonical-self distances − 2σ")
  - The rule is fixed before any number exists
  - Mutation test runs after calibration to verify operationality — it does NOT adjust the threshold

## Adherence arm against mode collapse (M2 item 3)

- **The falsification test must test what N1a says validity rests on.**
- N1a says the gap licenses the causal claim only if mode collapse is ruled out. The standard mutation test (canonical vs self, canonical vs unrelated) tests METRIC DISCRIMINATION, not MODE COLLAPSE. Mode collapse produces a large gap driven by copying.
- **Add an independent adherence measure:**
  - Declared in advance, computed in code, no model adjudication
  - Compares output content to prompt requirements (elements present, requested actions)
  - Report alongside return rate
- **Decision rule:**
  - Return rate UP + Adherence FLAT → conditioning works
  - Return rate UP + Adherence DOWN → COPYING, not conditioning (KILL)
  - Return rate FLAT → write path inert

## n derivation (M2 item 2 spec defect)

- **n without a power calculation is a spec defect.** A preregistered n without a declared minimum detectable effect (MDE) is UNMEASURED(n not derived).
- **Registration template:** n must be accompanied by:
  - Stated MDE (e.g., "0.08 cosine units at α=0.05, β=0.80")
  - Population variance estimate (from literature or pilot)
  - The test statistic used in the power calculation
- **Inherited n:** A number copied from convention ("n ≥ 100 per arm is standard") without derivation is a defect. Record it as such.

## Search width for negative claims (M2 item 4 correction)

- **"The number does not exist" without N is unfalsifiable (§1.9).**
- **Report:** how many searches, which venues, which query terms, what the closest near-miss was.
- **Label the claim EXPLORATORY(N={n})** where n is the number of searches.
- **Near-miss must be reported in full:** what it measured, how it differs from the target.
- **N=3 across 3 venues is weak.** The number MAY exist in a venue not searched. The claim is exploratory, not established.

## Format rules (from user corrections across G0 and M2)

- **Emit content, not status.** Do not disclose completed work inside a status line about the next step.
- **Every cell MEASURED(n) or UNMEASURED(reason).** No third state.
- **Truth-engine ref:** `truth-engine-deployment.md` covers spec-gap handling, spectral method failure taxonomy, Fourier fallback, and H-B criterion adaptation on finite domains.
- **No arithmetic in prose.** Recompute from logged values, show the inputs (counts, not rates). A conclusion stated in prose without showing the arithmetic is a fabrication risk.
- **A failed gate is a result.** Stop and report. Do not remediate, do not propose alternatives, do not adjust the budget to fit.
- **No "well within $8" or similar.** Show the arithmetic or it doesn't stand.
- **Do not report a gate by its status word.** Status words belong in tables, not as the deliverable.

## Third-wall rule: the cost/data distinction (proposed amendment to §2.3)

- **Literal reading:** Three walls → UNTESTABLE. This is what governs the close-out.
- **Proposed amendment:** The rule conflates permanent constraints (locked dataset, deprecated API — half-life: years) with decaying constraints (API pricing that drops ~50%/year — half-life: 6-12 months).
  - Data walls: permanent. Count toward 3-strike limit.
  - Cost walls (design-time parameter error): fixed once corrected. Do NOT count.
  - Cost walls (market pricing): decay on a ~6-12 month cycle. Count, but the counter resets when market pricing crosses the registered budget.
- **Stated reading:** The literal reading governs unless the amendment is adopted. Program recorded as UNTESTABLE(3 walls) under literal reading.

## Selection wall: when recoverability IS selection (FIND-24)

A third wall type not anticipated by the original three-strike rule:

- **Data wall:** The data does not exist at any price. Permanent. Counts toward 3-strike limit.
- **Cost wall:** The data exists but costs more than the registered budget. Decaying (pricing drops ~50%/year). Counts, but counter resets when market pricing crosses the budget.
- **Selection wall:** The data exists but is biased on the signal dimension. The very mechanism that makes recovery possible (e.g., a dead firm's filing footprint) is correlated with the outcome of interest. Recovery campaigns improve coverage but also narrow the selection gap — the residual unmapped are the discovery.

**Detection pattern:** Run multiple recovery campaigns. If coverage improves AND the selection ratio moves toward the target but does not cross the bar, the gap is structural. The data is telling you something about the world: the population that cannot be recovered is systematically different on the signal dimension.

**Consequence:** A selection wall is NOT a test failure. It is a finding about the population. The hypothesis is not dead — it is unanswerable with the available data. The forward panel (prospective, contemporaneous recording) is the only cure, because it captures the population at the time of observation, not retroactively.

**Decision rule:** If the selection ratio improves with recovery effort but cannot cross the registered bar, log the finding and close the retrospective branch. Do not declare a data wall — the data exists and was characterized. The characterization IS the output.

**Real-world example (D-31/D-32):** Coverage improved from 42.5% to 52.3% across three recovery campaigns. The pressure selection ratio improved from 2.73x to 2.04x. The 1.5x bar was not crossed. The residual unmapped (47.7% of dead firms) were lower-pressure, deeper-history firms that no free resource reaches. The finding: "recoverability is selection" — the trail a dead firm leaves is proportional to visible survival, and visible survival under pressure approximates the exposure construct. The retrospective branch was closed, and the hypothesis moved to the forward panel.

## Blind amendment registration (D-33 pattern)

Before running a test, register amendments that could KILL it. The three-amendment pattern:

1. **Lagged exposure amendment:** Exclude the terminal window (t-3..t) from the primary exposure. Deal churn and collapse-quiescence in final quarters could let the exit cause the signature. Measure exposure at t-8..t-4. Report terminal window separately as TERMINAL SIGNATURE — never pooled with lagged.

2. **Power census amendment:** Before the test, emit the usable N with valid exposure, the variance of the exposure within that group, and the event counts per ordinal category. Kill if any cell implies detectable effect requires more observations than available.

3. **Named confound amendment:** Pre-register the dominant alternative explanation. Any confirming result ships with the disclaimer: "consistent with [mechanism] AND with [confound]; the design excludes [narrow-causality] but not [broader-causality]." No stronger claim is licensed.

**Registration rule:** All three amendments are written BEFORE any count from the test exists. They are registered as amendments to the existing protocol, with the same frozen-spec discipline. The author states "registered blind" and "could kill as easily as license."

## Practical pattern: the pre-compute phase

Before any experiment generation, the PROSECUTOR must emit (all as content, no status):

1. **N1a** — two sentences + coincidence verdict
2. **Prior art** — what exists, what it measured, what is new. If the number exists, stop.
3. **Tolerances** — numeric, frozen, per-embedder, with cited basis
4. **Measured price table** — per-model cost/gen from one real call, provider URL, date
5. **n derivation** — MDE, variance, test statistic
6. **Search width** for negative prior-art claims
7. **Adherence measure** if N1a rests on ruling out mode collapse
8. **Substrate declaration** — modality stated as first line

If any of these cannot be produced, the gate is blocked at design time — report the reason and stop.