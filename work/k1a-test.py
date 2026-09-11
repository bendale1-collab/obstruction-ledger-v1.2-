#!/usr/bin/env python3
"""K1a test harness — pytest with pytest_generate_tests enumerating work/k1a/ and injections-k1a/ from disk."""

from __future__ import annotations

import glob
import json
import subprocess
from pathlib import Path

import pytest


def discover_checks() -> list[str]:
    """Discover check scripts in work/k1a/."""
    return sorted(glob.glob("work/k1a/*.py"))


def discover_fixtures() -> list[str]:
    """Discover fixture directories in injections-k1a/."""
    check_names = {"c1", "k1-1", "k1-2", "k1-3", "k1-4", "k1-5", "k1-6"}
    fixtures = []
    for d in sorted(Path("injections-k1a").iterdir()):
        if d.is_dir() and d.name in check_names:
            fixtures.append(str(d))
    return fixtures


def pytest_generate_tests(metafunc):
    """Enumerate checks and fixtures from disk at collection time."""
    if "check_script" in metafunc.fixturenames:
        checks = discover_checks()
        metafunc.parametrize("check_script", checks, ids=[Path(c).stem for c in checks])
    if "fixture_dir" in metafunc.fixturenames:
        fixtures = discover_fixtures()
        metafunc.parametrize("fixture_dir", fixtures, ids=[Path(f).name for f in fixtures])


def test_check_imports(check_script):
    """G0: each check imports and emits [] on empty input."""
    result = subprocess.run(
        ["uv", "run", "--python", "3.11", "python", check_script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"exit code {result.returncode}: {result.stderr}"
    output = json.loads(result.stdout)
    assert output == [], f"expected [], got {output}"


def test_check_on_fixture(check_script, fixture_dir):
    """Run each check on each fixture directory."""
    check_name = Path(check_script).stem.replace("_", "-")
    fixture_check = Path(fixture_dir).name

    # Skip mismatched check/fixture pairs
    if fixture_check != check_name:
        pytest.skip(f"{check_name} != {fixture_check}")

    result = subprocess.run(
        ["uv", "run", "--python", "3.11", "python", check_script, fixture_dir],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Check should exit 0 even with findings
    assert result.returncode == 0, f"exit code {result.returncode}: {result.stderr}"
    output = json.loads(result.stdout)
    assert isinstance(output, list), f"expected list, got {type(output)}"
