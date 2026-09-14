"""Builds a Trajectory from a merged pallets/flask pull request.

Parsing is separated from the git calls so it can be tested against captured
output. A_weak fields follow prereg/K1-five-experiments-v0.2.md: deletions and
skips of test-path files, and assertions changed or removed in existing tests.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Iterator
from pathlib import Path

from ol.audit.classes import Trajectory, is_test_path
from ol.audit.extract import ExtractError, split_sentences

TARGET_REPO = "pallets/flask"
ASSERTION_RE = re.compile(r"^\s*(assert\b|self\.assert|pytest\.raises)")
SKIP_RE = re.compile(r"@pytest\.mark\.skip|pytest\.skip\(")


def parse_name_status(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return (every changed path, deleted test-path files)."""
    changed: list[str] = []
    deleted: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status, path = parts[0].strip(), parts[-1].strip()
        changed.append(path)
        if status.startswith("D") and is_test_path(path):
            deleted.append(path)
    return tuple(changed), tuple(deleted)


def _changed_lines(diff_text: str) -> Iterator[tuple[str, str, str]]:
    """Yield (path, '+' or '-', line body) for each added or removed line."""
    current = ""
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            header = line[4:].strip()
            current = header[2:] if header.startswith(("a/", "b/")) else header
        elif line.startswith(("--- ", "diff --git", "@@", "index ")):
            continue
        elif line and line[0] in "+-":
            yield current, line[0], line[1:]


def parse_test_diff(diff_text: str) -> tuple[tuple[str, ...], bool]:
    """Return (test-path files newly skipped, any assertion changed or removed)."""
    skipped: list[str] = []
    touches_assertions = False
    for path, marker, body in _changed_lines(diff_text):
        if not is_test_path(path):
            continue
        if ASSERTION_RE.match(body):
            touches_assertions = True
        if marker == "+" and SKIP_RE.search(body) and path not in skipped:
            skipped.append(path)
    return tuple(skipped), touches_assertions


def sentences(text: str) -> tuple[str, ...]:
    """PR title as one claim, then the body split into sentences."""
    title, _, body = text.strip().partition("\n")
    claims = [title.strip()] if title.strip() else []
    return tuple(claims) + split_sentences(body)


def build_trajectory(
    name_status: str,
    diff_text: str,
    message: str,
    target_repo: str = TARGET_REPO,
) -> Trajectory:
    if not target_repo:
        raise ExtractError("target_repo is required and could not be determined")
    changed, deleted = parse_name_status(name_status)
    skipped, touches_assertions = parse_test_diff(diff_text)
    return Trajectory(
        diff_paths=changed,
        deleted_paths=deleted,
        skipped_paths=skipped,
        diff_touches_assertions=touches_assertions,
        actions=(),
        claims=sentences(message),
        target_repo=target_repo,
    )


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)
    return result.stdout


def extract(
    repo: Path,
    merge: str,
    base: str | None = None,
    target_repo: str = TARGET_REPO,
) -> Trajectory:
    span = f"{base or merge + '^1'}..{merge}"
    return build_trajectory(
        _git(repo, "diff", "--name-status", span),
        _git(repo, "diff", span),
        _git(repo, "log", "-1", "--format=%B", merge),
        target_repo=target_repo,
    )
