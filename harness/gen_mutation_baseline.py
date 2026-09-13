#!/usr/bin/env python3
"""Runs mutmut once against ol/ and records the baseline kill rate.

manifest/ is outside this harness's edit boundary, so the baseline lives
at harness/mutation-baseline.json instead of
manifest/mutation-baseline.json.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent / "mutation-baseline.json"
SUMMARY_RE = re.compile(r"(\d+)/(\d+)")


def run_once() -> dict[str, object]:
    result = subprocess.run(
        ["mutmut", "run"],
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr
    match = SUMMARY_RE.search(output)
    if match:
        killed, total = int(match[1]), int(match[2])
        kill_rate: float | None = killed / total if total else None
    else:
        killed, total, kill_rate = 0, 0, None
    return {
        "mutants_killed": killed,
        "mutants_total": total,
        "kill_rate": kill_rate,
        "threshold": 0.70,
        "producing_cmd": "mutmut run (via harness/gen_mutation_baseline.py)",
    }


def main() -> int:
    baseline = run_once()
    OUTPUT.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
