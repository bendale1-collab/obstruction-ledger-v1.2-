#!/usr/bin/env python3
"""Runs check-jsonschema over every existing file each schema governs.

agent-runbook.md P0-15: check-jsonschema on all existing files. There is
no hardcoded expectation of nonzero files per schema — most result/card/
manifest paths belong to phases and roles that have not run yet; a
schema with zero matching files today is not a failure.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TARGETS: dict[str, str] = {
    "schemas/fixture.schema.json": "**/fixtures/**/index.json",
    "schemas/result.schema.json": "results/**/*.json",
    "schemas/card.schema.json": "cards/**/*.json",
    "schemas/manifest.schema.json": "manifest.json",
}


def main() -> int:
    failures = 0
    for schema, pattern in TARGETS.items():
        files = sorted(str(p) for p in REPO_ROOT.glob(pattern))
        if not files:
            print(f"{schema}: no files match {pattern}")
            continue
        result = subprocess.run(
            ["check-jsonschema", "--schemafile", schema, *files],
            cwd=REPO_ROOT,
            check=False,
        )
        if result.returncode != 0:
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
