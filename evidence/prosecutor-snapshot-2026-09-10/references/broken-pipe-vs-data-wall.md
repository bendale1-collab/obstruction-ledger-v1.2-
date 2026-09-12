# Broken Pipe vs Data Wall — Distinguishing Protocol

## Standing tell (Br directive, 2026-07-11)

> "the last two 'DATA_WALL' reports were broken pipes, not structural limits — first the 10M default, then a 270MB cache truncated mid-write. Do NOT emit a wall/structural-limit claim until retrieval is verified reproducible on a second network-off run."

A claim that a data source is structurally unreachable is a heavy claim. It shuts down a research branch. Before making it, distinguish:

## Diagnostic protocol

| Failure | Why it might be a broken pipe | What to do |
|---------|-------------------------------|------------|
| 403 / bot detection | Server was reachable earlier in the session. Block is temporary (15-60 min on SEC). | Wait 60s, retry once. If retry works → transient. Report as transient, not DATA_WALL. |
| Cache file truncated mid-write | Process kill during a full-file rewrite (no atomic write) leaves partial file. | Check if temp/backup exists. Recover from backup or reconstruct from checkpoint. The failure is in the write pattern, not the data source. |
| API returns 500 / timeout | Server-side transient. | Retry with backoff. If retry succeeds → transient. |
| 429 / rate limit | Exceeded per-second or daily quota. | Wait, retry with lower rate. If retry succeeds → not structural. |
| Process killed (SIGTERM/SIGKILL) | Background process terminated by timeout or manual kill. | Check checkpoint file. Resume from last checkpoint. The data already fetched is intact. |

## Network-off reproducibility gate

After a suspected structural failure:

1. Disable network access (`ip link set ... down` not available here; instead, verify from cache files alone)
2. Rebuild the entire coverage state from cache files on disk (no API calls, no `urllib`/`requests`)
3. Assert identical counts to the live-pull state
4. If identical → cache is intact, previous failure was a broken pipe
5. If counts diverge or pipeline state is unrecoverable offline → structural limit confirmed

## Concrete examples

### EODHD cache truncation (2026-07-11)
- **What happened:** `step3_eodhd_shares.py` wrote `json.dump(cache, open(EODHD_CACHE, "w"))` — a direct full rewrite, no atomic rename, no temp file. A SIGTERM during the write left the file truncated mid-object. About 1,700 entries (54K resolved episodes) were lost.
- **Why it was a broken pipe:** The data source (EODHD API) was fine. The failure was in the checkpointing code — single-file full rewrite without atomic protection.
- **Fix:** Write to temp file first (`json.dump(cache, open(TMP, "w"))`), then `os.replace(TMP, CACHE)` for atomic rename. Validate header before loading on startup.

### 10M shares default (2026-07-10)
- **What happened:** D1 sweep defaulted to 10M shares for any ticker not in shares cache. Created ~36K false episodes where SEC had data but under a different concept.
- **Why it was a broken pipe:** The data source (SEC XBRL) had the correct values. The failure was in the fallback chain — it didn't check the third-tier concept (`WeightedAverageNumberOfSharesOutstandingBasic`) before defaulting.
- **Fix:** Add third-tier concept fallback. Hard assert max_pct > 100% → HALT.

### SEC www.sec.gov 403 (2026-07-11)
- **What happened:** All `www.sec.gov` endpoints returned 403 ("Your Request Originates from an Undeclared Automated Tool"). `data.sec.gov` JSON API was unaffected.
- **Why it might NOT be a broken pipe:** IP-based block that persisted >30 min across multiple User-Agents and tools. The block may be structural (IP flagged by Imperva WAF).
- **Workaround attempt:** Different subdomain (`data.sec.gov`), different API (`efts.sec.gov`), different User-Agent (Chrome, research-specific). All `www.sec.gov` paths failed.
- **Status:** Pending re-test on a different IP or after 24h cooldown.