# Corpus-Circularity Gate — Sourcing Orphan Catalyst Claims

## When to use

A PROSECUTOR-style thesis requires an external labeled corpus (not LLM-annotated) for validation, but the obvious source (LLM annotation) is circular — you'd bootstrap ground truth from the pipeline you're trying to validate. This reference documents the full resolution path: dual-signal corpus construction + citation-death measurement + evidence reconstruction + label-set sampling.

## The circular-oracle problem

The spec says: "The cheapest fatal test needs a hand-labeled orphan set. Building that set by LLM annotation is the same r≈0.9 judgment task the spec calls suspect." Resolution: use **two external signals, intersected, neither using an LLM**.

### Signal definitions (frozen)

- **C (citation death):** scientific community stopped paying attention. Bibliometric fact, no LLM.
- **P (patent lapse):** commercial entity stopped paying maintenance fees. Legal fact, no LLM.
- **Intersection (P ∩ C):** abandoned-for-cause — both signals agree. Measured separately, intersected (never ORed).

## C — Cohort-relative citation death (replaces two bad defs)

### Bad definitions (rejected)
- **BAD1:** lifetime ≤2 citations → measures *never-had-traction* (noise, dominates sample)
- **BAD2:** absolute 0 in last 3 years → measures *base age-decay* (all old works decline)

### Correct cohort-relative definition
Requires BOTH conditions:

1. **Early traction:** ≥5 citations in first 3 years post-publication (it lived)
2. **Relative decline:** recent-3-year citation share < absolute floor (5%) AND < cohort median for the same publication year

The cohort median cancels base age-decay. The absolute floor ensures the count is data-driven, not a fixed fraction (median cut alone flags ~50% by construction).

### Cohort curve
Built once from all works in the topic for the publication year, then reused by T2 (revival-lag measurement). Key output: `cohort_median_decline` = median recent-share among works with early traction.

### Source
OpenAlex works endpoint with cursor pagination:
```
https://api.openalex.org/works?filter=topics.id:T10030,from_publication_date:2012-01-01,to_publication_date:2012-12-31&select=id,publication_year,cited_by_count,counts_by_year
```
- Use `topics.id:` filter (includes works where topic is primary OR secondary) for broader corpus
- Use `primary_topic.id:` for stricter matching
- `counts_by_year` field gives per-year citation counts for decline calculation
- Avoid `title_and_abstract.search` — rate-limited without API key
- Cursor pagination (`cursor=*`, then use `meta.next_cursor`) — works for full corpus pulls

### Example result (T10030, 2012, HER electrocatalysis)
| Metric | Value |
|--------|-------|
| Corpus | 8,208 works |
| Early traction (≥5 cites in 3yr) | 3,784 |
| Cohort median recent-share | 0.131 |
| Abandoned | **525** (13.9% of traction works) |

## P — Patent lapse via BigQuery

### Problem
The USPTO PatentsView API (`api.patentsview.org`) has been **deprecated** and replaced by `data.uspto.gov` — a JS SPA behind AWS WAF that is not machine-accessible without authentication. Google Patents BigQuery requires OAuth.

### BigQuery solution
Public datasets: `patents-public-data.patents.publications` + `patents-public-data.uspto_oce_assignment.maintenance`.

SQL works as of 2026-07:
```sql
WITH lapsed AS (
  SELECT DISTINCT publication_number
  FROM `patents-public-data.patents.publications`,
       UNNEST(cpc) AS c
  WHERE c.code LIKE ANY UNNEST(@cpc_prefixes)
    AND country_code = 'US'
),
fee AS (
  SELECT patent_number
  FROM `patents-public-data.uspto_oce_assignment.maintenance`
  WHERE event_code IN ('EXP.','EXPX','EXPD')
)
SELECT l.publication_number
FROM lapsed l
JOIN fee f ON REGEXP_REPLACE(l.publication_number, r'[^0-9]','') = f.patent_number
```

### Linkage problem
C yields **OpenAlex work IDs** (paper identifiers like `https://openalex.org/W...`), P yields **US patent numbers**. Direct set intersection is WRONG. A paper↔patent linkage mechanism is needed before intersection is computable. Options:
- OpenAlex `cites:` filter can find citing patents for a work
- Google Patents cross-references
- Author/institution join (messy)
Without linkage, intersection is UNMEASURABLE — do NOT report as 0.

## Evidence reconstruction cascade

For each orphan in the label set, reconstruct foreclosure evidence from cheapest source first:

1. **Citing-context** (OpenAlex `cites:` filter) — WHY THE FIELD MOVED ON lives in the works that CITE the orphan, not the orphan itself. Query:
   ```
   /works?filter=cites:{openalex_id}&per-page=5&sort=cited_by_count:desc&select=title,abstract_inverted_index
   ```
   De-invert the abstract_inverted_index by reconstructing word positions.

2. **Own abstract** — try in order:
   - **OpenAlex** (already fetched above — 27/50 had abstracts on T10030)
   - **Crossref API** (`https://api.crossref.org/works/{doi}` — abstracts via `message.abstract`)
   - **Semantic Scholar** (rate-limited without API key — skip if 429)
   - **Unpaywall** (needs API key)

