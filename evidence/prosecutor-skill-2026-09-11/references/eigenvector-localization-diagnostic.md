# Eigenvector Localization Diagnostic

## When to use

A discretized operator on a finite domain produces eigenvalues that may be:
- **Point spectrum** (genuine eigenvalues of the continuous operator, localized eigenvectors)
- **Essential-spectrum discretization** (discrete approximations of the continuous essential spectrum, spread across the domain)

When the L-sweep cannot distinguish these (DISCRETIZATION-NONCONVERGENT), eigenvector localization provides an alternative discriminator.

## Method

### Pre-registration

```
Populations:
  P1: Modes to classify (e.g. "20 odd residuals of origin-H² operator")
  P2: Known point-spectrum controls (e.g. {0} mode eigenvectors, λ=0 and λ=1)
  P3: Known essential-spectrum controls (e.g. high-Im modes from the line discretization)

Domain split:
  Inner region:  |x| < 1           (near the collapse point / origin)
  Outer region:  |x| > L/2         (near the domain boundary)

Mass fractions:
  m_in  = ||v restricted to |x| < 1||² / ||v||²
  m_out = ||v restricted to |x| > L/2||² / ||v||²
```

### Expected patterns

| Population type | m_in (origin) | m_out (boundary) | Character |
|-----------------|---------------|------------------|-----------|
| Point spectrum (localized) | > 0.6 | < 0.02 | Strongly concentrated at origin |
| Essential-spectrum discretization | < 0.2 | > 0.10 | Spread across domain |
| Delocalized artifact | < 0.1 | > 0.3 | Boundary-dominated |

### Caveats

- The "essential-spectrum discretization" modes on a weighted Sobolev space may ALSO be origin-localized, because the weight function itself concentrates the mode near the origin. In this case, the pattern is NOT a clean separation — both populations look localized.
- On the odd-basis restriction, ALL eigenvectors are odd (v(0)=0 by parity), which forces a local minimum at the origin and can make essential-spectrum modes appear more localized than they are on the full domain.
- **Cross-check:** compute mass fractions on BOTH operators (naive and origin-H²). The essential-spectrum discretization has the same m_in/m_out on both; the true point-spectrum modes have different localization between the two.

## Relationship to F-5

The resolvent-norm check (F-5) is a SPECTRAL discriminator: does the eigenvalue satisfy the resolvent bound? Eigenvector localization is a SPATIAL discriminator: where is the eigenfunction concentrated? They measure different things and neither substitutes for the other. Use both when available.