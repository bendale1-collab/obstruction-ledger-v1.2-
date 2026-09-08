Ledger Entry — Fourier Differentiation Tolerance
Filed: 2026-09-07
Type: PRECISION-CHARACTERIZATION
Mechanism: implicit tolerance derived from grid resolution

The test suite reports Fourier differentiation error = 0.3656 for
f(x) = sin(x).e^{-x^2/50} at N=64, L=10.0.

This tolerance was computed AFTER the first run (post-hoc). No
pre-registered tolerance for differentiation accuracy exists in the
frozen bundle. The test [2/7] uses err < 0.5 as a pass criterion,
which was chosen by inspection of the first error value (~0.37).

Status: the 0.5 threshold is not pre-registered in SPEC sec 14 or
any bundle file. This is a spec gap of the same class as the CCF
equation gap: a numeric target exists (err < 0.5) with no
in-bundle derivation path.

Resolution: this is a smoke test only; the gold-standard H-A
tests validate the solution to the actual PDE, not a generic
differentiation stencil. The differentiation error does not
affect any gate-bearing result. However, per the class audit
discipline, the un-derived threshold is a defect.