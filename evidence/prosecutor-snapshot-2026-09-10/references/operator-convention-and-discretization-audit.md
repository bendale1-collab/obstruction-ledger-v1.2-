# Operator Convention & Discretization Audit

**Domain:** Spectral operator discretization — verifying a numerical engine against
a source-paper operator, distinguishing sign convention from construction bug from
truncation effect.

**When to use:** After a new engine discretization is built or an existing one is
challenged. Before any fork decision (keep Fourier vs switch to Mellin). Whenever
the engine's eigenvalues differ from expected values by O(1).

---

## 1. Operator convention audit (root out sign/convention mismatches)

Before comparing engine eigenvalues to source paper values, verify the sign
convention at the algebraic level.

### Protocol

1. **Extract the operator definition verbatim from the source paper.** Include
   the equation number. Example: "Xu Eq 3.1: L_a φ = −φ − (c_l y + aU)φ' − aV(φ)Ω' + φHΩ + ΩHφ"
   Note: is the eigenvalue problem L φ = λ φ or a time-evolution equation ∂_τ φ = L φ?

2. **Write the operator as coded in the engine.** Extract from the actual code,
   term by term. Example: "engine apply_L: v + x·v' + a(U·v' + Uv·Ω') − HO·v − Hv·Ω"

3. **Build a SymPy expression for each.** Use exact rational closed forms for
   Hilbert transforms of rational functions (see §5 below).

4. **Compute the difference.** If L_engine = −L_source (every term sign-flipped),
   all eigenvalues are negated. This is a conventional choice, not a bug. Document
   it and rename: "λ_eng = −λ_Xu" or similar.

5. **Apply to a known eigenfunction.** If the source paper gives an explicit
   eigenfunction φ₀, test both operators: L_eng(φ₀) and L_source(φ₀). The ratio
   L(φ₀)/φ₀ should be constant across y (not y-dependent). If y-dependent, check
   for a formula error in the Hilbert transforms.

### Pitfall: verifying the quote

**NEVER assume a quoted sentence from a previous session or report is accurate
without re-verifying against the primary source.** Search the actual paper text
(arXiv HTML or PDF) for the exact sentence. The searches to run:

- Miraculous-sounding attribution ("by direct substitution", "one checks",
  "it can be shown")
- The exact function name and eigenvalue ("φ₀ = Ω + ξ·Ω' at λ=0")
- Any claim that a function is "the" mode without an equation number

**If the sentence doesn't exist in the paper, file FABRICATED-QUOTE immediately.**
Do not use the quote in any further reasoning. The eigenfunction-enumeration
problem reverts to what the paper actually proves (often a spectral existence
theorem with no closed form).

---

## 2. Half-domain test: construction bug vs truncation effect

When an operator is built on a restricted domain (odd basis, right half-line,
origin-H² projection), the eigenvalue shift from the ℝ reference value could be
either a construction bug or a truncation effect. Use this two-way comparison:

### Two methods

| Method (i) | Method (ii) |
|------------|-------------|
| Full-grid FFT (2049 pts) → apply operator → restrict to subspace | Build the restricted matrix directly (e.g., P·H_full·P restricted to right_ix) |
| Uses the full FFT Hilbert/derivative, then restricts | Uses the matrix that the engine actually uses |

### Criterion

| Outcome | Diagnosis | Action |
|---------|-----------|--------|
| (i) ≈ 1e-4, (ii) ≈ 0.7 | **Half-domain construction bug** | The full-grid FFT works correctly; the restricted matrix introduces error. Fix the restricted construction. **Fourier stays.** |
| Both ≈ 0.7 | **Genuine truncation effect** | The periodic [−L, L] operator cannot represent the ℝ Hilbert for non-periodic functions. Both methods fail. **Consider Mellin/ℝ discretization.** |
| (i) ≈ 0.7, (ii) ≈ 1.0 | Truncation amplified by construction | The half-domain adds error on top of truncation. Fix the construction first, then re-evaluate. |

### Application to H(φ₀) and T2 = x·φ₀'

