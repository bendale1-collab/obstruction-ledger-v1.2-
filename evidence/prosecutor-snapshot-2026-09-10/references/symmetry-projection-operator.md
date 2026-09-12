# Symmetry Projection Operator Construction

## When to use

Building a symmetry-restricted linear operator for a spectral method on a periodic domain [−L, L]. Instead of hand-rolling a restricted basis (right-half + symmetry extension + center constraint), use symmetry projection: mathematically cleaner and avoids accidentally discarding degrees of freedom.

## The pattern

For a reflection-symmetric operator (f(x) → f(−x) is a symmetry of the PDE):

1. Build the full-domain operator matrix L of dimension M×M (M = 2N+1 for Fourier collocation)
2. Construct the reflection operator R: (Rf)(x) = f(−x) via R[i, M-1-i] = 1.0
3. Build the symmetry projector: P = (I − R)/2 for odd functions, (I + R)/2 for even
4. Project: L_sym = P @ L @ P
5. Restrict to right-half independent degrees of freedom: center = M//2, right_ix = arange(center, M), return L_sym[ix_(right_ix, right_ix)]

## Advantages over hand-rolled construction

- Center-point constraint: automatic from projection — no explicit zero that discards derivative mode
- Odd extension: built into R operator — no manual sign-flip loop
- Matrix construction: single M×M build + matrix multiply — O(M³) vs O(M²) per column nested loop
- Mathematically correct: eigenstructure of P@L@P IS the restriction of L to the odd subspace

## Theorem

If L is a linear operator on ℝ and P = (I − R)/2 is the orthogonal projector onto the odd subspace, then P@L@P restricted to the odd subspace has exactly the eigenvalues of L with odd eigenvectors. Point spectrum with odd eigenfunctions (λ=0, scaling mode) survive; those with even eigenfunctions (λ=1, translation mode dΩ/dξ) are removed.

## Important limitation: λ=1 on periodic Fourier approximations

Even with symmetry projection, the periodic Fourier approximation on [−L, L] does NOT produce λ=1 at |λ−1| < 0.1. The nearest eigenvalue on the naive full operator sits at Re ≈ 0.375 (distance 0.625 from 1) and does not converge to 1 with increasing N or L. The reason: the periodic Hilbert transform (kernel cot(πx/2L)) approximates the continuous Hilbert transform (kernel 1/x) to O(1/L) accuracy, and the continuous eigenvalue at λ=1 does not survive as a precise eigenvalue of the periodic approximation.

The Defect A acceptance criterion from the pre-registration (|λ−1| < 5e-4) cannot be met by any periodic Fourier discretization on [−L, L]. A different discretization (mapped compactification, log-scale Mellin-adapted grid) is required to resolve λ=1. This falsifies the periodic Fourier method against the continuous operator theorem — it means the discretization is inconsistent with the theorem's function space, not that the theorem is wrong or the implementation is buggy.