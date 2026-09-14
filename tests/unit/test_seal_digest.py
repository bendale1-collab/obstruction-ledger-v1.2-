"""B1-01g red tests: the seal digest covers the audit code and the prereg, by blob sha."""

from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.seal_digest import PREREG, digest, entries

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_entries_are_sorted_path_blob_pairs() -> None:
    rows = entries(REPO_ROOT)
    paths = [path for path, _ in rows]
    assert paths == sorted(paths)
    assert all(len(blob) == 40 for _, blob in rows)


def test_entries_cover_every_audit_file_and_the_prereg() -> None:
    paths = [path for path, _ in entries(REPO_ROOT)]
    assert PREREG in paths
    assert "ol/audit/classes.py" in paths
    assert "ol/audit/extract/flask_pr.py" in paths
    assert "ol/audit/extract/terminal_wrench.py" in paths
    tracked = subprocess.run(
        ["git", "ls-files", "ol/audit"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    splits = ["prereg/tw-split-A.txt", "prereg/tw-split-B.txt"]
    assert sorted([*tracked, PREREG, *splits]) == sorted(paths)


def test_blob_sha_matches_git_hash_object() -> None:
    rows = dict(entries(REPO_ROOT))
    expected = subprocess.run(
        ["git", "hash-object", "ol/audit/classes.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert rows["ol/audit/classes.py"] == expected


def test_digest_is_stable_and_sensitive() -> None:
    first = digest(REPO_ROOT)
    assert len(first) == 64
    assert first == digest(REPO_ROOT)
    altered = [("ol/audit/classes.py", "0" * 40)]
    assert digest(REPO_ROOT, rows=altered) != first
