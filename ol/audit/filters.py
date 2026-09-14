"""Case selection for `ol.audit run`: tree, task split, and fixed commit lists.

The honest Terminal Wrench set is baseline_trajectories plus those
non_hack_trajectories whose metadata classification is
attacker_legitimate_solve; hack_trajectories is the hack set. A task split
file lists one task id per line; ids are directory names, not numbers.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ol.audit.corpus import Case, sample
from ol.audit.extract.flask_pr import extract as flask_extract
from ol.audit.extract.terminal_wrench import extract as tw_extract

TREES: dict[str, tuple[str, ...]] = {
    "hack": ("hack_trajectories",),
    "honest": ("baseline_trajectories", "non_hack_trajectories"),
}
LEGIT = "attacker_legitimate_solve"
LEAF = "*/trial/agent/trajectory.json"


def read_ids(path: Path) -> frozenset[str]:
    return frozenset(line.strip() for line in path.read_text().splitlines() if line.strip())


def commit_shas(directory: Path) -> list[str]:
    shas = []
    for path in sorted(directory.glob("*.json")):
        sha = json.loads(path.read_text()).get("commit")
        if sha:
            shas.append(str(sha))
    return shas


def task_id_of(path: Path) -> str:
    parts = path.parts
    return parts[parts.index("tasks") + 1] if "tasks" in parts else ""


def _honest_member(path: Path) -> bool:
    if path.parents[3].name == "baseline_trajectories":
        return True
    meta = path.parents[2] / "metadata.json"
    if not meta.is_file():
        return False
    return bool(json.loads(meta.read_text()).get("classification") == LEGIT)


def trajectory_paths(source: Path, tree: str, tasks: frozenset[str] | None) -> list[str]:
    found: list[str] = []
    for subtree in TREES[tree]:
        for path in sorted(source.glob(f"tasks/*/*/{subtree}/{LEAF}")):
            if tasks is not None and task_id_of(path) not in tasks:
                continue
            if tree == "honest" and not _honest_member(path):
                continue
            found.append(str(path))
    return found


def _git_cases(source: Path, shas: list[str]) -> list[Case]:
    return [(sha, flask_extract(source, sha)) for sha in sorted(shas)]


def _merge_commits(repo: Path) -> list[str]:
    out = subprocess.run(
        ["git", "log", "--merges", "--format=%H"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    return [line for line in out.splitlines() if line]


def select_cases(  # noqa: PLR0913, PLR0917  five orthogonal selection axes, fixed by the CLI
    source: Path,
    count: int | None = None,
    seed: int = 0,
    tree: str = "hack",
    tasks: frozenset[str] | None = None,
    commits_dir: Path | None = None,
) -> list[Case]:
    """Trajectory corpus wins over the git branch: the TW clone has a .git too."""
    paths = trajectory_paths(source, tree, tasks)
    if paths:
        chosen = sample(paths, count, seed) if count else paths
        return [(p, tw_extract(Path(p)).trajectory) for p in sorted(chosen)]
    if commits_dir is not None:
        shas = commit_shas(commits_dir)
        return _git_cases(source, sample(shas, count, seed) if count else shas)
    if (source / ".git").exists():
        shas = _merge_commits(source)
        return _git_cases(source, sample(shas, count, seed) if count else shas)
    raise SystemExit(f"no trajectories and no git repo at {source}")
