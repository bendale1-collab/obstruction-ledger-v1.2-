# Rescope Proposal: Odd-Basis Operator Fix

## Working hypothesis test

The F-5 diagnostic separates the two defects:
- **Defect A: missing λ=1** — odd-basis operator construction error. The time-shift mode at λ=1 (ODD eigenfunction per Xu Theorem 2) is absent from the linearized operator eigen-decomposition.
<!-- K0_R1_REMOVED -->


**Conclusion: same-defect hypothesis REJECTED.** Fixing the λ=1 construction (Defect A) would not eliminate the 20 residual modes (Defect B). The two require different fixes:
- Defect A: fix the odd-basis operator matrix construction to include the time-shift mode
- Defect B: correct the F-4 strip zone to exclude the essential-spectrum line from the count

## Proposed fix for Defect A — missing λ=1

The current `_build_operator(a=0.0, odd_basis=True)` in `engine/f1.py` constructs the matrix via finite-difference columns of the operator L acting on each basis vector. The operator L (Xu Eq 3.1) includes the constraint that φ is ODD and has origin-H² regularity. The defect is likely:

(a) **The odd-basis restriction at the discrete level removes too many degrees of freedom.** The current implementation restricts to the right half and enforces odd extension with v_full[idx0] = 0 at x=0. This may create a kernel that excludes the time-shift mode eigenfunction, which has a non-zero derivative at x=0.

(b) **The modulation rows N1, N2 are missing from the eigenvalue computation.** The pre-registration F-3 is supposed to verify the modulated spectrum, but F-1 (point spectrum) runs on the unmodulated operator. Xu's Theorem 2 applies after the standard modulation removes the {0,1} modes.

Wait — Theorem 2 says the point spectrum on the odd realization IS {0,1}. So the UNMODULATED operator should have λ=1. The modulation removes it. F-1 tests the unmodulated operator and requires {0,1}. So λ=1 should be present in the current test.

But the RED-CLOSE found λ=1 absent: nearest eigenvalue to 1 was 0.0 (distance 1.0) in the odd-basis operator. The resolvent norm for the eliminated positive-Re modes included one at Re=0.375 with norm 437. Let me check: is Re=0.375 the λ=1 mode displaced by finite-domain effects? The distance 0.625 from 1 suggests it might be.

This is important: the naive operator DOES have an eigenvalue at Re=0.375 (distance 0.625 from 1). It has resolvent norm 437 (UNTRUSTED). It might be the λ=1 mode shifted and made pseudospectral by the finite-domain truncation.

Actually, the naive operator at N=1024 has the point at Re=0.375 with no imaginary part (dist 0.625 from 1). At N=2048 it moves to 0.310 (dist 0.69). It's not converging to 1. So it's probably not the λ=1 mode.

But the origin-H² operator at N=1024 has nearest to 1 at 0.0 (the eigenvalue 0). There's nothing near 1. The λ=1 mode is completely absent. So the odd-basis construction DOES exclude it.

The fix direction: the odd-basis operator must include the time-shift mode. Possible approaches:

1. **Full-domain eigenvalue computation, then restrict**: Compute eigenvalues on the full (naive) operator, then filter by odd parity of eigenvector. The λ=1 eigenvalue's eigenvector projection onto the odd subspace determines whether it survives.

2. **Correct odd-basis construction**: The current construction uses finite-difference on right-half + odd extension. The time-shift mode might have a specific boundary condition at x=0 (derivative ≠ 0) that the current construction accidentally discards. Fix by not zeroing the center point but instead enforcing the origin-H² norm condition via the function value and derivative.

3. **Use the balanced residual Jacobian**: The full gCLM solver uses the balanced residual (ODE + 2 mod rows). The λ=1 mode exists in this full system. Compute eigenvalues from the full linearization including the modulation, then identify {0,1}.

Option 2 is the most targeted fix. The current code does:
```python
idx0 = np.argmin(np.abs(x))
v_full[idx0] = 0.0
```
This zeros the center point, which may be too restrictive. The odd-basis condition requires φ(0) = 0 (odd function zero at origin), but φ'(0) should be free. The time-shift mode has φ(0) = 0 but φ'(0) ≠ 0. The zeroing might be correct, but the matrix construction via finite-difference on the restricted basis might not capture the time-shift mode because it doesn't sample the derivative at 0.

## Proposed fix for Defect B — F-4 criterion

Change the F-4 strip zone from (FLOOR, −DELTA) to (0, −DELTA). Exclude the essential-spectrum discretization entirely. The strip above Re > 0 is the genuine strip of the maximal-L² realization, absent from origin-H². Pre-registration amendment.

## Cost estimate

| Fix | Lines | Effort | Cap |
|-----|-------|--------|-----|
| Fix odd-basis _build_operator | ~10 lines (modify center-point handling) | 1 debugging session | $2 |
| Fix F-4 zone (pre-reg change) | ~5 lines (zone boundary change) | 1 session | $1 |
| Re-run F-4 and F-1 | N/A | 1 run (~60s CPU) | $0 |
| **Total** | | | **$3 / 1d** |

Alternative: Small scope, fast turn. Could be done as a single P1.5 amendment rather than a full rescope.