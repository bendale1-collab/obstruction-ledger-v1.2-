#!/usr/bin/env python3
"""Regenerates a fixture directory's index.json from its actual files.

Content hashes are computed, never typed (operational-standards.md §7a/§7d).
Usage: python harness/gen_fixture_index.py <check_id> <fixture_dir>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def classify(name: str) -> str:
    if name.startswith("pos-"):
        return "positive"
    if name.startswith("neg-"):
        return "negative"
    raise ValueError(f"cannot classify fixture name: {name}")


def build_index(check_id: str, fixture_dir: Path) -> dict[str, object]:
    cases = []
    for path in sorted(fixture_dir.iterdir()):
        if path.name == "index.json":
            continue
        content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        cases.append(
            {"name": path.stem, "class": classify(path.name), "content_hash": content_hash}
        )
    return {"check_id": check_id, "cases": cases}


def main(argv: list[str]) -> int:
    check_id, fixture_dir = argv[0], Path(argv[1])
    index = build_index(check_id, fixture_dir)
    out = fixture_dir / "index.json"
    out.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
