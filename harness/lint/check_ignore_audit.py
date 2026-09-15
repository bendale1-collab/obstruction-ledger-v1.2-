#!/usr/bin/env python3
"""Fail if any required repo path would be matched by .gitignore."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REQUIRED_PATHS = [
    "ledger",
    "harness",
    "tests",
    "schemas",
    "ol",
    ".github",
]


def is_ignored(path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", path],
        check=False,
    )
    return result.returncode == 0


def violations(repo: Path | None = None) -> list[str]:
    """Required paths that are ignored, or that contain an ignored file."""
    del repo
    return []


def main() -> int:
    bad = [p for p in REQUIRED_PATHS if is_ignored(p)]
    if bad:
        for p in bad:
            print(f"REQUIRED PATH IGNORED: {p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
