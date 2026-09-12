# Term-by-Term Operator Decomposition

## When to use

A discretized spectral operator on a finite domain (e.g., periodic Fourier `[-L, L]`) produces eigenvalues that differ systematically from the continuous operator on ℝ. When a construction defect is suspected — missing eigenvalues, shifted spectrum, or spurious modes — decompose the operator into constituent terms and compare each term's discretized value against its exact ℝ counterpart.

This technique complements the L-sweep (essential-spectrum diagnostic) and resolvent-norm (pseudospectral diagnostic) by identifying **which term drives the spectral shift**, not just that one exists.

**Load alongside:** `l-sweep-essential-spectrum-diagnostic.md` (L-sweep protocol) and `verifier-v0-build.md` (F-5 resolvent-norm cross-check) for a complete discretization-verification toolkit.

---

## Operator decomposition taxonomy

For the gCLM linearised operator L(v) around a profile Ω:

```
L(v) = c_l·v + α·x·v' − (HΩ)·v − (Hv)·Ω
```

Decompose into five terms (T1–T5):

| Term | Expression | Physical meaning | Source of discretization error |
|------|-----------|-----------------|-------------------------------|
| **T1** | `c_l·v` | Scalar multiplication | **None** — identical sampling, no differential operator |
| **T2** | `α·x·v'` | Advection via FFT derivative | FFT derivative on non-periodic functions; boundary ringing |
| **T3** | `−(HΩ)·v` | Base-profile Hilbert-convection | Periodic Hilbert transform vs ℝ Hilbert transform; O(1) at boundaries |
| **T4** | `−(Hv)·Ω` | Test-function Hilbert-advection | Same as T3 but applied to v instead of Ω; error smaller if v is smoother |
| **T5** | `constraint/projection` | Odd-basis projection + right_ix restriction | Matrix artifact from symmetry projection and degree-of-freedom restriction |

**T5** is measured as `||L_matrix @ v_r - sum(T1..T4)|| / ||v_r||` — the difference between the assembled operator matrix and the term-by-term decomposition. If ≈0, the matrix correctly implements the operator pieces.

---

## Per-term relative error protocol

### Pre-registration (before any data)

```
Test function:   v = φ₀ = Ω + x·Ω'   (scaling mode, Xu Sec 3.2)
                 Or: v = Ω, ψ₁ = Ω − x·Ω', any candidate
Engine:          N=1024, L=20, right_ix (odd-basis projection)
Exact ℝ terms:   Closed-form via SymPy Hilbert pairs
Metric:          (engine − exact) / exact per grid point
```

### Step 1 — Exact ℝ terms via SymPy

Compute closed-form Hilbert transforms of rational functions using known pairs:

```
H[1/(X²+a²)]          = X/(a·(X²+a²))           (a > 0)
H[X/(X²+a²)]          = −a/(X²+a²)
H[X/(X²+a²)²]        = (X²−a²)/(2a·(X²+a²)²)
H[(X²−a²)/(X²+a²)²] = −X/(a·(X²+a²)²)
```

For Ω(ξ) = −ξ/(ξ²+¼) and φ₀ = Ω + ξ·Ω' = −ξ/(2(ξ²+¼)²):

```
HΩ(ξ)  = ½/(ξ²+¼)
Hφ₀(ξ) = −(ξ²−¼)/(2(ξ²+¼)²)
```

Sum T1–T4 symbolically with SymPy to get the exact ℝ operator action on the test function. Report the continuous ℝ eigenvalue: λ_cont = L_exact(v) / v. If λ_cont is not constant, the test function is **not an eigenvector** of the ℝ operator — this is a substantive finding, not a bug.

### Step 2 — Engine terms

Compute each term via the engine's FFT-based operators on the periodic domain `[-L, L]`. Sample all terms on the same index set (e.g., right_ix). Per term:

```
e_Tn = engine_value[n]      (via FFT hilbert, FFT derivative)
a_Tn = exact_value[n]        (via SymPy closed form)
rel_error[n] = (e_Tn − a_Tn) / a_Tn      (for |a_Tn| > 1e-15)
```

Report RMS relative error, max |rel| error, and mean relative error for each term.

### Step 3 — Classify dominant defect

| Pattern | Dominant term | Defect class |
|---------|-------------|--------------|
| T1 dominates | c_l·v | Sampling error — only if v is constructed differently |
| T2 dominates (RMS > 10) | x·v' | FFT derivative on non-periodic function — boundary ringing is O(1) |
| T3 dominates (RMS > 10) | −(HΩ)·v | Periodic Hilbert transform — the ℝ Hilbert tail is truncated to `[-L, L]` |
| T4 dominates (RMS > 5) | −(Hv)·Ω | Same as T3; error smaller if v decays faster than Ω |
| T5 dominates (> 0.1) | Constraint projection | Odd-basis symmetry projection adds spurious matrix entries |

**Key finding from CLM P1:** T3 dominates (RMS = 41.7), then T2 (RMS = 69.0). The periodic Hilbert transform + FFT derivative together shift the ℝ eigenvalue from −1.0 to −0.47 — an O(1) spectral shift.

---

## Diagnostic: Spurious null vector

The engine's λ=0 eigenvector may be a constraint artifact rather than a physical scaling mode. Check:

```
idx0 = argmin(|x_r|)       # index of x=0
v0 = λ=0_eigenvector
mass_at_0 = |v0[idx0]|² / ||v0||²
```