Run the same comparison for:
- H(φ₀): full-grid FFT Hilbert vs odd-basis H matrix
- x·φ₀': full-grid FFT derivative vs odd-basis D matrix

---

## 3. Term-by-term decomposition for defect localization

Decompose L = Σ T_i and compare each term's engine value against its exact ℝ value.

### Protocol

1. **Identify the terms.** For the CLM operator at a=0:
   - T1 = c_l·φ (identity term)
   - T2 = α·x·φ' (advection/derivative term)
   - T3 = −(HΩ)·φ (profile-Hilbert term)
   - T4 = −(Hφ)·Ω (response-Hilbert term)
   - T5 = constraint/projection artifact (difference between L_matrix @ φ and Σ T_i)

2. **Compute vector norms, not pointwise ratios.** Use:
   ```
   RMS rel error = ‖engine_term − exact_term‖ / ‖exact_term‖
   ```
   This is the correct measure. Pointwise ratios (`(engine−exact)/exact`) are
   misleading near zero-crossings and at boundaries.

3. **Report restricted-domain norms too.** The key mass region (|x| < L/4) may
   have different error characteristics than the full domain.

4. **Resolve pointwise-vs-weighted-average contradictions.** When individual
   term errors are large (e.g., H(φ₀) RMS rel = 0.57) but the eigenvalue
   estimate is close to target (e.g., λ = 0.94 vs 1.0), there is no contradiction:
   - The eigenvalue is a WEIGHTED AVERAGE of L(φ)/φ over the domain
   - Large H errors at the boundary are suppressed by Ω(x) → 0 there
   - Different quantities measure different things

---

## 4. Truncation convergence protocol

Sweep L at fixed dx to verify the error scaling before attributing O(1) shifts
to construction defects.

### Protocol

| Step | Action |
|------|--------|
| 1 | Fix dx (e.g., dx ≈ 40/2049 ≈ 0.0195) |
| 2 | Run L = 20, 40, 80 (same dx) |
| 3 | Compute λ(L) for each test eigenfunction |
| 4 | Check error = |λ(L) − λ_ℝ| ∝ 1/L |

### Expected behavior

| Error scaling | Diagnosis |
|--------------|-----------|
| 1/L | Truncation — bounded, controlled, not structural |
| Constant | Construction bug — does not improve with larger domain |
| Other | Check for aliasing or boundary-condition mismatch |

### Action

- If error ∝ 1/L: **Fourier stays.** Accept the truncation floor as an
  expected-accuracy prior in P1 pre-registration.
- If error constant: **Mellin/ℝ discretization** — the periodic operator
  fundamentally cannot represent the ℝ Hilbert for non-periodic functions.
- At L=20: λ_Xu(φ₀) ≈ 0.94 (6% error from 1.0)
- At L=40: λ_Xu(φ₀) ≈ 0.97 (3% error)
- At L=80: λ_Xu(φ₀) ≈ 0.985 (1.5% error)

---

## 5. Acceptance tolerance must be narrower than spectral gap

**Rule:** A pre-registered acceptance tolerance must be narrower than the
smallest spectral gap being tested.

If the spectrum's entire content is {0, 1} with nothing between, a tolerance
of ±0.5 cannot distinguish 0 from 1. This is not a pre-registration; it is
surrender.

**Proper approach:** Derive the tolerance from the truncation convergence
study (e.g., 6% at L=20, 3% at L=40). The expected-accuracy floor is the
tolerance — not borrowed from a different quantity, not chosen to make the
test pass.

---

## 6. F-4 strip count: half-domain artifact warning

The naive-vs-odd strip count reduction is a standard diagnostic. But it is
only valid on the CORRECT full-grid operator. Running it on a half-domain
(right_ix restricted) or center-point-constrained operator produces
artifacts:

| Construction | F-4 strip count | Diagnosis |
|-------------|----------------|-----------|
| Full-grid odd-projected (P = (I−R)/2) | Naive ≈ odd | The strip reduction is an artifact of the half-domain restriction, not the odd projection. The correct full-grid operator preserves the strip. |
| Half-domain (right_ix only) | odd < naive | An artifact of the restriction, not the projection. The half-domain breaks the Hilbert transform's anti-symmetry, producing spurious reduction. |

