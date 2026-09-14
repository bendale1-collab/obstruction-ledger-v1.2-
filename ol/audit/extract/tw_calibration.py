"""A_pad calibration for Terminal Wrench: the honest set is the same task+model's
baseline_trajectories. Median total_completion_tokens over them; 0.0 when none
exist, which the class reads as NA rather than clean.
"""

from __future__ import annotations

import json
import statistics
from functools import lru_cache
from pathlib import Path

BASELINE_GLOB = "baseline_trajectories/*/trial/agent/trajectory.json"
MODEL_DIR_DEPTH = 4


def completion_tokens(traj: dict[str, object]) -> int:
    metrics = traj.get("final_metrics")
    if not isinstance(metrics, dict):
        return 0
    value = metrics.get("total_completion_tokens", 0)
    return int(value) if isinstance(value, int | float) else 0


@lru_cache(maxsize=4096)
def baseline_median(model_dir: str) -> float:
    tokens = []
    for path in sorted(Path(model_dir).glob(BASELINE_GLOB)):
        count = completion_tokens(json.loads(path.read_text()))
        if count > 0:
            tokens.append(count)
    return float(statistics.median(tokens)) if tokens else 0.0


def model_dir_of(trajectory_path: Path) -> Path | None:
    """tasks/<task>/<model>/<tree>/<label>/trial/agent/trajectory.json -> <model> dir."""
    parents = trajectory_path.resolve().parents
    return parents[MODEL_DIR_DEPTH] if len(parents) > MODEL_DIR_DEPTH else None
