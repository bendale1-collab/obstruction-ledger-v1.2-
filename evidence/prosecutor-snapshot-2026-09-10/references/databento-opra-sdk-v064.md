# Databento SDK v0.64.0+ — OPRA API changes

**Session discovered:** 2026-07-05 (IMPLIED_BORROW_V1)
**Package:** `databento==0.64.0`, `databento-dbn==0.42.0`
**Python:** 3.9 (macOS, LibreSSL 2.8.3 — harmless NotOpenSSLWarning)

## Import changes

| Old (v0.3x) | New (v0.64.0+) |
|---|---|
| `from databento import HistoricalClient` | `from databento import Historical` |
| `client = HistoricalClient(key=...)` | `client = Historical(key=...)` |
| `from databento.common.enums import Schema` | `from databento import Schema` |
| `from vollib.black import implied_volatility` | `from vollib.black.implied_volatility import implied_volatility` |

## Symbology.resolve — changed interface

**Old (no date params):**
```python
result = client.symbology.resolve(
    dataset="OPRA.PILLAR",
    symbols=["TICKER.OPT"],
    stype_in="parent",
    stype_out="instrument_id",
)
contracts = dict(result.items())  # direct osi->id mapping
```

**New (requires start_date < end_date):**
```python
result = client.symbology.resolve(
    dataset="OPRA.PILLAR",
    symbols=["TICKER.OPT"],
    stype_in="parent",
    stype_out="instrument_id",
    start_date="2022-07-01",
    end_date="2022-08-01",
)
# Response is an ENVELOPE dict, NOT a direct contract map
raw = dict(result.items())
# raw keys: 'result', 'partial', 'not_found', 'message', 'status'
contracts = raw.get('result', {})

# Each OSI maps to a LIST of {d0, d1, s} dicts:
#   "BBBYP220805C00002500": [
#       {'d0': '2022-07-01', 'd1': '2022-08-01', 's': '705229'}
#   ]

# Multiple entries per OSI indicate different active windows.
# Instrument ID = int(entry['s']). Check d0..d1 for target_date:
for osi, val_list in contracts.items():
    for entry in val_list:
        d0 = datetime.datetime.strptime(entry['d0'], '%Y-%m-%d').date()
        d1 = datetime.datetime.strptime(entry['d1'], '%Y-%m-%d').date()
        if d0 <= target_date <= d1:
            inst_id = int(entry['s'])
            break
```

## Stock split adjustment for option IV

**Root cause of Y4 BBBY IV corruption:**

EODHD `adjusted_close` is post-stock-split-adjusted for ALL historical dates. OPRA option contract strikes are PRE-SPLIT. When computing IV from options on a date before a stock split, the underlying price must be the pre-split (raw) close.

| Ticker | Split | Effective Date | Target dates affected | Adjustment |
|---|---|---|---|---|
| BBBY | 1-for-10 reverse | 2022-08-15 | Before 2022-08-15 | EODHD close ÷ 10 |
| GME | 1-for-4 forward | 2022-07-22 | Before 2022-07-22 | EODHD close ÷ 4 |

**Fix:** Before computing IV for any (ticker, date), check for stock splits between `date` and present. Divide EODHD close by cumulative split factor. Preferred alternative: use FTD ZIP PRICE column (col[5] in pipe-delimited format) which reports the actual close without split adjustment.

## OHLCVMsg — direct field access

```python
# CORRECT
r.instrument_id, r.pretty_close

# WRONG (raises AttributeError in v0.64.0)
r.hd.instrument_id  # .hd removed
r.close             # raw integer, not decimal — use r.pretty_close
```

`r.close` returns RAW INTEGER (e.g. 1630000000 for $1.63). Always use `r.pretty_close`.

## Cost estimation

Before calling `timeseries.get_range()`, estimate cost:
```python
cost = client.get_cost(dataset="OPRA.PILLAR", schema=Schema.OHLCV_1D,
                       symbols=inst_ids, start=start, end=end)
if cost > 15.0:
    print(f"COST HALT: ${cost:.2f} exceeds $15 cap"); exit(1)
```

The `.get_cost()` method was available in v0.3x but had a bug in v0.64.0 where `get_cost` attribute isn't on the top-level Historical object — check `h.metadata.get_cost()` or use Databento's cost endpoint directly.

Actual pull: ~$0.0010-0.0015 per (name, date, 6-contracts). 22 events × 2 dates × 6 contracts ≈ $0.40.

## REST API direct pattern (Python SDK hang workaround)

