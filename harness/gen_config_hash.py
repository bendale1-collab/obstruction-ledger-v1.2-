#!/usr/bin/env python3
"""Regenerates harness/config_hash.json from the sealed lint config.

manifest/ is out of this harness's edit boundary, so the config hash
required by P0-12/P0-16 lives here instead. Run: python harness/gen_config_hash.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FILES = ["pyproject.toml", ".pre-commit-config.yaml"]
OUTPUT = Path(__file__).resolve().parent / "config_hash.json"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    result = {f: sha256_of(REPO_ROOT / f) for f in FILES}
    result["producing_cmd"] = "python harness/gen_config_hash.py"
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
