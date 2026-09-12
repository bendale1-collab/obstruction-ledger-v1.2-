# L-Sweep Essential-Spectrum Diagnostic

## When to use

A discretized operator on a finite Fourier domain `[-L, L]` has discrete eigenvalues that approximate the continuous essential spectrum. When a continuous essential-spectrum line (e.g. Re λ = −½) is discretized, the eigenvalues **drift rightward** with increasing L as the domain expands and the discrete band representing the continuous spectrum spreads.

To distinguish **essential-spectrum discretization artifacts** from **genuine point spectrum**, run an L-sweep at fixed grid spacing dx = 2L/(2N+1).

## Protocol

### Pre-registration (required before any run)

```
Grid spacing dx = 2L/(2N+1) held constant
Sweep L ∈ {10, 20, 40, 80} with N ∈ {512, 1024, 2048, 4096}
Threshold: |dRe/dlogL| > 1e-2  => L-dependent (essential-spectrum discretization)
```

### Method

1. Build operator at each (L, N) pair with the same realization (e.g., origin-H² or naive)
2. Filter eigenvalues: keep only those with |eig| < 10 (remove high-wavenumber discretization artifacts)
3. Get strip modes: eigenvalues with Re > −0.5 + margin (P0 zone), excluding {0,1} by distance
4. Track modes across L by nearest eigenvalue matching (eigenvector overlap fails when the operator changes dimension)
5. Fit dRe/dlogL for each mode: linear regression Re = a·log(L) + b
6. Classify: |a| > 1e-2 → L-dependent

### Terminal outcomes

| Outcome | Condition | Meaning |
|---------|-----------|---------|
| SWEEP-CONVERGENT | dRe/dlogL < 0 for all modes | Modes converge toward the essential-spectrum line as L grows. Essential-spectrum artifact CONFIRMED. |
| SWEEP-CONFOUNDED | dRe/dlogL ≈ 0 for all modes | No L-dependence. v1's positive sign was a resolution confound. |
| DISCRETIZATION-NONCONVERGENT | dRe/dlogL > 0 for all modes | The Fourier discretization on [-L, L] does not approach the continuous operator as L grows. The eigenvalue band representing the essential spectrum is **spreading rightward**, not converging. Escalate before any F-4 zone proposal. |

## Key findings from the CLM P1 program

On the origin-H² realization of the gCLM a=0 linearized operator:

- **v1 (varying dx):** dRe/dlogL ≈ +0.20 to +0.29 (positive, all modes) — suggested spurious L-sensitivity
- **v2 (fixed dx):** dRe/dlogL ≈ +0.05 to +0.07 (still positive, all modes) — confirmed it's NOT a resolution confound
- **Terminal: DISCRETIZATION-NONCONVERGENT** — the finite Fourier domain's discrete approximation of the essential-spectrum line spreads rightward as L grows, even at fixed resolution

### Nuance overriding the mechanical terminal

Both populations (20 negative-Re essential-spectrum discretization AND 22 positive-Re true strip) had the **same positive dRe/dlogL** (+0.06 vs +0.07). They are **indistinguishable by L-dependence alone**. The real discriminator is the **sign of Re**:

- True strip (wrong realization): always Re > 0 at all L
- Essential-spectrum discretization: always Re < 0 at all L

This means the **naive vs origin-H² realization comparison** is the correct discriminator — not an L-sweep convergence test. The L-sweep's value is in detecting DISCRETIZATION-NONCONVERGENT (which prevents using "increase L" as a convergence strategy), not in distinguishing strip types.

## Why the L-sweep fails as a strip discriminator

Fourier spectral methods on truncated domains `[-L, L]` for operators with continuous spectrum produce a **discrete eigenvalue band** around the continuous essential-spectrum line. The bandwidth (extremal eigenvalue's distance from the continuous line) grows with L:

- More Fourier modes are available to represent the continuous spectrum's tail
- The =−½ line is an essential spectrum, so every discretization produces eigenvalues near it
- As L increases, the domain can accommodate longer-wavelength modes that carry eigenvalues further from the line

**Consequence:** The "increase L to converge" strategy does not work for essential-spectrum discretization. The correct approach is the **realization switch discrimination** (naive vs constrained) — the realization swap changes which eigenvalues belong to the operator, but the discretization artifact is present in both.

## Cross-check: F-5 resolvent norm

Run alongside the L-sweep: for each mode population, compute ε·||(z−ε−L)⁻¹|| on BOTH operators (native and cross-operator). Pattern from CLM P1:

| Population | On native operator | On cross-operator |
|------------|------------------|-------------------|
| Residual essential-spectrum (negative-Re) | Norm O(1) — genuine eigenvalues | Same — same operator eigenvalues |
| Eliminated strip (positive-Re) | 8/22 > 10² (pseudospectral) | Norm < 0.02 (nearly vanish on correct operator) |

The cross-operator check is the strongest discriminator: the "strip" eigenvalues of the wrong realization nearly vanish on the correct operator.