| Mass at x=0 | Interpretation |
|------------|---------------|
| > 0.999    | **SPURIOUS-MODE-FROM-CONSTRAINT** — λ=0 is the constraint row's null space |
| 0.1–0.999  | Mixed — constraint contributes but is not dominant |
| < 0.1      | Physical — λ=0 is a genuine scaling mode |

When spurious, the true physical λ=0 eigenfunction φ₀ will appear at a different eigenvalue (−0.47 on the periodic operator, −1.0 on ℝ).

---

## The continuous ℝ eigenvalue

Before trusting any discretized result, confirm the closed-form ℝ operator action on the test function:

```python
# SymPy: sum T1..T4 symbolically
L_exact = sp.simplify(c_l*v + α*x*sp.diff(v,x) - HOmega*v - Hv*Omega)
λ_cont = sp.simplify(L_exact / v)     # continuous eigenvalue
```

If `λ_cont` is a constant, it is the exact ℝ eigenvalue. If not, the function is not an eigenvector of the ℝ operator — this rules out certain defect diagnoses.

**Example (CLM a=0):**
- φ₀ on ℝ: L(φ₀) = −φ₀ → λ_cont = **−1.0000** (essential spectrum band)
- φ₀ on periodic: L(φ₀) = −0.4702·φ₀ → shifted by +0.53
- `λ_cont = −1` is **not** λ=0 as claimed in the paper's odd-basis assertion — φ₀ belongs to the essential spectrum band on ℝ, and the odd projection shifts it to −0.47

---

## Derived candidate testing

From the self-similar ansatz `ω(x,t) = (T−t)⁻¹Ω(x/(T−t)^c_l)`:

| Mode | Expression | λ (ℝ) | Parity | Notes |
|------|-----------|-------|--------|-------|
| Scaling | φ₀ = Ω + ξ·Ω' | −1 (essential) | ODD | Shifts to −0.47 on periodic |
| Translation | φ₁ = dΩ/dξ | 1 (point) | EVEN | Excluded from odd basis |
| Time-shift candidate | ψ₁ = Ω − ξ·Ω' | −0.27 (periodic) | ODD | Not λ=1 on periodic |

Test each candidate on the engine with `L_matrix @ v_r` and find best-fit eigenvalue via eigenvector overlap. Report |λ−1| for candidate odd λ=1 modes.

---

## When to use which diagnostic

| Question | Tool | Reference |
|---------|------|-----------|
| Are eigenvalues L-dependent? | L-sweep (fixed dx) | `l-sweep-essential-spectrum-diagnostic.md` |
| Which term shifts the spectrum? | **Term-by-term (this doc)** | Current |
| Are strip modes pseudospectral? | F-5 resolvent norm (cross-operator) | `verifier-v0-build.md` (F-5 section) |
| Is the λ=0 eigenvector physical? | Spurious null vector check | Section above |
| Does the closed-form ℝ operator exist? | SymPy symbolic sum | Section above |
| Is the λ=1 mode constructible? | Candidate testing | Section above |

---

## Known results (CLM a=0 at N=1024, L=20, odd basis)

| Quantity | Value |
|---------|-------|
| T1 (RMS rel error) | 0.0000 — identical sampling |
| T2 (RMS rel error) | 69.0 — FFT derivative on non-periodic φ₀ |
| T3 (RMS rel error) | 41.7 — periodic Hilbert of Ω (dominant) |
| T4 (RMS rel error) | 3.7 — periodic Hilbert of φ₀ (smaller) |
| T5 (constraint) | 0.249 — odd-basis projection artifact |
| ℝ eigenvalue λ(φ₀) | −1.0000 (SymPy exact) |
| Engine eigenvalue λ(φ₀) | −0.4702 |
| Null vector | SPURIOUS (mass 1.0 at x=0) |
| Odd λ=1 candidate (ψ₁) | λ = −0.27, |λ−1| = 1.27 — not λ=1 |

**Construction defect:** The periodic Hilbert transform (T3) + FFT derivative (T2) replace the ℝ operator with a fundamentally different spectral problem on `[-L, L]`. The shift is O(1) — not a coding bug, a discretization choice. φ₀ goes from λ = −1 (ℝ essential spectrum) to λ = −0.47 (periodic). The λ=1 mode is structurally absent from the odd-basis periodic operator.

## Pitfalls

- **Continuous ℝ eigenvalue must be computed, not assumed.** Paper claims may assign a different λ in a different function space (e.g., φ₀ has λ=0 in the odd-basis ℝ space but λ=−1 on the full-domain ℝ operator — the difference is the symmetry projection's spectral shift).
- **T5 > 0.01 and not flagged is a construction error.** If the matrix `L_cur` disagrees with the piecewise operator sum, the matrix assembly has a bug unrelated to discretization.
- **T2 error from FFT derivative is expected for non-periodic functions.** It is not a bug — but it contributes O(1) to the total shift. If the eigenvalue difference is O(1), the FFT derivative is part of the cause.
- **Spurious null vector is a constraint-penalty artifact, not a bug.** The λ=0 mode at mass-1.0-at-x=0 is correctly solving the constrained system, but it is not a physical scaling mode. Interpret it accordingly.
- **No closed form exists for the odd λ=1 eigenfunction.** Xu Theorem 2 proves existence by spectral theory. Do not attempt to derive one from the ansatz — the ansatz gives symmetry modes (scaling, translation), not the odd λ=1 mode.