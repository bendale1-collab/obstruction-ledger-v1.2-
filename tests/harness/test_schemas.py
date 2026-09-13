"""P0-15: the four schemas are valid JSON Schema and accept/reject as designed."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMAS_DIR = Path(__file__).resolve().parent.parent.parent / "schemas"


def _schema(name: str) -> dict[str, object]:
    data: dict[str, object] = json.loads((SCHEMAS_DIR / name).read_text())
    return data


@pytest.mark.parametrize(
    "name",
    ["fixture.schema.json", "result.schema.json", "card.schema.json", "manifest.schema.json"],
)
def test_schema_is_well_formed(name: str) -> None:
    jsonschema.Draft202012Validator.check_schema(_schema(name))


def test_fixture_schema_accepts_valid_and_rejects_invalid() -> None:
    schema = _schema("fixture.schema.json")
    valid = {
        "check_id": "_selftest",
        "cases": [{"name": "pos-01", "class": "positive", "content_hash": "a" * 64}],
    }
    jsonschema.validate(valid, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"check_id": "_selftest"}, schema)


def test_result_schema_accepts_valid_and_rejects_invalid() -> None:
    schema = _schema("result.schema.json")
    valid = {
        "numerator": 3,
        "denominator": 10,
        "ci_low": 0.1,
        "ci_high": 0.5,
        "producing_cmd": "python -m ol.audit run",
    }
    jsonschema.validate(valid, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"numerator": 3, "denominator": 10}, schema)


def test_card_schema_rejects_free_text_field() -> None:
    schema = _schema("card.schema.json")
    with_notes = {
        "id": "B1-03",
        "phase": "B1",
        "depends_on": [],
        "role": "operator",
        "inputs": [],
        "cmd": "true",
        "output": "results/x.json",
        "accept_cmd": "true",
        "gate": False,
        "max_attempts": 2,
        "budget": {"usd": 5, "minutes": 60},
        "halt_if": [],
        "notes": "not allowed",
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(with_notes, schema)


def test_manifest_schema_accepts_valid() -> None:
    schema = _schema("manifest.schema.json")
    valid = {
        "freeze_hash": "b" * 64,
        "authors": {"operator": "mahamara <mahamara@ol.local>"},
        "models": {"operator": {"slug": "qwen/qwen3-coder-next", "source": "config"}},
        "datasets": {"flask": {"sha": "c" * 40, "license_sha": "d" * 64}},
    }
    jsonschema.validate(valid, schema)
