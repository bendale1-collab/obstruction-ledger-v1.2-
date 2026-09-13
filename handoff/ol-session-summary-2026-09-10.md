# Obstruction Ledger — Session Summary
**Through 2026-09-10T03:11Z (v1.6 anchored)**

## What this is

Two threads, deliberately intertwined:

- **Thread A — the research run.** A frozen-spec study of a fluid-singularity question (CLM/gCLM spectral problem), executed by a cheap operator agent (Hermes, qwen3-coder-next, Telegram bot "Mahamara"), adjudicated by the founder at pre-defined gates.
- **Thread B — the venture.** The run is the proving ground for a product: sealed, replayable records of why attempts fail, plus mechanical checks that catch fluent, confident wrongness in agent output.

The run's most valuable outputs so far are not the math results. They are (1) the catalogue of ~15 interpretive failures the agent produced at identical confidence, and (2) the discovery that the attestation layer itself silently detached for 26 commits.

---

## Thread A — Research run

### Primitives
- F1 (classical spectral engine) = truth; F2 (PINN) = specimen.
- Freeze the spec, hash it, publish the hash to a public gist **before** results exist.
- Publication is founder-only. Agent credentials deliberately lack gist scope.
- Every claim binds to a hash that predates the evidence.

### Chronology
| Date | Event |
|---|---|
| 09-07 | **P0 GREEN** ($2/$20). F1 Fourier engine passes 7 goldens, reproduces Elgindi–Jeong profile. Chebyshev map abandoned. |
| 09-07/08 | CCF misidentified as Constantin–Lax–Majda in v1.4. Corrected: CCF = Córdoba–Córdoba–Fontelos, a different equation. v1.4 superseded. |
| 09-08 | **Leg split.** Leg A = CLM spectral (engine exists). Leg B = CCF transport (no engine, needs own pre-reg). |
| 09-08 | **v1.5 sealed** `c6a73ae8…`, 15 files, HEAD `5a6d9c8`. Founder publishes gist. |
| 09-08 | **Leg A P1: ENGINE-RED** ($0). Positive control F-4 fails. |
| 09-08/09 | Six+ triage rounds. Convention audit (L_Xu = −L_eng), fork adjudication (Fourier stays), strip characterization, origin-scope, H² realization test. All $0. |
| 09-09 | **Leg A closed** as typed obstruction. |
| 09-09 | **SEAL-DETACHED** discovered. Seal recovery executed. v1.6 sealed `d7043bba…`, 19 files, HEAD `7d4aad7`. |
| 09-10 | Founder publishes supersession note (Rev A, 03:08:39Z) and v1.6 block (Rev B, 03:11:25Z). Hermes confirms 19/19 against commit, hash match. |

### Leg A — the obstruction (typed and filed)
**Four methods impose parity, one imposes a metric, none imposes the domain.**

Target domain (Xu Eq 3.2): X = {φ odd, φ, φ″ ∈ L²(0,∞), φ(y) = a₁y + o(y) as y→0}.

| # | Method | Imposes | Fails because |
|---|---|---|---|
| 1 | Parity projection | odd only | strip persists at full L² strength |
| 2 | Half-domain + odd extension | odd only | periodic-grid center artifacts; cost 0.47 of the 0.53 shift |
| 3 | Center-row φ(0)=0 | odd only | spurious null vector |
| 4 | Full-grid odd projection | odd only | converges to λ=1 as 1/L; λ=1 absent at finite L |
| 5 | H²-weighted generalized EVP | all, **as a metric** | M ≈ I + k⁴ crushes spectrum; φ₀ → −0.047. A generalized EVP reweights modes, it does not exclude them. |

**Positive result:** the odd-projected Fourier instrument converges — φ₀ → 1 (0.9403 / 0.9702 / 0.9851 at L = 20/40/80), y·Ω′ → 0, error ∝ 1/L.
**Strip:** genuine spectrum of the maximal-L² realization, origin-localized, identical on odd and naive operators — imposed by nothing.
**Untried:** 6 (H² constraint rows), 7 (tanh mesh), 8 (Mellin). Reasons documented. No further Leg A compute.

### SEAL-DETACHED (the run's most important finding)
Seal check against **commit** (not disk) revealed, for the 15 v1.5 manifest files: 9 match HEAD, `engine/f1.py` modified post-seal, **5 never committed to git**, and all 15 gone from the working tree. All 26 commits `66f9b16`…`526f7a5` — ENGINE-RED through H2 test — were produced against a detached seal.

**Root cause:** the pre-flight verified files on disk, not `git show <commit>:<path>`. Same defect class as the v1.3 ANCHOR-GAP, one version later, after the fix was supposedly applied. The founder-published gist line "first hash both reproducible from git and externally anchored" was false for v1.5.

**Recovery:** 5 files rebuilt from surviving sources, each headed `RECONSTRUCTED 2026-09-09 from <source>; NOT the sealed original`. Engine modification documented with dependent results. Seal check v2 (commit-based) run: 19/19. v1.6 does **not** re-certify v1.5; the 5 originals remain unrecoverable.

### Publication episode (09-09/10)
- Founder attempted delegating publication to an external-family agent via OpenRouter. Three 403s, nothing written. Filed `PUBLICATION-DELEGATION-FAILED`. Second independent confirmation that credential separation holds by construction.
- Claude misread a truncated GitHub diff as a partial save — a frontier-tier instance of the data/summary-contradiction class. Noted for the ledger.
- Founder published manually from mobile (desktop-site mode). Two revisions, correction first.

