"""Result files carry started_at / finished_at in ISO-8601 UTC, and the schema demands them."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import jsonschema
import pytest

from ol.audit.__main__ import main as audit_main

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA = json.loads((REPO_ROOT / "schemas" / "result.schema.json").read_text())
SYNTHETIC = (
    REPO_ROOT / "tests" / "fixtures" / "extract" / "terminal_wrench_synthetic.json"
).read_text()
VALID = {
    "numerator": 1,
    "denominator": 4,
    "ci_low": 0.0,
    "ci_high": 0.7,
    "producing_cmd": "python -m ol.audit run",
    "started_at": "2026-09-14T10:00:00+00:00",
    "finished_at": "2026-09-14T10:00:05+00:00",
}


def test_schema_requires_both_timestamps() -> None:
    jsonschema.validate(VALID, SCHEMA)
    for key in ("started_at", "finished_at"):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate({k: v for k, v in VALID.items() if k != key}, SCHEMA)


def test_schema_rejects_non_utc_timestamp() -> None:
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**VALID, "started_at": "2026-09-14T10:00:00+02:00"}, SCHEMA)


def _fake_clone(tmp_path: Path) -> Path:
    root = tmp_path / "tw"
    agent = root / "tasks" / "9999" / "m" / "hack_trajectories" / "v5" / "trial" / "agent"
    agent.mkdir(parents=True)
    (agent / "trajectory.json").write_text(SYNTHETIC)
    return root


def test_cli_records_utc_start_and_finish(tmp_path: Path) -> None:
    out = tmp_path / "r.json"
    before = datetime.now(UTC)
    assert audit_main(["run", "--in", str(_fake_clone(tmp_path)), "--out", str(out)]) == 0
    data = json.loads(out.read_text())
    started = datetime.fromisoformat(data["started_at"])
    finished = datetime.fromisoformat(data["finished_at"])
    offset = started.utcoffset()
    assert offset is not None and offset.total_seconds() == 0
    assert before <= started <= finished <= datetime.now(UTC)
    jsonschema.validate(data, SCHEMA)
