#!/usr/bin/env python3
"""Local pre-push gate: red-before-green order (P0-14) and pre-registration
sequencing (P0-09). Replaces the GitHub Actions workflows; runs from
.githooks/pre-push as `uv run python -m harness.ci.prepush` (the -m form
puts the repo root on sys.path). Exits non-zero on any violation.

Environment (all optional):
  PREPUSH_REPO         repo to inspect (default: current directory)
  PREPUSH_BASE_REF     base for the seal range (default: origin/main)
  PREPUSH_HEAD_REF     head for the seal range (default: HEAD)
  GIST_REVISION_TIME   ISO-8601; when unset, the seal check reports and skips
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from harness.ci.red_green_check import commit_subjects, find_violations
from harness.ci.seal_check import first_commit_time, verdict

RETRODICTION = "RETRODICTION"


def check_red_green(repo: Path | None, head_ref: str) -> int:
    violations = find_violations(commit_subjects(repo, head_ref))
    for v in violations:
        print(f"GREEN-WITHOUT-RED: {v}")
    return 1 if violations else 0


def check_seal(repo: Path | None, base_ref: str, head_ref: str, gist_time: str | None) -> int:
    if not gist_time:
        print("seal: GIST_REVISION_TIME unset; nothing to compare against")
        return 0
    try:
        code_time = first_commit_time(base_ref, head_ref, repo)
    except (subprocess.CalledProcessError, ValueError) as exc:
        print(f"seal: could not resolve {base_ref}..{head_ref} ({exc})")
        return 1
    result = verdict(code_time, gist_time)
    if result["label"] == RETRODICTION:
        print(
            f"{RETRODICTION}: first code commit {code_time} is not after gist revision {gist_time}"
        )
        return 1
    print(f"seal: ok, first code commit {code_time} > gist revision {gist_time}")
    return 0


def run(
    repo: Path | None = None,
    base_ref: str = "origin/main",
    head_ref: str = "HEAD",
    gist_time: str | None = None,
) -> int:
    failed = check_red_green(repo, head_ref) + check_seal(repo, base_ref, head_ref, gist_time)
    if failed:
        print("pre-push: REJECTED")
    return 1 if failed else 0


def main() -> int:
    repo_env = os.environ.get("PREPUSH_REPO")
    return run(
        repo=Path(repo_env) if repo_env else None,
        base_ref=os.environ.get("PREPUSH_BASE_REF", "origin/main"),
        head_ref=os.environ.get("PREPUSH_HEAD_REF", "HEAD"),
        gist_time=os.environ.get("GIST_REVISION_TIME"),
    )


if __name__ == "__main__":
    sys.exit(main())
