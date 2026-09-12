# Invariant-Misspecification Pattern — Cross-Domain Replication

## The pattern

Approximately-right invariants look exactly like working ones. The signature is
consistent across domains:

| Domain | Invariant | Missing term | Apparent failure | Corrected | FP rate |
|--------|-----------|-------------|-----------------|-----------|---------|
| SEC | Assets = Liabilities + StockholdersEquity | noncontrolling interest | 26.1% | dropped, 97% FP | 97% |
| SEC | CFops + CFinv + CFfin = ΔCash | FX reconciling line | 64.5% | 2.9% | — |
| USAspending | n_txn == n_mod + 1 | admin actions (extra txns) | 17.8% | — | 100% |
| USAspending | base <= total | de-obligations | 0.7% | — | 100% |
| USAspending | first_action in [start-30d, end+365d] | pre-award actions | 5.1% | — | 100% |

Every invariant in this table was reasonable on paper. Every one fires on
legitimate operations, not errors. The common pattern: high apparent failure
rate + near-total false positives on hand audit.

## Critical measurement rules (from Stage 2-4 corrections)

### FP must be measured, never assumed
Recurred across three consecutive stages. Estimated FP produces a computed DV
that is not a result. Rules:
- Every FP cell states the sample size: "FP = X% (N/Y hand audit)"
- No FP cell reads "assumed", "estimated", or "~X%"
- A DV computed from an unmeasured FP is not a result and must not be reported
- Exception: INERT invariants (0 failures) have no FP to measure — say "0% (no failures)"

### Recall and precision both labeled, never one as the other
F1 was inverted in the Stage 4 first run: 12/15 = 80% is PRECISION of generated
invariants, not RECALL. F1 preregistered RECALL: fraction of official edits
rediscovered. Both numbers reported every time, both labeled.

### Sample sizes stated per invariant, not aggregated
"15/15 on all checked" across five invariants is one audit reported as five.
State sample size per invariant: "FP = 0% (36/36)", "FP = 0% (15/15)",
"FP = 100% (15/15)". Never aggregate across invariants.

### Singletons dropped from percentages
N=1 or any denominator below 10 cannot carry a headline percentage.
Report raw counts. "5/7 = 71% R2-shaped" with two singletons in a denominator
of seven is not a result.

### Hand audit that invents a rationale for a parse bug is worse than no audit
If a violation looks economically impossible, the first hypothesis is a parse
or sign-convention defect, not a novel legitimate operation. Check the parse
before writing the rationale. G14 ("negative deposits") was a code-mapping
error (RCON3210 = Total Equity Capital, not Total Deposits).

### Check MDRM dictionary/code mappings before scoring
The model's generated invariants used RCON codes that mapped to semantically
different fields than assumed. RCON0071 = INT-BEARING CASH (not "Cash"),
RCON0081 = NONINT-BEARING CASH (not "Interest-Bearing Balances"). Verify
every code mapping against the source dictionary before scoring.

### Tier 0 floor checks (Stage 5 fix for three stages of parse-contaminated results)
Run before any invariant scoring:
1. Check digit/validation on identifiers (NPI Luhn, EIN, etc.)
2. Round-trip: parse, re-serialize, diff against source
3. Closed-vocabulary membership on taxonomy codes and state codes
4. Range bounds on amounts; flag sentinels explicitly

### C1 vs generation comparison
The comparison that matters for contamination: N_recite (edits from memory)
vs N_generate (edits from data). If N_generate <= N_recite, the pipeline is
a memory probe with extra steps. Report the three numbers: N_recite,
N_generate, N_overlap. Show the set difference explicitly.

### Saturation curve to establish recall ceiling
A single generation pass doesn't establish the ceiling. Run multiple passes
at varied prompts, track cumulative unique valid codes vs cumulative spend.
Report where the curve flattens. The recall-per-dollar curve is the
economically meaningful number.

## Missing-term audit protocol (preregistered, run BEFORE scoring)

Before computing failure_rate for any invariant:

1. **Enumerate candidate omitted terms.** For each term in the invariant,
   ask: "what else could affect this value?" Examples from actual data:
   - Balance identity: noncontrolling interest, preferred stock, accumulated
     other comprehensive income
   - Cash flow identity: FX translation, discontinued operations, acquisition
     effects
   - Count identity: administrative actions, modifications without obligations,
     pre-award activities
   - Sequential identity: de-obligations, terminations, closeouts

2. **Test each candidate.** For each term, check whether records that fire the
   invariant have that term present. If a term is present in 90%+ of firing
   records, it is the missing term and the invariant is misspecified.

3. **Measure FP rate BEFORE reporting failure rate.** Audit 15 firing records
   by hand. Classify each as:
   - **Genuine error** — a real data inconsistency
   - **Misspecification** — the invariant is approximately right; the firing
     record is a legitimate operation captured by the missing term
   - **Data artifact** — a feed-level issue (truncation, rounding, stale cache)

4. **If FP rate > 5%, the invariant is misspecified.** Do not report DV.
   Report the missing-term audit findings instead.

## Hand-audit halt threshold (2/15 rule)

Any hand audit disagreeing with mechanical classification by more than 2/15
halts the stage. The scoring is broken, and every downstream number computed
under it is invalid until recomputed.

| Agreement | Action |
|-----------|--------|
| >= 13/15 (>= 87%) | Pass — mechanical scoring matches human judgment |
| 11-12/15 (73-80%) | Flag — the invariant is marginal; report the disagreement |
| < 11/15 (< 73%) | **HALT** — scoring method is suspect |

2/15 is the threshold because:
- At 1/15 disagreement, the error rate is 7% — acceptable for mechanical methods
- At 2/15, it's 13% — the method is missing systematic real failures
- At 3+/15, the method is failing on a pattern, not a random sample

## Missing-term signature test

After the missing-term audit, the invariant's corrected form should have a
failure rate below 5% (or the expected base error rate for the domain). If
adding the missing term does NOT collapse the failure rate, the invariant has
a different problem (wrong unit, wrong tolerance, wrong domain).

## Domain generalization

This pattern replicated across two structurally different domains:

| Domain | Nature | Why it happened |
|--------|--------|-----------------|
| SEC (EDGAR) | Regulated, pre-validated | GAAP is a taxonomy, not an identity. Every identity is a choice: which terms to include, which to exclude, how to handle cross-period effects. |
| USAspending | Operational, not pre-validated | Federal contracting processes are business operations, not arithmetic. De-obligations, pre-award actions, and admin actions are legitimate lifecycle events. |

The common cause: **domain knowledge was assumed in the invariant design.** The
invariant writer knew the accounting identity "Assets = Liabilities + Equity"
but did not know that "Equity" as reported by SEC filers excludes noncontrolling
interest. The invariant writer knew federal contracts have a base and a total,
but did not know that de-obligations are a standard lifecycle event.

**Implication for the invariant-cheapness bet (VDH §10.1):** If domain experts
writing invariants by hand miss these terms, can a cheap model generating
invariants from examples do better? The Stage 4 test (FFIEC Call Reports vs
answer key) is designed to settle this.