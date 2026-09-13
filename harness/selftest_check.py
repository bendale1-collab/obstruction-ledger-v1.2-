"""Minimal check module satisfying the harness's check protocol.

Exists so the P0-06 invariant tests exercise real invocation, real
fixture reads, and a real in_scope() predicate instead of running
vacuously over an empty registry until ol/checks/ has content.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

CHECK_ID = "_selftest"


def in_scope(path: Path) -> bool:
    return path.suffix == ".selftest"


def parse(path: Path) -> dict[str, str]:
    return {"text": path.read_text()}


def run(path: Path) -> bool:
    """Return True (finding) iff the fixture's first line is 'positive'."""
    data = parse(path)
    return data["text"].splitlines()[0].strip() == "positive"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="selftest_check")
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    return 1 if run(args.path) else 0


if __name__ == "__main__":
    sys.exit(main())
