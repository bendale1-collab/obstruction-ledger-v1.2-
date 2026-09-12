#!/usr/bin/env python3
"""
C RE-RUN — cohort-relative citation death. Replaces the two bad defs:
  BAD1: lifetime <=2 cites        -> measures never-had-traction (noise)
  BAD2: absolute 0 in last 3yr   -> measures aging, not abandonment (base decay)

FROZEN DEF (abandoned-for-cause):
  (a) EARLY TRACTION: >=5 cites in first 3 yrs post-publication  (it lived)
  (b) RELATIVE DECLINE: recent-window citation share fell STEEPER than the cohort
      median decline for the same publication year (it died faster than peers age)
  (c) ABS_DEAD floor: recent-window share < 0.05 (genuinely near-dead, not aging)
  All three required. (a) without (b/c) = still-cited. (b/c) without (a) = never-lived.

Cohort curve is built ONCE here and reused by T2. Agent computes, decides nothing.

  python rerun_C.py --topic T10030 --pubyear 2012 --out ./corpus_out
"""
import argparse, json, sys, time, traceback, urllib.request, urllib.parse
from pathlib import Path
import numpy as np

OPENALEX = "https://api.openalex.org/works"
# ---- FROZEN ----
EARLY_YRS = 3
EARLY_CITE_FLOOR = 5          # (a) real traction, guards against dead-cohort low bar
RECENT_YRS = 3                # trailing window for decline
ABS_DEAD = 0.05               # (c) absolute floor: recent-share < this = near-dead
# Rule = ABS_DEAD AND below cohort median. Absolute kills age-decay artifacts;
# cohort kills dead-cohort false positives. Intersection => count is data-driven.
# ----------------

def log(m): print(f"[C] {m}", flush=True)
def emit(out, s): (Path(out) / "C_state.json").write_text(json.dumps(s, indent=2))

def get_json(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "orphan-gate/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            last = str(e); time.sleep(2 ** i)
    raise RuntimeError(f"GET failed {tries}x: {url} :: {last}")

def counts_by_year(work):
    return {c["year"]: c["cited_by_count"] for c in work.get("counts_by_year", [])}

def decline_ratio(cby, pubyear):
    """recent-window share of a work's own citations. Lower = more declined."""
    total = sum(cby.values())
    if total == 0: return None
    now = 2025
    recent = sum(v for y, v in cby.items() if y > now - RECENT_YRS)
    return recent / total

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--pubyear", type=int, required=True)
    ap.add_argument("--out", default="./corpus_out")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    state = {"topic": a.topic, "pubyear": a.pubyear, "status": "PENDING",
             "def": {"early_yrs": EARLY_YRS, "early_floor": EARLY_CITE_FLOOR,
                     "recent_yrs": RECENT_YRS, "abs_dead": ABS_DEAD,
                     "rule": "early>=floor AND recent_share<abs_dead AND recent_share<cohort_median"},
             "cohort_median_decline": None, "count": 0, "blocker": None}
    emit(out, state)
    try:
        works, cursor, pages = [], "*", 0
        filt = f"topics.id:{a.topic},from_publication_date:{a.pubyear}-01-01,to_publication_date:{a.pubyear}-12-31"
        while cursor:
            q = urllib.parse.urlencode({"filter": filt, "per-page": 200, "cursor": cursor,
                                        "select": "id,publication_year,cited_by_count,counts_by_year"})
            d = get_json(f"{OPENALEX}?{q}")
            works.extend(d.get("results", []))
            cursor = d.get("meta", {}).get("next_cursor")
            pages += 1; state["pages"] = pages; state["fetched"] = len(works); emit(out, state)

        early_ok, declines = {}, {}
        for w in works:
            cby = counts_by_year(w)
            early = sum(v for y, v in cby.items() if y <= a.pubyear + EARLY_YRS)
            dr = decline_ratio(cby, a.pubyear)
            wid = w["id"]
            early_ok[wid] = early >= EARLY_CITE_FLOOR
            if dr is not None: declines[wid] = dr

        traction_declines = [declines[w] for w in declines if early_ok.get(w)]
        if len(traction_declines) < 20:
            raise RuntimeError(f"Only {len(traction_declines)} works clear early-traction floor; "
                               f"cohort median unstable. Lower floor or widen pubyear.")
        med = float(np.median(traction_declines))
        state["cohort_median_decline"] = round(med, 4)

        # abandoned = traction AND recent-share < ABS_DEAD AND < cohort median
        dead = sorted(w for w in declines
                      if early_ok.get(w) and declines[w] < ABS_DEAD and declines[w] < med)
        (out / "C_ids.json").write_text(json.dumps(dead))
        state["count"] = len(dead); state["status"] = "COMPLETE"; emit(out, state)

        (out / "C_REPORT.md").write_text(
            f"# C (cohort-relative citation death) — counts only\n\n"
            f"Corpus {a.pubyear}/{a.topic}: {len(works)} works\n"
            f"Cleared early-traction (>= {EARLY_CITE_FLOOR} in {EARLY_YRS}yr): {len(traction_declines)}\n"
            f"Cohort median recent-share: {med:.3f}\n"
            f"**Abandoned (traction + recent_share<{ABS_DEAD} + below cohort median): {len(dead)}**\n\n"
            f"vs BAD1 (<=2 lifetime): different population — this is died-after-living,\n"
            f"not never-lived. Cohort median cancels base age-decay.\n\n"
            f"> Counts only. Human authors gate. Cohort curve reused by T2.\n")
        log(f"done. corpus={len(works)} traction={len(traction_declines)} abandoned={len(dead)} med={med:.3f}")
        sys.exit(0)
    except Exception:
        state["fatal"] = traceback.format_exc(); state["status"] = "FATAL"; emit(out, state)
        (out / "C_ERROR.txt").write_text(state["fatal"])
        log("FATAL — C_state.json + C_ERROR.txt. No count fabricated."); sys.exit(2)

if __name__ == "__main__":
    main()