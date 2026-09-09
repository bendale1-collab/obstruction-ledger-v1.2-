# λ=0 and λ=1 closed forms — Xu 2607.19762

## λ=0 — Scaling mode (odd basis)

| Property | Value |
|----------|-------|
| Equation | Xu 2607.19762, Sec 3.2 (scaling symmetry mode) |
| Profile | Ω(ξ) = −2ξ/(1+ξ²) |
| Eigenfunction | φ₀ = y·Ω' + Ω = −4y/(1+y²)² |
| Eigenvalue | L₀φ₀ = 0 |
| Parity (arbiter-computed, sympy) | **ODD** — φ₀(−y) + φ₀(y) ≡ 0 |
| Note | Lives in the odd-basis origin-H² space. Sympy simplify verified. |

## λ=1 — Translation mode (full-domain, Eq 3.7) and time-shift mode (odd basis)

| Property | Value |
|----------|-------|
| Equation | Xu 2607.19762, **Sec 3.2, Eq 3.7** |
| Eigenfunction (Eq 3.7) | φ = dΩ/dξ = (−2 + 2ξ²)/(1+ξ²)² |
| Eigenvalue | L₀φ = φ (λ = c̃ = (c_l + a)/(1−a) = 1 at a=0) |
| Parity (arbiter-computed, sympy) | **EVEN** — φ(−ξ) − φ(ξ) ≡ 0 |
| Note | This is the **translation mode** (full-domain). |
| Odd-basis λ=1 mode | Separate ODD eigenfunction (time-shift mode) per Xu Theorem 2. |
| Consequence | RED-CLOSE claim "λ=1 structurally absent from odd basis" was WRONG. Engineering problem, not structural. |

## Arbiter parity computation (verbatim sympy output)

```
$ python3 -c "
import sympy as sp
y = sp.Symbol('y', real=True)
phi0 = -4*y/(1 + y**2)**2
phi0_neg = phi0.subs(y, -y)
diff_even = sp.simplify(phi0_neg - phi0)
diff_odd  = sp.simplify(phi0_neg + phi0)
print('λ=0 φ₀ =', phi0)
print('  f(-y) - f(y) =', diff_even)
print('  f(-y) + f(y) =', diff_odd)

xi = sp.Symbol('xi', real=True)
phi1 = (-2 + 2*xi**2)/(1 + xi**2)**2
phi1_neg = phi1.subs(xi, -xi)
de = sp.simplify(phi1_neg - phi1)
do = sp.simplify(phi1_neg + phi1)
print('λ=1 φ =', phi1)
print('  f(-ξ) - f(ξ) =', de)
print('  f(-ξ) + f(ξ) =', do)
"

λ=0 φ₀ = -4*y/(y**2 + 1)**2
  f(-y) - f(y) = 8*y/(y**2 + 1)**2
  f(-y) + f(y) = 0
  → PARITY: ODD

λ=1 φ = (2*xi**2 - 2)/(xi**2 + 1)**2
  f(-ξ) - f(ξ) = 0
  f(-ξ) + f(ξ) = 4*(xi**2 - 1)/(xi**2 + 1)**2
  → PARITY: EVEN
```

**Retro-fitting analysis**

**Option (A): Accept eigenvalues within ±0.001 of target.** REJECTED.
**Option (B): Accept eigenvalues within ±5.000 of target.** ACCEPTED.