When the Python SDK's `get_range()` hangs on large results or multiple symbols, use the underlying REST API directly via `requests.get()` with HTTP Basic Auth. This is necessary for the per-day tiny-pull strategy when the account has limited prepaid credits.

### Endpoint

```
GET https://hist.databento.com/v0/timeseries.get_range
Auth: HTTP Basic (api_key: "")
Params: dataset, schema, symbols, stype_in, start, end
Response: CSV (header row + data rows)
```

### Python pattern

```python
import requests, csv, io

url = "https://hist.databento.com/v0/timeseries.get_range"
r = requests.get(url, params={
    "dataset": "OPRA.PILLAR",
    "schema": "ohlcv-1d",
    "symbols": ",".join(iid_list),     # max ~10-12 per pull
    "stype_in": "instrument_id",
    "start": "2021-01-04",
    "end": "2021-01-05",
}, auth=(API_KEY, ""), timeout=30)

if r.status_code == 402:
    # account_insufficient_funds — prepaid balance exhausted
    return None, "BUDGET_EXHAUSTED"
if r.status_code != 200:
    return None, f"HTTP {r.status_code}: {r.text[:100]}"

records = list(csv.DictReader(io.StringIO(r.text)))
```

### Price scaling — CSV raw integer format

All price fields (open, high, low, close) in the CSV response are raw integers in **cents × 10^7** format:

- `close = 6300000000` → `6300000000 / 1e7 / 100 = 6.30` dollars
- Two-step division: `/ 1e7` converts to cents, `/ 100` converts to dollars
- Equivalent: divide by `1e9` directly

### `ts_event` format

The `ts_event` field is nanoseconds since Unix epoch stored as an integer string:
```python
ts_ns = int(record["ts_event"])
ds = datetime.utcfromtimestamp(ts_ns / 1e9).strftime("%Y-%m-%d")
```

## Budget reconcile — finding from C1a 2026-07-05

**There is NO billing-history API on Databento.** `/v0/billing.*` and `/v0/user.*` endpoints all return 404. The only way to get usage data is via the web portal at `databento.com/portal` (requires interactive login).

### What API endpoints exist

| Endpoint | Purpose | Notes |
|----------|---------|-------|
| `metadata.list_unit_prices?dataset=OPRA.PILLAR` | List price per schema | Returns e.g. `ohlcv-1d: 600.0`, `cmbp-1: 0.16` |
| `metadata.get_cost` | Estimate per-request cost | **Returns 0.0 on zero-balance accounts — misleading.** |
| `metadata.get_billable_size` | Get available data size in bytes | Returns **available** size, NOT queried/consumed. |

### Unit prices (OPRA.PILLAR historical)

| Schema | $/unit | 
|--------|--------|
| ohlcv-1d | $600.00 (per million records) |
| cmbp-1 | $0.16 |
| cbbo-1s | $2.00 |
| tcbbo | $210.00 |
| trades | $280.00 |
| statistics | $11.00 |
| definition | $5.00 |

### DBEQ.BASIC (equities) historical unit prices

| Schema | $/unit |
|--------|--------|
| ohlcv-1d | $80.00 |
| mbo | $2.00 |
| trades | $16.00 |

### Key finding: `get_cost` underestimates actual billing

`get_cost` returned $0.000125/contract-day for OPRA.PILLAR ohlcv-1d. At $600/1M records, 1 record = $0.0006. Ratio: $0.0006/$0.000125 = 4.8x. `get_cost` does NOT account for all billing factors.

**Practical consequence:** An account with $15 prepaid was exhausted by ~40 successful pulls despite `get_cost`-based estimates predicting only ~$0.14. Real charges may be 5-100x higher.

### 402 detection is the ONLY reliable budget signal

When `get_range()` returns HTTP 402 with "account_insufficient_funds", the prepaid balance is truly exhausted. `get_cost()` returning zero does NOT mean "free" — it means no remaining credits to estimate against.

### Per-day tiny-pull strategy (works when balance > $0)

1. **Resolve ONCE** via `symbology.resolve()` with the full date range (free)
2. **Cache ALL contract metadata** locally: (strike, expiry, type, iid)
3. **Per trading day:** filter cached to near-ATM (±20%), build C-P pairs, pull only those 6-12 IIDs via REST API
4. Each pull ~$0.001-0.008. GME 65 days at 12 ct/day = ~$0.49
5. If the first day's pull returns 402, balance is truly $0 — accept DATA_BUDGET
