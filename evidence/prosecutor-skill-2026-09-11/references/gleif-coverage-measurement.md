**Note:** The precision guard rule, missing-term audit protocol, negative control
requirement, and staged validation suite pattern are documented in
`references/precision-guard-rule.md` in the same skill. Read that first for the
general methodology; this file covers the specific GLEIF coverage measurement
session.

---

## GLEIF LEI Coverage Measurement

### Context
PC2 (precheck 2) reported 0.0% hop-3 LEI coverage for USAspending awardees —
0 of 1,322 awardee names matched a cached 5,000-record GLEIF slice. This was
recorded as a structural KILL. It was a **sampling artifact**: GLEIF holds
~2.5M active LEIs, a 5,000-record slice is ~0.2% of the register, and the
probability any specific entity appears in a random 0.2% sample is near zero.

### Correct method
Live API lookup against the full GLEIF register, not a cached slice.

### Name normalization
Strip legal-form suffixes from both USAspending and GLEIF names before matching.
The suffix regex must cover abbreviations federal contractors actually use, not
just the full legal forms:

```
corp, co, intl, international, svcs, services, tech, technologies,
sys, systems, assoc, associates, mfg, manufacturing, ent, enterprises,
grp, natl, national, amer, american
```

### Cascade
1. Exact match on raw awardee name (`filter[entity.legalName]`)
2. Fuzzy (fulltext) on normalized awardee name (`filter[fulltext]`)

### Cache
Cache results by normalized name so a rerun after a matcher change costs
nothing for names already resolved. Checkpoint to disk every 100 names.

### Hand-verify sample
15 clean matches, threshold: ≤ 2/15 wrong.

### Result
After three precision filters, clean coverage was 28% of unique names, 45% of
awards — far below the 65% reported by the unfiltered method. The difference
is the precision failure.