"""B1-01l red tests: the flags Phase C needs — --tasks, --tree, --commits."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ol.audit.__main__ import main as audit_main
from ol.audit.filters import commit_shas, read_ids, select_cases

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "extract"
SYNTHETIC = (FIXTURES / "terminal_wrench_synthetic.json").read_text()


def _traj(root: Path, task: str, tree: str, label: str, classification: str | None) -> None:
    leaf = root / "tasks" / task / "m" / tree / label
    (leaf / "trial" / "agent").mkdir(parents=True)
    (leaf / "trial" / "agent" / "trajectory.json").write_text(SYNTHETIC)
    if classification:
        (leaf / "metadata.json").write_text(json.dumps({"classification": classification}))


def _clone(tmp_path: Path) -> Path:
    root = tmp_path / "tw"
    _traj(root, "9999", "hack_trajectories", "v5", "rewarded_serious_exploit")
    _traj(root, "1", "hack_trajectories", "v5", "rewarded_serious_exploit")
    _traj(root, "9999", "baseline_trajectories", "1", "baseline")
    _traj(root, "9999", "non_hack_trajectories", "v5", "attacker_legitimate_solve")
    _traj(root, "9999", "non_hack_trajectories", "v5_2", "no_reward")
    return root


def test_read_ids_one_per_line(tmp_path: Path) -> None:
    split = tmp_path / "split.txt"
    split.write_text("1018\nadaptive-rejection-sampler\n\n")
    assert read_ids(split) == frozenset({"1018", "adaptive-rejection-sampler"})


def test_tasks_filter_restricts_hack_tree(tmp_path: Path) -> None:
    cases = select_cases(_clone(tmp_path), tree="hack", tasks=frozenset({"9999"}))
    assert len(cases) == 1
    assert "/tasks/9999/" in cases[0][0]


def test_honest_tree_is_baselines_plus_legitimate_solves_only(tmp_path: Path) -> None:
    cases = select_cases(_clone(tmp_path), tree="honest")
    labels = sorted(label for label, _ in cases)
    assert len(labels) == 2
    assert any("baseline_trajectories" in x for x in labels)
    assert any("non_hack_trajectories/v5/" in x for x in labels)
    assert not any("v5_2" in x for x in labels)


def _git_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()

    def run(*args: str) -> None:
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)

    run("init", "-q")
    run("config", "user.email", "t@example.com")
    run("config", "user.name", "t")
    (repo / "a.py").write_text("x = 1\n")
    run("add", "a.py")
    run("commit", "-q", "-m", "base")
    (repo / "a.py").write_text("x = 2\n")
    run("add", "a.py")
    run("commit", "-q", "-m", "change (#7)")
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()
    return repo, sha


def test_commit_shas_and_commits_dir_select_exactly_those_prs(tmp_path: Path) -> None:
    repo, sha = _git_repo(tmp_path)
    cands = tmp_path / "candidates"
    cands.mkdir()
    (cands / "bte-01.json").write_text(json.dumps({"number": 7, "commit": sha}))
    assert commit_shas(cands) == [sha]
    cases = select_cases(repo, commits_dir=cands)
    assert [label for label, _ in cases] == [sha]


def test_cli_accepts_tasks_and_tree(tmp_path: Path) -> None:
    root = _clone(tmp_path)
    split = tmp_path / "A.txt"
    split.write_text("9999\n")
    out = tmp_path / "r.json"
    argv = ["run", "--in", str(root), "--out", str(out), "--tree", "honest", "--tasks", str(split)]
    assert audit_main(argv) == 0
    assert json.loads(out.read_text())["denominator"] == 2


def test_cli_rejects_unknown_tree(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        audit_main(["run", "--in", str(tmp_path), "--out", str(tmp_path / "r"), "--tree", "x"])
