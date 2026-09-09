# FORK ADJUDICATION — Terminal Report

**ORDER-ID:** OL-v1.5-P1-FORK
**AUTHORITY:** Founder directive (fork adjudication)
**VERDICT:** FOURIER STAYS. Mellin deferred indefinitely.
**CAP:** $0
**DATE:** 2026-09-08

══════════════════════════════════════════════════════════════════════

## 1. SYMBOLIC verification (ℝ, exact)

| Mode | Expression | L_Xu(φ) | λ_Xu | Status |
|------|-----------|---------|------|--------|
| y·Ω' | y·(y²-¼)/(y²+¼)² | **0** | **0** | ✅ Identically 0 |
| φ₀ = Ω + y·Ω' | −y/(2(y²+¼)²) | **φ₀** | **+1** | ✅ Identically φ₀ |

Both derived algebraically from the profile identity, no quotes needed.

---

## 2. H(φ₀): exact vs FFT, resolving 0.57-vs-0.94

**Exact H[φ₀](y) = (¼ − y²)/(2(y²+¼)²)** (SymPy)

| y | Exact | L=20 FFT | L=20 rel err | L=40 FFT | L=40 rel err |
|---|-------|---------|-------------|---------|-------------|
| 0.5 | **0.000000** | −0.016276 | ∞ (0-crossing) | −0.015518 | ∞ |
| 2.0 | **−0.103806** | −0.105489 | **1.6%** | −0.104726 | **0.9%** |
| 10.0 | **−0.004963** | −0.006119 | **23.3%** | −0.005226 | **5.3%** |

**Resolution:** The "0.57" was RMS relative error of H(φ₀) alone. The "0.94"**FABRICATED_K0_QUOTE_42493**_NONEXISTENT_DOES_NOT_APPEAR_ANYWHERE_"accept within ±0.5" — too wide for a {0,1} spectrum.
**Rejected:** Mellin build — deferred indefinitely; not needed when truncation is bounded.
**Rejected:** Half-domain construction — use full-grid P = (I−R)/2, which is correct.

**Mellin re-opened only if** convergence at L=160+ deviates from the 1/L scaling, or if P1 pre-registration requires accuracy better than 1% at feasible resolution.

---

## 6. Updated RB-05 (derived modes, no quotes)

| Extraction | Expression | Parity | λ_Xu | Source | Status |
|-----------|-----------|--------|------|--------|--------|
| A | dΩ/dξ = (−2+2ξ²)/(1+ξ²)² | **EVEN** | 1 | Xu Eq 3.7 | ✓ |
| B | φ₀ = −y/(2(y²+¼)²) | **ODD** | +1 | Derived (scaling) | ✓ |
| C | y·Ω' = 4y(4y²−1)/(4y²+1)² | **ODD** | 0 | Derived (time-shift) | ✓ |

Arbiter parity check: 1 EVEN + 2 ODD → **HALT-REFERENT** (correct: distinct modes).

**Commit:** `cf218e8` (plus fork-adjudication files pending)

**Script:** `/Users/brukendale/ol-run/obstruction-ledger-v1.2/work/fork-adjudication.py`
**Report:** This file