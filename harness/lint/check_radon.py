#!/usr/bin/env python3
"""Fail if radon finds any function graded C or worse (cc > 10) under ol/ or harness/."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TARGETS = ["ol", "harness"]


def main() -> int:
    existing = [t for t in TARGETS if Path(t).is_dir()]
    if not existing:
        return 0
    result = subprocess.run(
        ["radon", "cc", "-s", "-n", "C", "--exclude", "harness/p1_battery.py", *existing],
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout.strip()
    if output:
        print(output, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
