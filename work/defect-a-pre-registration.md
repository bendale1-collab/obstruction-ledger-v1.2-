# Defect A — Pre-registration: λ=1 acceptance in odd basis

## Acceptance criteria (frozen before fix)

The odd-basis `_build_operator(a=0.0, odd_basis=True)` must produce eigenvalue λ=1
satisfying ALL of:

| Criterion | Value | Rationale |
|-----------|-------|-----------|
| Complex distance | `|λ−1| < 5×10⁻⁴` | Matches F-3(a) BORROWED-TOLERANCE δ |
| Eigenvector residual | `||L₀·v − 1·v|| / ||v|| < 10⁻⁸` | Eigenvalue equation residual against computed eigenvector |
| N-doubling stability | "1" present at both N=1024 and N=2048 | Count and value stable under resolution doubling |
| Eigenvector parity | ODD (arbiter-computed from closed form) | Matches Xu Theorem 2 — odd-basis time-shift mode |

## Verification method

1. Compute `L_h2 = _build_operator(a=0.0, odd_basis=True)` at N=1024.
2. Find `λ_candidate = argmin |λ − 1|` over all eigenvalues.
3. Check `|λ_candidate − 1| < 5×10⁻⁴`.
4. Compute eigenvector v_candidate, check `||L₀·v − λ·v|| / ||v|| < 10⁻⁸`.
5. Same at N=2048.
6. Check eigenvector parity: `v_candidate(0) = 0`, `v_candidate(x) = −v_candidate(−x)`.

## Failure consequence

If λ=1 fails any criterion → the fix is incomplete → **ENGINE-RED continues**.
Do NOT score F-1/F-2/F-3/F-5 until this criterion passes.

## Engine change scope

- File: `engine/f1.py`, `RealizationPair._build_operator` method
- Change: center-point constraint (odd-basis construction)
- Re-seal required: new MANIFEST.sha256, new freeze hash, founder publish
- The V0 arbiter's parity check will independently verify eigenvector parity

## Sequence

L-sweep → Defect A fix → re-seal → F-4 v2 through adversary → re-run battery
No P1.5 shortcut.