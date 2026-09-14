#!/usr/bin/env python3
"""Enforces agent-runbook.md §17d: a green commit needs an earlier red one.

`[<check>] red: <test>` must appear, in commit order, before any
`[<check>] green: <test>` for the same (check, test) pair. This is the
mechanical form of "the test's failure is on record before the code."
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PATTERN = re.compile(r"^\[(?P<card>[^\]]+)\] (?P<kind>red|green): (?P<test>.+)$")


def find_violations(subjects: list[str]) -> list[str]:
    """subjects must be oldest-first."""
    seen_red: set[tuple[str, str]] = set()
    violations: list[str] = []
    for subject in subjects:
        match = PATTERN.match(subject)
        if not match:
            continue
        key = (match["card"], match["test"])
        if match["kind"] == "red":
            seen_red.add(key)
        elif key not in seen_red:
            violations.append(subject)
    return violations


def commit_subjects(repo: Path | None, ref: str = "HEAD") -> list[str]:
    result = subprocess.run(
        ["git", "log", "--reverse", "--format=%s", ref],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def main(argv: list[str] | None = None) -> int:
    ref = argv[0] if argv else "HEAD"
    subjects = commit_subjects(None, ref)
    violations = find_violations(subjects)
    if violations:
        for v in violations:
            print(f"GREEN-WITHOUT-RED: {v}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
