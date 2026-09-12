# ISP GATE Methodology — Mining Pipeline Verification

**When this applies:** Any task that uses linear-algebra mining (null-space / SVD / RREF) to extract identities from tabular data, or tests whether a corpus has exploitable structure for enforcement differencing. The ISP (Invariant Specification Pipeline) gate pattern tests the premises of a design before building anything.

---

## The ISP Gate Pattern

A two-gate pre-check that tests whether a downstream pipeline has a target:

- **G0a — Residue Existence**: After subtracting what the publisher already checks, is there anything left for a pipeline to shortlist?
- **G0b — Interrogation Probe**: Does a model with the source document in context name a missing term it cannot name from memory?

Both gates run before any pipeline exists. A failing gate is the result — do not build Stage A on a failed G0a. A clean negative is worth more than a pipeline.

---

## G0a — Null-Space Mining Protocol

### Instrument verification (F1 applied to mining)

Before trusting the mining output, verify the pipeline can recover known-true identities:

1. **Select 5+ known identities** that:
   - Are linear identities (A = B or A = B + C)
   - Reference fields present in the corpus
   - Hold in this quarter's data at the stated tolerance (verify by direct arithmetic)
2. **Run the full pipeline**: mine → extract → match
3. **Check per identity**: surfaced Y/N, matched Y/N
4. **Require 5/5**. Anything below 5/5 means extraction or matching is broken and no residue count from this pipeline is interpretable.

**Pitfall — official edits are not linear identities.** Published edit lists (e.g., FFIEC 4,066 edits, SEC validation rules) are often XBRL formula constraints with conditional logic (`If(A > 0, B > 0, TRUE)`), not simple linear identities. They cannot be used as F1 probes without parsing the formula structure. Use identities verified by direct arithmetic on the corpus instead.

### Extraction: null space → sparse identities

SVD returns an orthonormal basis, which is dense by construction. Real identities are sparse sums over few fields. A coefficient threshold applied to a single SV basis discards them.

**Do both, report both:**

1. **RREF over the null-space basis** — deterministic, produces pivot-sparse rows directly.
2. **Per-vector L1 minimization within the null space** — find the sparsest vector in the span. Report the solver and its tolerance.

**Compare yield** from RREF, L1, and the original coefficient threshold. If yield differs materially, extraction was the binding constraint.

**Report identity FAMILIES, not vectors.** Multiple expressions of one field set is one candidate, not five. The RREF resolves this.

### Pruning parameters (report every time)

- SVD tolerance (relative and absolute)
- Coefficient threshold for null-space vector extraction
- Identity complexity limits (min/max terms)
- All of these are specifier's blind spots re-entering through the back door (Filter H1)

### D3 applied to ALL counts

The D3 rule (exact 0.00% or 100.00% is auto-flagged) applies to every count, rate, and denominator in the report, not just the final percentage. This includes:
- Match count of 0 against the official edit list
- Residue count of 0 or 5 (must be investigated)
- Any intermediate count that is exactly zero

The prior review passed Class D by checking only the residue percentage. Apply each class to EVERY number.

### Degenerate identity detection

Many fields in regulatory data are sentinel values (always 0, or equal to a single other value). These produce degenerate identities:
- `RCFD6724` (a sentinel field) equals ~40 other fields in the RC schedule
- `RCONPR06` equals any two fields whose sum is zero
- All 42,000+ sum identities in the RC corpus involve adding a zero-valued field

**Filter:** Before counting an identity as a candidate, confirm at least one field has nonzero variance. A sum of two zero-valued fields is not a finding.

---

## G0b — Interrogation Probe Protocol

### Target selection

Choose a known-misspecified identity where:
- The correction was MEASURED (e.g., 64.5% → 2.9% after adding FX term), not asserted by an audit
- The answer is externally documented (standard, regulation, published guidance)
- The missing term is a single identifiable concept, not a compound

### Arm structure

**ARM 1 (memory):** State the identity, give the failure rate, no documents. Prompt: "This identity fails on X% of filings. What term is missing?"

**ARM 2 (retrieval):** Identical prompt, plus the relevant source text in context (e.g., ASC 230, SEC guidance, FFIEC instructions).

Three samples per arm, same model, same temperature. Report all six outputs verbatim.

### Preregistered thresholds

- PASS: ARM 2 names the missing term and ARM 1 does not, on a majority of samples.
- CONTAMINATED: Both arms name it → the probe is too easy; the identity is in training data. Pick a second target and rerun.
- FAIL: Neither arm names it → retrieval does not close the gap. Stage E is dead.

### Scope note

G0b tests document EXTRACTION (can the model locate a term the document names?). Stage E's task is harder — form instructions describe legitimate operations without tagging any as the missing one. G0b is a pass on extraction and a partial test of the INFERENCE capability Stage E needs. If Stage A is ever built, Stage E requires its own probe on a target where the document does not name the answer.

---

## Round-Trip Parse Verification

Before any mining, verify the parse round-trips for EVERY schedule that feeds the merged matrix:

1. Parse the TSV/CSV
2. Re-serialize numeric values
3. Diff against the source
4. Report: values checked, mismatches, and per-schedule breakdown

A parse defect in one schedule reproduces the T5 error pattern (95.24% failure on 0.3% of corpus). Round-trip testing only one schedule is insufficient.

---

## Result interpretation

Both outcomes from G0a are acceptable:

- **PASS (>= 50 residue candidates)** → enforcement differencing has a target; Stage A is buildable.
- **FAIL (< 50, with verified instrument)** → the publisher checks essentially everything the data reveals in these schedules. A clean structural negative, stronger than three availability walls, and it kills the architecture for $0. Report it as a result.

What is NOT acceptable is a FAIL from a pipeline that cannot recover known-true edits. The instrument must be verified before the verdict is established.