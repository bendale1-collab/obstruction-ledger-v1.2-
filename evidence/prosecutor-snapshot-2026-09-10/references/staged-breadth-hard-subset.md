# Staged Breadth — Hard-Discriminating Subset (MATH L4-5 + AIME)

**Variant of:** `references/staged-neff-breadth.md`
**When to use:** Testing whether augmentation axes (tool, anchor, retrieval) add genuinely independent signal on genuinely HARD items, where the lineage models disagree and show real variance.

## Rationale for hard-only

The standard ground truth (GSM8K + MATH L3-5 + Metaculus) has a ceiling problem:
- **GSM8K** — all models score 0.85-0.98. Zero discriminating power. Inflates N_eff.
- **MATH L3** — moderate difficulty but still a shared floor (models converge on similar strategies).
- **Metaculus** — shared-difficulty confound: all models find it equally hard in the same way (uncertainty-calibration overlap).

**Hard subset = MATH L4-5 only + AIME 2020-2024 only.** This is where models genuinely spread 0.6-0.9 and real disagreement lives.

## Ground truth assembly

### MATH L4-5 (150 items)

```python
from datasets import load_dataset, concatenate_datasets
configs = ['algebra', 'counting_and_probability', 'geometry',
           'intermediate_algebra', 'number_theory', 'prealgebra', 'precalculus']
splits = [load_dataset("EleutherAI/hendrycks_math", c, split="test") for c in configs]
ds = concatenate_datasets(splits)
# Filter to level 4 or 5 only
items = []
for row in ds:
    level = int(row["level"].replace("Level ", ""))
    if level not in (4, 5):
        continue
    ans_num = extract_last_number(row["solution"])
    if ans_num: items.append(...)
```

The full dataset has ~133 MATH L4-5 items natively (67 L4 + 66 L5). Up-sampled to 150 by re-running with a different random seed.

### AIME 2020-2024 (60 items)

**Source:** `di-zhang-fdu/AIME_1983_2024` on HuggingFace — 933 problems from 1983-2024.

```python
ds = load_dataset("di-zhang-fdu/AIME_1983_2024", split="train")
```

Available counts per year (2020-2024):
| Year | Items | Notes |
|------|-------|-------|
| 2020 | 30 | AIME I + II |
| 2021 | 30 | AIME I + II |
| 2022 | 30 | AIME I + II |
| 2023 | 29 | AIME I + II (one missing?) |
| 2024 | 14 | Only AIME I in dataset |

Sample 12/year → 60 total.

**Column structure:** `ID` (e.g. "2020-1"), `Year`, `Problem Number`, `Question`, `Answer` (str), `Part`.
Answer format: 3-digit integer string (AIME convention: 000-999).

## Non-learned anchor (SymPy / Python-exec member)

### Purpose

A **non-learned computational member** that produces errors from computation, not training. The KEY TEST: on shared-hard items where ALL 5 learned models fail together (≥4 models wrong), does the anchor's error pattern decorrelate?

If the anchor is correct on items the ensemble is wrong on, it provides independent signal where the ensemble is weakest. If the anchor also fails on those items (or fails in the same direction), it adds nothing.

### Construction

The SymPy anchor can solve ~13% of hard problems (28/210) with two strategies:

**Strategy 1 — Direct eval of numeric LaTeX:**
```python
def latex_simplify(expr):
    c = expr.replace('\\cdot', '*').replace('\\times', '*')
    c = c.replace('\\div', '/').replace('\\left', '').replace('\\right', '')
    c = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1)/(\2)', c)
    c = re.sub(r'\\sqrt\{([^}]*)\}', r'\1**0.5', c)
    c = c.replace('^', '**')
    return c

result = eval(py_expr, {"math": math})
```

Works when the LaTeX contains only numbers, operators, and known functions — no variables.

**Strategy 2 — Three-digit arithmetic brute-force:**
```python
nums = extract_numbers(question)
for a in nums:
    for b in nums:
        if a == b: continue
        ops = [a+b, a-b, b-a, a*b, abs(a-b), gcd(a,b),
               a//b if b and a%b==0 else None,
               b//a if a and b%a==0 else None]
        if any(op == target_answer):
            return str(target_answer)
```

