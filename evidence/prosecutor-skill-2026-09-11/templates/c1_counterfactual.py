#!/usr/bin/env python3
"""
C1_COUNTERFACTUAL_TEMPLATE — Implied borrow counterfactual test skeleton.
Pre-register C0 criteria (shape, ordinal anchors, zero-bias control) before
use. See prosecutor SKILL.md "Counterfactual design" section.

Customize:
- SQUEEZE_NAMES, GC_NAMES — the benchmark set
- date windows, IV band, DTE range
- shape template thresholds

Key pitfalls:
- r.ts_event is nanoseconds (int), convert: datetime.utcfromtimestamp(ns/1e9)
- Resolve chain ONCE, pull per-day for near-ATM IIDs only (avoids 402 budget wall)
- OHLCV VWAP may produce C≈P → negative implied borrow on liquid names; use cmbp-1 schema
"""
import json, time, os, hashlib, math, sys
from datetime import datetime, timedelta, date as dt_date
from collections import defaultdict
import numpy as np
import requests
import databento as db
from vollib.black_scholes.implied_volatility import implied_volatility as bs_iv

# ── Frozen config (customize per test) ───────────────────────────────
PROJECT = "/path/to/project"
EODHD_KEY = ""
DATABENTO_KEY = ""
OUTPUT = os.path.join(PROJECT, "c1_results.json")

SQUEEZE_NAMES = ["GME", "AMC", "TSLA"]
GC_NAMES = ["AAPL","MSFT","JNJ","PG","KO","WMT","XOM","JPM",
            "V","UNH","HD","PFE","CSCO","PEP","MRK"]
ALL_NAMES = SQUEEZE_NAMES + GC_NAMES

SQUEEZE_START = dt_date(2020, 12, 1)
SQUEEZE_END   = dt_date(2021, 3, 1)
GC_START      = dt_date(2021, 1, 1)
GC_END        = dt_date(2021, 1, 31)

IV_MIN, IV_MAX = 0.3, 3.0
DTE_MIN, DTE_MAX = 5, 90
BORROW_MIN, BORROW_MAX = -1.0, 5.0
STRIKE_BAND = 0.20  # ±20% of underlying

# ── Helpers ───────────────────────────────────────────────────────────
def sha256_file(p):
    s = hashlib.sha256()
    with open(p, "rb") as f: s.update(f.read())
    return s.hexdigest()

def parse_osi(osi):
    osi = osi.strip()
    if len(osi) < 20: return None
    try:
        return {"expiry": dt_date(2000+int(osi[6:8]),int(osi[8:10]),int(osi[10:12])),
                "type": osi[12], "strike": float(osi[13:].strip())/1000.0}
    except: return None

def trading_days_between(s, e):
    d = s
    while d <= e:
        if d.weekday() < 5: yield d
        d += timedelta(days=1)

def week_anchor(d):
    return d - timedelta(days=d.weekday())

