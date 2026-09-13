"""Proves P0-09's retrodiction check on a disposable git repo.

Uses a throwaway repo under tmp_path rather than a branch of this repo:
a concurrent-agent hazard was observed sharing this working tree during
this session, and this check has no business creating branches in it.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from harness.ci.seal_check import first_commit_time, verdict


def _run(cwd: Path, *args: str, env: dict[str, str] | None = None) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=env)


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "throwaway"
    repo.mkdir()
    _run(repo, "init", "-q")
    _run(repo, "config", "user.email", "test@example.com")
    _run(repo, "config", "user.name", "test")
    (repo / "base.txt").write_text("base\n")
    _run(repo, "add", "base.txt")
    _run(repo, "commit", "-q", "-m", "base")
    return repo


def _commit_at(repo: Path, filename: str, iso_date: str) -> None:
    (repo / filename).write_text(f"{filename}\n")
    env = {
        "GIT_AUTHOR_DATE": iso_date,
        "GIT_COMMITTER_DATE": iso_date,
        "HOME": str(repo),
        "PATH": "/usr/bin:/bin",
    }
    _run(repo, "add", filename, env=env)
    _run(repo, "commit", "-q", "-m", f"[code] {filename}", env=env)


def test_backdated_commit_is_labeled_retrodiction(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()
    _commit_at(repo, "early.py", "2026-01-01T00:00:00+00:00")

    code_time = first_commit_time(base_sha, "HEAD", repo=repo)
    v = verdict(code_time, "2026-06-01T00:00:00+00:00")
    assert v["label"] == "RETRODICTION"


def test_commit_after_gist_revision_is_not_labeled(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()
    _commit_at(repo, "late.py", "2026-09-01T00:00:00+00:00")

    code_time = first_commit_time(base_sha, "HEAD", repo=repo)
    v = verdict(code_time, "2026-06-01T00:00:00+00:00")
    assert v["label"] is None
