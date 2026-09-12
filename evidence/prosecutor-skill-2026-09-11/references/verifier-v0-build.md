# Verifier V0 Build Pattern

## When to use

Building a **non-neural verifier pipeline** that catches extraction-disagreement and referent-mismatch errors before a spec freeze. First phase of the three-stage verifier (V0 arbiter → V1 extractors → V2 adversary). No model calls, no network, no GPU. sympy + numpy only.

## Registry Schema (per spec §0)

Every named object in a bundle gets a YAML record under `registry/<id>.yaml`:

```yaml
id: OL-EQ-001        # <bundle>-<kind>-<NNN>
name: CLM equation
kind: equation        # equation | mode | theorem | value | test
source:
  authors: [Author1, Author2]
  year: 2025
  venue: "Journal Name Vol, Page"
  locator: "Eq 2.1"
  artifact: sources/paper.pdf
  artifact_sha256: null
executable: null      # write-once by arbiter, never by hand
status: UNRESOLVED    # UNRESOLVED | RESOLVED | HALT-REFERENT | HALT-SOURCE
extractions: []       # populated by blind extractors in V1
```

**Rule:** `executable` is write-once by the arbiter. A human or agent writing it directly is a ledger violation.

## Arbiter Implementation (spec §2)

**Non-negotiable:** assert no LLM/network imports at import time. Pattern:

```python
import sys
_bad = ['requests', 'openai', 'anthropic', 'transformers', 'torch', 'tensorflow', 'httpx']
for m in _bad:
    if m in sys.modules or any(k.startswith(m) for k in sys.modules):
        raise ImportError(f"forbidden import: {m}")
```

### Per-kind checks

| kind | Check method | Outcome |
|------|-------------|---------|
| `equation` | Pairwise symbolic simplify(A-B)==0 + 20-point numeric check to 1e-12 | RESOLVED if both agree; HALT-REFERENT if any disagreement |
| `mode` | Compute parity from expression via f(-x) vs f(x): even (difference zero), odd (sum zero), neither | Returns parity dict with 'parity', 'reasoning', 'expr', 'var' |
| `value` | Exact string match at source-stated precision. Extra digits → UNSOURCED-PRECISION note | RESOLVED on exact match; HALT-REFERENT on mismatch |
| `theorem` | Parse assertion as sympy Rel. If checkable symbolically → RESOLVED; else deferred to engine smoke run | RESOLVED / HALT-REFERENT / HALT-SOURCE (requires engine smoke) |
| `test` | Deferred to stage 3 adversary — arbiter has no test-semantic validation in V0 | Always passes V0 (RESOLVED) |

### Engine smoke run (`smoke_engine`)

Import `engine/f1.py`'s `main()` via `sys.path.insert`, capture stdout with `io.StringIO`+`redirect_stdout`. Check return code (0=pass). This tests that the sealed engine is runnable and produces the expected output structure.

## Retrodiction Corpus (spec §4)

`known-bad-specs/RB-<NN>.yaml` — planted-defect bundles. Each is a YAML file with:

```yaml
name: "Human-readable defect name"
defect: "What's wrong"
spec_fragment:
  registry:
    - id: OL-XX-NNN
      kind: equation|mode|etc
      executable: null
      status: UNRESOLVED
      extractions: [...]  # hand-filled "blind extractor output"
pre_registered: "Expected outcome text"
```

### Standard corpus (RB-01 to RB-05)

| Case | Planted defect | Must return |
|------|----------------|-------------|
| RB-01 | Equation named, no body, no extractions | UNRESOLVED |
| RB-02 | Mixed extraction bodies (e.g. 1 CCF + 2 CLM on same record) | HALT-REFERENT — pairwise disagreement |
| RB-03 | Test criterion weaker than theorem | NOT CAUGHT (resolves in V0; needs stage 3) |
| RB-04 | Strip zone bounded on Re only | NOT CAUGHT (resolves in V0; needs stage 3) |
| RB-05 | Mode extraction parity mismatch (2 even + 1 odd) | HALT-REFERENT — parity disagreement |

Gate: corpus runs before every real freeze. Score < N/N catchable → PIPELINE-RED.

## Kill Test Structure

