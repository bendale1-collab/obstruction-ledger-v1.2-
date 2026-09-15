"""Each run's invocations log is named after its --out, so runs sharing a
directory do not overwrite each other. Four Phase C runs into results/C
could leave only one log.
"""

from __future__ import annotations

import json
from pathlib import Path

from ol.audit.__main__ import main as audit_main

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "extract"
SYNTHETIC = (FIXTURE / "terminal_wrench_synthetic.json").read_text()


def _clone(tmp_path: Path, task: str) -> Path:
    root = tmp_path / f"tw-{task}"
    agent = root / "tasks" / task / "m" / "hack_trajectories" / "v5" / "trial" / "agent"
    agent.mkdir(parents=True)
    (agent / "trajectory.json").write_text(SYNTHETIC)
    return root


def test_log_is_named_after_the_out_file(tmp_path: Path) -> None:
    out = tmp_path / "run" / "tw_hack_B.json"
    assert audit_main(["run", "--in", str(_clone(tmp_path, "1")), "--out", str(out)]) == 0
    log = out.parent / "tw_hack_B.invocations.log"
    assert log.is_file()
    assert len(log.read_text().splitlines()) == 1


def test_two_runs_into_one_directory_leave_two_logs(tmp_path: Path) -> None:
    shared = tmp_path / "results-C"
    first = shared / "tw_hack_B.json"
    second = shared / "tw_honest_B.json"
    assert audit_main(["run", "--in", str(_clone(tmp_path, "1")), "--out", str(first)]) == 0
    assert audit_main(["run", "--in", str(_clone(tmp_path, "2")), "--out", str(second)]) == 0

    logs = sorted(p.name for p in shared.glob("*.invocations.log"))
    assert logs == ["tw_hack_B.invocations.log", "tw_honest_B.invocations.log"]
    assert not (shared / "invocations.log").exists()


def test_each_log_holds_its_own_run(tmp_path: Path) -> None:
    shared = tmp_path / "results-C"
    for task in ("1", "2"):
        out = shared / f"run_{task}.json"
        assert (
            audit_main(
                [
                    "run",
                    "--in",
                    str(
                        _clone(tmp_path, task),
                    ),
                    "--out",
                    str(out),
                ]
            )
            == 0
        )
    for task in ("1", "2"):
        log = (shared / f"run_{task}.invocations.log").read_text()
        assert f"/tasks/{task}/" in log
        other = "2" if task == "1" else "1"
        assert f"/tasks/{other}/" not in log
        cases = json.loads((shared / f"run_{task}.json").read_text())["denominator"]
        assert len(log.splitlines()) == cases
