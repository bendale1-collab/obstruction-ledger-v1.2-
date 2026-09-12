# Reporting and Mutation Discipline

## When to reference

Any prosecutor-gate report that involves VLM extraction, budget claims, data-availability escalation, or reporting a gate verdict by status instead of content.

## Emit content, not status

A gate whose output is reported as a status word ("complete / authored / passed") is unfalsifiable. Every gate verdict must ship with its reasoning and the evidence that produced it.

**Rule:** Before any call that costs money or bandwidth, emit the $0 artifacts that justify the experiment: prior-art paragraph, N1a statements (instrument's selection criterion + target's defining property + coincidence verdict), ledger with rejected fields and failing tests. These are the kill screens that exist precisely to stop the run before resources are spent. Report them by content, not by reference.

**Correction signal:** If the user asks for content a second time, the first emission was a status word without the content. Do not report a gate by its status.

## Budget arithmetic required

Claims like "well within $8" are prose arithmetic and do not stand. Every budget claim must show:
- Pairs × extractors × tokens per call × price per token, per extractor family, summed to a total
- The arithmetic, not the conclusion
- Separate Arm C (exploratory) from Arms A and B

## Third-wall rule

Data-availability walls are counted. Three walls and the gate is UNTESTABLE — stop and report, do not seek a fourth substrate.

- Wall 1: primary data source unavailable (portal down, URL expired, licence blocked)
- Wall 2: fallback source unavailable
- Wall 3: second fallback unavailable

If the first source fails and a fallback is proposed, the substitution cost must be stated in the report. Register the fallback decision before knowing whether the primary will succeed — a decision made after a failure is a post-hoc choice.

## Mutation gate (VLM pre-test)

Before any VLM-based extraction pipeline runs, test the extractor with maximally obvious breaks:

- 5 synthetic breaks (full-saturation hue flip on masked region)
- Recall < 5/5 → extractor is inert. STOP. Report. Do not proceed.
- The mutation gate tests whether the extractor CAN detect changes at all; the main experiment tests whether it can detect THE RIGHT changes at acceptable false-flag rates.
- Test with the cheapest usable extractor first (e.g. GPT-4o-mini). A passing gate means the class of extractors can do the job; the gate is a property of the instrument class, not the difficulty bucket.

## Background-process env-var rule

Hermes background processes (`terminal(background=true)`) run in a clean environment — they do not inherit shell env vars including API keys.

**Fix:** read `os.environ` fresh inside the function that makes the API call, not at module import time. A module-level `API_KEY = os.environ.get(...)` is evaluated at module import which happens BEFORE the env var is set in a background context.

```python
# WRONG — evaluated at import, empty in background processes
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")  # module level

# RIGHT — read fresh each call
def call_vlm(...):
    key = os.environ.get("OPENROUTER_API_KEY", "")
```

**Diagnosis:** If the request returns 401 "Missing Authentication header" from a background process but 200 from a foreground terminal, the env var was evaluated at import time. Fix by moving the read into the function body.