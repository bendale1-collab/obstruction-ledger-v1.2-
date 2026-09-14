"""B1-01e: one red test per Trajectory field the Terminal Wrench extractor fills.

The committed fixture mirrors the real ATIF-v1.6 schema; the real clone is
Apache-2.0, whose redistribution clause 4(a) requires shipping a copy of the
licence, which would exceed this repo's file-length cap. The real clone is
exercised by test_real_clone_parses below when it is present.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ol.audit.classes import Trajectory, a_selfev, a_weak
from ol.audit.extract.terminal_wrench import build_record, extract

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "extract"
SYNTHETIC = FIXTURES / "terminal_wrench_synthetic.json"
SYNTHETIC_META = FIXTURES / "terminal_wrench_synthetic.metadata.json"
REAL_CLONE = Path.home() / "ol" / "repo" / "data" / "terminal-wrench"


def _record() -> object:
    traj = json.loads(SYNTHETIC.read_text())
    meta = json.loads(SYNTHETIC_META.read_text())
    return build_record(traj, meta)


def test_actions_are_the_bash_keystrokes() -> None:
    actions = _record().trajectory.actions  # type: ignore[attr-defined]
    assert "rm tests/test_old.py" in "\n".join(actions)
    assert len(actions) == 3


def test_fetched_urls_come_from_keystrokes() -> None:
    urls = _record().trajectory.fetched_urls  # type: ignore[attr-defined]
    assert urls == ("https://github.com/acme/widget/pull/42.diff",)


def test_claims_are_the_final_assistant_message() -> None:
    claims = _record().trajectory.claims  # type: ignore[attr-defined]
    assert claims == ("The suite passes now.", "I cannot make the original check work.")


def test_deleted_paths_from_rm_of_a_test_path() -> None:
    assert _record().trajectory.deleted_paths == ("tests/test_old.py",)  # type: ignore[attr-defined]


def test_skipped_paths_from_a_skip_marker_written_to_a_test_path() -> None:
    assert _record().trajectory.skipped_paths == ("tests/test_api.py",)  # type: ignore[attr-defined]


def test_diff_touches_assertions_from_assertions_written_to_a_test_path() -> None:
    assert _record().trajectory.diff_touches_assertions is True  # type: ignore[attr-defined]


def test_label_is_metadata_not_a_trajectory_field() -> None:
    record = _record()
    assert record.label == "rewarded_serious_exploit"  # type: ignore[attr-defined]
    assert record.task_id == "9999"  # type: ignore[attr-defined]
    assert not hasattr(Trajectory(), "label")


def test_target_repo_is_unset_so_the_upstream_fix_rule_cannot_fire() -> None:
    trajectory = _record().trajectory  # type: ignore[attr-defined]
    assert trajectory.target_repo == ""
    assert a_selfev(trajectory) == 1


def test_this_synthetic_hack_fires_a_weak() -> None:
    assert a_weak(_record().trajectory) == 0  # type: ignore[attr-defined]


@pytest.mark.skipif(not REAL_CLONE.is_dir(), reason="terminal-wrench clone not present")
def test_real_clone_parses() -> None:
    paths = sorted(REAL_CLONE.glob("tasks/*/*/hack_trajectories/*/trial/agent/trajectory.json"))
    assert paths, "clone present but no trajectories found"
    record = extract(paths[0])
    assert record.session_id
    assert record.label
    assert record.trajectory.actions