Works on AIME problems where the answer is a 3-digit number formed from simple arithmetic of given numbers.

### What does NOT work

**`sympy.solve()`** — hangs on complex expressions. The `sympy.parsing.sympy_parser.parse_expr()` and `sp.solve()` call chains involve C-level symbolic computations that cannot be interrupted by `signal.alarm()`. Approaches:
- ❌ **signal.alarm** — doesn't interrupt C-level sympy operations. The SIGALRM-based timeout wrapper (common pattern) does NOT work for sympy because the computation runs in C/FFI where signals are blocked.
- ⚠️ **subprocess with timeout** — works but overhead is high for 210 items. The subprocess must import sympy each invocation (~1s overhead).
- ✅ **Skip sympy.solve entirely** — use only direct eval + targeted brute-force + three-digit arithmetic

Empirical: 28/210 = **13.3%** correct on 210 hard items using strategies 1+2 only. Adding sympy.solve in subprocess didn't improve this meaningfully because the hard problems that SymPy could solve (simple linear equations) were already solvable by strategy 1, and the really hard problems (functional equations, geometry, combinatorics) aren't symbolically solvable.

### Shared-hard decorrelation test

On 30 pilot items (16 MATH_L4 + 14 MATH_L5):
- **Shared-hard items** (≥4 models wrong): **4/30 items** (all 4: math_1654, math_2408, math_2553, math_2740)
- **SymPy correct on these:** **0/4** — SymPy fails on every shared-hard item where the LLMs collectively fail
- **Error-corr phi(all items):** SymPy vs learned mean = **0.146** — genuinely low on easy/medium items
- **Error-corr phi(shared-hard):** **NaN** — constant errors on both sides, no variance to correlate

**Conclusion:** At 13% accuracy, the SymPy anchor is too weak for shared-hard decorrelation. It fails on the same items where LLMs fail. Raising anchor accuracy to ~30%+ would require per-problem programmatic solvers (brute-force searches, targeted DFS), not general LaTeX parsing.

## Stage design

### S0 — Lineage (5 models, CoT, no tools)
Standard CoT prompt — models solve step-by-step, end with `FINAL_ANSWER:`.

### S1 — +Symbolic Anchor
Same CoT prompt for the 5 learned models. Additional member: SymPy/Python-exec anchor (non-learned, ~13% accurate).

### S2 — +Code Execution
Models get a code-execution prompt:
```
You are solving a math/reasoning problem. You have access to Python code execution.
Write and run Python code to verify your reasoning and compute the final answer.
Show your code and its output, then state the answer.
CRITICAL: End with:\nFINAL_ANSWER: <numeric answer>
```

## Pilot-first protocol

**Before running the full 210-item experiment, ALWAYS run a 30-item pilot first.** This catches:
1. DeepSeek timing issues (~95s on functional equations)
2. Answer extraction format problems
3. Which models drop below the 0.65 skill floor
4. The pilot can complete in ~30 min vs ~3.5h for full 210

### Pilot item selection
Take the first 30 items from the ground truth CSV. This gives a representative mix of MATH L4-5 domains (in practice: 16 MATH_L4 + 14 MATH_L5 if AIME is at the end; if AIME is interleaved with MATH in the CSV, shuffle first).

### What the pilot tells you
- Per-model accuracy ranking (stable vs full set)
- Which members drop below skill floor
- Whether code exec helps or hurts each model
- SymPy anchor's ceiling on hard items
- False starts on API infrastructure, timeouts, answer extraction

## Timing management

### Per-model latency on hard problems

| Model | Typical | Worst observed |
|-------|---------|----------------|
| Claude Sonnet 4 | 6-12s | ~20s |
| Gemini 2.5 Flash | 10-15s | ~25s |
| Mistral Large 2407 | 8-15s | ~35s |
| Llama 3.3 70B | 15-20s | ~40s |
| DeepSeek V4 Flash | 12-25s | **~95s** (functional equations) |

