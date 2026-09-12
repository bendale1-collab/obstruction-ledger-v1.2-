# Operator Verification Protocol

**Purpose:** Systematically verify that a numerical operator matches its
mathematical definition (source paper). Catches sign conventions,
fabricated claims, truncation artifacts, and construction bugs.

---

## 1. Convention Audit (sign convention detection)

When a paper defines a linear operator L and you have a numerical
implementation L_eng, verify they match **term by term**.

**Procedure:**
1. Transcribe the paper's operator verbatim, with equation number.
2. Transcribe your engine's operator verbatim, from the code.
3. Write both as sympy expressions, substituting the same test function(s).
4. Compute L_paper(φ) / φ and L_eng(φ) / φ at several points.
5. Report the sign relation: L_paper = ±L_eng or L_paper ≠ L_eng.

**Example (this session):**
- Xu Eq 3.1 at a=0: L_Xu φ = −φ − yφ' + φ·HΩ + Ω·Hφ
- Engine: L_eng φ = φ + yφ' − HΩ·φ − Hφ·Ω
- Result: L_Xu = −L_eng (every term sign-flipped). All eigenvalues negated.

**Pitfalls:**
- The paper may use L = −dRes/dΩ (evolution sign) while the engine
  uses dRes/dΩ (profile-ODE sign). Both are internally consistent;
  the difference is a conventional choice, not a bug.
- Check whether the paper's eigenvalue equation is Lφ = λφ or
  ∂_τ φ = Lφ or some other convention.
- Verify the sign of the residual definition: the profile equation
  may be Res[Ω] = 0, and the linearization may be L = ±dRes/dΩ.

---

## 2. FABRICATED-QUOTE Detection

When a corpus entry or prior report claims a specific sentence from a
source paper, verify it against the source text.

**Procedure:**
1. Identify the exact claimed sentence, with page/section/equation refs.
2. Fetch the paper (HTML preferred; PDF as backup).
3. Full-text search for the claimed sentence. If not found:
   a. Search for the claimed equation number.
   b. Search for keywords (~3 non-overlapping phrases from the claim).
   c. Extract the surrounding passage for comparison.
4. File FABRICATED-QUOTE with: the claimed text, the actual text (or
   'no matching passage'), and the source reference.

**Example (this session):**
- Claimed: "The scaling transformation (T-dilation) generates φ₀ at λ=0"
- Found: Abstract says "{0,1} are the scaling and time-shift modes"
  but NO closed form for either odd mode. Sentence is FABRICATED.
- The odd λ=0 mode is a spectral existence theorem (Thm 2), not a formula.

**Prevention:**
- Never assert a "known property" without a citation you have read.
- The quote verification step should run BEFORE the analysis that
  depends on it (pre-registration control-gate design).

---

## 3. Term-by-Term Decomposition

Decompose L(φ) into its constituent pieces and compare engine terms
against exact ℝ terms term by term.

**Procedure:**
1. Write L(φ) = Σᵢ Tᵢ(φ) where each Tᵢ is a single operator piece
   (e.g. T₁ = c_l·φ, T₂ = α·x·φ', T₃ = −HΩ·φ, T₄ = −Hφ·Ω).
2. For each Tᵢ, compute:
   - The exact ℝ expression (via sympy + known Hilbert pairs).
   - The engine expression (via FFT/collocation on the numerical grid).
3. Report (engine − exact) / exact:
   - Vector L₂ norm (full domain and restricted to a mass-carrying region).
   - RMS and max |relative| error.
4. Identify the dominant term (largest RMS rel error) — this is the
   construction defect or dominant truncation artifact.

**Interpretation of error pattern:**
- T1 error = 0: identical sampling, no defect.
- T2 large: FFT derivative on non-periodic function (boundary ringing).
- T3 large: periodic Hilbert transform differs from ℝ Hilbert.
- T4 large: same as T3 for second function (often worse, since φ has
  less spatial localization than the base profile Ω).
- T5 ≈ 0: symmetry projection adds no spurious content.
- T5 > 0.1: symmetry projection degrades the operator.

**Example (this session):**
| Term | Definition | RMS rel | Diagnosis |
|------|-----------|---------|-----------|
| T1 | c_l·φ₀ | 0.000 | identical sampling |
| T2 | x·φ₀' | 18.5% | FFT derivative boundary ringing |
| T3 | −(HΩ)·φ₀ | 4.4% | periodic HΩ (Ω is localised) |
| T4 | −(Hφ₀)·Ω | 67.7% | **dominant defect — periodic Hφ₀** |
| T5 | projection | 0.0% | odd-basis adds no spurious content |

---

## 4. Half-Domain Hilbert Test

Distinguish truncation effects (periodic vs ℝ Hilbert) from construction
bugs (half-domain/odd-basis restriction). Compare H(φ) computed two ways:
(i) full-grid periodic FFT → restrict, (ii) odd-basis H matrix.

**Diagnostic table:**

| (i) error | (ii) error | Interpretation |
|-----------|-----------|---------------|
| ~1e-4 | ~0.7 | **Construction bug in half-domain projection** — Fourier stays. Fix odd-basis construction. |
| ~0.7 | ~0.7 | **Genuine truncation effect** — periodic Hilbert itself cannot represent ℝ Hilbert for non-periodic functions. Mellin (or ℝ discretization) required. |
| ~1e-4 | ~1e-4 | No defect. Truncation negligible for these functions. |
| ~0.7 | ~1e-4 | Inconsistency in measurement. Re-check H matrix extraction. |

**Procedure:**
1. Build the full FFT Hilbert matrix H_full (size M×M).
2. Build the odd-projected matrix H_odd = P·H_full·P, then restrict to
   right_ix → H_cur (1025×1025).
3. Compute exact ℝ H(φ) via sympy closed form.
4. Compare: H_full[right_ix] @ φ_r vs exact, and H_cur @ φ_r vs exact.
5. Apply the diagnostic.

**Same test for derivative matrix D:**

| (i) error | (ii) error | Interpretation |
|-----------|-----------|---------------|
| ~1e-4 | ~0.7 | Half-domain derivative construction bug |
| >0.1 | >0.1 | Genuine truncation — FFT derivative of non-periodic φ |

---

## 5. Full-Grid L_Xu Test

Apply the CORRECT paper operator (L_Xu or L_eng) on the full grid using
FFT-computed H and derivatives, then restrict and solve for the eigenvalue.

**Procedure:**
1. Compute each term of L_paper via full-grid FFT: HO, Hφ, φ', etc.
2. Assemble L_paper(φ) on the full grid. Restrict to right_ix.
3. Best-fit eigenvalue: λ = ⟨Lφ, φ⟩ / ⟨φ, φ⟩.
4. Expected λ (from ℝ, exact): should match known closed-form eigenvalue.
5. Distance from target = |λ − expected|.
6. If full-grid λ is close (~1e-1) but odd-basis λ is far, the defect
   is in the odd projection. If both are far, the defect is truncation.

---

## References

- `prosecutor/references/referent-resolution-control.md` — referent identity verification
- `prosecutor/references/verifier-v0-build.md` — arbiter construction
- This session's reports: `work/term-by-term-report.md`, `work/convention-audit-report.md`, `work/half-domain-test-report.md`