Framework `kill_test.py`:
- Each RB case has a runner function returning `(actual_outcome, detail_string)`
- Expected outcomes stored per case (those pre-registered as catchable vs not)
- Score = `catchable_passed / catchable_total`
- 3/3 on RB-01/02/05 = V0-GREEN
- <3/3 = V0-RED

**Important:** The framework distinguishes `NOT CAUGHT` (correct miss, cases RB-03/RB-04) from fails. Never score a correct miss against the pass rate.

## Identified Arbiter Gaps (V0 limitations, in-scope per spec §1)

1. **Monoculture risk:** Three agreeing-but-wrong extractions pass V0 arbiter (extraction agreement ≠ correctness). Requires stage 3 adversary.
2. **Test-theorem mismatch** (RB-03/04): Arbiter cannot evaluate test strength vs theorem — deferred to adversary.
3. **Semantic mode-space check:** Arbiter computes expression parity but doesn't verify the mode belongs in the correct function space (e.g., odd-basis vs full-domain). A perfectly agreeing set that all return the wrong mode would pass.
4. **Import guard nuance:** Python stdlib modules (`urllib`, `http`, `socket`) are pre-loaded by the runtime and will always appear in sys.modules. The arbiter's forbidden-import check should only test LLM/frontier-API modules (`openai`, `anthropic`, `transformers`, `torch`, `tensorflow`, `requests`, `httpx`), not stdlib. Otherwise the arbiter fails on import.

These are NOT V0 defects — they are scoped out deliberately.

## F-5 Resolvent-Norm Diagnostic (cross-operator pattern)

A reusable technique for distinguishing pseudospectral artifacts from genuine eigenvalues:

1. Compute eigenvalues of two realizations (naive L² and origin-H²)
2. Filter by |eig| < 10 (remove discretization artifacts at high wavenumbers)
3. Partition into populations:
   - Residual + eliminated strip modes
4. For each eigenvalue, compute ε·||(z−ε−L)⁻¹|| via smallest singular value of (z−ε)I − L
5. Evaluate on BOTH operators (cross-operator check amplifies asymmetry)
6. Trusted ≤ 10² / Untrusted > 10² (per pre-registration F-5 threshold)

Key finding from CLM P1: the 20 residual origin-H² modes had resolvent norm 2–5 (genuine essential-spectrum discretization), while 8/22 eliminated positive-Re modes had norm > 10² (pseudospectral strip). On the origin-H² operator the eliminated modes nearly vanish (norm < 0.02).

## Ledger Entry Types (spec §7)

Under `ledger/verifier/`:
- `v0-corpus-commit.yaml` — corpus hash before run
- `v0-kill-test-result.md` — full kill test table with mechanisms
- `v0-arbiter-design-finding.yaml` — MONOCULTURE-MISS or other design findings

## Lambda=1 Closed Form (Xu 2607.19762) — CRITICAL CORRECTION

Source: Xu (2026), arXiv 2607.19762, Section 3.2, Equation 3.7.

**FULL-DOMAIN translation mode (Eq 3.7, EVEN):**
- φ = dΩ/dξ = (−2 + 2ξ²)/(1+ξ²)², parity=EVEN (arbiter-verified via sympy)
- L₀φ = φ at eigenvalue λ = c̃ = (c_l + a)/(1−a) = 1 at a=0
- This mode is EVEN — cannot appear in the odd-basis origin-H² space

**ODD-BASIS time-shift mode (Theorem 2, ODD):**
- Xu Theorem 2: the full point spectrum on the **odd realization** is EXACTLY {0,1}
- Therefore λ=1 **DOES exist** in the odd basis (a separate ODD eigenfunction, not φ=dΩ/dξ)
- The even translation mode (Eq 3.7) and the odd time-shift mode (Theorem 2) are **distinct eigenfunctions** at the same eigenvalue

**Consequence:** Do NOT claim "λ=1 is structurally absent from the odd basis." This was the RED-CLOSE error. The engine's failure to produce λ=1 is an **engineering construction problem**, not a structural limitation. An engine that correctly realizes the odd-basis operator will have λ=1.

**Same-defect hypothesis (tested and rejected via F-5 diagnostic):**
The missing λ=1 and residual essential-spectrum discretization modes are DIFFERENT defects:
- Missing λ=1: odd-basis operator construction error (center-point constraint too restrictive)
- 20 residual strip modes: correct essential-spectrum discretization on finite domain; F-4 zone criterion design error (zone includes essential line, should exclude it)