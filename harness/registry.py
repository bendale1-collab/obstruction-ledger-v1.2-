"""Discovers checks and their fixtures for the harness invariant tests.

A check is any module exposing CHECK_ID, in_scope(path), parse(path),
and a CLI runnable as `python -m <module> <path>`. ol/checks/ (author
territory, not this harness) is scanned if present; harness.selftest_check
is always registered so the invariants exercise real invocation even
before any author check exists.
"""

from __future__ import annotations

import importlib
import importlib.util
import pkgutil
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Protocol

from harness import selftest_check

REPO_ROOT = Path(__file__).resolve().parent.parent
MIN_FIXTURES = 2


class CheckModule(Protocol):
    CHECK_ID: str

    def in_scope(self, path: Path) -> bool: ...
    def parse(self, path: Path) -> object: ...


@dataclass(frozen=True)
class CheckSpec:
    name: str
    module_name: str
    module: ModuleType

    def in_scope(self, path: Path) -> bool:
        result = self.module.in_scope(path)
        return bool(result)

    def parse(self, path: Path) -> object:
        return self.module.parse(path)


def _discover_ol_checks() -> dict[str, CheckSpec]:
    found: dict[str, CheckSpec] = {}
    if importlib.util.find_spec("ol") is None:
        return found
    if importlib.util.find_spec("ol.checks") is None:
        return found
    pkg = importlib.import_module("ol.checks")
    for info in pkgutil.iter_modules(pkg.__path__):
        module = importlib.import_module(f"ol.checks.{info.name}")
        check_id = getattr(module, "CHECK_ID", info.name)
        found[check_id] = CheckSpec(check_id, f"ol.checks.{info.name}", module)
    return found


def _discover_selftest() -> dict[str, CheckSpec]:
    return {
        selftest_check.CHECK_ID: CheckSpec(
            selftest_check.CHECK_ID, "harness.selftest_check", selftest_check
        )
    }


def build_registry() -> dict[str, CheckSpec]:
    registry = _discover_selftest()
    registry.update(_discover_ol_checks())
    return registry


CHECK_REGISTRY: dict[str, CheckSpec] = build_registry()


def fixtures_for(name: str) -> list[Path]:
    candidates = [
        REPO_ROOT / "fixtures" / name,
        REPO_ROOT / "tests" / "harness" / "fixtures" / name,
    ]
    for directory in candidates:
        if directory.is_dir():
            return sorted(p for p in directory.iterdir() if p.is_file())
    return []
