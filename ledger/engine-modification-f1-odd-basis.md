# Ledger Entry — ENGINE-MODIFICATION (post-seal, v1.5)
# Type: ENGINE-MODIFICATION
# Filed: 2026-09-09
# Engine: engine/f1.py
# Seal commit: 5a6d9c8 (v1.5 ENGINE SEAL)
# Current HEAD: 526f7a5

## What changed

The odd_basis branch of `RealizationPair` was rewritten after the v1.5
seal. The sealed version constructed the restricted operator directly:

```python
if odd_basis:
    # Restrict to right half (x > 0) with odd extension enforced
    center = M // 2
    right_ix = np.arange(center, M)
    n_sub = len(right_ix)
    def apply_L_odd(v_sub):
        # odd extension to full grid, enforce origin-H2 vanishing,
        # compute L, return right-half restriction
        ...
    L_mat = np.zeros((n_sub, n_sub))
    for j in range(n_sub):
        v = np.zeros(n_sub); v[j] = eps
        L_mat[:, j] = apply_L_odd(v) / eps
    return L_mat
```

The HEAD version builds the full naive operator first, then applies
the odd-projection / restriction as a separate step:

```python
if odd_basis:
    # Build full naive operator first
    L_full = np.zeros((M, M))
    eps = 1e-5
    for j in range(M):
        v = np.zeros(M); v[j] = eps
        L_full[:, j] = apply_L(v) / eps
    # ... (odd projection applied subsequently)
```

Manifest hash at seal: 78f0abd6660f53dcc0b4f0c19cd1d1f3493e1118a1c8989c52d178f0167fd2b6
HEAD hash:               509f0ca2b20194a34f0b22dafb00cb501cc34422b5f2e084b2eeb00753d0d161

## Which results depend on the modified engine

All spectral results computed after the rewrite — i.e., from commit
f349725 (Defect A implemented) onward — used the odd-basis
construction as modified. This includes:

- Defect A symmetry-projection implementation (f349725)
- L-sweep v2 discretization-nonconvergence result (67a97e0)
- Eigenvector localization report (f349725)
- HALF-DOMAIN test (cf218e8)
- STRIP CHARACTERIZATION (49f05cc)
- ORIGIN-SCOPE (3e05597)
- H2 REALIZATION TEST (526f7a5) — including the A1/A5 numbers
  (near1=0.9997, |λ_φ₀−1|=1.047) that entered the reconciliation

The P1 ENGINE-RED verdict (66f9b16) and V0 kill test (1d3c312)
predate the rewrite and used the sealed engine version.

## Status

The modification is documented, not reverted. The current engine is
the one that produced the typed obstruction (Candidate 5 TRIED-FAILED).
Any future LEG B or resumed LEG A work must re-verify engine state
against a v1.6 manifest entry for engine/f1.py.