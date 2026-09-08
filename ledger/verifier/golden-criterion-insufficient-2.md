# GOLDEN-CRITERION-INSUFFICIENT #2

## Finding
The Defect-A symmetry-projection fix changes the odd-basis operator matrix by
Frobenius ratio 0.5 (||L_proj - L_current||_F / ||L_current||_F = 0.50).
Yet ALL 7 P0 golden tests pass identically under both operators.

## Mechanism

The P0 golden tests (H-A) check:
1. Hilbert transform smoke (initial condition-independent)
2. Fourier differentiation accuracy (grid+operator independent)
3. gCLMSolver convergence (profile solve, not matrix construction)
4. CLM a=0 exact profile + c_l (profile solve, not eigenvalue)
5. Modulation (profile solve + rank analysis, not eigenvalue)
6. H-B realization pair (naive strip count, not origin-H² eigenvalue structure)
7. CCF leg (not implemented)

**None of the P0 goldens test the eigenvalue spectrum of the odd-basis operator.**
The eigenvalue spectrum requires F-1/F-2 (the P1 battery, which is NOT in P0).

## Consequence

P0 GREEN is insufficient to certify the engine for P1. A test that directly
checks the odd-basis operator's eigenvalue spectrum (specifically λ=1 and λ=0
presence) must be added to the P0 golden suite before any future P1.

## Pre-registered acceptance violated

The Defect A acceptance criterion requires |λ−1| < 5×10⁻⁴. The measured
nearest eigenvalue to 1 on the Defect-A-modified operator is 0.0 (dist=1.0).
This stands as-is — the periodic Fourier discretization on [−L, L] does not
produce λ=1 for ANY construction tested (naive, current odd-basis, Defect A).
The criterion cannot be met on this discretization.

## Disposition

Filed. Not a defect of the fix — it reveals that the P0 golden suite has
a coverage hole for eigenvalue spectrum verification.

## File

`ledger/verifier/golden-criterion-insufficient-2.md`