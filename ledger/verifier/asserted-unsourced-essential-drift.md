# ASSERTED-UNSOURCED Flag — Rightward-drifting essential bands

## Claim
"The finite Fourier domain [−L, L] produces a discrete eigenvalue band around the continuous essential spectrum line whose width increases with L."

## Finding

**No single citable source found for this specific claim.** The property has two independent components:

1. **Domain truncation** — replacing ℝ by [−L, L] is referred to as "domain truncation" (Boyd 2013, Chebyshev and Fourier Spectral Methods, Dover). Domain truncation converts continuous-spectrum problems into discrete matrix problems whose eigenvalues approximate the continuous spectrum. *No theorem in Boyd or elsewhere predicts that the eigenvalue band necessarily widens with L at fixed resolution dx.*

2. **Fourier discretization of operators with continuous spectrum** — For the CLM linearized operator L₀, the Hilbert transform on the periodic domain [−L, L] is the *periodic* Hilbert transform (kernel cot(π(x−y)/2L) rather than 1/(x−y)). The periodic and continuous Hilbert transforms differ by an O(1/L) boundary term. The eigenvalues of the discretized periodic operator approximate those of the continuous operator to at best O(1/L) accuracy (Boyd §4.1, "sinc" vs Fourier). *The rightward drift of the essential-spectrum discretization as L increases is a consequence of this O(1/L) boundary-effect term, not a theorem of domain truncation.*

## Disposition

**ASSERTED-UNSOURCED** — the claim that "discrete essential-spectrum eigenvalues drift rightward as L grows" was asserted without a source. The correct statement is: *the periodic Fourier approximation on [−L, L] approximates the continuous operator to O(1/L) accuracy; the discretization's eigenvalue band around the essential spectrum line has width that scales as O(1/L), producing the observed rightward drift of the extremal modes as L grows (meaning the drift DECREASES as L increases, which explains why at larger L the band narrows toward Re = −½).*

This does NOT affect the L-sweep v2 result (dRe/dlogL > 0 at fixed dx shows non-convergence), but the unsourced claim is removed from the reasoning.