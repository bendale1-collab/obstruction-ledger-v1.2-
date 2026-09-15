"""The check-ignore audit must catch an ignored file *inside* a required path.

The defect it missed was `.gitignore:5 *.log` swallowing
results/**/invocations.log while results/ itself was not ignored, so checking
the directory alone is not enough.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from harness.lint.check_ignore_audit import REQUIRED_PATHS, violations


def _repo(tmp_path: Path, gitignore: str, files: dict[str, str]) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / ".gitignore").write_text(gitignore)
    for name, body in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    return repo


def test_required_paths_cover_results_and_queue() -> None:
    assert "results" in REQUIRED_PATHS
    assert "queue" in REQUIRED_PATHS


def test_excluded_invocations_log_under_results_is_flagged(tmp_path: Path) -> None:
    repo = _repo(tmp_path, "*.log\n", {"results/C/run/invocations.log": "case\tA_weak=1\n"})
    found = violations(repo)
    assert any("invocations.log" in v for v in found), found


def test_negation_clears_it(tmp_path: Path) -> None:
    repo = _repo(
        tmp_path,
        "*.log\n!results/**/invocations.log\n",
        {"results/C/run/invocations.log": "case\tA_weak=1\n"},
    )
    assert violations(repo) == []


def test_ignored_required_directory_is_still_flagged(tmp_path: Path) -> None:
    repo = _repo(tmp_path, "ledger/\n", {"ledger/entry.md": "x\n"})
    assert any("ledger" in v for v in violations(repo))


def test_transient_caches_are_not_flagged(tmp_path: Path) -> None:
    repo = _repo(tmp_path, "__pycache__/\n", {"ol/audit/__pycache__/classes.pyc": "x\n"})
    assert violations(repo) == []


def test_queue_is_audited(tmp_path: Path) -> None:
    repo = _repo(tmp_path, "queue/decided/\n", {"queue/decided/P0.md": "P0 LOADED\n"})
    assert any("queue" in v for v in violations(repo))
