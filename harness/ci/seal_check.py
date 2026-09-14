#!/usr/bin/env python3
"""Pre-registration sequencing check (operational-standards.md §3).

Compares the first code commit's committer time on this branch (relative
to a base ref) against the gist revision timestamp the pre-registration
was published at. If the code predates the pre-registration, the run is
RETRODICTION, not a sealed pre-registration, and every result file must
say so automatically rather than relying on someone noticing.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def first_commit_time(base_ref: str, head_ref: str, repo: Path | None = None) -> str:
    result = subprocess.run(
        ["git", "log", "--reverse", "--format=%cI", f"{base_ref}..{head_ref}"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise ValueError(f"no commits found in range {base_ref}..{head_ref}")
    return lines[0]


def verdict(first_code_time: str, gist_revision_time: str) -> dict[str, object]:
    code_dt = datetime.fromisoformat(first_code_time)
    gist_dt = datetime.fromisoformat(gist_revision_time)
    is_retrodiction = code_dt <= gist_dt
    return {
        "first_code_commit_time": first_code_time,
        "gist_revision_time": gist_revision_time,
        "label": "RETRODICTION" if is_retrodiction else None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gist-revision-time", required=True)
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--head-ref", default="HEAD")
    args = parser.parse_args(argv)

    first_time = first_commit_time(args.base_ref, args.head_ref)
    result = verdict(first_time, args.gist_revision_time)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
