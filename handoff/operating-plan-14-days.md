# Operating Plan — Obstruction Ledger, Next 14 Days

**Drafted 2026-09-12. Not sealed. Compute blocked until the pre-registration for W2 has a gist revision timestamp.**

Three tracks. They do not depend on each other and can interleave. Every item has an owner, a cost, a threshold, and a stop rule.

---

## Track A — Deflation checks (no compute, no code)

Run these first. Either could cut the program's premise, and both are afternoons.

### A1. Is anyone being asked for Article 12 evidence? (Q2)
**Do:** five calls or emails. Targets: two compliance leads at EU-exposed companies deploying agents, one AI governance vendor (Credo AI / Holistic AI), one Big-4 AI assurance practice, one procurement contact.
**Ask, verbatim:** "Since 2 August, has any customer, auditor, or regulator asked you to produce logs of what an AI system actually did? What did they ask for specifically?"
**Record:** yes/no, what was requested, who requested it.
**Threshold:** ≥2 of 5 report a concrete request → the Nash-regulator leg holds. 0 of 5 → the leg is aspirational; downgrade it in the score and stop citing Art. 12 as demand.
**Cost:** one afternoon. **Owner:** founder only.

### A2. Rescore IISE under the reformulation (Q3)
**Do:** rescore against `R_T = U_T · A` with the sealed-record product, not the subspace instrument. Score bootstrap, novelty, and each power leg separately.
**Explicitly rescore:** Helmer power — replace "bit-deterministic replay" (falsified on hosted APIs) with "cornered resource: dated rule-exploit ledger," and credit it only at the length the ledger actually has today.
**Threshold:** if the reformulated score is below 46%, the reformulation is a retreat, not an improvement — say so in the ledger.
**Cost:** two hours. **Deliverable:** `ledger/iise-rescore-2026-09.md`, appended not edited.

### A3. Traceability claim audit (Q16, Q17)
**Do:** two edits to the postmortem before Rev I.
- Implement per-profile git author (standing rule 9, filed twice, never done). Until done, strike "traceable to an author" from all copy.
- Mark K1a as **retrodiction, not pre-registration** — Rev H postdates the code commits by three hours (already filed as ANCHOR-POSTDATES-ARTIFACT; the postmortem does not carry the consequence).
- Add denominators to every count in §4b.
**Cost:** one hour plus a terminal for the gateway restart. **Stop rule:** do not publish Rev I until all three are done.

---

## Track B — External numbers (weekend, no customer needed)

The cheapest route to standing: run your own checks on data you didn't generate.

### B1. Audit classes on public trajectories (Q8)
**Corpus:** TRACE code benchmark (517 trajectories, 54 hack categories) and Terminal Wrench (3,632 exploit trajectories). Both public, both labeled. Pin commit SHAs.
**Do:**
1. Freeze the four audit class definitions (mechanical versions from the K1 pre-reg draft: `A_weak`, `A_selfev`, `A_nonex`, `A_pad`).
2. Hash the definitions file. Publish the hash to the gist **before** running.
3. Run all four classes over both corpora.
4. Report per class: recall against their labels, FPR on their clean trajectories, confusion matrix, Wilson 95% CI. Denominators on everything.

**Thresholds, pre-registered:**
- Any class with FPR > 0.05 → retire it before it enters any product claim.
- Aggregate veto `V = 1 − Π(1 − FPR_i)` > 0.15 → the gate is a tax; disclose that number wherever the gate is described.
- Recall < 0.3 on a class their labels cover → the class is not mechanically detectable as defined.

**Why this first:** it produces comparable numbers on their data, which is the credential. It needs nobody's permission. It is a weekend.
**Deliverable:** `results/B1-public-trajectory-audit.json` + a two-page note citing the frozen-definitions hash.

### B2. Reasoning-model shelf life (Q9)
**Do:** re-run the six failure classes on 20 tasks with a reasoning model. The catalogue was built on non-reasoning output.
**Threshold:** if ≥4 of 6 classes still appear at >5%, the catalogue holds. If ≤2 appear, the catalogue is a 2025 document — say so in its header and date-stamp its scope.
**Cost:** ~$20.

