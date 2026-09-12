# Standing Rules 18-22 (from r5 closeout archive)

These rules were added at r5 (NSB-P1 closeout) and belong in the PROSECUTOR framework.

## Rule 18 — Measure the payoff before building the forecast

*Ask whether the predicted event is worth predicting before building machinery to make one.*

Three instruments were tested before anyone measured what the cure event does to the security. The answer — median −64.8% at twelve months, indistinguishable from delisting — would have closed the program at G0 and saved four expressions of instrument work. Measure the payoff of a correct forecast before building the instrument to capture it.

## Rule 19 — Check the population before writing the cut

*One line of composition arithmetic precedes any stratified design.*

D-90: a five-bucket type cut specified against a one-bucket population, discovered when four rows returned empty. The population composition (`Counter(type for ep in episodes)`) is free and runs before the spec.

## Rule 20 — Cross-check the verdict against the evidence

*A verdict line and its own evidence table must be checked against each other.*

D-89 inverted the program's central finding while printing the correct table directly above it. Any return stating a preregistered verdict must restate the criterion, then the evidence, then the verdict, in that order.

## Rule 21 — CANNOT-QUOTE is not a shortcut

*A tick after CANNOT-QUOTE is a fabrication, not a shortcut.*

Honest inability to verify is an acceptable return (D-88, D-85). Filling the slot with a tick is the D-59/D-60 family. Leave the rule unticked.

## Rule 22 — Vendor coverage is a survivorship filter

*Vendor coverage is a survivorship filter wearing a different hat.*

Yahoo returned 98.6% of survivors and 25.0% of ABSENT-NOW names. Any price study on a delisting population must probe delisted-name coverage first and treat the answer as a gate, not a caveat. Rule 10, extended from filters to sources.

## Additional notes from the P1 cycle

### CAR vs RAW return labeling

Always label whether a return figure is CAR (benchmark-subtracted) or raw. The two differ by the benchmark return. Over 18 months, IWM can contribute ~20 points. Comparing CAR to raw produces a spurious "gap." State the metric with every figure.

### Mean vs median: wrong tool for the question

The ban on means is correct for kill tests (overlapping distributions, where a mean is a statement about the tail). For distribution questions (the tail IS the question), means are licensed alongside full percentiles, skew, and threshold counts. Both statistics appear together, never separately. State which answers which question.

### Collision diagnosis requires Form 25

TRUE-COLLISION = `series_first > Form 25 date`. Without a Form 25, the rule cannot fire. Do not infer from gap size alone. AXDX and BIOR were assigned TRUE-COLLISION with no Form 25 — the rule cannot produce that classification.

### Borrow data is point-in-time constrained

Historical borrow rates are not available from free sources. IBKR short-stock file, Fintel, and iBorrowDesk are current-snapshot only. Nasdaq short interest is point-in-time but measures shares short, not rate. The borrow gate requires a paid vendor or operator-side access. Current-snapshot data standing in for historical rates is D-49/D-10 class.

---

## Rule 23 — Output precision binding

*Eigenvalues, residuals, and spectral distances must be stored at ≥12 significant digits in machine-readable form (JSON), not only as report tables.*

The A1/A5 reconciliation (2026-09-09) showed that no 12-digit precision was available for the H2 generalized eigenvalue nearest to 1 — only a 4-digit table summary existed. The output JSON is the source of truth; the report table is a human-readable view.

### Implementation

Every eigenvalue computation output MUST be saved as a `.json` file alongside the report, containing:
- The full eigenvalue array (complex, ≥12 digits)
- Residual norms (≥12 digits)
- The parameter values (N, L, a) that produced them

The JSON file must be in the work directory. The seal's manifest should contain the JSON files.

### Exceptions

- Floating-point results from iterative solvers where the convergence criterion gives <12 stable digits: store at the achieved precision and note the convergence delta.
- Partition/classification counts (integers by definition): JSON with integer types is sufficient.