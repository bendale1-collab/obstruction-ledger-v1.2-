# Symmetry-Projection Odd-Basis Construction

## Problem

Restricting a differential operator L on [-L, L] to the odd-parity subspace
(i.e., functions satisfying f(−x) = −f(x)) while preserving its eigenvalue
spectrum on that subspace.

## Two construction methods

### Method A — Manual odd-extension (fragile)

Construct the matrix column-by-column: for each basis vector in the right-half
space, extend it oddly to the full domain, apply L, return the result on the
right half, zero the center point.

```python
for j in range(n_sub):
    v = np.zeros(M)
    v[right_ix] = v_sub
    for i_r, ix in enumerate(right_ix):
        v[M-1-ix] = -v_sub[i_r]    # odd extension
    v[center] = 0.0                 # enforce zero at origin
    L_mat[:, j] = apply_L(v) / eps  # finite-difference column
```

**Problems:** The zero-at-center enforcement overspecifies the odd condition
(odd parity already forces v(0)=0) and may exclude eigenfunctions with
non-zero derivative at the origin. Also, the column-by-column construction
accumulates different boundary-condition errors in each column.

### Method B — Symmetry projection (preferred)

Build the full-domain matrix L (M×M), then project onto the odd subspace via
the reflection operator R and the projector P = (I − R)/2.

```python
# Reflection operator: (Rf)(x) = f(-x)
R = np.zeros((M, M))
for i in range(M):
    R[i, M - 1 - i] = 1.0

# Projector onto odd functions
P = (np.eye(M) - R) / 2.0

# Projected operator
L_odd = P @ L @ P

# Restrict to right-half DOFs
right_ix = np.arange(center, M)
L_odd_rh = L_odd[np.ix_(right_ix, right_ix)]
```

**Advantages:**
- No manual column-by-column construction — uses the known-correct full matrix
- The projector P enforces the odd condition VARIATIONALLY: P² = P, P = P^T
- No over-specification at the origin — the odd condition emerges from the projection
- The center point is handled automatically by the reflection

## Performance note

Method B requires building the full M×M matrix first (O(M²) operations), then
projecting (O(M³) for the triple product). For M=2049 at N=1024, this is
~30s vs ~3s for Method A. The cost is acceptable for diagnostic runs and
does not scale with the number of operator applications after construction.

## Spectral consequences

- The projected operator preserves the ODD subset of the full spectrum exactly
- Eigenvalues of the projected operator are eigenvalues of the full operator
  restricted to odd functions — they match the odd-parity subset of the full spectrum
- The zero eigenvalue (scaling mode) survives in both constructions
- λ=1 (time-shift mode) is absent from BOTH constructions on periodic [−L, L]:
  the continuous λ=1 mode requires ℝ-line domain and does not discretize
  onto the periodic Fourier basis regardless of construction

## When to use which

| Scenario | Method |
|----------|--------|
| Quick P0 smoke test | A (manual, fast) |
| Publishing eigenvalue spectrum | B (projected, correct) |
| P1 goldens verification | B (projected) |
| Mellin or alternative discretization | N/A — odd condition is inherent |