### B3. Naming audit (Q10)
**Do:** systematic search for prior naming of (a) self-validating reference, (b) confidence recorded alongside error. Search by description, not by your names.
**Output:** either a citation (drop the novelty claim) or a confirmed gap (publish the names).
**Cost:** two hours. **Feeds:** the novelty leg in A2.

---

## Track C — The instrument (gated behind a pre-registration)

Nothing here runs until the pre-reg is sealed and its hash is published.

### C1. Base rate first (Q5)
**Do:** sample 500 Mathlib theorems. Run Lean's `unusedVariables` linter plus explicit hypothesis ablation. Count how often a stated hypothesis is unnecessary for the given proof.
**Threshold:** unnecessary rate < 0.05 → **no negative class; Λ has nothing to discriminate. STOP Track C.**
**Also measure (Q4):** for hypotheses flagged unnecessary-for-this-proof, attempt counterexample search to separate *proof-necessity* from *statement-necessity*. Report both rates.
**Also measure (Q13 precursor):** proof-dependence — for theorems with multiple Mathlib proofs, how often does the necessary set differ.
**Cost:** CPU only. **Deliverable:** `results/C1-necessity-base-rates.json`.

### C2. Λ separation (Q1)
**Only if C1 gives a non-empty negative class.**

**Corpus construction, to dodge the 0.67 autoformalization ceiling:** generate NL claims *from* verified Lean statements (informalization), not the reverse. Labels are exact by construction. 200 claims, half with a necessary hypothesis present, half with an unnecessary one.

**Operator:**
```
Λ(h) = E_π [ 1 − agree( f(c), f(π(c ∖ h)) ) ]
```
- `π` = perturbation family: deletion, negation of the hypothesis, quantifier swap, entity substitution. Family sealed in the manifest.
- `f` = entailment judge. **Three independent judges** (MiniCheck + two open-weight models, no shared lineage); majority vote. Never the model that generated the claim (Q6).
- Report per-perturbation-type Λ as well as the aggregate.

**Threshold:** `AUC(Λ, N) ≥ 0.7` at n=200, after controlling for claim length and token overlap.
**Falsifier:** AUC < 0.6 → surface perturbation cannot see necessity. File it and close the instrument line for good — that is four instrument ideas, and the pattern is the finding.

### C3. Non-math transfer (Q7)
**Only if C2 clears.** One corpus, pre-registered before C2 results are seen. Candidate: code review — necessity = "remove this line, does the test still pass." Free labels, buyer exists.
**Threshold:** AUC ≥ 0.65 on the second corpus. Below that, the instrument is math-only and has no buyer.

---

## Deferred — not this cycle

- **Q11** (reuse vs human importance), **Q12** (Λ as leading indicator of reuse), **Q13** (self-reuse rate). All require the reuse metric, which requires a library and a horizon. Nothing here is decision-relevant in 14 days.
- **Q14, Q15** (who to approach, what triggers a citation). Answer after B1 produces numbers. Approaching anyone before that is a pitch without evidence.

---

## Q18 — What if Λ works

Pre-commit now, before the result, so the answer isn't fitted to it.

**If C2 and C3 both clear:** the artifact is the sealed audit run, not the metric. Route: publish B1 + C2 + C3 as one note with all hashes predating results. Approach one benchmark author (TRACE or Terminal Wrench) with the confusion matrices as a contribution, not a pitch. The ask is a citation, not a contract. Sell the audit as eval-data labor to a lab currently paying humans to read trajectories; the comparable is the 731-trajectory manual audit.

**If C2 clears and C3 fails:** math-only instrument, no buyer. Publish as a research note, close the venture line, keep the ledger.

**If C2 fails:** file it. Four instruments, four deaths, one pattern — plausible mechanism, confounded measurement. That pattern, documented with dates and sealed rules, is itself the most citable thing produced this year. Write it up as the negative result and stop building instruments.

---

## Gate summary

```
A1 → 0 of 5 : regulator leg is aspirational; downgrade, do not cite Art. 12 as demand
A2 → <46%   : reformulation is a retreat; say so
A3          : blocks Rev I publication
B1 → FPR>.05: retire the class before any product claim
C1 → <5% neg: STOP Track C
C2 → AUC<.6 : close the instrument line permanently
C3 → AUC<.65: math-only, no buyer
```

**Budget:** under $50 compute. **Calendar:** 14 days. **Standing block remains in force** for Track C until its pre-registration has a published gist revision timestamp.
