"""B1-01f red tests: audit CLI schema conformance, report producing_cmd gate, rollup."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import jsonschema
import pytest

from ol.audit.__main__ import main as audit_main
from ol.audit.__main__ import sample
from ol.audit.stats import wilson_ci
from ol.report import main as report_main
from ol.rollup import render, statuses_from_log

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA = json.loads((REPO_ROOT / "schemas" / "result.schema.json").read_text())
TW_GLOB = "tasks/*/*/hack_trajectories/*/trial/agent/trajectory.json"
CLONE = Path.home() / "ol" / "repo" / "data" / "terminal-wrench"


def _run_audit(tmp_path: Path, extra: list[str] | None = None) -> dict[str, object]:
    out = tmp_path / "result.json"
    argv = [
        "run",
        "--classes",
        "A_weak,A_selfev,A_nonex,A_pad",
        "--in",
        str(CLONE),
        "--out",
        str(out),
    ]
    assert audit_main(argv + (extra or [])) == 0
    data: dict[str, object] = json.loads(out.read_text())
    return data


@pytest.mark.skipif(not CLONE.is_dir(), reason="terminal-wrench clone not present")
def test_audit_output_conforms_to_result_schema(tmp_path: Path) -> None:
    jsonschema.validate(_run_audit(tmp_path, ["--prs", "5", "--seed", "7"]), SCHEMA)


@pytest.mark.skipif(not CLONE.is_dir(), reason="terminal-wrench clone not present")
def test_audit_reports_each_class_with_its_producing_cmd(tmp_path: Path) -> None:
    data = _run_audit(tmp_path, ["--prs", "5", "--seed", "7"])
    classes = data["classes"]
    assert isinstance(classes, dict)
    for name in ("A_weak", "A_selfev", "A_nonex", "A_pad"):
        entry = classes[name]
        assert set(entry) >= {"fires", "cases", "wilson_ci_low", "wilson_ci_high", "producing_cmd"}
        assert entry["cases"] == 5
        assert entry["producing_cmd"]


@pytest.mark.skipif(not CLONE.is_dir(), reason="terminal-wrench clone not present")
def test_audit_writes_one_invocation_line_per_case(tmp_path: Path) -> None:
    _run_audit(tmp_path, ["--prs", "4", "--seed", "3"])
    lines = (tmp_path / "invocations.log").read_text().splitlines()
    assert len(lines) == 4


@pytest.mark.skipif(not CLONE.is_dir(), reason="terminal-wrench clone not present")
def test_audit_scores_canaries_separately(tmp_path: Path) -> None:
    canaries = tmp_path / "canaries"
    canaries.mkdir()
    sample = sorted(CLONE.glob(TW_GLOB))[0]
    (canaries / "canary-01.json").write_text(sample.read_text())
    data = _run_audit(tmp_path, ["--prs", "3", "--seed", "1", "--canaries", str(canaries)])
    assert data["canary_fire"] == "0/1" or data["canary_fire"] == "1/1"
    classes = data["classes"]
    assert isinstance(classes, dict)
    weak = classes["A_weak"]
    assert weak["cases"] == 3


def test_seed_makes_sampling_deterministic() -> None:
    items = [f"item-{i}" for i in range(50)]
    assert sample(items, 5, 11) == sample(items, 5, 11)
    assert sample(items, 5, 11) != sample(items, 5, 12)


def test_wilson_ci_brackets_the_point_estimate() -> None:
    low, high = wilson_ci(3, 10)
    assert 0.0 <= low < 0.3 < high <= 1.0
    assert wilson_ci(0, 0) == (0.0, 0.0)


def test_report_exits_1_when_a_number_lacks_a_producing_cmd(tmp_path: Path) -> None:
    run_dir = tmp_path / "results" / "B1"
    run_dir.mkdir(parents=True)
    (run_dir / "bad.json").write_text(json.dumps({"numerator": 1, "denominator": 2}))
    assert report_main(["B1", "--out", str(tmp_path / "note.md"), "--results", str(run_dir)]) == 1


def test_report_writes_each_number_with_its_producing_cmd(tmp_path: Path) -> None:
    run_dir = tmp_path / "results" / "B1"
    run_dir.mkdir(parents=True)
    (run_dir / "good.json").write_text(
        json.dumps(
            {
                "numerator": 1,
                "denominator": 4,
                "ci_low": 0.01,
                "ci_high": 0.7,
                "producing_cmd": "python -m ol.audit run --prs 4",
            }
        )
    )
    note = tmp_path / "note.md"
    assert report_main(["B1", "--out", str(note), "--results", str(run_dir)]) == 0
    text = note.read_text()
    assert "1/4" in text
    assert "python -m ol.audit run --prs 4" in text


def test_rollup_takes_the_last_status_per_card() -> None:
    log = [
        "[P0-03] PASS",
        "[B1-01] red: test_x",
        "[B1-01] green: test_x",
        "[P0-04] CANNOT docker",
    ]
    statuses = statuses_from_log(log, budgets={})
    assert statuses["B1-01"] == "green: test_x"
    assert statuses["P0-03"] == "PASS"
    assert "[P0-04] CANNOT docker" in render(statuses, {"P0-04": "usd=1 minutes=5"})


def test_rollup_cli_writes_status_file(tmp_path: Path) -> None:
    out = tmp_path / "ROLLUP.md"
    result = subprocess.run(
        ["uv", "run", "python", "-m", "ol.rollup", "--out", str(out)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "B1-01" in out.read_text()
