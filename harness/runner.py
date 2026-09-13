"""Runs every registered check over every one of its fixtures.

Never edits anything it tests. Emits one invocation record per case so a
run with fewer records than fixtures is visibly incomplete rather than a
silent PASS (operational-standards.md §7e).
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from harness.registry import CHECK_REGISTRY, fixtures_for


@dataclass(frozen=True)
class Invocation:
    check: str
    fixture: str
    returncode: int


@dataclass
class RunLog:
    checks_invoked: set[str] = field(default_factory=set)
    invocations: list[Invocation] = field(default_factory=list)


def _invoke(module_name: str, fixture: Path) -> int:
    result = subprocess.run(
        [sys.executable, "-m", module_name, str(fixture)],
        capture_output=True,
        check=False,
    )
    return result.returncode


def run_all() -> RunLog:
    log = RunLog()
    for name, spec in CHECK_REGISTRY.items():
        for fixture in fixtures_for(name):
            returncode = _invoke(spec.module_name, fixture)
            log.checks_invoked.add(name)
            log.invocations.append(Invocation(name, fixture.name, returncode))
    return log
