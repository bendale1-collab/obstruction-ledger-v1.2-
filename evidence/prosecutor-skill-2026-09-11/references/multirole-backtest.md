# Multi-Role Backtest — Cross-Model Reasoning Trust Detection

**Domain:** Applying the PROSECUTOR adversarial-falsification framework to LLM reasoning conclusions, not to computational chemistry or finance.

**Core claim:** Cross-model DISPERSION (agreement/disagreement among mechanism-decorrelated model families) predicts which reasoning conclusions are FRAGILE (later overturned) better than any single model's self-reported confidence.

If true: multi-role ensembling is a trust-detector for reasoning. If not dead.

## Two mandatory circularity breaks

These were violated in the catalysis project (two GNNs same data, ρ=0.996). The multirole backtest MUST enforce them or be void:

**C1 — Mechanism decorrelation, not surface.** The three roles MUST be three DIFFERENT MODEL FAMILIES (e.g., Claude + DeepSeek + a third via OpenRouter). NOT one model prompted three ways. One model = rank-one = the fake-decorrelation version. Reason: models share training-data blind spots; prompting them differently does not create independent error mechanisms.

**C2 — External labels, not self-labeling.** Each conclusion's outcome (KEPT/CORRECTED/KILLED) comes from an EXTERNAL anchor (a downstream test, real data, the actual later resolution). NEVER from asking a role "was this right?". No self-labeling.

## The point-in-time discipline

Each conclusion was stated at some moment T in the source transcript. Models must judge it using ONLY information available UP TO T — never downstream text that reveals the outcome.

Build each item as:
- `conclusion_text`: the claim as stated at T
- `context_PIT`: the transcript/context ENDING AT T (everything up to and including the conclusion, NOTHING after). Strip all later turns. Verify no outcome leakage.
- `external_outcome`: KEPT / CORRECTED / KILLED — the resolution that happened AFTER T, anchored externally. HELD OUT from models. Used for scoring only.

If you cannot cleanly cut the context at T, EXCLUDE the item. A leaked item silently inflates the result.

## Step 1 — Build the labeled corpus

From the source arc, extract ~20-40 SUBSTANTIVE conclusions (claims that were acted on or drove a decision). For each:
1. Locate T. Cut context_PIT at T. Verify no downstream leakage.
2. Assign external_outcome from the ACTUAL later resolution, anchored to an external test.
3. Record: id, conclusion_text, context_PIT, external_outcome, anchor_note.

Report: n, class balance (KEPT vs CORRECTED+KILLED), # excluded for leakage or missing anchor. If <5 in either class → feasibility probe, underpowered.

**Known corpus (from electrocat project arc, 2026-06-29 session):**
- 22 conclusions, 11 KEPT : 11 fragile (adequate balance)
- All externally anchored to measured values (convergence counts, correlation coefficients, RMSE, AUC+t-stat)
- Files at: `multirole_test/data/pit_conclusions_unscored.csv` in the handoff bundle

## Step 2 — Collect three DIFFERENT models' point-in-time judgements

For EACH conclusion, send EACH of three different-family models ONLY (conclusion_text + context_PIT). Same prompt to all three:

> "Given only the context up to this point, assess whether the following conclusion will hold up. Give: (a) the strongest case it's right, (b) the strongest case it's wrong, (c) a single probability 0.0-1.0 that it HOLDS."

Record all three probabilities into a CSV:
```
conclusion_text, external_outcome, role_steelman, role_counter, role_adjudicator
```

**Hard rule:** Different MODELS, same prompt. Not one model in three rhetorical costumes. The model-family difference is the mechanism-decorrelation source (C1). If only one model is available → DO NOT RUN.

## Step 3 — Run the kill-test

```bash
python multirole_killtest.py --csv data/pit_conclusions.csv
```

### Decorrelation gate (run FIRST — C1)
Compute the error-correlation of the three roles' judgements vs ground truth across the corpus:
- `err = role_judgements - (1 - y)` where y=1 for fragile (CORRECTED/KILLED)
- eff_rank of the 3x3 error-correlation matrix
- Gate: eff_rank ≥ 1.5 AND max pairwise |corr| < ~0.9
- If VOID: roles share error structure. NO CLAIM. Report eff_rank as the finding ("cross-model reasoning not decorrelated enough to ensemble"). Do NOT interpret dispersion AUC.

### Primary test (only if gate passes)
AUC(dispersion → fragile) vs AUC(1 − single_role_conf → fragile):
- dispersion = std of three role probabilities
- incumbent = 1 − adjudicator's hold-probability
- Win bar: mean(AUC_disp − AUC_single) > 0 AND t > 1.0 across folds, not one-fold-driven

## Verdicts

| Gate | Primary test | Verdict |
|------|-------------|---------|
| VOID | — | Models not decorrelated. Cant ensemble correlated estimators. A real finding (the arc's law generalizes to LLM reasoning), not a failed test. |
| PASS | Dispersion beats single-role unc (bar cleared) | Multi-role dispersion is a real reasoning trust-detector. The primitive lives in judging reasoning. |
| PASS | Ties/loses | KILL. One model's own uncertainty is as good. |
| — | Small n / near-bar | INCONCLUSIBLE. Cf. the +0.157 → +0.032 collapse. Power up before believing. |

## Traps

1. **Biggest risk is LOOKAHEAD.** A pretty result on leaked context is worthless. Spot-check items: does context_PIT contain any hint of the outcome?
2. **Different MODELS, same prompt** — not one model in three rhetorical costumes (rank-one trap).
3. **Do NOT let a model label external_outcome.** Labels are external anchors only (C2).
4. **A gorgeous dispersion AUC under a VOID gate means NOTHING.** Gate first, always (smoke-test: hit AUC 0.96 under a failed gate).
5. **Small seed corpus is underpowered.** Report per-fold variance; near-bar = inconclusive.

## Session-specific result (2026-06-29)

**Step 1 corpus built** — 22 conclusions from the electrocat project arc:

| Class | Count |
|-------|-------|
| KEPT | 11 |
| CORRECTED | 5 |
| KILLED | 6 |
| Fragile (CORR+KILLED) | 11 |
| Balance | 11:11 — adequate |
| Excluded (leakage/no-anchor) | 0 |

All externally anchored to specific measured values (convergence counts, correlation coefficients, RMSE, AUC+t-stat). PIT cuts verified clean — no outcome-cueing terms found in context_PIT text.

**Corpus file:** `multirole_test/data/pit_conclusions_unscored.csv` in the handoff bundle (SHA256 verified against MANIFEST.txt).

**Step 2 NOT executed** — only one model family (DeepSeek V4 Flash) available on this agent, which is a rank-one scenario. OpenRouter API IS reachable with the configured provider key and has three different families available (DeepSeek, Anthropic Claude, OpenAI GPT). Step 2 requires sending each of the 22 conclusions to all three models with the same prompt. The OpenRouter key is managed through Hermes auth and cannot be read directly, but `hermes chat -q "prompt" --provider openrouter -m anthropic/claude-sonnet-4.6 --max-turns 1 --safe-mode --cli` works for querying different models. A scoring script (`score_corpus.py`) was prepared but not executed because the session focus shifted to skill maintenance before the multi-model calls were completed.