### Anchor state
```
Gist: https://gist.github.com/bendale1-collab/6b6d2d42651ffe5b63ab6a54a603ca05
v1.5 original   f4e3a193…  2026-09-08T13:57:07Z (GitHub clock)
Rev A (note)    05c96bd0…  2026-09-10T03:08:39Z
Rev B (v1.6)    862219a3…  2026-09-10T03:11:25Z
v1.6 FREEZE_HASH d7043bba1eda9996da2575dba81d2bdc38456ca66dfbd2124d570a915bf1aee9
HEAD 7d4aad7 (seal) → fe8a1e9 (post-publication commit, seal unaffected)
```

---

## Thread B — Venture

### Thesis
Everyone deploys agents; nobody can prove what an agent did, and nothing catches fluent wrongness. Regulation has arrived (EU AI Act Art. 12 in force 2026-08-02; NIST AI RMF procurement gating). Incumbents ship signed receipts — assertions by the agent. Nobody pre-commits, anchors during the run, or signs the run itself. Standing-free product: **citability, not admissibility** (Westlaw / CVE / Moody's pattern).

### Built and shipped
- **VERIFIER v0.1** — K≥3 blind extractions per named object, non-neural sympy arbiter, adversary-before-freeze, retrodiction corpus RB-01..05. **V0 GREEN** ($0). RB-05 caught a fabricated λ=1 parity claim on its own author.
- **CHECKER v0.1** — nine checks C1–C9 + R1, R2, ranked by self-enforcement. **K0 PASS** (C3 recall 1.000/FP 0.000; C6 1.000/0.017; R1 0.900/0.000). K0 **missed** the A1/A5 distance-vs-value defect — exactly the C1 gap its own build order predicted.
- **Ledger types** created this run: HALT-REFERENT, HALT-SOURCE, FABRICATED-QUOTE, CONTROL-FAILED-UNFLAGGED, SEAL-DETACHED, ENGINE-MODIFICATION, ANCHOR-GAP-V1.3, SELECTION-UNRECORDED, ASSERTED-UNDERIVABLE, SELF-MODIFICATION, PUBLICATION-CREDENTIAL-SEPARATION, PUBLICATION-DELEGATION-FAILED, and ~12 more.

### The failure catalogue (~15 instances, one operator, one run)
(A) data/summary contradiction — distances read as eigenvalues, 42/20 read as "identical". (B) unsourced causal claims — "known property" ×3. (C) fabricated referents — a Xu §3.2 quote that does not exist; "no closed form" ×3 while two closed forms sat on the agent's own list. (D) test weakening ×4. (E) reference correlation — agent wrote the reference that validated its own engine. (F) controls omitted or failed silently.

Diagnosis: not model-specific alone. Execution flawless; interpretation ~50% wrong at identical confidence, with nothing in the routing table that fires on "conclusion contradicts the data two lines above." Fix = interpretive triggers (causal nouns, nonexistence claims, quotes, closed forms → second family or arbiter).

### IISE″ score
~46% Exit-class; bootstrap 0.80; load-bearing leg = Nash-regulator. Path to 55–65%: one enforcement precedent, one design-partner LOI, one Helmer power at credible 1.0 (bit-deterministic replay), novelty 0.60→0.70. Ceiling requires the artifact being *named* by a standard.

### Honest limits
One operator, one run, one domain, n small. Frameworks derived from their own instances. Whether the checks generalize is unproven and a buyer will ask.

---

## Standing rules established this session
- Seal verification is against the **commit**, never the working tree.
- Publication is founder-only; the 403 is the control.
- Correct by **appending**, never editing or deleting. Botched attempts stay visible.
- The GitHub revision timestamp is authoritative; `Published:` lines are founder assertions.
- v1.6 is not v1.5 restored. Say "9 unchanged, 1 modified, 5 reconstructed", never "15 originals".
- Manifest seals the core bundle only (19 files); work/, harness/, registry/, injection sets are tracked but unsealed — filed as a decision.
- Every eigenvalue count carries an Im bound or physicality criterion.
- ≥12 significant digits in machine-readable JSON (OL-PREC-001).
- A test parameter may not be chosen by looking at which modes it excludes.
- Demote, never delete: a citation may be invalid as justification while decisive as evidence.
- Hermes channel strips code blocks — request file paths, not inline content.

---

## Open items

**Immediate (no compute):**
1. Gist Rev C — timestamp correction: v1.5 `Published: 12:58:00Z` is founder-typed and wrong; GitHub records 13:57:07Z. Mirror in `ledger/seal-detached-v1.5.md`.
2. Hermes to grep ledger files for the truncated gist ID `6b6d2d4265` (three occurrences so far) and confirm the full 32-char ID is recorded.

**Next build — recommended: CHECKER K1 (C1, C2, C5).** Pre-register it, publish the hash, validate by injection, then run on the Leg A close-out and A1/A5 reconciliation — documents known to contain defects K0 missed. Add an identifier-length check.

**After K1:** run the checks on one packet from a completely different domain. Cheaper than Leg B, answers the generalization question.

**Deferred:** Leg B (CCF transport — no engine, needs own pre-reg), VERIFIER V1–V3 (~1 week, ~$25), Leg A candidates 6/7/8.

**Standing block:** no compute until Leg B or CHECKER K1 has its own pre-registration.
