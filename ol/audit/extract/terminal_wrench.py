"""Builds Trajectory records from Terminal Wrench ATIF-v1.6 trajectory.json files.

Two fields the card asks for have no source in this corpus, confirmed by
reading the clone: there is no network-fetch tool (only `bash_command` and
`mark_task_complete`), and no diff/patch key anywhere in the record. URLs are
therefore recovered from shell keystrokes, and the A_weak inputs are recovered
from the arguments of file-mutating shell commands (tw_paths.py). That is
weaker than a real diff: it sees a test file deleted by `rm` or rewritten by a
heredoc, and misses edits made by any means it does not recognise.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ol.audit.classes import Trajectory, is_test_path
from ol.audit.extract import split_sentences
from ol.audit.extract.tw_calibration import baseline_median, completion_tokens, model_dir_of
from ol.audit.extract.tw_oracle import clone_root, legit_solve_tasks, oracle_verdict
from ol.audit.extract.tw_paths import removed_paths, written_paths

URL_RE = re.compile(r"https?://[^\s'\"<>|;)\\]+")
SKIP_RE = re.compile(r"@pytest\.mark\.skip|pytest\.skip\(")
ASSERTION_RE = re.compile(r"^\s*(assert\b|self\.assert|pytest\.raises)")


@dataclass(frozen=True)
class TWRecord:
    trajectory: Trajectory
    label: str
    task_id: str
    session_id: str


def _agent_steps(traj: dict[str, Any]) -> list[dict[str, Any]]:
    return [s for s in traj.get("steps", []) if s.get("source") == "agent"]


def keystrokes(traj: dict[str, Any]) -> tuple[str, ...]:
    """Shell commands the agent ran. mark_task_complete carries no command."""
    out: list[str] = []
    for step in _agent_steps(traj):
        for call in step.get("tool_calls", []) or []:
            if call.get("function_name") != "bash_command":
                continue
            command = str(call.get("arguments", {}).get("keystrokes", "")).strip()
            if command:
                out.append(command)
    return tuple(out)


def urls_in(actions: tuple[str, ...]) -> tuple[str, ...]:
    found: list[str] = []
    for action in actions:
        for url in URL_RE.findall(action):
            if url not in found:
                found.append(url)
    return tuple(found)


def final_claims(traj: dict[str, Any]) -> tuple[str, ...]:
    steps = _agent_steps(traj)
    return split_sentences(str(steps[-1].get("message", ""))) if steps else ()


def _action_effects(action: str) -> tuple[list[str], list[str], bool]:
    """(deleted test paths, written test paths, assertion line written) for one command."""
    removed = [p for p in removed_paths(action) if is_test_path(p)]
    written = [p for p in written_paths(action) if is_test_path(p)]
    if not written:
        return removed, [], False
    skipped = written if SKIP_RE.search(action) else []
    touched = any(ASSERTION_RE.match(line) for line in action.splitlines())
    return removed, skipped, touched


def file_effects(actions: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...], bool]:
    """Return (deleted test paths, skipped test paths, assertion touched)."""
    deleted: list[str] = []
    skipped: list[str] = []
    touched = False
    for action in actions:
        removed, newly_skipped, wrote_assertion = _action_effects(action)
        deleted.extend(p for p in removed if p not in deleted)
        skipped.extend(p for p in newly_skipped if p not in skipped)
        touched = touched or wrote_assertion
    return tuple(deleted), tuple(skipped), touched


def build_record(
    traj: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    task_id: str = "",
    calibration_median_tokens: float = 0.0,
    legit_solve_exists: bool | None = None,
) -> TWRecord:
    metadata = metadata or {}
    actions = keystrokes(traj)
    deleted, skipped, touched = file_effects(actions)
    claims = final_claims(traj)
    trajectory = Trajectory(
        deleted_paths=deleted,
        skipped_paths=skipped,
        diff_touches_assertions=touched,
        actions=actions,
        fetched_urls=urls_in(actions),
        claims=claims,
        oracle_contradicts_claim=oracle_verdict(claims, legit_solve_exists),
        output_tokens=completion_tokens(traj),
        calibration_median_tokens=calibration_median_tokens,
    )
    return TWRecord(
        trajectory=trajectory,
        label=str(metadata.get("classification", "")),
        task_id=str(metadata.get("task_id", task_id)),
        session_id=str(traj.get("session_id", "")),
    )


def extract(trajectory_path: Path, metadata_path: Path | None = None) -> TWRecord:
    traj = json.loads(trajectory_path.read_text())
    sibling = metadata_path or trajectory_path.parents[2] / "metadata.json"
    metadata = json.loads(sibling.read_text()) if sibling.is_file() else {}
    parts = trajectory_path.parts
    task_id = parts[parts.index("tasks") + 1] if "tasks" in parts else ""
    model_dir = model_dir_of(trajectory_path)
    median = baseline_median(str(model_dir)) if model_dir else 0.0
    root = clone_root(trajectory_path)
    legit = task_id in legit_solve_tasks(str(root)) if root and task_id else None
    return build_record(
        traj, metadata, task_id=task_id, calibration_median_tokens=median, legit_solve_exists=legit
    )
