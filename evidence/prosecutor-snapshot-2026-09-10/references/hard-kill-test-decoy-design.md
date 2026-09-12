# Hard Kill-Test Decoy Design

## The pattern

When testing a matcher/classifier (SAME/ADJACENT/UNRELATED discrimination), the hardest kill uses decoys that are **right target, real mechanism the target exhibits, but the WRONG pathway for the proposition being tested.**

```
DECOY DESIGN
  target:     <the correct entity/claim>
  mechanism:  <a REAL mechanism the target exhibits — not a hallucination>
  pathway:    <the specific proposition being tested — the decoy mechanism
               does NOT explain this pathway, even though it's genuinely
               associated with the target>
```

## Why weak decoys fail the test

A decoy with a *completely wrong* mechanism (e.g. "ACE inhibition" for minoxidil, which minoxidil does not do) is trivially UNRELATED. The matcher doesn't even need to understand the domain — it just pattern-matches "these two things don't go together." This passes the matcher but tells you nothing about whether it can distinguish real barriers from plausible alternatives.

Weak decoys give false confidence. The #5 compound-match matcher on MP deprecation reversals passed 30/30 SAME but only 3/10 UNRELATED on decoys — and was KILLED. But the easy drug-repurposing decoys (wrong pharmacology families) passed. Only when decoys became HARD (real mechanisms the drug HAS, just wrong pathway) did the matcher fail.

## Anchor contamination

Famous/historical cases (thalidomide→myeloma, sildenafil→ED) are CONTAMINATED. The matcher pattern-matches the *familiarity* of the association, not the *mechanism* of the match. A matcher that classifies 5/5 famous anchors as SAME reveals nothing — it's doing biographical association, not mechanism matching.

**Rule:** Judge on decoy rejection ONLY. Ignore SAME rate on anchors. If the decoy rejection rate meets the threshold, the matcher survives regardless of anchor performance. If decoy rejection fails, the matcher is dead regardless of anchor performance.

## Verified failure mode — "same compound" threshold

When the matcher sees target=X + candidate_mechanism=M where M IS a real mechanism of X, it defaults to ADJACENT rather than UNRELATED. This is because compound-level matching dominates mechanism-level matching. The matcher sees "these two things both refer to the same compound" and refuses to say UNRELATED even when M has nothing to do with the specific pathway being tested.

**Workaround:** Force the matcher to reason at the mechanism/pathway level, not the entity level. The probe's test field should explicitly de-emphasize the compound identity: "Ignore that compound X is involved. Does mechanism M explain pathway P?"

## The canonical example

From the #5 drug-repurposing kill-test:

| Decoy | Real mechanism of drug | Used for revival pathway | Verdict needed | Matcher said |
|---|---|---|---|---|
| methotrexate | DHFR inhibition (cancer) | RA (adenosine pathway) | UNRELATED | ADJACENT |
| sildenafil | PDE5-pulmonary vasodilation | ED (PDE5-cGMP in corpus cavernosum) | UNRELATED | ADJACENT |
| minoxidil | K-ATP channel opening (BP) | Hair (sulfotransferase/VEGF) | UNRELATED | ADJACENT |
| raloxifene | SERM-breast antagonist | Osteoporosis (SERM-bone agonist) | UNRELATED | ADJACENT |
| propranolol | beta-1 cardiac blockade | Hemangioma (beta-2 proliferation) | UNRELATED | ADJACENT |
| thalidomide | sedation | Myeloma (anti-angiogenic) | UNRELATED | UNRELATED |

Only thalidomide was caught — because sedation is a *clinical effect* not a *molecular mechanism*, making it easier to distinguish from the revival pathway.

## When to use

- Any kill-test for a classifier/matcher that identifies whether a candidate mechanism solves a problem
- Pre-registered probes where the claim is "this matcher can distinguish barrier-matched from spurious solutions"
- After an initial easy-decoy pass gives a false SURVIVE — immediately dial up to hard decoys on the re-test

## Pre-registration template

```
KILL-TEST: <matcher name>
HARD-DECOY: <target>, REAL MECHANISM: <real_mech>, WRONG PATHWAY: <target_pathway>, NEEDED: <SAME/ADJACENT/UNRELATED>
ANCHOR-CONTAMINATION: <y/n — if y, IGNORE SAME rate on anchors>
THRESHOLD: <count/rate needed on decoys only, e.g. ≥5/6 UNRELATED>
```
