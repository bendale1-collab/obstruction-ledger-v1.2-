# CONTROL-FAILED-UNFLAGGED

## Discovery

The continuous closed-form eigenfunction φ₀ (Xu Sec 3.2) was tested as a control
against the engine's discrete λ=0 eigenvector. Result: **overlap = 0.0000.**

## Mechanism

The periodic Fourier Hilbert transform on [-L, L] differs from the continuous
Hilbert transform on ℝ. The continuous eigenvalue problem and the periodic
discrete eigenvalue problem are DIFFERENT spectral problems.

Specifically:
- φ₀ is a λ=0 eigenfunction of L₀ on ℝ (exact)
- φ₀ is an approximate eigenvector of the periodic L at λ ≈ -0.47 (residual 4e-3)
- The continuous eigenvalue 0 shifted to -0.47 by the periodic H mismatch
- The engine finds its OWN λ=0 eigenvector (exact, residual < 1e-14) — this is
  the discrete scaling symmetry mode, a DIFFERENT function from φ₀

## Disposition

The control tested the wrong hypothesis: "the continuous closed-form eigenfunction
should be an approximate discrete eigenvector at the same eigenvalue." This
assumed the periodic and continuous operators are spectrally close, which the
data falsifies.

Retracted from the adjudication packet: "the periodic Fourier discretization
changes the spectral problem at O(1)" — this statement is replaced with the
precise finding: the continuous and periodic operators have different
eigenfunctions and eigenvalues. The periodic operator preserves the scaling
symmetry (λ=0 exact) but not the time-shift (λ=1 absent), because the time-shift
mode λ=1 eigenfunction has non-zero derivative at x=0 which the odd-basis
restriction on a finite periodic domain misrepresents.

## Impact on fork decision

None. The fork (Fourier vs Mellin) is governed by whether the missing λ=1
spectrum is acceptable. The control repair confirms λ=1 is absent but λ=0
is present. Fork decision remains the founder's.