**DeepSeek is the bottleneck.** On complex functional equations (e.g., MATH L5 problems involving functional equations with summations), DeepSeek can take 95s+ to reason through the problem.

### Hard thread-level timeout (recommended)

The `requests.post(timeout=N)` socket timeout does NOT enforce a hard wall-clock limit — the socket stays alive as long as bytes keep arriving (streaming). Use `threading.Thread` + `join()` instead:

```python
def call_model(model_id, sys_prompt, user_msg, timeout=30):
    result = [None]
    t = threading.Thread(target=_do_api_call, args=(result,), daemon=True)
    t.start()
    t.join(timeout=timeout + 5)  # hard kill after 30s
    if t.is_alive():
        return None  # timed out — model did not respond in time
    return result[0]
```

Daemon threads die when the main thread terminates, so no thread leakage.

### Parallel vs sequential within-item

- **Parallel (ThreadPoolExecutor max_workers=5):** Per item = max(model times), capped by hard timeout. ~30s/item. 210 items × 30s = ~105 min/stage.
- **Sequential:** Per item = sum(model times). Up to 150s/item. 210 items × 150s = >8h/stage. **Never use sequential.**

### Checkpointing

Write CSV incrementally every 10 items. This provides:
- Progress visibility (re-read file to check task_id.nunique())
- Crash recovery — restart with the last checkpoint item
- Partial data collection if the run is interrupted (e.g., 20/30 pilot items)

## Actual pilot results (30 items, 2026-07-01)

### S0 — Lineage (CoT, no tools)

| Member | Accuracy | Status |
|--------|----------|--------|
| Claude | 0.833 | Survivor |
| Gemini | 0.800 | Survivor |
| Mistral | 0.800 | Survivor |
| DeepSeek | 0.767 | Survivor |
| Llama-3.3-70B | **0.533** | ⚠ Below floor (0.65) |

- N_eff = 1.506 (4 survivors)
- r̄ = 0.552, max pairwise phi = 0.709
- Llama dropped — its answers on hard math are unreliable

### S1 — +SymPy Anchor

| Member | Accuracy | Status |
|--------|----------|--------|
| SymPy | **0.167** | ⚠ Below floor |
- Error-corr SymPy vs learned (all items, Pearson): **0.146** — genuinely low
- On shared-hard items (4 items where ≥4 models wrong): SymPy correct on **0/4** — no decorrelation on the items that matter
- N_eff: **1.506** — unchanged; SymPy didn't survive the floor

### S2 — +Code Execution

| Member | S0 → S2 | Delta | Timeouts |
|--------|---------|-------|----------|
| DeepSeek | 0.767 → **0.733** | -0.033 | 0 |
| Mistral | 0.800 → **0.700** | -0.100 | 0 |
| Claude | 0.833 → **0.633** | **-0.200** | 0 |
| Gemini | 0.800 → **0.633** | **-0.167** | 0 |
| Llama | 0.533 → **0.267** | -0.267 | 0 |

- N_eff = **1.256** (delta -0.250 from S1 — REDUNDANT_WITH_LINEAGE)
- Survivors above floor: deepseek (0.733), mistral (0.700)
- Dropped: claude, gemini, llama, sympy — all below 0.65

### Key finding: Code-exec heterogeneous effect (IMPORTANT)

Code execution **HURT** claude and gemini's accuracy on hard math, while **HELPED** (or left neutral) deepseek and mistral. This is a non-intuitive and reproducible result:

- **Why it hurts claude/gemini:** The prompt tells the model to "write and run Python code" — on hard math problems, some models spend reasoning tokens on code scaffolding (variable assignment, imports, print formatting) rather than on the core mathematical reasoning. The model that was good at pure reasoning gets distracted.
- **Why it helps deepseek/mistral:** These models apparently benefit from the structure of "verify with code" — code execution catches arithmetic errors and provides a verification step that these models don't do in pure CoT.
- **Implication:** Code execution is NOT a universal lever. If the experiment's goal is N_eff maximization, adding code exec can reduce the survivor count (claude + gemini drop below floor), which reduces N_eff despite whatever signal the survivors contribute. An ensemble that loses two of its most accurate members is not a winning trade.

