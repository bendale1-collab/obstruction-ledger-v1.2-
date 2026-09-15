#!/usr/bin/env python3
"""Fail if a required repo path is ignored, or holds an ignored file.

Checking the directory alone is not enough: results/ was never ignored, yet
`.gitignore *.log` swallowed every results/**/invocations.log inside it, and
the per-case evidence behind a verdict went missing without a word.
"""

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
    "results",
    "queue",
]
TRANSIENT = {
    "__pycache__",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
    "node_modules",
    "mutants",
}


def _git(repo: Path | None, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=False)


def is_ignored(path: str, repo: Path | None = None) -> bool:
    return _git(repo, "check-ignore", "-q", path).returncode == 0


def _transient(path: str) -> bool:
    return any(part in TRANSIENT for part in Path(path).parts)


def ignored_within(path: str, repo: Path | None = None) -> list[str]:
    """Files present under path that git would ignore, transient caches aside."""
    result = _git(repo, "ls-files", "--others", "--ignored", "--exclude-standard", "--", path)
    return [line for line in result.stdout.splitlines() if line and not _transient(line)]


def violations(repo: Path | None = None) -> list[str]:
    """Required paths that are ignored, or that contain an ignored file."""
    found: list[str] = []
    for required in REQUIRED_PATHS:
        if is_ignored(required, repo):
            found.append(f"REQUIRED PATH IGNORED: {required}")
        found.extend(
            f"IGNORED FILE UNDER REQUIRED PATH: {p}" for p in ignored_within(required, repo)
        )
    return found


def main() -> int:
    found = violations()
    for line in found:
        print(line, file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
