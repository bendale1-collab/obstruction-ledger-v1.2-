# Precision Guard Rule & Invariant Scoring Protocol

Produced from the CVN program's USASpending + GLEIF measurement work.
Documents the missing-term audit protocol, precision guard rule, negative
control requirement, staged validation suite pattern, and off-target
distinction.

---

## Missing-Term Audit Protocol (for invariant-based measurement)

When scoring any invariant or constraint-based check, run a missing-term audit
BEFORE measuring the failure rate. This is the highest-value step in the protocol
and has caught misspecification in three domains (SEC GAAP, USASpending procurement,
GLEIF referential).

**The pattern:** Every hand-enumerated invariant that appeared powerful was
misspecified in the same direction — it was missing a term, and the missing term
made it fire on *correct* records. The signature is: high apparent failure rate +
near-total false positives on hand audit.

**Protocol:**
1. Enumerate candidate omitted terms for the identity BEFORE scoring.
2. Test each candidate: does adding it collapse the failure rate?
3. If the failure rate drops from ~60% to ~3% after adding a term, the invariant
   was misspecified, not the data.
4. A DV (discriminative value) that looks high because of misspecified terms is
   not a working invariant. The collapse is diagnostic.

**Examples (from the CVN program):**

| Invariant | Missing term | Apparent failure | Corrected |
|-----------|-------------|-----------------|-----------|
| Assets = Liabilities + StockholdersEquity | noncontrolling interest | 26.1% → 97% FP | dropped |
| CFops + CFinv + CFfin = ΔCash | FX reconciling line | 64.5% → 2.9% | collapsed |
| n_txn == n_mod + 1 | admin actions | 17.78% → 100% FP | pre-award actions |
| base <= total | de-obligations | 0.68% → 100% FP | delivery order lifecycle |
| first_action >= start - 30d | pre-award actions | 5.14% → 100% FP | DoD procurement timeline |

**Preregistered rule:** Run the missing-term audit BEFORE scoring any invariant.
Do not compute DV until candidate missing terms are enumerated and tested.
If the failure rate collapses after correction, the uncorrected DV is invalid.
Record the corrected DV as the finding.

---

## Invariant Scoring (DV)

For each invariant, measure:
  - **Evaluability** — fraction of records where all required fields are present
  - **Failure rate** — violations / evaluations, at the stated tolerance
  - **FP rate** — hand-audit against raw records: genuine inconsistency vs
    misspecification vs data-feed artifact
  - **DV** — evaluability × failure_rate × (1 - FP_rate)

Threshold: DV ≥ 0.05 for a working invariant. Also: per-constraint
evaluability must be reported separately from per-filing coverage (a constraint
that fires on 3% of records has near-zero value regardless of failure rate).

An invariant that passes all filters but still has high FP rate on hand audit
is a PRECISION FAILURE in the invariant specification, not a detection success.

---

## Precision Guard Rule (for fuzzy/recall-expanding operations)

**Any operation that expands recall must ship with a precision measurement,
or the aggregate will look like success.**

When widening a matcher (suffix regex, abbreviation list, fuzzy fallback,
fulltext search) to fix a real miss, the same widening lets degenerate records
absorb false matches. The worst failures are labelled EXACT (not fuzzy), because
the exact endpoint returns the degenerate record as the best match.

**Three-filter cascade for name-based matching:**
1. **Filter 1 — degenerate-record rejection.** Reject records whose normalized
   name is empty, consists entirely of legal-form tokens (llc, inc, ltd, lp,
   corp, etc.), or has no distinguishing content.
2. **Filter 2 — content-token agreement.** After stripping legal-form suffixes
   from BOTH the query name and the matched name, require the first two
   content-bearing tokens to agree.
3. **Filter 3 — domain-specific entity rejection.** For financial-chain joins,
   reject benefit-plan/trust entities (pension trusts, SERP trusts, defined
   contribution plans) that have no financials, no parent hierarchy, and no CIK.
   Generalizes to: reject entities whose name contains terms indicating they
   lack the data the downstream join requires.
4. **Jurisdiction flag.** For cross-border matching, flag non-US matches as
   SUSPECT rather than clean. Report three-way classification: clean / suspect
   / rejected.

**Report the three-way split:** The inflated number was 65% coverage; the
filtered truth was 28%. The difference is the precision failure. Always report
the three-way split (clean / suspect / rejected) so the reader can see the
inflation.

**The GLEIF trap (calibrated, reusable):** 4.03% of the 2.5M+ GLEIF register
has legal-form-only names. These are NOT corner cases — they are a measurable
fraction of the entire register. The degenerate-name census is a reusable
artifact: before any name-based matching against GLEIF, know that ~4% of records
are traps.

**Same failure class as the 5,000-record slice artifact:** A number produced by
a method nobody had checked was fit for the question, and the aggregate looked
like success.

---

## Recall vs Precision — Mandatory Labeling Rule

