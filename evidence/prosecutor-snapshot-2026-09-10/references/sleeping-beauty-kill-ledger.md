# Sleeping-Beauty Revival Detector — Kill Ledger

**Status:** SHUTTERED (7 frames killed, pre-registered gate not met).
**Target:** Detect catalyst/technology claims that were foreclosed by a barrier
that has since dissolved — a sleeping-beauty detector.
**Domain attempted (final frame):** Exoplanet prediction papers (1952-2009)
with named precision thresholds, dormant then load-bearing cited post-capability.

## Dead lines (7 frames killed)

### Frame 1: MACE-verifiability conditioning
**Killed by:** Construct invalidity. Electrocatalysis barriers are interfacial,
kinetic, under-potential — periodic MLIPs don't measure these.
**Lesson:** The condition that MACE verifiability predicts within-stage error
correlation is false: N_eff was identical (3.00/3) on verifiable and unverifiable
splits. Conditioning claim collapsed to generic ensembling. KILLED.

### Frame 2: T3b N_eff conditioning
**Killed by:** Power (n=20). With only 20 truth labels, N_eff was at ceiling
(3.00/3) on all splits regardless of content. T3/T4 are power-bound at this
sample size. KILLED.

### Frame 3: Electrocatalysis corpus
**Retired:** Descriptively useful (20 papers annotated), inferentially dead.
90/10 barrier_dissolved split collapses model decorrelation to noise.
Recalibration attempt produced 30/70 split but with no clear ground truth.
KILLED.

### Frame 4: #5 barrier-specificity matcher (MP deprecation reversals)
**Killed by:** Formula-matching, not barrier-matching. On 30 MP deprecation
reversals with 10 decoys (right compound, wrong fix), 30/30 SAME on true
restorations but only 3/10 UNRELATED on decoys. Matcher operates at
compound level, not mechanism level. KILLED.

### Frame 5: #5 matcher (drug repurposing, weak decoys)
**Killed by:** Passed but didn't test specificity. Decoys were completely wrong
pharmacology families (COX-2 for thalidomide). 5/6 UNRELATED on decoys.
User rejected — decoys too weak. KILLED (retroactively).

### Frame 6: #5 matcher (drug repurposing, hard decoys)
**Killed by:** Hard decoys exposed matcher's fundamental weakness. 6 decoys
= right drug, real mechanism it has, wrong revival pathway. Only 1/6
UNRELATED (thalidomide → sedation). The remaining 5 were classified
ADJACENT because the matcher sees "real pharmacology of the drug" and
can't distinguish same-target/different-tissue (PDE5), same-receptor/
different-selectivity (SERM), same-class/different-subtype (beta-1 vs beta-2).
KILLED. #5 load-bearing filter dead — Sleeping-Beauty detector loses its
critical gate.

### Frame 7: Exoplanet pilot (read-based)
**Pre-registered gate:** ≥4 obscure load-bearing hits AND rate above baseline.
**Result:** FAIL — 2 verified load-bearing hits (Cumming 2004) from 14 seed
sleepers. Photometric sleepers (Jenkins 1996, Borucki 1984, Rosenblatt 1971)
unverifiable via APIs (ADS, S2, OpenAlex). Gate requirement not met. KILLED.

## What was learned (banked knowledge)

### Hard-decoy design (moved to adversarial-validation skill)
The hardest matcher decoys are "right entity, real attribute, wrong task."
See `adversarial-validation` skill, Hard-decoy design section.

### Reframe-over-commit risk (moved to prosecutor skill)
After 3+ kills of related frames, the next action should be a NEW test,
not a refined spec. See PROSECUTOR skill, Risk: reframe-over-commit section.

### API data walls (exoplanet frame)
- **ADS API:** Token-based. Parentheses URLs need URL-encoding (`citations()` →
  `citations%28...%29`) or HERE-doc Python to avoid shell quoting errors.
  Older papers (pre-1990) and conference proceedings (LPICo) may not be
  indexed at all or have broken citation links.
- **OpenAlex:** Free tier exhausts at ~50-100 requests. Not usable for
  multi-sleeper pipelines without caching/rate-limit budgeting.
- **Semantic Scholar:** Returns 429 aggressively after ~10 sequential calls
  from an unauthenticated IP. With 2s delays, returns ~50-100 calls before
  throttling. Citation context endpoint works but is rate-limited.
- **Google Scholar:** Blocks automated access with "unusual traffic" detection
  even via browser. Not a viable API for multi-paper workflows.
- **Crossref:** Reliable for DOI resolution. Conference proceedings and older
  papers often lack DOIs. Good for abstract retrieval, not citation context.

### Pipelines that survived their kill-tests
- **Cumming 2004** (RV detection limits → HARPS): 2 verified load-bearing cites
  showing equation reuse and threshold value reuse in survey post-processing.
  Genuine sleeping beauty, but one paper doesn't make a detector.