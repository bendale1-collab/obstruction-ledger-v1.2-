# Control-Repair Procedure

## Problem

A closed-form eigenfunction of the continuous operator (e.g. L₀ on ℝ) is used as a control vector to verify a discretized operator (e.g. periodic Fourier on [-L, L]). The control reports ||Lv - λv||/||v|| = O(1), far above the expected 1e-6. The control appears to "fail."

## Diagnosis steps

### Step 1 — Verify the coordinate map

The continuous and discretized problems may use different normalizations or coordinate conventions:
- Check for scaling: is the profile expressed as −y/(y²+¼) or −2ξ/(1+ξ²)? These differ by ξ = 2y.
- Apply the coordinate transformation to the eigenfunction before sampling
- Verify: does the transformed profile satisfy the correct discrete equation?

### Step 2 — Check overlap with engine's own eigenvalue

```python
eigvals, eigvecs = linalg.eig(L_discrete)
i0 = np.argmin(np.abs(eigvals))  # engine's λ=0 eigenvector
u0 = eigvecs[:, i0]
v0 = sampled_closed_form
overlap = abs(np.vdot(u0.conj(), v0)) / (|u0|·|v0|)
```

| Overlap | Diagnosis |
|---------|-----------|
| ≈ 1.0 | Same mode. Different eigenvalue — the periodic operator shifts eigenvalues. Find λ_fit = <Lv,v>/<v,v> and report residual at that λ. |
| ≈ 0.0 | Different mode entirely. The closed form is an eigenvector of the CONTINUOUS operator; the discrete operator has a different eigenspace. |
| 0.1–0.9 | Mixed mode or coordinate error. Verify the coordinate map and try other eigenvalues. |

### Step 3 — Find the closed form's best-fit eigenvalue

```python
lam_fit = real(<Lv, v> / <v, v>)
resid = ||Lv - lam_fit·v|| / ||v||
```

If resid < 1e-3, the closed form IS an eigenvector of the discrete operator, but shifted from its continuous eigenvalue.

### Step 4 — Classify the shift

Compute the error's spatial distribution:
- **Boundary-dominated** (≥60% at |x| > L/2): The periodic boundary conditions (Hilbert kernel difference, periodicity) cause the shift. This is a DOMAIN TRUNCATION effect.
- **Origin-dominated** (≥60% at |x| < 1): The discretization of the origin condition (odd-basis restriction, zero at origin) causes the shift. This is a CONSTRAINT effect — may be fixable with better construction.
- **Uniform** (spread across domain): Likely a global operator error (coefficient, sign, or Hilbert transform implementation).

## Resolution

1. **If the engine has its OWN eigenvector at the expected eigenvalue** (exact, residual < 1e-14): the continuous closed form is irrelevant. The discrete operator's eigenvalue is the correct one for the discretized problem. Use the engine's eigenvector as the control.

2. **If the engine does NOT have an eigenvector anywhere near the expected eigenvalue** (minimum distance > 0.1): the discretization fundamentally does NOT capture this spectral feature. This is a discretization choice, not a bug. File as discretization limitation, not control failure.

3. **If the engine has an eigenvalue at the shifted position:** the discrete operator's eigenspace contains a mode related to the continuous one, but at a different eigenvalue. File with both eigenvalues and the spatial distribution of the shift.

## Ledger entry

File a CONTROL-FAILED-UNFLAGGED entry with:
- Overlap value
- Best-fit λ (continuous vs discrete)
- Residual at best-fit λ
- Spatial distribution (origin vs boundary fraction)
- Which of the three diagnoses above applies
- Recommendation: retract/rephrase any "changes the spectral problem at O(1)" sentence — the correct statement is "the continuous and periodic operators have different eigenfunctions and eigenvalues."