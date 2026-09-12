# Verification and Disambiguation Protocols

Protocol patterns for verifying cache-based computation and disambiguating composite verdicts. Captured from FCD_VERIFY_20260711 session.

---

## 1. Reproducibility Gate (Q1 pattern)

Before any cache-computed number is banked as authoritative, it must pass the following verification:

1. **Write a self-contained script** that loads all caches, computes the resolved count/output, and prints it. Must not import `requests`, `yfinance`, or any network library.
2. **Run twice, fresh process each time.** Same Python interpreter, same caches.
3. **Confirm byte-identical output.** Compare stdout SHA256 or full diff.
4. If the two runs differ → **HALT**. The pipeline is nondeterministic. Find the divergence source (unsorted dict iteration, random seed, clock dependency, unclosed file handle) before trusting any output.
5. If identical → that count is the **authoritative resolved figure** for the current cache state. State it once, with SHA.

**Standing tell:** If the count has changed across prior reconciliations (due to different cache states, different scripts, different pipeline versions), label it clearly as superseding prior values. Do not sum prior reconciliations — only the current reproducibility gate result is authoritative.

**Implementation example (FCD project):**
```python
# q1_reproducibility.py — self-contained, no network
import json, csv, hashlib
# Load caches, compute resolved count, print + SHA256
# Run: python3 q1_reproducibility.py > /tmp/r1.txt; python3 q1_reproducibility.py > /tmp/r2.txt
# diff /tmp/r1.txt /tmp/r2.txt → empty = byte-identical PASS
```

---

## 2. Cache Completeness Floor Declaration (Q2 pattern)

When a resolved count comes from a partial cache, the number is a **floor**, not a measurement.

To determine whether a cache-computed number is a floor or a measurement:

1. **Enumerate the universe.** How many total items exist to fetch (e.g., FTD tickers minus SEC-resolved = EODHD-eligible).
2. **Count what's cached.** How many entries in the cache, how many with usable data.
3. **Count the gap.** Eligible minus cached = unfetched.
4. **Compute episode/cell coverage of the gap.** Sum episodes attributable to unfetched items.
5. **Assess marginal benefit.** Top-100 unfetched items likely cover a small fraction of remaining episodes. Publish both the marginal benefit and the absolute gap.

**Declaration format:**
```
Resolved: N (X.Y%) — FLOOR, not measurement
Unfetched: M items covering E episodes (Z.Z% of total)
True count unknown until all M items are fetched (~H hours at R req/s)
```

If unfetched > 0, the resolved number MUST be labeled as a floor, with unfetched proportion stated. A floor is not an artifact — it is the correct provisional measure until the drain completes.

---

## 3. Composite Verdict Disambiguation (Q3 pattern)

When a verdict like `NOT_CONFIRMED` or `EPIPHENOMENAL` subsumes multiple distinct outcomes, decompose it before reporting.

**A single NOT_CONFIRMED collapses at least three distinct things:**

| Sub-verdict type | Meaning | Example |
|-----------------|---------|---------|
| `MISS` | Prediction was wrong — specific counterexample found | C8→FAST-or-MEDIUM×EPISODIC×COMMON: all events land in SLOW |
| `SIGNAL_PRESENT_BELOW_THRESHOLD` | The phenomenon exists but detection method is too conservative | T2 control: max z=1.90 in cutover week, 3σ threshold misses it |
| `DISCONFIRMED` | Null hypothesis not rejected (but prediction was explicitly "no effect") | T3: 1/9 cells significant, not all-null |
| `UNDERPOWERED_ZERO_CELLS` | Not enough data to test the prediction at all | T3 would be UNDERPOWERED if no COMMON cells had N≥100 |
| `FLOOR_NOT_MEASUREMENT` | The resolved count is from a partial cache | Q2: 129,759 from top-5,000 tickers, 57,829 unfetched |

**Disambiguation protocol:**
1. List every registered prediction for the study.
2. For each prediction, state the specific observable that would confirm or disconfirm it.
3. Test each independently (do NOT sum-test "is the composite verdict correct").
4. Report per-prediction status as one of the typed sub-verdicts above.
5. Only then aggregate: "X/Y predictions confirmed, Z fixable, W disconfirmed."

**This prevents** a false equivalence where a dead prediction (MISS) and a fixable one (SIGNAL_PRESENT_BELOW_THRESHOLD) are reported with the same label.

---

## 4. Standing Tell — Shifting Reconciliation

When a computed number has changed across multiple reconciliation passes (N1 → N2 → N3 → N4), each moving in the same direction, no single number is yet a measurement.

Protocol:
1. Identify the cause of each shift: cache truncation, different pipeline version, different script, different data source.
2. The current number from the reproducibility gate (Q1) is authoritative only for the CURRENT cache state.
3. Do not defend or explain away the shifts. Report them as: which cache state produced each number, and what caused the change between states.
4. The number stops moving only when: (a) the cache is fully drained, (b) the same reproducibility gate produces the same number on two consecutive network-off runs, and (c) the cache has not been modified between runs.