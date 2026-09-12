# OCC Stock-Loan Endpoint Diagnostic — 2026-07-05

## Result: DATA_WALL — all endpoints return no records

The OCC (Options Clearing Corporation) stock-loan data endpoints are non-functional. All tested
endpoint/parameter combinations return "No record(s) found" for dates spanning 2018-2026.

## Endpoints tested

| Endpoint | Result |
|----------|--------|
| `marketdata.theocc.com/stock-loan-volume` | `reportType=daily&format=csv` → "No record(s) found" |
| `marketdata.theocc.com/stock-loan-bal-by-security` | `format=csv` → "No record(s) found" |
| `www.theocc.com/Market-Data/.../Stock-Loan-Volume` | Cloudflare challenge (unscrapeable) |

## Date formats verified

- `MM/DD/YY` (e.g. `07/02/26`) — accepted by API, returns "No record(s) found"
- `MM/DD/YYYY` — returns "Invalid daily date."
- `YYYYMMDD` — returns "Invalid daily date."

## Key findings

1. **`stock-loan-volume`** requires BOTH `reportType=daily` AND `format=csv`. Without `reportType`, returns "Invalid report type." Without `format=csv`, returns "Invalid Report Format." With both, returns "No record(s) found."
2. **`stock-loan-bal-by-security`** returns CSV when data exists but consistently returns "No record(s) found" for 2018-2026. Content-Type is `application/octet-stream` with `Content-Disposition: attachment; filename=daily-stock-loan-data.csv`.
3. **HTML page** behind Cloudflare — cannot extract form params programmatically.
4. No ticker symbols (AMC, CGC, LCID, TLRY, SPY) were found in any response for any date.

## Alternative sources

- **iBorrowDesk API** — borrow rate data, not loan volume. Free for limited use.
- **IBKR FTP** — `shortstock:anonymous` at IBKR FTP server. Provides FEERATE field. Free, requires FTP client.
- **FINRA OTC transparency** — `api.finra.org` — equity short interest, not stock loan. Public but slow for multi-name pulls (~32h for 52 names).
