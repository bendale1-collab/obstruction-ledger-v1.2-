# LEG A — CLOSE-OUT OBSTRUCTION

**ORDER-ID:** OL-v1.5-LEG-A-CLOSED
**DATE:** 2026-09-09
**SEAL:** DETACHED (see seal check below)

---

## 1. SEAL CHECK — c6a73ae82f2e8bda1cdac2f348d6a2342ce5c07e5d43ae97516db05d178c00a4

### Per-file report

| File | Status | Detail |
|------|--------|--------|
| amendment-log-v1.4.txt | ✅ | Hash match in HEAD |
| anchors/ANCHORS.md | ✅ | Hash match in HEAD |
| engine/f1.py | ⚠ | **MODIFIED** (hash mismatch) — odd_basis construction rewritten after seal |
| HANDOFF-CHECKLIST.md | ✅ | Hash match in HEAD |
| ledger/chebyshev-mapping-rejection-2026-09-07.yaml | ❌ | **NEVER COMMITTED** — existed in working tree at seal time, lost |
| ledger/chebyshev-mapping-rejection.md | ✅ | Hash match in HEAD |
| ledger/conv-flag-diagnosis-2026-09-07.yaml | ❌ | **NEVER COMMITTED** |
| ledger/conv-flag-diagnosis.md | ✅ | Hash match in HEAD |
| ledger/fourier-diff-tolerance-2026-09-07.yaml | ❌ | **NEVER COMMITTED** |
| ledger/fourier-diff-tolerance.md | ✅ | Hash match in HEAD |
| ledger/misidentification-by-acronym-collision-2026-09-08.yaml | ❌ | **NEVER COMMITTED** |
| ledger/misidentification-by-acronym-collision.md | ❌ | **NEVER COMMITTED** |
| RUNBOOK.md | ✅ | Hash match in HEAD |
| SPEC.md | ✅ | Hash match in HEAD |
| specs/leg-a-p1-pre-registration-v1.5.txt | ✅ | Hash match in HEAD |

**Total: 9 match, 1 modified, 5 never committed — out of 15.**

**SEAL-DETACHED.** The MANIFEST.sha256 file hashes correctly to c6a73ae8, but:
- 5 of 15 files (the YAML ledger entries + misidentification.md) were **never committed** to git — they existed only in the working tree at seal time and are gone
- `engine/f1.py` was **modified** after the seal (odd_basis construction rewritten)
- All 15 files are **absent from disk** (working tree deleted them)

**Last verified check:** commit `5a6d9c8` (v1.5 ENGINE SEAL), 2026-09-08.
**Results after detachment:** ALL 26 subsequent commits (`66f9b16` P1 ENGINE-RED through `526f7a5` H2 REALIZATION TEST) were produced against a SEAL-DETACHED tree. This includes the ENGINE-RED verdict, all K0 validation, all strip characterizations, fork adjudications, and the H2 realization test.

---

## 2. OUTPUT-PRECISION POLICY

**Registered effective immediately as a standing policy.**

Eigenvalues, residuals, and distances stored at **≥12 significant digits** in machine-readable form (JSON), not only as report tables.

**Rationale:** The A1/A5 reconciliation (2026-09-09) showed that no 12-digit precision was available for the H2 generalized eigenvalue nearest to 1 — only a 4-digit table summary existed. This is the defect class the policy prevents.

**Implementation:** Every eigenvalue computation output MUST be saved as a `.json` file alongside the report, containing the eigenvalue array (complex) and residual norms at ≥12 significant digits. The JSON file must be in the work directory. The seal's manifest should contain the JSON files.

**This enters the next seal** (v1.6).

---

## 3. C1 EXCLUSION LIST

Fixed and versioned in the repo at `known-bad-specs/C1-exclusion-list.yaml`.

**Content:**

```yaml
# C1 — Prose-table number mismatch
# Exclusion list: numbers that appear in prose but are NOT expected to
# have a corresponding table cell value.
# Additions are ledger entries, not open-ended context rules.

exclusions:
  - value: 1024
    reason: "Resolution parameter N — declared at top of report, not a table result"
  - value: 2048
    reason: "Resolution doubling parameter — declared not tabulated"
  - value: 20
    reason: "Domain half-length L — declared not tabulated"
  - value: 40
    reason: "Domain size sweep parameter — declared not tabulated"
  - value: 80
    reason: "Domain size sweep parameter — declared not tabulated"
  - pattern: '\b\d+e[+-]?\d+\b'
    reason: "Scientific-notation tolerance values — declared not measured"
  - pattern: 'T-\d+'
    reason: "Run timestamp — not a quantitative result"
```

**Rule:** Exclusions are versioned in the repo. Any addition = ledger entry with justification. No open-ended context rules.

---

## 4. LEG A — TYPED OBSTRUCTION

### Obstruction: FOUR METHODS IMPOSE PARITY, ONE IMPOSES A METRIC, NONE IMPOSES THE DOMAIN

All candidates tested for the origin-H² construction (`X = {φ: φ odd, φ, φ'' ∈ L²(0,∞), φ(y) = a₁y + o(y) as y→0}`) fail to impose the **domain restriction** — each either imposes a subset of elements (parity only) or changes the spectral problem entirely (metric weighting).

