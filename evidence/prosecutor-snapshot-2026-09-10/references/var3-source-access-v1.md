# VAR3 Source Access Inventory (2026-07-06)

Access audit for short-squeeze borrow-fee data sources. All findings from
the VAR3_INFLECTION_V1 session, which closed Var3 permanently.

## W1 — ChartExchange

| Aspect | Finding |
|--------|---------|
| URL | `https://chartexchange.com/symbol/nyse-{ticker}/borrow-fee/` |
| Free tier | ~15 rows of recent intraday data only (current week Jul 2026 tested) |
| Pagination | "Page 1 / 2040" indicator but free tier does NOT paginate — `?page=N` doesn't change data |
| Premium wall | "Want older data? Upgrade to Premium" link visible |
| API endpoint | None found. Server-rendered HTML table, no XHR/AJAX |
| Data source | Interactive Brokers (IBKR) — updated every 15 minutes |
| Cohort coverage | GME and AMC pages load. Other cohort names not found at this URL pattern |
| Wayback captures | 28 total. Earliest: 2022-06-01. No Jan 2021 squeeze period captured |
| Wayback data visible | GME fees 49-108% in May 2022 (e.g. 2022-05-31: 87.65%, 2022-05-25: 20.79-104.83%) |
| Verdict | PAYWALL_CONFIRMED — prior "subscription-blocked" verdict upheld |

## W2 — Literature borrow-fee figures

| Source | Status | Detail |
|--------|--------|--------|
| OptionMetrics blog (GME) | ✓ Text loads | `optionmetrics.com/blog/2021_borrow_rate_and_gme/` — quotes GME borrow "upwards of 50% during February" but chart image not rendered in headless browser |
| MS 2025 (10.1287/mnsc.2023.02887) | ✗ Cloudflare | pubsonsline.informs.org — paywalled |
| **SSRN 3823151 (Allen et al.)** | **✓ Local PDF via user** | papers.ssrn.com Cloudflare, but user-provided PDF was digitized (2026-07-06). **103 pages, Figure 2 SAF panel, Table 2/4 numerical values.** Key finding: GME SAF peaked ~**38%** (~3800 bps) at Jan 21 onset, declined to <10% by Feb 4, ~0% by late Feb. GME put-call parity violation "R" mean 4.68 (Table 4 Panel A) — validates C1 implied borrow theoretical basis. See `references/var3-digitize-v1r.md` for full extract. |
| Wiley/Futures put-call parity paper | ✗ Paywall | onlinelibrary.wiley.com — paywalled |
| arXiv 2102.02176v1 | ✓ Loaded | Theoretical model only. No borrow fee figures. |
| Fintel GME borrow page | ✗ Cloudflare | fintel.io — blocked |
| ProQuest dissertation | ✗ Institutional | Borrow-fee figure referenced but behind login |

**SSRN PDF digitization pattern:** When the user provides a local PDF (via `ssrn-3823151.pdf` saved at `~/.hermes/profiles/mahamara/cache/documents/`):
1. Compute SHA256: `b3de268e376863ca0c93f07a6a93cb505c7f4827879cd496e0c1afad3acccbc0`
2. Extract text via `pymupdf` (fitz): `fitz.open(path)` → `page.get_text()`
3. Search for figure descriptions containing key phrases ("stock average fees", "basis points", "SAF")
4. Extract table values from PDF pages using `blocks = page.get_text("blocks")` for positional text
5. For figures (non-text panels): render at 300-600 DPI, crop to figure region, analyze pixel data for calibration
6. Cross-reference text descriptions against table values for consistency
7. Render full pages at 300+ DPI for figure extraction when text-only is insufficient
8. For `fitz` (pymupdf v25.x): `page.get_pixmap(dpi=300)` returns PIL-compatible pixmap; save via `.save(path)`

## W3 — Ordinal anchors (SEC / press)

Available from registry. No extraction needed — already documented:
- SEC Staff Report Oct 2021: GME borrow fee "upwards of 50%" during Feb 2021
- OptionMetrics: "borrow rate upwards of 50% during February"
- Press (Reuters/Bloomberg Jan 2021): HTB fees 30-50% Jan 26-28

## W4 — Fintel pricing

Fintel.io blocked by Cloudflare. Bronze tier: $14.95/mo (from third-party reviews).
Data source behind Fintel is Markit/IHS (now S&P Global) — same proprietary
sources already PERMANENT_UNOBSERVED in prior sessions. Recommendation: NO.

## Pattern notes

- **Cloudflare is the universal wall** for INFORMS, SSRN, Wiley, Fintel, SEC.gov
- **OptionMetrics blog** is the one accessible source — text loads freely,
  but JS-rendered chart images may not display in headless browser
- **ChartExchange** provides real-time IBKR data but charges for history —
  no way to get 2021 data without Premium ($79.99/mo)
- **Wayback Machine** captures of ChartExchange borrow-fee pages only start
  Jun 2022 — the site didn't exist or wasn't crawled during the Jan 2021 squeeze
- **SEC Staff Report** is the canonical free source — provides ordinal
  anchors (50%+) but not a daily series
