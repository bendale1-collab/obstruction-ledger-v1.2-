"""Corpus loading and deterministic sampling for the audit CLI."""

from __future__ import annotations

import hashlib
from pathlib import Path

from ol.audit.classes import Trajectory
from ol.audit.extract.terminal_wrench import extract as tw_extract

TW_GLOB = "tasks/*/*/hack_trajectories/*/trial/agent/trajectory.json"

Case = tuple[str, Trajectory]


def sample(items: list[str], count: int, seed: int) -> list[str]:
    """Deterministic sample by hash of (seed, item), per the pre-registration."""
    ranked = sorted(items, key=lambda i: hashlib.sha256(f"{seed}:{i}".encode()).hexdigest())
    return ranked[:count]


def canary_cases(directory: Path) -> list[Case]:
    out: list[Case] = []
    for path in sorted(directory.glob("*.json")):
        if path.name.endswith(".metadata.json"):
            continue
        record = tw_extract(path, metadata_path=path.with_suffix(".metadata.json"))
        out.append((str(path), record.trajectory))
    return out
