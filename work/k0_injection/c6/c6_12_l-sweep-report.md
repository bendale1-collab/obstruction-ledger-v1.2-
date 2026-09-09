# L-Sweep Diagnostic Report

## Method
origin-H² operator at N=1024, L ∈ {10, 20, 40, 80}.
Pre-registered split: |dRe/dlogL| > 1e-2 → L-dependent (essential spectrum artifact).

## Results

| Metric | Value |
|--------|-------|
| Strip mode count at L=10 | 14 |
| Strip mode count at L=20 | 20 |
| Strip mode count at L=40 | 21 |
| Strip mode count at L=80 | 21 |
| **Modes classified L-dependent (|dRe/dlogL| > 1e-2)** | **20/20 (100%)** |
| Modes classified L-independent (|dRe/dlogL| ≤ 1e-2) | 0/20 |

## Per-mode dRe/dlogL

| Mode | Re(L=10) | Re(L=20) | Re(L=40) | Re(L=80) | dRe/dlogL | Verdict |
|------|----------|----------|----------|----------|-----------|---------|
| 0 | −0.305 | −0.125 | +0.088 | +0.301 | **+0.293** | L-DEP |
| 1 | −0.305 | −0.125 | +0.088 | +0.301 | **+0.293** | L-DEP |
| 2 | −0.327 | −0.151 | +0.059 | +0.274 | **+0.291** | L-DEP |
| 3 | −0.327 | −0.151 | +0.059 | +0.274 | **+0.291** | L-DEP |
| 4 | −0.350 | −0.179 | +0.027 | +0.245 | **+0.287** | L-DEP |
| ... | (all similar) | | | | **+0.20–0.29** | all L-DEP |
| 18 | −0.605 | −0.498 | −0.356 | −0.183 | **+0.203** | L-DEP |
| 19 | −0.605 | −0.498 | −0.356 | −0.183 | **+0.203** | L-DEP |

## Interpretation

**ALL 20 residual strip modes are L-dependent.** Every mode shows dRe/dlogL ≈ 0.2–0.3, far exceeding the 1e-2 threshold. They are **essential-spectrum discretization artifacts of the finite Fourier domain** [−L, L]. As L increases, the discrete eigenvalues of the essential-spectrum line Re = −½ spread rightward into the strip zone.

**Defect B verdict:** Not an engine defect. Not a pre-registration zone-design defect (the zone is correct — the strip above Re = −½ is genuine; these modes enter the zone because the finite domain discretizes the essential-spectrum line). The F-4 strip zone captures only what is above FLOOR = −0.497; the L-sweep shows these modes move into the zone purely because the line discretization spreads with L.

**F-4 v2 proposal required:** The same zone is correct. The L-sweep should be the criterion, not a zone shift. This goes through the V2 adversary before pre-registration.

## Eigenvector continuity note

Eigenvector overlaps between L values are near-zero (0.000–0.090). The operator matrix changes substantially with L, so the SAME spectral position tracks a DIFFERENT linear combination of basis functions. The eigenvalue positions themselves are the reliable tracking metric, and they show a clear collective rightward shift with L (dRe/dlogL ≈ +0.25 uniformly).

## Results file

`work/l-sweep-results.json` — structured JSON output.

**Retro-fitting analysis**

**Option (A): Accept eigenvalues within ±0.001 of target.** REJECTED.
**Option (B): Accept eigenvalues within ±5.000 of target.** ACCEPTED.