**Always re-run the diagnostic on the full-grid operator before drawing
conclusions about strip reduction.**

---

## 7. Hilbert transforms of rational functions (CLM family)

Closed forms for the CLM a=0 profile Ω(y) = −y/(y² + ¼):

| Function | H[f] | Notes |
|----------|------|-------|
| 1/(y² + a²) | y/(a·(y² + a²)) | Standard pair |
| y/(y² + a²) | −a/(y² + a²) | Standard pair |
| y/(y² + a²)² | (y² − a²)/(2a·(y² + a²)²) | Derivative of above |
| Ω(y) = −y/(y² + ¼) | ½/(y² + ¼) | For a=½ |
| φ₀(y) = −y/(2(y² + ¼)²) | (¼ − y²)/(2(y² + ¼)²) | H[φ₀] = −(y²−¼)/(2(y²+¼)²) |
| y·Ω'(y) = φ₀ − Ω | −y²/(y² + ¼)² | H[y·Ω'] = H[φ₀] − H[Ω] |

**Common mistake:** Forgetting the factor of 2 in H[φ₀]. The correct formula
has denominator 2·(y²+¼)², not (y²+¼)². A missing factor of 2 changes the
eigenvalue from a constant (λ = −1) to a y-dependent ratio (λ = −2/(4y²+1)),
which is a pure algebra error.

---

## 7. SymPy parity check (arbiter)

The arbiter's `check_mode` function computes parity from the expression
symbolically: f(−x) − f(x) = 0 → EVEN; f(−x) + f(x) = 0 → ODD.

Always verify parity independently of any claimed parity in the source. The
arbiter's parity check is the ground truth — a claimed parity that disagrees
with the arbiter is a defect in the corpus extraction, not in the arbiter.

---

## 8. Spurious null vector — constraint artifact detection

**When eigenvalue λ=0 appears but is not the physical scaling mode.**

The odd-basis projection combined with a center-point constraint row can produce
a trivially null eigenvector: nonzero only at x=0, zero everywhere else, with
eigenvalue exactly 0. This is NOT the physical scaling mode — it is a constraint
artifact.

### Detection protocol

1. **Compute the λ=0 eigenvector** from the odd-projected operator.
2. **Measure mass at index 0 (x=0):**
   ```
   m₀ = |v₀(idx₀)|² / ‖v‖²  (where idx₀ = center of grid)
   ```
3. **Diagnose:**
   - m₀ ≥ 0.999 → **SPURIOUS-MODE-FROM-CONSTRAINT** — the λ=0 eigenvalue is
     carried by the constraint row's null space, not by a physical scaling mode.
     The operator at x=0 has a trivially null direction.
   - m₀ ≤ 0.5 → The λ=0 mode has spatial structure and is likely the physical
     scaling mode.

### When this happens

- The operator used a **center-point row** (enforcing φ(0) = 0 as an explicit
  constraint) combined with **half-domain restriction** (right_ix only).
- The full-grid odd-projected operator (P = (I−R)/2, no center row) does NOT
  produce this artifact — the λ=0 mode is correctly the physical scaling mode.

### Version history

- 2026-09-08: First detection during Control Repair v2. The engine's "λ=0 mode"
  was confirmed as a constraint artifact (mass at x=0 = 1.000). Led to
  fork-adjudication: Fourier stays, but the full-grid odd-projected construction
  replaces the half-domain + center-row construction.

---

## 9. Zero-crossing artifact in relative error computation

**When computing `(engine − exact) / exact` at x where exact ≈ 0, the ratio
diverges.** This is not a real error — it is a zero-crossing artifact.

### Rule

- For pointwise relative error computations, mask points where |exact| < 1e-15
- For vector-norm relative error, use ‖engine − exact‖ / ‖exact‖ (the vector
  norm naturally weights toward larger values and avoids the division-by-zero
  issue at zero-crossings).
- Report both full-domain and restricted-domain (|x| < L/4) vector norms when
  assessing which terms drive the O(1) spectral shift. The restricted domain
  focuses on the physically relevant mass region while excluding boundary
  truncation artifacts.

