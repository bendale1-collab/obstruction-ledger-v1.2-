# Audit Discipline Rules

These rules were added after the five-domain program close-out identified recurring failure modes in quantitative research execution. They complement the "Report Format (hard rules)" section in the main SKILL.md.

## 1. Audit notes must name the invariant they audited

A note that says "15/15 across all checked" is one audit reported as five. Each audit note must include the invariant ID (e.g., "G2: 36/36, FP=0%"). In one session, three of three audit notes did not match their invariant's definition — the labels were swapped or the audits examined something else. Re-audit each invariant against its own definition, not the description of another invariant.

**Tell:** An audit note that describes a relationship that doesn't match the invariant's stated formula (e.g., "minority interest term" for an invariant described as "Total Deposits = Domestic Deposits") means the descriptions are scrambled. Fix the descriptions first, then re-audit.

## 2. Code-mapping corrections propagate to every invariant using that code

When a single MDRM code (e.g., RCON3210) is found to map to a different concept than stated, every invariant referencing that code must be re-derived. Do not fix one and skip the rest. Verify EVERY code in all invariants against the dictionary in one pass, not just the one that caught your attention. Report the verification table.

**Protocol:**
1. Build a complete code→definition mapping from the data source (TSV headers, ontology TTL, API schema)
2. For each invariant, list every code it uses
3. Verify each code against the mapping
4. Re-derive what the invariant actually computes (not what it was described as)
5. Re-audit all invariants using the corrected code mapping

**2026-07-24 session finding:** All 15 FFIEC invariants had wrong descriptions. The model hallucinated code meanings (e.g., RCON3210 described as "Total Deposits" when it's actually "Total Equity Capital"). The `safe_get` RCON→RCFD conversion was correct, so the invariants fired against the right data columns. But every description was fabricated. This was caught only because one invariant (G6) was flagged — the other 14 were never checked.

## 3. Demonstrate random sampling before drawing from a sample

A 200K-out-of-9.7M sample that gives 5.7% resolution vs 100% on the full join is not random — it is undersized. Report the sampling method, the population size, and the sampling fraction before drawing any conclusion.

**Protocol:**
1. State the population size (N_total)
2. State the sample size (N_sample)
3. Compute sampling fraction = N_sample / N_total
4. If sampling fraction < 20%, report the expected bias direction
5. For registry-keyed exact joins, always load the full key column as a set rather than sampling. 9.7M 10-digit strings fits in ~500MB — use `zipfile.ZipFile` streaming to read the NPI column in chunks, build a Python set, then join.

**2026-07-24 session finding:** N1 originally reported 5.7% resolution from a 200K sample. The full-register join (9.7M NPIs) gave 100% resolution. The sample was not biased toward deactivated NPIs — it was simply undersized for the join. The "true resolution near 100%" estimate was correct but the sample could not confirm it.