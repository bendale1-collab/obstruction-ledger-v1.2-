"""Proves the P0-17 lint rule actually catches a missing derandomize=True."""

from __future__ import annotations

from pathlib import Path

from harness.lint.check_derandomize import check_file

BAD = """
from hypothesis import given, strategies as st

@given(st.integers())
def test_missing_derandomize(x):
    assert x == x
"""

GOOD = """
from hypothesis import given, settings, strategies as st

@settings(derandomize=True)
@given(st.integers())
def test_has_derandomize(x):
    assert x == x
"""


def test_flags_given_without_derandomize(tmp_path: Path) -> None:
    path = tmp_path / "bad.py"
    path.write_text(BAD)
    assert check_file(path) != []


def test_accepts_given_with_derandomize(tmp_path: Path) -> None:
    path = tmp_path / "good.py"
    path.write_text(GOOD)
    assert check_file(path) == []
