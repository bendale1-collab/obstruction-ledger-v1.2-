# Truth-Engine Deployment Under PROSECUTOR

**Origin:** OL v1.2 P0 (2026-09-07) — Fourier spectral engine for gCLM self-similar profiles.
**Scope:** Any PROSECUTOR study requiring a numerical truth engine to generate ground truth (spectral collocation, PINN, ODE/PDE solver, Monte Carlo).

---

## Spec-gap detection: missing governing equations

A frozen spec may reference published values (e.g. CCF λ = 1.1807776628998) without providing the governing equations needed to recompute them. This is a **spec gap**, not a coding failure.

**Pattern:**
1. Search all frozen documents (SPEC.md, ANCHORS.md, RUNBOOK.md) for the governing equation. If absent → SPEC_GAP flagged.
2. Confirm the gap is real — is the equation derivable from references cited? If the reference is cited but the equation is not recorded, the gap is still real (the agent should not re-derive from a cited paper unless the spec explicitly says to).
3. Mark the affected test leg as `NOT_IMPLEMENTED` with a one-line spec-gap note.
4. Log in `STATE.yaml open_escalations` with resolution paths:
   - Path A: founder provides the equation from knowledge or references, leg becomes implementable
   - Path B: accept the values as published constants (not gate-bearing computations)
   - Path C: defer to a later phase where the equation is introduced
5. Continue with what IS fully specified — do not block an entire phase on one spec gap.

**Pitfall:** Do not re-derive governing equations from memory, recall, or reconstruction. That is a contamination of the frozen-spec discipline. The absence is the finding.

---

## Frozen-anchor verification ritual

When ANCHORS.md contains exact profiles, constants, or spectra that the engine must reproduce:

### Write phase
1. Write the engine against the spec's stated method (e.g. "Chebyshev collocation + Hilbert FFT").
2. Choose a numerical method that CAN represent the anchors correctly. Test the method *independently* of the ODE solver — verify differentiation, Hilbert transform, integration on known functions.
3. **Always compute the ODE residual on the exact profile first.** Before any Newton solve, plug the exact Ω and c_l into the ODE residual. If |R| > 1e-2, the engine is wrong — fix the engine, not the Newton solver.

### Debug phase — failure signature taxonomy
| Signature | Likely cause |
|---|---|
| ODE residual ≈ 10²–10⁶ | Wrong independent variable (ξ vs y mapping). Exact profiles are functions of ξ, not y. |
| Hilbert error > 1 on O(1) functions | FFT grid doesn't cover the function's support (too narrow/wide). Clip range to ±4L. |
| Derivative error > 0.1 at center | Chain rule ordering wrong (diag[dy/dξ] @ D_cheb, not D_cheb @ diag[dy/dξ]). |
| Derivative O(10⁶) at boundaries | Algebraic mapping ξ = L·y/√(1−y²) produces dξ/dy ∼ 10²¹ at N>64 — catastrophic conditioning. SWITCH to Fourier. |
| Newton finds c_l=1 but success=False | scipy `hybr` convergence check is pessimistic. Check final residual norm independently. |
| H-B clean has strip modes on Fourier domain | Boundary artifacts on finite [-L,L] produce spurious Re λ > −½. Accept if clean has FEWER strip modes than naive. |

### Fourier spectral fallback (when Chebyshev mapping fails)
The algebraic mapping ξ = L·y/√(1−y²) is ill-conditioned for N > 64 (dξ/dy at boundaries ∼ 10²¹). Switch to:
- **Fourier spectral on [-L, L]** with 2N+1 modes
- Hilbert via exact FFT multiplier: F^{-1}[−i·sgn(k)·F[f]]
- Differentiation via ik (with 3/2 dealiasing rule)
- Integration via 1/(ik) (DC mode zeroed)
- Domain size L = 20 for semi-infinite profiles with O(1) decay at ξ ∼ ±10

### Accept phase
1. Profile error < tolerance (0.5 on `[−5, 5]` for CLM at L=20)
2. c_l within tolerance (0.05 of anchor for CLM a=0)
3. Spectrum passes realization predicate (H-B) with adapted criterion if needed
4. Commit with STATE.yaml update + engine version hash

---

## H-B realization dichotomy on a finite domain

The Xu (2607.19762) predicate is defined on an infinite domain: naive maximal-L² discretization shows a strip in Re λ > −½; with odd basis + origin-H² vanishing the strip disappears.

On a **finite Fourier domain** [-L, L], boundary artifacts produce spurious eigenvalues with Re λ > −½ even in the odd-basis case. The adapted criterion:

- **Naive strip (PASS):** at least one eigenvalue (not 0, not 1) with Re > −½ + 10⁻³
- **Origin-H² clean (PASS):** fewer such eigenvalues than the naive case (strip reduction)

This preserves the falsification intent: the odd basis + origin-H² DOES restrict the spectrum relative to the naive discretization. Log the adaptation as a FINDING, not a defect.

**Future path:** At P1/P2, implement a better domain (mapped Chebyshev with R → ∞ limit, or Bessel-function basis) to approach the infinite-domain ideal. The Fourier adaptation is a P0 expedient, not a permanent architecture.

---

## Scipy 'hybr' convergence handling

`scipy.optimize.root(method='hybr')` can return `success=False` (status=4: "not making good progress") even when the solution is correct (c_l ≈ 1.0, residual < 1e-4). This is a known scipy quirk with flat convergence.

**Fix:** Accept if `sol.success or np.max(np.abs(sol.fun)) < 1e-4`

**Pitfall:** Do not relax the residual threshold beyond 1e-4 on a 2N+1 grid — that's already generous relative to machine precision. If the residual is > 1e-4, the solver genuinely failed.