3. **Residual** — if neither citing-context nor own-abstract yielded evidence, flag `inference_required=true`.

### Silent-orphan fraction (R10/R14 measurement)
The percentage of orphans where evidence must be inferred. **Low residual (<10%) means the pipeline is buildable — evidence is extractable for most orphans.** In the T10030 test, citing-context covered 48/50 = 96%, residual was 4%.

## Label set sampling for hand-labeling

### Stratification
From C_ids (abandoned works), sample N=50 stratified by cited_by_count:
1. Divide the 525 into terciles by total citations
2. Sample evenly from each tercile (floor + distribute remainder)
3. Same seed for reproducibility

### Label schema (human assigns, agent never does)
| Field | Meaning | Values |
|-------|---------|--------|
| `label_foreclosure_reason` | Why abandoned? | synthesis / cost / DFT-intractable / instrument / unknown / ... |
| `label_barrier_dissolved` | Has barrier lifted since? | yes / no / unknown |
| `label_mace_verifiable` | Can MACE adsorption-E check the claim? | yes / no |

The agent fetches citing_context + abstract for each entry; the human reads and assigns labels. This is the truth layer — non-delegable.

## OpenRouter model names (volatile)

OpenRouter model IDs change as providers release new versions. Before running the T3b harness, always verify current model names:

```python
import urllib.request, json
req = urllib.request.Request("https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {key}"})
models = json.loads(urllib.request.urlopen(req).read())["data"]
# Filter to desired lineages
for m in models:
    if any(x in m["id"] for x in ["claude","deepseek","mistral"]):
        print(m["id"])
```

**Known mappings (July 2026):**
- Claude → `anthropic/claude-sonnet-5`
- DeepSeek → `deepseek/deepseek-chat`
- Mistral → `mistralai/mistral-large`

The T3b script auto-falls back to the cached OpenRouter key at `~/.hermes/profiles/mahamara/cache/.or_key_tmp` if `OPENROUTER_API_KEY` env var is unset.

## Key derivatives from the OC22/electrocatalysis domain

- Topic T10030 (Electrocatalysts for Energy Conversion) has ~134k works (2000+), 54k in 2010-2020
- CPC subclasses C25B + B01J map to HER electrocatalysis (human confirmation needed)
- 2012 cohort median recent-share = 0.131 for works with early traction
- 2012 citation-death count = 525 (3-tier criteria: traction + <5% recent + below cohort median)
- Silent-orphan fraction = 4% (48/50 had extractable evidence via citing-context)

## T3b — Adjudicator decorrelation test

After the label set is built, T3b measures whether multiple different-lineage models produce decorrelated foreclosure judgments. If error-correlation is high (N_eff ~1), consensus is one model voting N times — unsafe for unsupervised monitoring.

### Protocol

1. **Seed the truth set:** hand-label ≥20 works from the label set with foreclosure_reason (human only — non-delegable)
2. **Select lineage-diverse models** — at least 3 from different families (Anthropic, DeepSeek, Mistral)
3. **Prompt each model** with the work's title + citing-context abstract, asking for barrier type, dissolution guess, and confidence
4. **Compute split rate:** fraction of works where models disagree on barrier type. High split (>50%) means models have different priors — human audit needed
5. **Compute error-correlation N_eff** (requires ground truth):
   ```
   E = 1 - correctness_matrix  (binary per model per work)
   err_centered = E - E.mean(axis=0)
   C = normalize(err_centered).T @ normalize(err_centered)
   rho = mean_off_diagonal(C)
   N_eff = M / (1 + (M-1) * max(0, rho))
   ```
   Where M = number of models. N_eff ~1 = models share blind spots.

### Pitfalls

- **OpenRouter model names change:** Always query `/api/v1/models` before running. As of July 2026: `anthropic/claude-sonnet-5`, `deepseek/deepseek-chat`, `mistralai/mistral-large`.
- **Model priors differ dramatically:** Claude defaults to `none_apparent` (42%), Mistral to `stability` (66%), DeepSeek to `synthesis` (46%). This inflates split rate but does NOT necessarily mean decorrelation is useful.
- **Confidence calibration varies:** Claude self-reports ~0.40, Mistral ~0.80 despite similar task. Don't use confidence as a quality metric across models.
- **JSON in prompt strings:** If the prompt contains JSON-like `{"barrier": ...}`, Python's `.format()` will try to interpret the curly braces as format placeholders. Use `{{` and `}}` to escape: `{{\"barrier\": one of [...]}}`.

### T3b example results (T10030, 2012, 3 models × 50 works)

| Metric | Value |
|--------|-------|
| Split rate (models disagree) | 82% |
| Models | Claude Sonnet 5, DeepSeek Chat, Mistral Large |
| Claude mean confidence | 0.40 |
| DeepSeek mean confidence | 0.72 |
| Mistral mean confidence | 0.80 |
| T3b N_eff | Needs ≥20 hand-labeled truth works |