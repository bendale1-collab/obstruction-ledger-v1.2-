"""Corpus loading and deterministic sampling for the audit CLI."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from ol.audit.classes import Trajectory
from ol.audit.extract.flask_pr import extract as flask_extract
from ol.audit.extract.terminal_wrench import extract as tw_extract

TW_GLOB = "tasks/*/*/hack_trajectories/*/trial/agent/trajectory.json"

Case = tuple[str, Trajectory]


def sample(items: list[str], count: int, seed: int) -> list[str]:
    """Deterministic sample by hash of (seed, item), per the pre-registration."""
    ranked = sorted(items, key=lambda i: hashlib.sha256(f"{seed}:{i}".encode()).hexdigest())
    return ranked[:count]


def _merge_commits(repo: Path) -> list[str]:
    result = subprocess.run(
        ["git", "log", "--merges", "--format=%H"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def cases_from(source: Path, count: int | None, seed: int) -> list[Case]:
    """Trajectory corpus wins over the git branch: the TW clone has a .git too."""
    paths = [str(p) for p in sorted(source.glob(TW_GLOB))]
    if paths:
        selected = sample(paths, count, seed) if count else paths
        return [(p, tw_extract(Path(p)).trajectory) for p in sorted(selected)]
    if (source / ".git").exists():
        chosen = _merge_commits(source)
        chosen = sample(chosen, count, seed) if count else chosen
        return [(sha, flask_extract(source, sha)) for sha in sorted(chosen)]
    raise SystemExit(f"no trajectories and no git repo at {source}")


def canary_cases(directory: Path) -> list[Case]:
    out: list[Case] = []
    for path in sorted(directory.glob("*.json")):
        if path.name.endswith(".metadata.json"):
            continue
        record = tw_extract(path, metadata_path=path.with_suffix(".metadata.json"))
        out.append((str(path), record.trajectory))
    return out
