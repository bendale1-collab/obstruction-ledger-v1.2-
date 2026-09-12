#!/usr/bin/env python3
"""
P via BigQuery — Google Patents public dataset + maintenance_fee_events.
RUN OFF-MACHINE. Needs: pip install google-cloud-bigquery; a Google account;
`gcloud auth application-default login` (BigQuery sandbox, no billing card).

Agent computes counts, decides nothing. Emits P set, then flags the paper<->patent
linkage problem rather than fabricating an intersection.

  python fetch_P_bigquery.py --project YOUR_GCP_PROJECT \
      --cids ./corpus_out/C_ids.json --cpc C25B B01J --out ./corpus_out
"""
import argparse, json, sys, traceback
from pathlib import Path

def log(m): print(f"[P] {m}", flush=True)

# Patent lapse = maintenance fee NOT paid -> expiration for nonpayment.
# USPTO fee-event codes for non-payment/expiry (EXP.*), filtered to CPC subclass.
SQL = """
WITH lapsed AS (
  SELECT DISTINCT publication_number
  FROM `patents-public-data.patents.publications`,
       UNNEST(cpc) AS c
  WHERE c.code LIKE ANY UNNEST(@cpc_prefixes)
    AND country_code = 'US'
),
fee AS (
  SELECT patent_number
  FROM `patents-public-data.uspto_oce_assignment.maintenance`
  WHERE event_code IN ('EXP.','EXPX','EXPD')
)
SELECT l.publication_number
FROM lapsed l
JOIN fee f ON REGEXP_REPLACE(l.publication_number, r'[^0-9]','') = f.patent_number
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--cids", required=True)
    ap.add_argument("--cpc", nargs="+", default=["C25B", "B01J"])
    ap.add_argument("--out", default="./corpus_out")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    state = {"source": "BigQuery", "cpc": a.cpc, "status": "PENDING",
             "P_count": None, "intersection": None, "gate_N": 30, "blocker": None}
    (out / "P_state.json").write_text(json.dumps(state, indent=2))

    try:
        cids_path = Path(a.cids)
        if not cids_path.exists():
            raise RuntimeError(f"C_ids missing: {cids_path}. No fabrication. Halt.")
        C = set(json.loads(cids_path.read_text()))
        if not C:
            raise RuntimeError("C_ids empty. Nothing to intersect. Halt.")

        from google.cloud import bigquery
        client = bigquery.Client(project=a.project)
        prefixes = [f"{c}%" for c in a.cpc]
        job = client.query(SQL, job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ArrayQueryParameter("cpc_prefixes", "STRING", prefixes)]))
        P = {r["publication_number"] for r in job.result()}
        (out / "P_ids.json").write_text(json.dumps(sorted(P)))
        state["P_count"] = len(P)

        # NOTE: C is OpenAlex work IDs; P is patent numbers. Direct set-intersect is WRONG
        state["intersection"] = None
        state["blocker"] = ("C=paper IDs, P=patent numbers. No paper<->patent join wired. "
                            "Intersection UNMEASURABLE until a linkage (patent-to-paper "
                            "citation, author, or DOI-in-patent) is defined. Do NOT read as 0.")
        state["status"] = "P_FETCHED_LINKAGE_MISSING"
        (out / "P_state.json").write_text(json.dumps(state, indent=2))
        (out / "P_REPORT.md").write_text(
            f"# P (patent lapse) \u2014 counts only\n\n"
            f"|P| lapsed US patents in {a.cpc}: **{len(P)}**\n"
            f"|C| abandoned papers: **{len(C)}**\n"
            f"|P \u2229 C|: **UNMEASURABLE** \u2014 no paper\u2194patent linkage.\n\n"
            f"{state['blocker']}\n\n"
            f"> Gate needs the LINKAGE decision, not just P. Human authors next step.\n")
        log(f"P={len(P)} C={len(C)} intersection=UNMEASURABLE (linkage missing). No verdict.")
        sys.exit(1)
    except Exception:
        state["fatal"] = traceback.format_exc(); state["status"] = "FATAL"
        (out / "P_state.json").write_text(json.dumps(state, indent=2))
        (out / "P_ERROR.txt").write_text(state["fatal"])
        log("FATAL \u2014 P_state.json + P_ERROR.txt. No count fabricated."); sys.exit(2)

if __name__ == "__main__":
    main()