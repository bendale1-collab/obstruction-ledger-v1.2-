#!/usr/bin/env python3
"""
CORPUS FETCH — Orphan-Catalyst gate. Agent computes counts, decides nothing.

ANTIFRAGILE = every failure degrades to a LABELED partial artifact + non-zero exit.
Never a fabricated fill, never a verdict. A blocked source is reported AS blocked.
The human reads state.json and authors the gate.

Signals (measured SEPARATELY, intersected — never ORed):
  C = citation death (OpenAlex)          P = patent lapse (USPTO maintenance fee)
Gate candidate = |P ∩ C| >= 30. Script reports; human decides.

  python fetch_corpus.py --class her --citedeath-cutoff-year 2012 --out ./corpus_out
"""
import argparse, json, sys, time, traceback, urllib.request, urllib.parse
from pathlib import Path

GATE_N = 30
OPENALEX = "https://api.openalex.org/works"
CLASS_TOPIC = {"her": "T10030"}
CLASS_CPC   = {"her": ["C25B", "B01J"]}
CITEDEATH_MAXCITES = 2    # OBSOLETE: use rerun_C.py (scripts/) for cohort-relative def

def log(m): print(f"[fetch] {m}", flush=True)
def emit(out, state): (out / "state.json").write_text(json.dumps(state, indent=2))

def get_json(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "orphan-gate/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read().decode())
        except Exception as e: last = str(e); time.sleep(2 ** i)
    raise RuntimeError(f"GET failed after {tries}: {url} :: {last}")

def fetch_citation_death(topic, cutoff_year, out, state):
    dead, cursor, pages = [], "*", 0
    filt = f"topics.id:{topic},from_publication_date:{cutoff_year}-01-01,to_publication_date:{cutoff_year}-12-31"
    try:
        while cursor:
            q = urllib.parse.urlencode({"filter": filt, "per-page": 200, "cursor": cursor,
                                        "select": "id,publication_year,cited_by_count"})
            d = get_json(f"{OPENALEX}?{q}")
            for w in d.get("results", []):
                if w.get("cited_by_count", 0) <= CITEDEATH_MAXCITES:
                    dead.append(w["id"])
            cursor = d.get("meta", {}).get("next_cursor")
            pages += 1; state["C"]["pages_fetched"] = pages
            state["C"]["count"] = len(dead); emit(out, state)
        state["C"]["status"] = "COMPLETE"
    except Exception as e:
        state["C"]["status"] = "PARTIAL"; state["C"]["blocker"] = str(e)
    (out / "C_ids.json").write_text(json.dumps(dead))
    state["C"]["count"] = len(dead); emit(out, state)
    return set(dead)

def fetch_patent_lapse(cpc_list, out, state):
    try:
        raise NotImplementedError(
            "Patent source not wired. Use fetch_P_bigquery.py (templates/) "
            "with a GCP project for BigQuery access.")
    except Exception as e:
        state["P"]["status"] = "DATA_WALL"; state["P"]["blocker"] = str(e)
        state["P"]["count"] = None; emit(out, state)
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="klass", required=True, choices=list(CLASS_TOPIC))
    ap.add_argument("--citedeath-cutoff-year", type=int, default=2012)
    ap.add_argument("--out", default="./corpus_out")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    state = {
        "class": a.klass, "gate_N": GATE_N, "verdict": "NONE (human authors)",
        "C": {"source": "OpenAlex", "topic": CLASS_TOPIC[a.klass], "status": "PENDING",
              "count": 0, "blocker": None},
        "P": {"source": "USPTO maintenance fee", "cpc": CLASS_CPC[a.klass],
              "status": "PENDING", "count": None, "blocker": None},
        "intersection": {"count": None, "meets_gate": None},
    }
    emit(out, state)

    try:
        C = fetch_citation_death(CLASS_TOPIC[a.klass], a.citedeath_cutoff_year, out, state)
        P = fetch_patent_lapse(CLASS_CPC[a.klass], out, state)

        if P is None:
            state["intersection"] = {"count": None, "meets_gate": None,
                "note": "P blocked; intersection UNMEASURABLE. |C| known; gate UNKNOWN, not failed."}
        else:
            inter = C & P
            state["intersection"] = {"count": len(inter), "meets_gate": len(inter) >= GATE_N}
            (out / "intersection_ids.json").write_text(json.dumps(sorted(inter)))
        emit(out, state)

        inter_str = "\u2014" if state["intersection"]["count"] is None else str(state["intersection"]["count"])
        (out / "REPORT.md").write_text(
            f"# Corpus Gate — mechanical counts (no verdict)\n\n"
            f"| set | status | count | threshold |\n|---|---|---|---|\n"
            f"| C (citation death) | {state['C']['status']} | {state['C']['count']} | \u2014 |\n"
            f"| P (patent lapse) | {state['P']['status']} | {state['P']['count']} | \u2014 |\n"
            f"| P \u2229 C | {inter_str} | \u2265 {GATE_N} |\n\n"
            f"meets_gate: {state['intersection']['meets_gate']}  "
            f"(None = unmeasurable, not failed)\n\n"
            f"Blockers \u2014 C: {state['C']['blocker']}  P: {state['P']['blocker']}\n\n"
            f"> Counts only. A human authors the gate GO/NO-GO.\n")
        blocked = state["P"]["status"] == "DATA_WALL" or state["C"]["status"] == "PARTIAL"
        log(f"done. C={state['C']['count']} P={state['P']['count']} "
            f"inter={state['intersection']['count']} \u2014 verdict human-reserved.")
        sys.exit(1 if blocked else 0)
    except Exception:
        state["fatal"] = traceback.format_exc(); emit(out, state)
        (out / "ERROR.txt").write_text(state["fatal"])
        log("FATAL \u2014 state.json + ERROR.txt written. No counts fabricated."); sys.exit(2)

if __name__ == "__main__":
    main()