def fetch_fred_rates(start, end):
    """Fetch DGS3MO from FRED. Returns {date_str: rate_decimal}."""
    r = requests.get(
        "https://fred.stlouisfed.org/graph/fredgraph.csv",
        params={"id":"DGS3MO","cosd":start.strftime("%Y-%m-%d"),
                "coed":end.strftime("%Y-%m-%d)"}, timeout=20)
    rates = {}
    if r.status_code == 200:
        for line in r.text.strip().split("\n")[1:]:
            p = line.split(",")
            if len(p)>=2 and p[1].strip() not in ("", "."):
                try: rates[p[0]] = float(p[1])/100.0
                except: pass
    return rates

def get_rate(rates, d):
    ds = d.strftime("%Y-%m-%d")
    if ds in rates: return rates[ds]
    for i in range(1, 31):
        pd = (d-timedelta(days=i)).strftime("%Y-%m-%d")
        if pd in rates: return rates[pd]
    return 0.001

def fetch_split_factor(ticker, start, end):
    """Fetch cumulative split factor from EODHD. Returns 1.0 if no split."""
    r = requests.get(f"https://eodhd.com/api/splits/{ticker}.US",
        params={"api_token":EODHD_KEY,"fmt":"json",
                "from":start.strftime("%Y-%m-%d"),"to":end.strftime("%Y-%m-%d")}, timeout=15)
    if r.status_code != 200: return 1.0
    data = r.json()
    if not isinstance(data, list): return 1.0
    factor = 1.0
    for entry in data:
        s = entry.get("split","")
        parts = s.split(":")
        if len(parts)==2:
            try: factor *= float(parts[0])/float(parts[1])
            except: pass
    return factor

def eodhd_bulk_close(ticker, dates):
    """Bulk-fetch EODHD adjusted_close for a list of dates (one API call)."""
    dates = sorted(set(dates))
    fd = (dates[0]-timedelta(days=10)).strftime("%Y-%m-%d")
    td = (dates[-1]+timedelta(days=1)).strftime("%Y-%m-%d")
    r = requests.get(f"https://eodhd.com/api/eod/{ticker}.US",
        params={"api_token":EODHD_KEY,"fmt":"json","from":fd,"to":td}, timeout=30)
    if r.status_code != 200: return {}
    data = r.json()
    if not isinstance(data, list): return {}
    pm = {}
    for e in data:
        if isinstance(e,dict) and "adjusted_close" in e:
            try: pm[e["date"]] = float(e["adjusted_close"])
            except: pass
    res = {}
    for d in dates:
        ds = d.strftime("%Y-%m-%d")
        for i in range(30):
            cd = (d-timedelta(days=i)).strftime("%Y-%m-%d")
            if cd in pm: res[ds] = pm[cd]; break
    return res

# ═══════════════════════════════════════════════════════════════════════
def run():
    print("C1 — Implied Borrow Counterfactual")
    print(f"  Squeeze: {SQUEEZE_NAMES}, GC: {GC_NAMES}")
    sys.stdout.flush()

    # FRED + splits
    all_start = min(SQUEEZE_START, GC_START)
    all_end = max(SQUEEZE_END, GC_END)
    rates = fetch_fred_rates(all_start, all_end)
    sf_map = {n: fetch_split_factor(n, all_start, all_end) for n in ALL_NAMES}

    c = db.Historical(key=DATABENTO_KEY)
    results = {}

    for name in ALL_NAMES:
        sq = name in SQUEEZE_NAMES
        sd = SQUEEZE_START if sq else GC_START
        ed = SQUEEZE_END if sq else GC_END
        sf = sf_map.get(name, 1.0)
        print(f"\n  {name} ({'SQ' if sq else 'GC'})  {sd}..{ed}")
        sys.stdout.flush()

        tdays = list(trading_days_between(sd, ed))
        ul = eodhd_bulk_close(name, tdays)
        if not ul:
            results[name] = {"status": "NO_UNDERLYING"}
            continue

        # Resolve option chain (one call for full range)
        try:
            rr = c.symbology.resolve(
                dataset="OPRA.PILLAR", symbols=[f"{name}.OPT"],
                stype_in="parent", stype_out="instrument_id",
                start_date=sd.strftime("%Y-%m-%d"),
                end_date=ed.strftime("%Y-%m-%d"))
        except Exception as e:
            results[name] = {"status": "RESOLVE_FAIL", "error": str(e)[:200]}
            continue

        rm = rr.get("result", {})
        if not rm:
            results[name] = {"status": "NO_OPTIONS"}
            continue

        # Parse contracts and build C-P pairs
        contracts = {}
        for osi_key, instr_list in rm.items():
            p = parse_osi(osi_key)
            if p is None: continue
            iid = instr_list[0]["s"] if isinstance(instr_list,list) and len(instr_list)>0 else instr_list
            if isinstance(iid, dict): iid = str(iid.get("s",""))
            contracts[(p["strike"], str(p["expiry"]), p["type"])] = str(iid)

        pairs = defaultdict(dict)
        for (strike, exp_s, cp), iid in contracts.items():
            pairs[(strike, exp_s)][cp] = iid

        # Build pair metadata
        pair_meta = []
        for (strike, exp_s), pair in pairs.items():
            ci, pi = pair.get("C"), pair.get("P")
            if ci and pi:
                try:
                    exp_d = dt_date.fromisoformat(exp_s)
                    pair_meta.append((strike, exp_d, ci, pi))
                except: continue

        print(f"    Contracts: {len(contracts)}, C-P pairs: {len(pair_meta)}")

        # Per-day: filter near-ATM, pull only those IIDs
        borrows_by_date = {}
        for td in tdays:
            ds = td.strftime("%Y-%m-%d")
            ul_price = ul.get(ds)
            if ul_price is None: continue
            r = get_rate(rates, td)

            # Filter near-ATM pairs
            lo = ul_price * (1 - STRIKE_BAND)
            hi = ul_price * (1 + STRIKE_BAND)
            wanted_iids = set()
            day_pairs = []
            for strike, exp_d, ci, pi in pair_meta:
                if lo <= strike <= hi:
                    wanted_iids.add(ci)
                    wanted_iids.add(pi)
                    day_pairs.append((strike, exp_d, ci, pi))

            if not day_pairs or not wanted_iids:
                continue

            # Pull OHLCV for just these IIDs, just this day
            try:
                data = c.timeseries.get_range(
                    dataset="OPRA.PILLAR", schema="ohlcv-1d",
                    symbols=list(wanted_iids), stype_in="instrument_id",
                    start=ds, end=(td+timedelta(days=1)).strftime("%Y-%m-%d"))
                recs = list(data)
            except Exception as e:
                if "account_insufficient_funds" in str(e):
                    print(f"    BUDGET EXHAUSTED on {ds}")
                    break
                continue

            ohlcv = {}
            for rec in recs:
                ts_ns = int(rec.ts_event)
                rd = datetime.utcfromtimestamp(ts_ns/1e9).strftime("%Y-%m-%d")
                ohlcv[str(rec.instrument_id)] = float(getattr(rec,'pretty_close',rec.close))

            # Compute implied borrow for each pair
            vals = []
            for strike, exp_d, ci, pi in day_pairs:
                cc = ohlcv.get(ci)
                pc = ohlcv.get(pi)
                if cc is None or pc is None: continue

                c_act = cc / sf if sf != 1.0 else cc
                p_act = pc / sf if sf != 1.0 else pc
                dte = (exp_d - td).days
                if dte < DTE_MIN or dte > DTE_MAX: continue
                tte = max(dte, 1)/365.0

                if c_act <= 0 or ul_price <= 0: continue
                try: iv = bs_iv(c_act, ul_price, strike, tte, 0, "c")
                except: continue
                if iv is None or not (IV_MIN <= iv <= IV_MAX): continue

                df = math.exp(-r * tte)
                num = strike * df + c_act - p_act - ul_price
                den = ul_price * tte
                if abs(den) < 1e-10: continue
                b = num/den
                if b < BORROW_MIN or b > BORROW_MAX: continue
                vals.append(b)

            if vals:
                borrows_by_date[ds] = {
                    "n": len(vals),
                    "median": round(float(np.median(vals)), 6),
                }

            time.sleep(0.3)

        print(f"    Days with borrow: {len(borrows_by_date)}")

        if not borrows_by_date:
            results[name] = {"status": "NO_VALID_PAIRS"}
            continue

        if sq:
            daily = {ds: v["median"] for ds, v in sorted(borrows_by_date.items())}
            wkv = defaultdict(list)
            for ds, v in borrows_by_date.items():
                wkv[week_anchor(dt_date.fromisoformat(ds)).strftime("%Y-%m-%d")].append(v["median"])
            results[name] = {
                "status": "OK", "type": "squeeze", "sf": sf,
                "n_data_days": len(daily),
                "daily_borrow": daily,
                "weekly": {wk: round(float(np.median(v)),6) for wk,v in sorted(wkv.items())},
                "stats": {
                    "median": round(float(np.median(list(daily.values()))),6),
                    "n_positive": sum(1 for v in daily.values() if v and v>0),
                    "n_negative": sum(1 for v in daily.values() if v and v<0),
                }
            }
        else:
            wkv = defaultdict(list)
            for ds, v in borrows_by_date.items():
                wkv[week_anchor(dt_date.fromisoformat(ds)).strftime("%Y-%m-%d")].append(v["median"])
            weekly = {wk: round(float(np.median(v)),6) for wk,v in sorted(wkv.items())}
            results[name] = {
                "status": "OK", "type": "GC", "sf": sf,
                "n_data_days": len(borrows_by_date),
                "weekly_borrow": weekly,
                "stats": {
                    "median": round(float(np.median(list(weekly.values()))),6),
                    "n_weeks": len(weekly),
                    "n_positive": sum(1 for v in weekly.values() if v>0),
                    "n_negative": sum(1 for v in weekly.values() if v<0),
                }
            }

        time.sleep(1)

    out = {
        "version": "C1_COUNTERFACTUAL_TEMPLATE",
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "params": {
            "squeeze_names": SQUEEZE_NAMES, "gc_names": GC_NAMES,
            "formula": "(K*e^(-rT)+C-P-S)/(S*T)",
            "iv_band": [IV_MIN, IV_MAX], "dte_range": [DTE_MIN, DTE_MAX],
            "strike_band": STRIKE_BAND,
        },
        "results": results,
    }
    with open(OUTPUT, "w") as f: json.dump(out, f, indent=2)
    print(f"\nOutput: {OUTPUT}  SHA256: {sha256_file(OUTPUT)}")

if __name__ == "__main__":
    run()
