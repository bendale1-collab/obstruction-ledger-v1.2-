"""The repo's own .gitignore, probed against a disposable repo.

The log rule is path-shaped, not filename-shaped: anything under results/ is
tracked whatever it is called, and .log files elsewhere stay ignored. A rule
pinned to a filename breaks the moment the file is renamed.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GITIGNORE = (REPO_ROOT / ".gitignore").read_text()


def _probe(tmp_path: Path, relative: str) -> bool:
    """True if the repo's .gitignore would ignore this path."""
    repo = tmp_path / "probe"
    if not repo.exists():
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        (repo / ".gitignore").write_text(GITIGNORE)
    target = repo / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("x\n")
    return (
        subprocess.run(["git", "check-ignore", "-q", relative], cwd=repo, check=False).returncode
        == 0
    )


def test_any_log_under_results_is_tracked(tmp_path: Path) -> None:
    for name in (
        "results/C/run/anything.log",
        "results/C/run/tw_hack_B.invocations.log",
        "results/C/run/invocations.log",
        "results/B1/debug.log",
    ):
        assert not _probe(tmp_path, name), name


def test_non_log_files_under_results_are_tracked(tmp_path: Path) -> None:
    assert not _probe(tmp_path, "results/C/run/replay.json")


def test_stray_log_at_repo_root_is_still_ignored(tmp_path: Path) -> None:
    assert _probe(tmp_path, "debug.log")


def test_log_outside_results_is_still_ignored(tmp_path: Path) -> None:
    for name in ("work/run.log", "harness/trace.log", "nested/deep/x.log"):
        assert _probe(tmp_path, name), name


def test_caches_are_still_ignored_even_under_results(tmp_path: Path) -> None:
    assert _probe(tmp_path, "results/C/__pycache__/x.pyc")
