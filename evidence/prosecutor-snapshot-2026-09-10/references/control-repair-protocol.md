# Control-Repair Protocol

## When to use

Testing whether a continuous closed-form eigenfunction (derived analytically or from a theorem) is an approximate eigenvector of a **periodic discrete Fourier operator** on a truncated domain `[-L, L]`.

## Core insight

**The continuous ℝ operator and the periodic Fourier discretization on `[-L, L]` have different eigenfunctions and eigenvalues.** This is NOT a harness bug — it is a property of the periodic Hilbert transform (kernel `cot(π(x−y)/2L)` vs `1/(x−y)`) and the finite domain truncation.

Before reporting "the discrete operator does/doesn't have eigenvalue X, verifying/falsifying the theorem," you must establish the **coordinate map** and **index space** between the continuous and discrete formulations.

## Protocol — five steps, in order

### Step 0: Source the closed form

From the paper/theorem, identify:
- The exact eigenfunction expression (if given — many theorems prove existence without providing one)
- The eigenvalue it corresponds to
- The function space it lives in (odd vs full, H² origin vs L²)

**If no closed form exists for the desired eigenvalue** (e.g., Xu 2607.19762 Theorem 2 proves λ=1 exists in the odd basis but gives no explicit eigenfunction — Eq 3.7 is the EVEN translation mode, NOT the odd time-shift mode), say so plainly. Do not substitute a different function and test it.

### Step 1: Coordinate map — state explicitly

Analytic expressions in papers use their own coordinate conventions. The engine uses different ones. Map before sampling.

Example from CLM P1:
```
Engine profile:       Ω(x) = -x/(x²+¼)           (ANCHORS form)
Paper profile:        Ω(ξ) = -2ξ/(1+ξ²)          (Xu notation)
Coordinate map:       ξ = 2x
φ₀_paper(ξ) = -4ξ/(1+ξ²)²  →  φ₀_engine(x) = -x/(2(x²+¼)²)
```

Print the mapping explicitly in the report before any measurement.

### Step 2: Index space — state BOTH explicitly

Every discrete vector lives in a specific index set. An overlap of exactly 0.0000 between two odd localized functions is a BUG until shown otherwise — always check index spaces first.

```
FULL grid:       x on [-L, L], M = 2N+1 points
RIGHT half:      x[right_ix], n_sub = M−center, INCLUDES x=0 at index 0
Engine eigenvec: lives on RIGHT half (length n_sub)
Sampled φ₀:     sampled on FULL grid, RESTRICTED to right_ix (length n_sub)
```

All inner products, overlaps, and residuals MUST use the SAME index set. Report the mapping explicitly before reporting any figure.

### Step 3: Control — engine's OWN eigenvector first

Before testing the closed-form against the discrete operator, find the engine's **own eigenvector** at the closest eigenvalue to the target λ. Report:

```
Engine λ=0 eigenvector (n_sub = 1025):
  λ = 0.000000000000  (exact)
  ||L u₀ − λ u₀||/||u₀|| = 0.00e+00  ✅  (< 1e-14)
```

If this residual is not machine-zero, the operator construction has a bug unrelated to the continuous/discrete gap. Fix that first.

### Step 4: Overlap + projection + residual

For the sampled closed form on the same index set:

1. **Overlap**: `<u_engine, φ_sampled>` / (||u_engine||·||φ_sampled||)
   - ≈ 1.0 → same mode, at correct eigenvalue
   - ≈ 0.0 → different mode (maybe at a shifted eigenvalue — check step 4b)
   - 0 < x < 1 → partial projection

2. **Projection onto eigenspace**: Compute `|⟨φ, v_j⟩|` for every eigenvector v_j. Find the best-fit eigenvalue:
   ```
   φ₀ best-fit λ on L_cur = -0.470182+0.000000j
   Overlap with best eigenvector = 1.000000  (φ₀ IS the -0.47 mode)
   Overlap with engine λ=0 eigenvector = 0.000000  (different mode)
   ```

3. **Residual at best-fit λ**: `||L φ − λ φ|| / ||φ||`
   - < 1e-6 → approximate eigenvector
   - O(1) → not an eigenvector at all

4. **Spatial distribution of residual**: where does the error live?
   ```
   Error at origin (|x|<1):    0.0465
   Error at boundary (|x|>L/2): 0.6501
   ```
   - Large at **boundary** → domain truncation problem (Mellin would fix)
   - Large at **origin** → constraint/construction problem (engine fix)
   - Evenly spread → genuine non-eigenvector

### Step 5: Report the three numbers

```
▸ λ=0 engine eigenvector:  0.000000000000  (residual: 0.00e+00)
▸ λ=1 nearest (odd basis): 0.000000+0.000000j  (|λ-1| = 1.00e+00)
▸ φ₀ overlap (corrected index space): 0.000000
```

Do NOT report λ=1 numbers until λ=0 control passes (< 1e-6).

## Common failure modes

| Mode | Symptom | Likely cause |
|------|---------|-------------|
| Missed coordinate map | φ₀ tested on wrong grid, overlap ≈ 0 everywhere | Forgot ξ=2x transformation |
| Wrong index set | Overlap ≈ 0.000 between two odd functions | Eigenvector on right half, sampled on full grid |
| No engine control | λ=0 residual O(1) used as baseline | Need to verify engine construction first |
| Post-hoc Eigenvalue shift | φ₀ is an eigenvector at λ≠0 on the discrete operator | Periodic H shifts eigenvalues — report as property, not bug |
| Closed form substitution | Tested dΩ/dξ as "λ=1 odd mode" when paper only proves existence, no explicit form | Theorem 2 proves λ=1 exists but gives no formula — don't fabricate one |

## The fork question

If the discrete operator lacks a predicted eigenvalue (e.g., λ=1 in the odd basis):

| Finding | Implication | Fork option |
|---------|-------------|-------------|
| Error at boundary ≥ 60% | Domain truncation — periodic H vs continuous H | Move to Mellin/log-radial |
| Error at origin ≥ 60% | Constraint bug — origin condition not correctly imposed | Fix engine construction on Fourier |
| Both errors small, eigenvalue absent | Discretization choice — continuous and periodic operators have different spectra | Accept limitation and revise pre-registration criteria |

## Key references from CLM P1

- Xu 2607.19762, Theorem 2: λ=1 exists in the odd basis (proved, no explicit formula given)
- Xu 2607.19762, Eq 3.7: EVEN translation mode φ=dΩ/dξ (not the odd-basis λ=1 mode)
- RED-CLOSE correction (v0-red-close-correction.md): the λ=1 structural-absence claim was withdrawn; it IS an engineering problem, not a structural limitation
- CONTROL-FAILED-UNFLAGGED (control-failed-unflagged.md): the continuous closed-form φ₀ is NOT the engine's λ=0 eigenvector (different eigenvalue on the periodic operator)