"""Proves the pre-push hook rejects a green-before-red branch and a backdated commit.

Disposable repos under tmp_path only; the hook script itself is exercised
end to end via subprocess with PREPUSH_REPO pointed at the disposable repo.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from harness.ci.prepush import run

HOOK = Path(__file__).resolve().parent.parent.parent / ".githooks" / "pre-push"
GIST_TIME = "2026-06-01T00:00:00+00:00"


def _git(repo: Path, *args: str, date: str | None = None) -> str:
    env = dict(os.environ)
    if date:
        env["GIT_AUTHOR_DATE"] = date
        env["GIT_COMMITTER_DATE"] = date
    out = subprocess.run(
        ["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True
    )
    return out.stdout.strip()


def _repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "throwaway"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "test")
    _git(repo, "commit", "-q", "--allow-empty", "-m", "base")
    return repo, _git(repo, "rev-parse", "HEAD")


def test_rejects_green_before_red(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo, base = _repo(tmp_path)
    _git(
        repo,
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "[B1-01] green: test_x",
        date="2026-09-01T00:00:00+00:00",
    )
    assert run(repo, base, "HEAD", GIST_TIME) == 1
    assert "GREEN-WITHOUT-RED" in capsys.readouterr().out


def test_rejects_backdated_commit_with_retrodiction_label(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, base = _repo(tmp_path)
    _git(repo, "commit", "-q", "--allow-empty", "-m", "early", date="2026-01-01T00:00:00+00:00")
    assert run(repo, base, "HEAD", GIST_TIME) == 1
    assert "RETRODICTION" in capsys.readouterr().out


def test_accepts_ordered_and_postdated_branch(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path)
    _git(
        repo,
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "[B1-01] red: test_x",
        date="2026-09-01T00:00:00+00:00",
    )
    _git(
        repo,
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "[B1-01] green: test_x",
        date="2026-09-02T00:00:00+00:00",
    )
    assert run(repo, base, "HEAD", GIST_TIME) == 0


def test_hook_script_rejects_end_to_end(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path)
    _git(
        repo,
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "[B1-01] green: test_x",
        date="2026-01-01T00:00:00+00:00",
    )
    env = dict(
        os.environ, PREPUSH_REPO=str(repo), PREPUSH_BASE_REF=base, GIST_REVISION_TIME=GIST_TIME
    )
    env.pop("VIRTUAL_ENV", None)
    result = subprocess.run(
        [str(HOOK)], cwd=HOOK.parent.parent, env=env, capture_output=True, text=True, check=False
    )
    assert result.returncode != 0
    assert "GREEN-WITHOUT-RED" in result.stdout
    assert "RETRODICTION" in result.stdout