---

## 10. RB-05 / Corpus fabrication handling

**When a corpus extraction contains an expression with no source in the cited
paper, it must be flagged and replaced.**

### Protocol

1. **Verify the source paper.** Search the actual paper (arXiv HTML or PDF)
   for the claimed formula. Search for:
   - The exact expression
   - A nearby equation number
   - The section name where it supposedly appears

2. **If not found:**
   - **Flag as CORPUS-FABRICATED** in a ledger entry
   - Replace the fabricated extraction with a DERIVED expression (computed
     from known identities, not quoted from the paper)
   - Document the derivation source (e.g., "derived: φ₀ = Ω + y·Ω' from
     the scaling ansatz, verified SymPy L_Xu(φ₀) = φ₀")
   - Re-run the arbiter kill test — the parity/comparison outcome should
     now be different

3. **RB-05 specific case (2026-09-08 corpus fix):**
   - Three extractions originally: A = dΩ/dξ (EVEN, Xu Eq 3.7 ✓),
     B = dΩ/dξ (EVEN ✓), C = fabricated odd λ=1 expression (no source ✗)
   - After correction: A = dΩ/dξ (EVEN, λ=1 translation), B = φ₀ (ODD,
     λ=+1 under L_Xu, derived scaling mode), C = y·Ω' (ODD, λ=0 under L_Xu,
     derived time-shift mode)
   - The parity disagreement (1 EVEN + 2 ODD) persists after correction,
     which is CORRECT — they are three distinct eigenmodes, not the same object

---

## 11. H²-realization test: generalized eigenproblem candidate 5

**When:** Candidate 5 (generalized eigenproblem Lv = λ Mv with M = I + (D²)ᵀD²)
is proposed as a method to enforce the origin-H² condition (Xu Eq 3.2).

### Mechanism

M = I + (D²)ᵀ · D² ≈ I + D⁴ (biharmonic). On the Fourier grid, eigenvalues of M
scale as ∼ 1 + k⁴. The generalized eigenproblem M⁻¹L has effective operator
L / (1 + k⁴). High-wavenumber components are strongly suppressed.

### Result (2026-09-08, CLM a=0, L=20, N=1024)

| Criterion | Threshold | Result | Verdict |
|-----------|-----------|--------|---------|
| A1: {0,1} above floor, 6% tolerance | near0<0.06, near1<0.06 | near0=0.000, near1=0.9997 | ❌ FAIL |
| A2: F-4 strip (H2), |Im|<10 | 0 | **1** (reduced from 18, not eliminated) | ❌ FAIL |
| A3: naive strip (control) | >0 | **18** | ✅ PASS |
| A4: y·Ω' eigenvalue → 0 | <0.06 | **0.015** | ✅ PASS |
| A5: φ₀ eigenvalue → 1 | <0.06 | **1.047** | ❌ FAIL |

### Diagnosis: smoothness-weighting ≠ domain restriction

The H² weight CRUSHES the spectrum toward 0 rather than restricting the
operator domain. The k⁴ denominator suppresses all structure at high
wavenumbers — including the λ=1 mode. The eigenfunctions delocalize
(φ₀ overlap drops from 1.0 to 0.50). This is NOT equivalent to the
origin-H² domain restriction.

### Template applicability

This approach works when the target function and target eigenvalue are
both low-wavenumber (smooth, large-scale). It FAILS when:
- The eigenvalue of interest has structure at moderate wavenumbers
- The spectrum contains multiple eigenvalues that must be distinguished
- A smoothness penalty averages out the distinction between modes

**Candidate 5: TRIED-FAILED.** Do not re-propose unless the failure
mechanism (smoothness-weighting vs domain restriction) is addressed.

---

## 12. Origin-condition candidate enumeration (Class C scoping)

Before implementing any origin condition, enumerate all possible approaches
against the condition's elements.

### Template

Condition definition (from source, verbatim):
> X = { φ : φ odd, φ, φ'' ∈ L²(0,∞), φ(y) = a₁y + o(y) as y → 0 }

