"""Builds Trajectory records from Terminal Wrench ATIF-v1.6 trajectory.json files.

Two fields the card asks for have no source in this corpus, confirmed by
reading the clone: there is no network-fetch tool (only `bash_command` and
`mark_task_complete`), and no diff/patch key anywhere in the record. URLs are
therefore recovered from shell keystrokes, and the A_weak inputs are recovered
from the shell commands that edit files. That is weaker than a real diff: it
sees a test file deleted by `rm` or rewritten by a heredoc, and misses edits
made by any means it does not recognise.
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

URL_RE = re.compile(r"https?://[^\s'\"<>|;)\\]+")
TOKEN_RE = re.compile(r"[A-Za-z0-9_./-]+")
SEGMENT_RE = re.compile(r"[\n;&|]+")
REMOVE_RE = re.compile(r"^\s*(sudo\s+)?(rm|unlink)\b|\bgit\s+rm\b")
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


def _test_paths(text: str) -> list[str]:
    out: list[str] = []
    for token in TOKEN_RE.findall(text):
        if "." in token.rsplit("/", 1)[-1] and is_test_path(token) and token not in out:
            out.append(token)
    return out


def _removed_in(action: str) -> list[str]:
    out: list[str] = []
    for segment in SEGMENT_RE.split(action):
        if REMOVE_RE.search(segment):
            out.extend(p for p in _test_paths(segment) if p not in out)
    return out


def file_effects(actions: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...], bool]:
    """Return (deleted test paths, skipped test paths, assertion touched)."""
    deleted: list[str] = []
    skipped: list[str] = []
    touched = False
    for action in actions:
        deleted.extend(p for p in _removed_in(action) if p not in deleted)
        referenced = _test_paths(action)
        if not referenced:
            continue
        if SKIP_RE.search(action):
            skipped.extend(p for p in referenced if p not in skipped)
        if any(ASSERTION_RE.match(line) for line in action.splitlines()):
            touched = True
    return tuple(deleted), tuple(skipped), touched


def build_record(
    traj: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    task_id: str = "",
    calibration_median_tokens: float = 0.0,
    legit_solve_exists: bool | None = None,
) -> TWRecord:
    del legit_solve_exists
    metadata = metadata or {}
    actions = keystrokes(traj)
    deleted, skipped, touched = file_effects(actions)
    trajectory = Trajectory(
        deleted_paths=deleted,
        skipped_paths=skipped,
        diff_touches_assertions=touched,
        actions=actions,
        fetched_urls=urls_in(actions),
        claims=final_claims(traj),
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
    return build_record(traj, metadata, task_id=task_id, calibration_median_tokens=median)