**When scoring generated invariants against an answer key, never report one as the other.**

- **RECALL** = fraction of the ANSWER KEY rediscovered (e.g., 14 valid codes / 4,066 official codes = 0.34%)
- **PRECISION** = fraction of the GENERATED SET that is valid (e.g., 14 valid codes / 15 generated invariants = 93%)

Both numbers must be reported, labeled, in every results table. The preregistered F1 threshold is on RECALL (≥40% of official edits), not precision. Reporting precision as recall inverts the gate and produces a false pass.

**Common failure mode:** "12/15 = 80% match" is PRECISION. F1 requires RECALL = 12/4,066 = 0.3%. The two differ by orders of magnitude when the answer key is large. Label them every time.

---

## C1 Recitation Probe (contamination control for model-generated content)

Before any model generates invariants from data, test whether the model has the target edit list memorized from training:

1. **Prompt** (no data provided): "List the FFIEC Call Report validity edit checks for schedule RC. Be as specific and comprehensive as possible."
2. **Score** against the answer key: extract MDRM codes mentioned, compare to official edit list, compute recall.
3. **Threshold** (preregistered): if recall ≥ 25%, the main result is CONTAMINATED — model is reciting memorized text, not generating from data. Report the held-out schedule rate as the primary result instead.
4. If recall ≪ 25%, the model is doing real generative work. Proceed.

The C1 probe is CHEAP (single API call, ~$0.0005) and runs before any generation. It is not optional — without it, a "rediscovery" number is unfalsifiably ambiguous between generation and memorization.

### C1 vs Generation Comparison

The comparison that matters is N_recite vs N_generate vs N_overlap, NOT C1 vs the full answer key:

- **N_recite** — edits recalled from memory (no data provided)
- **N_generate** — edits rediscovered from sample filings
- **N_overlap** — edits in both sets

**F2** (preregistered) requires BOTH: C1 recall < 25% AND N_generate > N_recite. If generation does not beat memory, the pipeline is a memory probe with extra steps. Report the three numbers and the set difference explicitly.

Result from CVN Stage 4 re-run: N_recite=18, N_generate=14, N_overlap=6 → F2 FAIL (generate < recite). The filings added nothing measurable.

---

## C2 Held-Out Schedule (second contamination control)

Split the edit list by schedule. Exclude a schedule's edits from every prompt and from any context the model sees. Generate invariants from sample filings for that schedule only. Score recall and precision against the held-out edits, and EXECUTE them per the standard protocol.

Compare held-out recall/precision to the primary schedule's. A large gap is contamination (model is reciting memorized RC edits, not generating from data). Parity is genuine generation.

The C2 control survives regardless of how C1 reads. It is not optional for any stage that reports recall against a published answer key.

Result from CVN Stage 4 re-run: RC-C generation produced only 1 MDRM code vs RC's 14. The gap confirms that RC is the friendliest domain — complex schedule-specific edits (risk ratings, maturity buckets, collateral types) are NOT generated from data alone.

---

## Execute-Before-Score Rule (generated invariants)

Generated invariants MUST be run against the full corpus before any scoring is reported. Failure rate, FP, and DV are ALL measured from execution, not from generation:

1. **Translate** each invariant into an executable check (e.g., `RCON2170 == RCON3300` with $1K tolerance)
2. **Run** against all filings in the corpus (not just the sample they were generated from)
3. **Measure**: evaluability, failure rate, FP via 15-record hand audit, DV
4. **Classify**: INERT (0% failure), FIRING (low failure, low FP), MISSPECIFIED (high failure, high FP)

A generated invariant that was not run against the corpus does not appear in any results table. A verdict about "does not show the anti-correlation signature" that is based on unexecuted invariants is not evaluable. This error recurred in Stage 4 and must not recur.

### Executed Invariant Classification

| Class | Criteria | Example |
|-------|----------|---------|
| INERT | 0% failure rate, pre-validated at write time | G1 Assets = Liabilities (0.00%) |
| FIRING (R2-shaped) | Low failure rate, low FP, genuine errors | G5 Securities >= HTM (1.55%, 0% FP) |
| MISSPECIFIED | High failure rate, high FP, missing term | G4 Gross = Net + Unearned + ALLL (99.45%, 100% FP) |

The R2 shape (low failure, low FP) is the positive instance — the same shape as GLEIF R2 (status vocabulary at 0.27%, FP~0%). Model-generated invariants that show this shape are the valuable output, even if recall against the full answer key is low.

---

## Negative Control Requirement

**A stage of all-zeros without a working negative control cannot distinguish
"invariants are bad" from "the scorer returns zero for everything."**

Before any measurement run, confirm the scorer produces non-zero failure rates
on a KNOWN-MISSPECIFIED invariant. SEC's three-term cashflow identity (47.4%
failure on the misspecified form using 2026q1 data) is the calibrated negative
control. Run it before every measurement session.