Elements:
| Element | What it requires |
|---------|-----------------|
| (a) ODD | φ(−y) = −φ(y) |
| (b) φ ∈ L² | Square-integrable (usually automatic on a bounded domain) |
| (c) φ'' ∈ L² | Second derivative integrable — the strong origin regularity |
| (d) φ(y) = a₁y + o(y) | φ(0)=0, φ'(0)=a₁ finite (follows from (a)+(c) by Sobolev embedding) |

### Candidate table

| # | Method | (a) | (c) | (d) | Tried? | Outcome |
|---|--------|:---:|:---:|:---:|:------:|---------|
| 1 | Parity projection P=(I−R)/2 | ✅ | ❌ | ❌ | ✅ | Partial (strip persists) |
| 2 | Half-domain restriction | ✅ | ❌ | ❌ | ✅ | Buggy (center artifacts) |
| 3 | Center-point row φ(0)=0 | ✅ | ❌ | ❌ | ✅ | Spurious null vector |
| 4 | Full-grid odd-projection | ✅ | ❌ | ❌ | ✅ | Fork winner (truncation OK) |
| 5 | H²-weighted generalized EVP | ✅ | ✅ | ✅ | ✅ | TRIED-FAILED (smoothness ≠ restriction) |
| 6 | H² constraint rows at origin | ✅ | ✅ | ✅ | ❌ | Untried |
| 7 | Exterior mesh (tanh clustering) | ✅ | ≈ | ≈ | ❌ | Untried |
| 8 | Mellin/log-radial mapping | ✅ | ✅ | ✅ | ❌ | Deferred |

### Rule

All TRIED candidates that only enforced (a) failed to eliminate the strip.
Candidate 5 enforced ALL elements but changed the spectral problem
(smoothness-weighting ≠ domain restriction). The remaining untried
candidates (6–8) represent fundamentally different approaches: algebraic
constraints, coordinate clustering, and domain transformation.

**When scoping:** Create this table before proposing any new construction.
It prevents re-proposing candidates that have already failed for known reasons.

---

## 13. Eigenvector indexing pitfall (filtered eig vs unfiltered vecs)

**When `scipy.linalg.eig()` returns `eig, vecs`, and you later filter `eig`
with a mask, the column indices in `vecs` do NOT correspond to the filtered
`eig` array if you kept only a subset.**

### Wrong pattern
```python
eig, vecs = linalg.eig(L)
# Filter eig
eig = eig[np.abs(eig) < 10.0]
# WRONG: vecs[:, i] no longer corresponds to eig[i]
strip_idx = np.where((eig.real > -0.5) & (eig.real < 0.0))
for i in strip_idx[0]:
    v = vecs[:, i]  # WRONG index!
```

### Correct pattern
```python
eig, vecs = linalg.eig(L)
# Keep original indices
keep = (np.abs(eig) < 10.0) & np.isfinite(eig)
eig_filtered = eig[keep]
vecs_filtered = vecs[:, keep]
# Now work with the filtered arrays — indexes match
strip_mask = (eig_filtered.real > -0.5) & (eig_filtered.real < 0.0)
for i in np.where(strip_mask)[0]:
    v = vecs_filtered[:, i]  # CORRECT — same index
```

### What went wrong (2026-09-08)

The strip-characterization.py first pass reported m_out=1.0 (100% boundary)
for strip modes because the post-filtered `eig` array was used to select
columns from the unfiltered `vecs_full[:, idx]` where `idx` was an index
into the filtered array, not the original. The corrected run showed the
strip modes were actually origin-localized (m_in=0.61–0.79, m_out=0.002–0.013).

---

## References

- `pre-registration-battery-design.md` — tolerance derivation, ambiguous-middle
  disposition, cap derivation
- `l-sweep-essential-spectrum-diagnostic.md` — related L-sweep methodology
- `verifier-disagreement-measurement.md` — verifier discrepancy protocol
- `k0-checker-validation.md` — injection-based report validation
- Xu 2607.19762, Eq 3.1 (operator definition), Eq 3.2 (origin-H² space), Eq 3.7 (Ω' translation mode)
- CCF: Cordoba-Cordoba-Fontelos (2005), Ann. Math. 162 — NOT CLM