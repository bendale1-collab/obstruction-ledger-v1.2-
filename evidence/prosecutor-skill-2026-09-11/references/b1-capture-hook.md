# B1 Capture Hook — Append-Only Named Capture List

The B1 capture hook maintains the live list of names being monitored via iBorrowDesk (daily fee pull) and Tick-236 (daily shortable shares snap).

## Trigger

Any G1 candidate flag event:
- Calendar insert for any class C1-C10
- Deadline falling in the next-60d window
- Manual add (e.g., INUV warrant redemption Jul 1)

## Capture list schema

```json
{
  "ticker": "INUV",
  "add_date": "2026-07-06",
  "status": "ACTIVE",
  "trigger_class": "C8",
  "trigger_deadline": "2026-07-01",
  "trigger_event": "Warrant redemption description",
  "inactive_date": null,
  "last_updated": "2026-07-06T12:00:00"
}
```

## Rules

- **Append-only.** Names are never removed from the list.
- **Dedupe by ticker.** Same ticker from multiple trigger events = one entry (first add_date preserved).
- **Exits flagged INACTIVE** (not deleted). Capture continues for 30 days post-deadline, then stops.
- **Status values:** ACTIVE (being captured daily), INACTIVE (capture stopped, retained for audit), SUSPENDED (temporary hold).
- **Log add_date + trigger_event per name** so the capture origin is auditable.

## Daily workflow

1. Read capture_list.json for all ACTIVE names
2. For each: GET iBorrowDesk `/api/ticker/{T}` + IBKR reqMktData with genericTick 236
3. Append results to daily capture log
4. Check each name's trigger_deadline: if >30 days past, set status=INACTIVE

## Build against calendar

When building initially from an existing calendar JSONL:

```python
for entry in calendar_entries:
    ticker = entry["ticker"]
    if ticker not in seen:
        capture_list.append({
            "ticker": ticker,
            "add_date": today,
            "status": "ACTIVE",
            "trigger_class": entry["class"],
            "trigger_deadline": entry.get("deadline_date") or entry["filing_date"],
            "trigger_event": entry.get("phrase", ""),
            "inactive_date": None,
            "last_updated": datetime.now().isoformat(),
        })
        seen.add(ticker)
```

## Existing names (as of Jul 2026)

- 63-name iBorrowDesk feed active since Jul 2025
- INUV added 2026-07-06 (first forward candidate)
- 66 names from calendar_q4_2025.jsonl coverage audit