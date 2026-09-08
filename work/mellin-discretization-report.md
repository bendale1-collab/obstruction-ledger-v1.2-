# Mellin / Log-Radial Discretization — Report Only

## What it is

A Mellin (log-radial) discretization represents functions on ℝ⁺ in the variable
y = ln x, where x ∈ (0, ∞). Under this transform:
- The dilation generator x·d/dx becomes a simple translation d/dy
- The Hilbert transform becomes a convolution with an exponential kernel
- The origin (x → 0⁺) maps to y → −∞; infinity maps to y → +∞
- The essential spectrum line Re λ = −½ becomes a Fourier symbol

## Why it applies here

Xu's operator L₀ operates on the odd half-line (0, ∞). The origin condition
(H² regularity at x=0) becomes a **function-space membership condition**
on the Mellin transform: the weight w(y) = e^(−y/2) · (mellin-transform
decay rate) determines which singular exponents are admissible. Modes
of the form x^{−½ + iω} (essential spectrum) become Fourier modes e^{iωy}
on the transformed domain, and the origin-H² condition excludes those with
Re λ > −½ by controlling the function's growth as y → −∞.

## Key differences from Fourier [−L, L]

| Aspect | Fourier [−L, L] | Mellin (log-radial) |
|--------|----------------|---------------------|
| Domain | Bounded periodic | Half-line (0, ∞) mapped to (−∞, ∞) |
| Origin condition | Parity + zero at origin | Boundary condition as y → −∞ |
| Essential spectrum | Discrete band around −½ | Exact Fourier line −½ + iℝ |
| λ=1 eigenfunction | Not representable (domain truncation) | Representable (decays at both ends) |
| Hilbert transform | Periodic kernel cot(π(x−y)/2L) | Exponential kernel (exact) |
| Non-normality | Finite matrix, scipy eigensolve | Fourier multiplier + convolution |

## What would be required

1. **Basis:** Fourier series on (−∞, ∞) after Mellin transform (y ∈ (−∞, ∞))
   OR Laguerre basis on (0, ∞) with weight matching the operator's domain.

2. **Operator assembly:**
   - Hilbert transform: kernel integral (exponential kernel, exact)
   - Profile coefficients Ω, c_l, U from the existing Newton solver (unchanged)
   - Modulation rows N1, N2: become boundary conditions at y → −∞

3. **Origin condition as boundary condition:**
   - H² regularity: v(y) ~ O(1) as y → −∞ with bounded v'(y), v''(y)
   - The time-shift mode λ=1 has the correct decay as y → −∞
   - The translation mode λ=1 (even, dΩ/dξ) has a DIFFERENT asymptotic
     and would still be excluded — CORRECT, since the odd basis excludes it

4. **Essential spectrum precisely:**
   - The line Re λ = −½ appears as the Fourier symbol of the dilation part
   - No discrete band, no L-dependent drift, no discretization artifact

## Estimated build cost

| Component | Estimate | Notes |
|-----------|----------|-------|
| Mellin transform library | ~50 lines | sympy + numpy for kernel evaluation |
| Operator assembly | ~100 lines | Replace differentiation with ik multiplier |
| Hilbert convolution | ~80 lines | Exponential kernel, trapezoidal or FFT |
| Eigendecomposition | unchanged | scipy.linalg.eig on resulting matrix |
| Verification (Xu closed forms) | ~30 lines | Should reproduce λ = {0,1} to machine precision |
| **Total** | **~260 lines**, 1–2 days dev, $0 compute | CPU only |

## Risk

The Mellin-Hilbert kernel is singular at y=0 and its accurate quadrature is
delicate. The operator is still non-normal. The spectral gap (½ after modulation)
should be exact, eliminating the pseudospectral concerns from the Fourier
discretization.

## Standing

This is not a proposal to build. It is an information item for the founder's
decision: continue on the Fourier engine (with accepted limitations) or move
to a dilation-native (Mellin) discretization.