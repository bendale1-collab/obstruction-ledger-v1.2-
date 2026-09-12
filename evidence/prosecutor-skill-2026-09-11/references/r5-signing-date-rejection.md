# R5 — Signing-Date Rejection for C4 Events

**Applied when:** Classifying merger/de-SPAC filings from DEFM14A, 8-K Item 1.01, 8-K Item 2.01, 8-K Item 5.07.

## Rule
Dates within 200 characters of any of these phrases in filing text are SIGNING DATES, not event dates — **reject them**:

- "signed"
- "executed"
- "entered into"
- "dated as of"

## Accepted Date Types
Only keep:
- **Meeting date** — "special meeting shall be held on [Date]" (DEFM14A)
- **Vote date** — "stockholders will vote on [Date]" (DEFM14A)
- **Outside/termination date** — "outside date of [Date]" or "termination date of [Date]" (DEFM14A, 8-K 1.01). Reject if date precedes filing by >30 days (signing reference artifact)
- **Consummation/closing date** — "business combination shall occur on [Date]" (8-K 2.01)
- **Record date** — "record date for the meeting is [Date]" (DEFM14A)

## CIK Fallback
When the issuer CIK archive path returns HTTP 503/403:
1. Extract the first 10 chars of the adsh (filing agent CIK)
2. Strip leading zeros
3. Use that as the archive path: `/data/{agent_cik}/{adsh_no_dashes}/{adsh}-index.htm`
This works because EDGAR stores filings under the filing agent's CIK even when the issuer CIK differs (filing-agents like Donnelley/Donnelley Financial file on behalf of the company).

## Extraction Workflow
1. EFTS lookup by adsh → get issuer CIK + verified ticker
2. Index page → discover primary doc filename (NEVER guess)
3. Primary doc text → regex scan for date patterns
4. Apply signing-date rejection (200-char context check)
5. For non-200 responses: 403 = missing UA header; 503 = server transient (retry 1s+); 404 = wrong filename (use index page)