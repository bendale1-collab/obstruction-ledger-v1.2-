#!/usr/bin/env python3
"""Select merged flask PRs whose test-path edits are all benign (B1-01k).

A PR qualifies when every changed line in its test-path files is classified
benign by scripts/benign_patterns.py. The selector never consults the audit
classes: these candidates exist to test A_weak, so the selector must not be it.

Run: python -m scripts.select_benign_test_edits [--repo /tmp/flask-full] [--limit 10]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path

from ol.audit.classes import is_test_path
from scripts.benign_patterns import Line, classify_file, docstring_lines, numbered_changes

PR_RE = re.compile(r"\(#(\d+)\)")
URL = "https://github.com/pallets/flask/pull/{}"
Loader = Callable[[str, str], str]


def _no_images(_side: str, _path: str) -> str:
    return ""


def classify_pr(diff_text: str, load: Loader = _no_images) -> str | None:
    removed: dict[str, list[Line]] = defaultdict(list)
    added: dict[str, list[Line]] = defaultdict(list)
    for path, marker, number, body in numbered_changes(diff_text):
        if is_test_path(path):
            (removed if marker == "-" else added)[path].append((number, body))
    files = sorted(set(removed) | set(added))
    if not files:
        return None
    patterns = set()
    for f in files:
        old_doc, new_doc = docstring_lines(load("old", f)), docstring_lines(load("new", f))
        patterns.add(classify_file(removed[f], added[f], old_doc, new_doc))
    return None if None in patterns else "+".join(sorted(p for p in patterns if p))


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=False
    ).stdout


def _loader(repo: Path, sha: str) -> Loader:
    def load(side: str, path: str) -> str:
        ref = f"{sha}^1" if side == "old" else sha
        return _git(repo, "show", f"{ref}:{path}")

    return load


def select(repo: Path, limit: int) -> list[dict[str, object]]:
    found: list[dict[str, object]] = []
    for line in _git(repo, "log", "--format=%H\t%s").splitlines():
        sha, _, subject = line.partition("\t")
        match = PR_RE.search(subject)
        if not match:
            continue
        pattern = classify_pr(_git(repo, "diff", f"{sha}^1..{sha}"), _loader(repo, sha))
        if pattern is None:
            continue
        found.append({"number": int(match[1]), "title": subject, "commit": sha, "pattern": pattern})
        if len(found) >= limit:
            break
    return found


def write_candidates(rows: list[dict[str, object]], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i, row in enumerate(rows, start=1):
        record = {**row, "url": URL.format(row["number"])}
        path = out_dir / f"bte-{i:02d}.json"
        path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        paths.append(path)
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="select_benign_test_edits")
    parser.add_argument("--repo", type=Path, default=Path("/tmp/flask-full"))
    parser.add_argument("--out-dir", type=Path, default=Path("fixtures") / "candidates")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)
    rows = select(args.repo, args.limit)
    write_candidates(rows, args.out_dir)
    for row in rows:
        print(f"{row['number']}\t{row['title']}\t{row['pattern']}")
    print(f"CANDIDATES: {len(rows)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
