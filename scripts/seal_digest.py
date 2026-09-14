#!/usr/bin/env python3
"""Seal digest over the audit code and the pre-registration it implements.

sha256 of the sorted (path, git blob sha) pairs for every tracked file under
ol/audit/, prereg/K1-five-experiments-v0.2.md, and the sealed task splits
prereg/tw-split-{A,B}.txt. Coverage comes from
`git ls-files`, so a new audit file cannot escape the seal by not being listed.
Blob shas come from the index, so the digest describes committed content.

Run: python scripts/seal_digest.py
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

AUDIT_DIR = "ol/audit"
PREREG = "prereg/K1-five-experiments-v0.2.md"
SPLITS = ("prereg/tw-split-A.txt", "prereg/tw-split-B.txt")


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout


def entries(repo: Path) -> list[tuple[str, str]]:
    """Sorted (path, blob sha) for the sealed set."""
    paths = [p for p in _git(repo, "ls-files", AUDIT_DIR).split() if p]
    paths.append(PREREG)
    paths.extend(SPLITS)
    rows = [(path, _git(repo, "hash-object", path).strip()) for path in sorted(paths)]
    return rows


def digest(repo: Path, rows: list[tuple[str, str]] | None = None) -> str:
    payload = "\n".join(f"{path} {blob}" for path, blob in (rows or entries(repo)))
    return hashlib.sha256(payload.encode()).hexdigest()


def main() -> int:
    repo = Path(__file__).resolve().parent.parent
    rows = entries(repo)
    for path, blob in rows:
        print(f"{blob}  {path}")
    print(f"SEAL-DIGEST: {digest(repo, rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
