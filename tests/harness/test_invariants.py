"""Harness invariants (operational-standards.md §1, agent-runbook.md P0-06).

Guards against the K1a failure modes: hardcoded check subsets, zero
fixtures counted as coverage, and fixtures a check cannot even read.
"""

from __future__ import annotations

from harness.registry import CHECK_REGISTRY, MIN_FIXTURES, fixtures_for
from harness.runner import run_all


def test_every_check_is_invoked() -> None:
    log = run_all()
    assert log.checks_invoked == set(CHECK_REGISTRY)


def test_fixture_count_nonzero() -> None:
    for name in CHECK_REGISTRY:
        assert len(fixtures_for(name)) >= MIN_FIXTURES, name


def test_check_can_read_its_fixtures() -> None:
    for name, spec in CHECK_REGISTRY.items():
        for fixture in fixtures_for(name):
            assert spec.parse(fixture) is not None, (name, fixture)


def test_in_scope() -> None:
    for name, spec in CHECK_REGISTRY.items():
        for fixture in fixtures_for(name):
            assert spec.in_scope(fixture) is True, (name, fixture)