Tags to use for the SEC negative control:
- Operating: `NetCashProvidedByUsedInOperatingActivities`
- Investing: `NetCashProvidedByUsedInInvestingActivities`
- Financing: `NetCashProvidedByUsedInFinancingActivities`
- Delta Cash: `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect`

The three-term identity (op + inv + fin = dcash, no FX correction) should
produce ~47-64% failure rate depending on the dataset. If it produces 0%, the
scorer is broken.

---

## Staged Validation Suite Pattern

When validating measurement machinery, sequence stages from easiest to hardest:

1. **Stage 1 — internal consistency ($0).** Against the cached data itself.
   Arithmetic identities, temporal ordering, computational consistency.
2. **Stage 2 — referential integrity ($0).** Against a published register.
   Foreign keys, status vocabularies, date coherence.
3. **Stage 3 — real filer errors ($0).** Against a substrate with known errors.
   IRS Form 990, FFIEC Call Reports.
4. **Stage 4 — answer key (~$5).** The load-bearing test: model-generated
   invariants vs a regulator's published edit-check list.

Each stage gates the next. Every stage has a negative control seeded from a
known domain (SEC must read sparse-oracle). Stop rules: hand-audit disagreement
> 2/15 halts the stage; third data wall on one question → close the thesis.

**Hand-audit stop rule (restated):** Hand audit must agree with the MECHANICAL
CLASSIFICATION on >= 13/15. Disagreement about whether a violation occurred
means the scorer is broken. Agreement that a violation is a false positive is a
finding about the INVARIANT, not the scorer.

**Third-wall stopping rule:** When three substrates produce three different
reasons the same question cannot be answered, the pattern is the finding. Stop.
Do not hunt a fourth substrate. An untestable thesis recorded honestly is worth
more than a fourth partial test that produces another artifact.

---

## Off-target ≠ Underpowered (distinction protocol)

A test can produce a clean negative on a substrate where the mechanism under
test cannot occur (e.g., zero attrition on a lake with 100% key coverage). From
the result table alone, this looks identical to a genuine null. The tell: check
whether the MECHANISM the test was designed to measure is *possible* in the
substrate. If the failure mode (row loss, partial key overlap, etc.) cannot
occur, the result is OFF-TARGET, not underpowered. More samples, more tables,
or a wider beam would not help — the test measured a different question.
Consequence: "unresolved, not refuted."

---

## GLEIF Golden Copy — Download & Processing

The GLEIF Golden Copy is published daily at:
`https://leidata-preview.gleif.org/storage/golden-copy-files/YYYY/MM/DD/...`

Level 1 (LEI records): CSV, ~500 MB compressed, ~4.9 GB uncompressed.
  URL pattern: `https://leidata-preview.gleif.org/storage/golden-copy-files/{date}/{id}/20260724-0000-gleif-goldencopy-lei2-golden-copy.csv.zip`

Level 2 (relationship records): JSON or XML, ~35 MB compressed, ~1.1 GB uncompressed.
  URL pattern: `https://leidata-preview.gleif.org/storage/golden-copy-files/{date}/{id}/20260724-0000-gleif-goldencopy-rr-golden-copy.json.zip`

Level 2 CSV is NOT available (returns 404). Use JSON format.

**CSV columns (Level 1, key fields):**
- `LEI` — unique identifier
- `Entity.LegalName` — registered legal name
- `Entity.LegalAddress.Country` — 2-letter country code
- `Entity.EntityStatus` — ACTIVE or INACTIVE or NULL
- `Registration.RegistrationStatus` — ISSUED, LAPSED, RETIRED, etc.
- `Registration.InitialRegistrationDate`, `LastUpdateDate`, `NextRenewalDate`

**JSON structure (Level 2):**
- `relations` array
- Each item: `RelationshipRecord.Relationship.{StartNode, EndNode, RelationshipType, RelationshipStatus}`
- Relationship types: `IS_DIRECTLY_CONSOLIDATED_BY`, `IS_ULTIMATELY_CONSOLIDATED_BY`, etc.

**Key invariants (R1-R6):**
| Invariant | Expectation | Actual (2026-07-24) |
|-----------|-------------|---------------------|
| R1: LEI uniqueness | INERT (0/3.4M) | 0 duplicates — enforced at write time |
| R2: Status vocabulary | FIRING | 'NULL' entity status not in published vocabulary |
| R3: Date coherence | FIRING | 8.90% failure (278K/3.1M active records) |
| R4: Parent resolution | Needs L1×L2 cross-ref | UNMEASURED |
| R5: Consistency | ANALYSIS | 125K direct vs 131K ultimate children |
| R6: Cycles | INERT (0/481K) | 0 — GLEIF validates at write time |

**Degenerate-name census:** 136,253 records (4.03%) have legal-form-only names.
The trap we hit in the coverage pass is not a corner case — it's 4% of the
entire register.