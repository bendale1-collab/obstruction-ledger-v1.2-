"""Proves P0-14's red-before-green check, on a disposable git repo."""

from __future__ import annotations

import subprocess
from pathlib import Path

from harness.ci.red_green_check import commit_subjects, find_violations


def _commit(repo: Path, message: str) -> None:
    subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", message], cwd=repo, check=True)


def test_green_without_red_is_rejected() -> None:
    subjects = [
        "base",
        "[B1-01] green: test_a_weak_fires",
    ]
    violations = find_violations(subjects)
    assert violations == ["[B1-01] green: test_a_weak_fires"]


def test_red_then_green_is_accepted() -> None:
    subjects = [
        "base",
        "[B1-01] red: test_a_weak_fires",
        "[B1-01] green: test_a_weak_fires",
    ]
    assert find_violations(subjects) == []


def test_red_for_different_test_does_not_cover_green() -> None:
    subjects = [
        "[B1-01] red: test_a_weak_fires",
        "[B1-01] green: test_a_selfev_fires",
    ]
    violations = find_violations(subjects)
    assert violations == ["[B1-01] green: test_a_selfev_fires"]


def test_on_a_disposable_repo_green_before_red_is_rejected(tmp_path: Path) -> None:
    repo = tmp_path / "throwaway"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=repo, check=True)
    _commit(repo, "base")
    _commit(repo, "[B1-01] green: test_a_weak_fires")

    violations = find_violations(commit_subjects(repo))
    assert violations == ["[B1-01] green: test_a_weak_fires"]
