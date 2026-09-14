"""Five-second gate (agent-runbook.md §17c). Runs first, before any research card.

Module list differs from the runbook's illustration: ol.checks, ol.harness,
ol.rollup, and ol.accept are author/operator territory that has not landed
yet, and manifest/ is outside this harness's edit boundary. This suite
smoke-tests what actually exists at each point in the build.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

import harness
import harness.runner
from harness.registry import CHECK_REGISTRY, fixtures_for


def test_imports() -> None:
    assert harness.runner.run_all is not None


def test_every_check_has_cli() -> None:
    for name, spec in CHECK_REGISTRY.items():
        result = subprocess.run(
            [sys.executable, "-m", spec.module_name, "--help"],
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, name


def test_one_fixture_per_check_runs() -> None:
    for name, spec in CHECK_REGISTRY.items():
        fixtures = fixtures_for(name)
        assert fixtures, name
        result = subprocess.run(
            [sys.executable, "-m", spec.module_name, str(fixtures[0])],
            capture_output=True,
            check=False,
        )
        assert result.returncode in (0, 1), (name, result.stderr)


def test_interpreter() -> None:
    assert sys.version_info[:2] == (3, 11)


@pytest.mark.skip(
    reason="manifest/ is outside this harness's edit boundary; "
    "sealed by the adjudicator, not authored under P0-13. Owner: adjudicator."
)
def test_manifest_loads() -> None:
    raise NotImplementedError
