# Xu Referent Check — Maximal-L² strip real-part extent

## Question
Does Xu 2607.19762 state the exact real-part extent of the maximal-L² strip?
If it includes (−½, 0), the "true strip is Re>0" claim is withdrawn.

## Finding

**Xu 2607.19762, Section 7 (Numerical methods):**
> "By the realization dichotomy (Proposition 2) this fixed-lower-cutoff grid renders the maximal-L² realization: at a=0.5 its rightmost mode sits at Re=+2.4931, within 0.3% of the plain-L² origin indicial line +5/2, so it corroborates Proposition 2 rather than certifying the far-field edge."

The maximal-L² realization's spectrum "fills the strip up to the origin indicial line." The origin indicial line is at Re λ = c̃(a)/2 where c̃ = (c_l + a)/(1 − a). At a=0: c_l = 1, c̃ = 1, origin indicial line = **Re λ = +½.**

Additionally, the abstract states:
> "A realization dichotomy identifies the smear that discretizations without an origin condition place **inside the strip** as the faithful spectrum of the maximal L² realization."

The strip in Theorem 1 and Section 4 is the open half-plane **Re λ > −½**. The essential spectrum is the single line Re λ = −½. The realization dichotomy says the maximal-L² spectrum fills this strip up to the origin indicial line.

## Consequence

**YES — the strip includes (−½, 0).** The "true strip is Re>0" claim is **WITHDRAWN**. Xu's maximal-L² strip extends from Re λ = −½ up to the origin indicial line at Re λ = +½ (at a=0). The positive-Re strip modes (Re ∈ [0.06, 0.80]) are the RIGHT HALF of the full strip. The negative-Re odd residuals (Re ∈ [−0.50, −0.12]) are the LEFT HALF of the same strip.

<!-- K0_R1_REMOVED -->


## Reference

Xu, J. (2026). "The spectral picture of self-similar collapse in the Constantin–Lax–Majda equation." arXiv:2607.19762, **Proposition 2** (Section 3.2), **Theorem 1** (essential spectrum), **Theorems 2** (point spectrum), **Section 7** (numerical realization dichotomy).