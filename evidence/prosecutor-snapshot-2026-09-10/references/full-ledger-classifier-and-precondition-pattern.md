# Full-Ledger Classifier and Precondition Resolution Pattern

## When to use
When running quantitative analysis where a filtered dataset (shares_cache gate, type filter, etc.) structurally excludes known-positive events, requiring a full-ledger rerun with preconditions.

## GATE 0b — Systematic Exclusion Pattern

When a filtered dataset drops known-positive events (C8 hits), trace which filter excluded each. If ==3/5 are excluded by the same filter, the clean set cannot be validated against the only available ground truth.

### Decision options
- **OPTION A** — Full ledger: drop the problematic filter, run on all episodes. Shares_cache gate is especially prone to structural exclusion of smaller-cap C8-type tickers.
- **OPTION B** — Keep clean set, document systematic exclusion. C8 findings cannot be validated.
- **OPTION C** — Revised filter with allowlist. Rejected because allowlist seeded by known positives = outcome-driven sample construction.

### Critical preconditions before full-ledger rerun

**P-A1 — Denominator Contradiction Resolution**
When a max_pct value is reported but the ticker has no shares_outstanding entry, the denominator must be stated exactly:
- Source: ledger construction code (e.g., `get_shares_out()` in d1_resweep_a1.py)
- Logic: ticker IN shares_cache → actual shares value; ELSE → 10,000,000 flat default
- Check if denominator is heterogeneous across the dataset
- Check if SEC companyfacts API can retrieve the real shares for the ticker
- Report the actual vs default shares ratio

**P-A2 — No-Episode Verification**
When an event has no covering episode, verify by checking DATE-RANGE COVERAGE (start <= event <= end), not start-date proximity. The first-pass check using `abs((start_date - event_date).days) <= 30` is WRONG — a long episode starting months before the event still covers it.

## Full-Ledger Instrument Classifier

When running on the full ledger (35K+ tickers vs 652 filtered), the classifier default changes:

| Context | Default for unknown tickers |
|---------|---------------------------|
| Filtered set (652 tickers) | OTHER (conservative) |
| Full ledger (35K+ tickers) | COMMON (OTC/foreign operating companies) |

**Rationale:** The FTD tape covers US equity settlement. Most unknown tickers are foreign/OTC/delisted operating companies, not warrants/units. ETFs are identified by EODHD fundamentals Type="ETF" field. The 3-letter blanket heuristic (e.g., `t[0] in 'IXADFTMRUBPSWCEHKLOGNJY'`) is too broad — use EODHD cache extension instead.

## Episode Date-Range Coverage Audit

When checking if an episode covers a specific event date:
- **CORRECT:** `sd <= event_date <= ed` (date range coverage)
- **WRONG:** `abs((sd - event_date).days) <= 30` (start proximity)

The first-pass code that checked only start proximity produced false negatives for NRGV (2022-08-01) and SMR (2024-11-19) — both had covering episodes that started 104-164 days before the event.

```python
def audit_episode_coverage(ticker, event_date, ledger):
    """Check if any episode's date range covers the event date."""
    rd = p(event_date)
    ticker_episodes = [ep for ep in ledger if ep['ticker'].strip() == ticker]
    covering = [ep for ep in ticker_episodes 
                if p(ep['start_date']) and p(ep['end_date']) 
                and p(ep['start_date']) <= rd <= p(ep['end_date'])]
    return covering
```

## 10M Default Deletion

The 10M flat default for shares outstanding was found in 8 codebase files. All must be replaced with `raise ValueError(...)`:

| File | Lines | Pattern |
|------|-------|---------|
| d1_resweep_a1.py | 37,40,41,49,51 | get_shares_out() returns 10M -> raise |
| d1_full_sweep.py | 35,36,47,49 | Same |
| x1_c8_outcomes.py | 84,243-247,312,314,364-368 | All 10M -> raise |
| gme_warrant_outcomes.py | 106,113 | Same |
| funnel_v4_validation.py | 205 | 10M -> None |
| funnel_v5_validation.py | 90 | get(t, 10M) -> raise if None |
| c8_endogeneity_control.py | 98-99,124,213 | All 10M -> raise |

**Rule:** Missing shares outstanding = episode EXCLUDED with status SHARES_UNAVAILABLE. Never defaulted, never imputed, never interpolated beyond 400-day gap limit.

## SANITY check for shares cache

For each ticker with known values from V2 P-A1(c) (SEC companyfacts):
- ASTS: 290,689,457
- NRGV: 178,246,198
- SMR: 236,754,948
- LUNR: 84,172,557
- PLSE: 69,209,712

Cache values must be within ±20% of these at matching dates. If not, the cache has a structural issue.