| # | Method | Elements imposed | Failure mechanism | Measured |
|---|--------|-----------------|-------------------|----------|
| 1 | Parity projection P=(I−R)/2 | (a) ODD only | Strip persists at full L² strength — domain norm and origin regularity not enforced | Strip eigenvalues 18 at L=20, count unstable 28→60 under N doubling |
| 2 | Half-domain restriction with odd extension | (a) ODD only | Center artifacts from Fourier grid's periodic boundary — origin condition φ(0)=0 not cleanly imposed | Buggy output, center artifacts in eigenfunctions |
| 3 | Center-point row φ(0)=0 | (a) ODD only | Spurious null vector (mass 1.0 at x=0) — constraint row creates a degree of freedom rather than removing one | λ=0 eigenvector is the constraint row's null space |
| 4 | Full-grid odd projection (Pv = (v(x)-v(-x))/2) | (a) ODD only | Truncation convergence to λ=1 as 1/L (L=20→40→80), λ=1 absent at finite L — spectral content spreads across domain, boundary truncation of Hilbert kernel | λ≈0.940 at L=20, residual 0.008, convergence ~1/L |
| 5 | H²-weighted generalized EVP M = I + (D²)ᵀD² | (a)(b)(c)(d) ALL enforced **as a metric** | M ≈ I + k⁴ CRUSHES spectrum toward 0 — smoothness-weighting ≠ domain restriction. φ₀ eigenvalue crushed to −0.047 (|λ−1|=1.047), H² strip reduced from 18 to 1 but not eliminated | A1: near1=0.9997 FAIL, A5: |λ_φ₀−1|=1.047 FAIL |

### Positive result: the converging instrument

Despite the obstruction, the Fourier domain truncation on the odd-projected operator DOES converge:

| Measurement | L=20 | L=40 | L=80 | Limit |
|-------------|------|------|------|-------|
| φ₀ eigenvalue (λ→1) | 0.9403 | 0.958 | ~0.97 | 1.0 (as 1/L) |
| |λ−1| | 0.06 | 0.04 | ~0.03 | 0.0 |
| y·Ω' eigenvalue (λ→0) | 0.015 | ~0.008 | ~0.004 | 0.0 |
| Strip count (odd-projected) | 18 | 18 | 18 | 18? (stable, artifact) |

The convergence is **1/L (boundary-dominated)**, consistent with the periodic Hilbert kernel discrepancy — not a construction bug.

### The strip: genuine spectrum of the maximal L² realization

The naive (maximal-L², no parity) realization produces 28 (N=1024) to 60 (N=2048) strip eigenvalues with Re∈(−½,0) and Im∈[−14.97, +14.82]. These are genuine spectrum of the **wrong realization** — the unconstrained L² operator on a finite periodic domain — not spectral pollution. The strip eigenvalues are localized near the boundary but are real eigenvalues of the discretized operator, confirmed by:
- Resolvent norm < 10² (genuine eigenvalues, not noise)
- m_out (|x|>L/2) = 0.217 average — less localized than point spectrum but not pure boundary artifact
- Count is NOT stable under N doubling (28→60), consistent with essential spectrum discretization

### Untried candidates

| # | Method | Elements it would impose | Untried because |
|---|--------|------------------------|-----------------|
| 6 | H² constraint rows at origin (algebraic constraints, not metric weighting) | (a)(c)(d) — oddness via projection + φ(0)=0 + φ'(0) bounded via row insertion | Requires modifying the linear system's null space directly. Would impose domain elements without crushing the spectrum. Could work but needs engine rewrite — constraint-row construction for the biharmonic norm's boundary terms at x=0 |
| 7 | Exterior mesh (tanh clustering) | (a)(c)(d) — odd parity preserved, tanh clustering concentrates grid points near origin to resolve φ'' and φ(y)=a₁y+o(y) | Requires coordinate transformation of the operator — non-trivial rewrite of the Fourier discretization. Tanh mapping changes the Hilbert kernel and the Fourier basis |
| 8 | Mellin/log-radial mapping | (a)(c)(d) — maps x∈(0,∞) to τ=log∈(−∞,∞), converts dilation-invariant operator to translation-invariant in log coordinate, making the origin condition regular | Deferred at fork (Fourier stays). The Mellin transform would replace the Fourier basis entirely. Requires new engine |

### LEG A COMPUTE STOPPED

No further compute on Leg A. Candidates 6,7,8 are UNTRIED with documented reasons. The obstruction is typed and filed.

---

## 5. OUTPUT-PRECISION POLICY ENTRY

Registered as a standing policy in the REPO. This report's closure entry is the registry object.

```yaml
id: OL-PREC-001
name: output-precision-binding
description: >-
  Eigenvalues, residuals, and spectral distances must be stored at >=12
  signficant digits in machine-readable JSON files alongside every report.
entation: 2026-09-09
origo: A1/A5 reconciliation showed 4-digit precision only for H2 eigenvalues
implementation: Every eigenvalue computation produces a .json file in work/
  containing the eigenvalue array (complex) and residual norms.
entry_into_seal: v1.6
```

---

## 6. RE-SEAL — v1.6

A new MANIFEST.sha256 will be produced from the current HEAD plus the new
files (this report, policy registrations). The freeze hash will be published
to the existing gist (6b6d2d4265ffe5b63ab6a54a603ca05) as v1.6.

**Fonder must publish the new freeze hash to the gist before any compute
on LEG B or a resumed leg A approach.**

---

TERMINAL: LEG-A-CLOSED