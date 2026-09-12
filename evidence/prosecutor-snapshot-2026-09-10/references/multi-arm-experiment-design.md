# Multi-arm experiment design for capability testing

Used when testing whether a model has a specific capability (semantic reasoning, understanding, meaningfulness). Cases: frontier-ranked join selection, LLM-based ranking, model comparison tests.

## Heuristic baseline (mandatory)

Before claiming "the model did X," verify that a simple deterministic rule does not reproduce the result. The heuristic baseline IS the finding when it matches.

- **E1** — unrestricted: among all candidates, pick the one with the most numeric-column features; tiebreak by containment.
- **E2** — containment-restricted: among the top-K by containment, pick the one with the most numeric-column features.

If either matches or beats the model, the claim reduces from "model can reason" to "task structure rewards a trivial heuristic."

## Model-class comparison

A finding from a single model says nothing about the model CLASS (completion vs reasoning, open vs closed, cheap vs expensive). Test at least two models from different classes. If only one is available, state: "TESTED ON ONE MODEL, NOT GENERALIZED."

Reference case: DeepSeek Chat (commodity completion) and DeepSeek V3.2 (current-gen completion) reproduced the same pattern. Kimi K2 (open reasoning) partially reproduced it on 3/3 tables before timeout. The pattern cross-cuts model class and generation.

## Prompt-variant controls

The prompt formulation can encode the heuristic. Always run a second prompt that asks about the RELEVANT dimension (e.g., semantic meaningfulness vs prediction-usefulness). Compare rankings via Spearman correlation.

- **Prediction prompt** ("how useful for predicting...") → picks numeric columns for regression tasks. This is the correct answer to the question asked, not evidence of semantic understanding.
- **Semantic prompt** ("meaningful relationship, same real-world entities...") → picks semantically related tables.

The Spearman between the two prompt variants is the informative quantity. High ρ means the rankings are similar despite different top-1; the bias is only at the extreme head. Low ρ means the prompts measure fundamentally different things.

## Fold variance on every score

Never report a point estimate without its fold-to-fold variance. Report mean, std, and per-fold values for every arm. "Ties within X" is an assertion about noise; measure it.

Reference case: YADL Binary join test — Arm A fold σ ranged from 0.003 (housing_prices) to 0.088 (company_employees). The "ties within 0.02" assumption held on 4/7 tables but failed on high-variance ones.

## Never assert an unmeasured claim

If the analysis suggests "a simple rule would match," the rule must be RUN as an arm — not left as prose. An unmeasured claim in a conclusion is an admission the experiment was incomplete.

Reference case: The first join-test report asserted that a 3-line rule "would replicate the frontier model's performance at zero cost." This was correct when measured (E1 matched or beat B on 5/7 tables), but the original report had no measurement and required a second pass.

## Scope limitation > downloading/rescuing

When a lake, model, or data source is unavailable, record the scope honestly: "RESULT ON X, UNTESTED ON Y." Do not wait for downloads or hunt alternatives. An honest null with limited scope is more useful than a delayed result.

Reference case: Open Data US lake (5,591 tables, the real-world messy lake) was unfetchable. YADL Wordnet (9.8 GB, 30K tables) was 47% downloaded when killed. The verdict was scoped as "NULL ON SYNTHETIC SINGLE-PREDICATE TABLES, UNTESTED ON REAL DATA" — which is correct and does not require more downloading.

## Confidence calibration check

When the model emits a confidence score, check whether it varies across inputs:
- Flat confidence (0.85 on every choice, including failed joins) → uncalibrated. Arm C (hybrid tiebreak) is mechanically inert.
- Varying confidence (0.88-0.95, correlated with data quality) → potentially usable for tiebreak.

## Total experimental procedure

1. Define the candidate pool (deterministic retrieval)
2. Run E1 and E2 heuristic arms (free, no API calls)
3. Run containment baseline (Arm A) + random baseline (Arm D)
4. Run model arm(s) with the PREDICTION prompt
5. Run model arm(s) with the SEMANTIC prompt on the same model
6. Run a second model from a different class if budget allows
7. Report: fold variance (+ mean, std) for every arm; Spearman between prompts; Spearman between models and containment; disagreement analysis (top-1 differences); total model calls and cost; typed verdict line with scope limitation
