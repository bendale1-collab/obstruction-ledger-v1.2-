#!/usr/bin/env python3
"""Fail if any @given-decorated test lacks a @settings(derandomize=True)."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

SEARCH_DIRS = ["tests", "harness", "ol"]


def _is_true_kw(call: ast.Call, name: str) -> bool:
    for kw in call.keywords:
        if kw.arg == name and isinstance(kw.value, ast.Constant) and kw.value.value is True:
            return True
    return False


def _decorator_name(dec: ast.expr) -> str | None:
    node = dec.func if isinstance(dec, ast.Call) else dec
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None


def check_file(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    problems = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        has_given = any(_decorator_name(d) == "given" for d in node.decorator_list)
        if not has_given:
            continue
        ok = False
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and _decorator_name(dec) == "settings":
                ok = ok or _is_true_kw(dec, "derandomize")
        if not ok:
            problems.append(f"{path}:{node.lineno}: @given on {node.name} missing derandomize=True")
    return problems


def main() -> int:
    problems: list[str] = []
    for d in SEARCH_DIRS:
        base = Path(d)
        if not base.is_dir():
            continue
        for path in base.rglob("*.py"):
            problems.extend(check_file(path))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