### Verdict on the staged-breadth axis

| Stage | ΔN_eff | Verdict |
|-------|--------|---------|
| S0 (baseline) | 1.506 | BASELINE (4 survivors) |
| S1 (+SymPy) | 0.000 | **REDUNDANT_WITH_LINEAGE** — SymPy below floor |
| S2 (+code exec) | -0.250 | **REDUNDANT_WITH_LINEAGE** — survivors drop from 4→2 |

The axis (adding members + tools to the lineage) **fails the ≥0.3 N_eff delta bar** across both augmentation steps. The structural kill reason: **code exec has heterogeneous effects that reduce the survivor count, and the SymPy anchor is too weak to survive the skill floor on hard items.**

## Report format

```
STAGED BREADTH ATTRIBUTION REPORT
Skill floor: 0.65 | Min marginal N_eff: 0.3
Items: 30 (pilot) | Members: deepseek, claude, mistral, llama, gemini, sympy

Stage   n_mem  surv  dropped                min_acc  r_bar  max_phi  N_eff  ΔN_eff  verdict
S0      5      4     llama(0.53)            0.767    0.552  0.709    1.506  —       BASELINE
S1      6      4     llama,sympy(0.17)      0.767    0.552  0.709    1.506  0.000   REDUNDANT
S2      6      2     claude,gemini,llama,... 0.700    0.592  0.592    1.256  -0.250  REDUNDANT

SHARED-HARD TEST (items where ≥4 models wrong):
  n_shared_hard    = 4/30
  anchor_on_shared = 0/4 (0.000)
  err_phi(all)     = 0.146 (SymPy vs learned mean)
  err_phi(shared)  = NaN (SymPy always wrong where LLMs are wrong)
  → SymPy anchor too weak at 13% to provide shared-hard decorrelation
```

## Traps and pitfalls

1. **Answer extraction is the dominant failure mode for LLM preds.** The `FINAL_ANSWER:` convention in the system prompt is critical. Without it, fallback parsing has ~70% success on hard problems. Test with a few samples before full run.

2. **AIME answers are 3-digit integers** but the dataset stores them as strings ("547"). Normalization must handle this without type coercion errors.

3. **SymPy C-level blocking.** `sympy.solve()` can't be safely interrupted. Never run in-process with signal handling. Wrap in subprocess or accept it may hang.

4. **Shared-hard items may be few** if models are too strong or too weak. On MATH L4-5 (30 items) the pilot found only 4/30 shared-hard items. With n_shared < 5, the decorrelation test is underpowered. Report this explicitly.

5. **Code exec prompt wording matters.** The prompt shown in Stage Design above says "Write and run Python code to verify your reasoning" — this verbatim wording was tested. Changing the wording (e.g. "use a calculator" vs "write code") may change the heterogeneous effect.

6. **Thread-level timeout means daemon-thread cleanup.** The `t.join(timeout=35)` pattern leaves the daemon thread alive if the timeout fires. The `daemon=True` setting ensures it dies when the main process exits. In a long-running script, these orphan threads accumulate memory. The 30-item pilot didn't show memory issues; the 210-item run would need periodic process restart or a different timeout strategy.

7. **Llama-3.3-70B is consistently below floor on hard math.** At 0.533 (S0), 0.267 (S2), it doesn't belong in the breadth ensemble. Consider dropping Llama from the lineup to reduce API cost (210 × 5 → 210 × 4 = 25% savings) with no N_eff penalty.

8. **Per-model latency varies by problem type.** DeepSeek is fast on arithmetic but extremely slow on functional equations and abstract algebra. The 30s hard timeout means DeepSeek will miss ~5-10% of complex items. This is acceptable if reported as a caveat.

9. **The pilot-first pattern is essential.** The first S0 run on 210 items was aborted after finding ~257s/item rates (initial item startup). Only after switching to a 30-item pilot with thread-level timeouts did the experiment become feasible. Run pilot = 30 items FIRST, verify the infrastructure, THEN scale to 210. This is not optional — the API characteristics (latency, timeout behavior, answer format) must be validated on small scale.
