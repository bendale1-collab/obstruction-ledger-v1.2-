"""`python -m ol.report <phase> --out <note.md>`.

Every number is written with the command that produced it. A number without
one is a founder assertion, not a result (operational-standards.md §7h), so
this exits 1 rather than emitting the note.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

RATE_KEYS = ("numerator", "denominator")


def _rows(payload: dict[str, Any], source: str) -> list[tuple[str, str, str]]:
    """Return (label, value, producing_cmd) triples; producing_cmd may be blank."""
    rows: list[tuple[str, str, str]] = []
    cmd = str(payload.get("producing_cmd", ""))
    if all(k in payload for k in RATE_KEYS):
        value = f"{payload['numerator']}/{payload['denominator']}"
        ci = ""
        if "ci_low" in payload and "ci_high" in payload:
            ci = f" (95% CI {payload['ci_low']:.4f}-{payload['ci_high']:.4f})"
        rows.append((f"{source} aggregate veto", value + ci, cmd))
    classes = payload.get("classes")
    if isinstance(classes, dict):
        for name, entry in sorted(classes.items()):
            rows.append(
                (
                    f"{source} {name}",
                    f"{entry['fires']}/{entry.get('evaluable', entry['cases'])} evaluable, "
                    f"{entry.get('na', 0)} NA of {entry['cases']} (95% CI "
                    f"{entry['wilson_ci_low']:.4f}-{entry['wilson_ci_high']:.4f})",
                    str(entry.get("producing_cmd", "")),
                )
            )
    if "canary_fire" in payload:
        rows.append((f"{source} canary_fire", str(payload["canary_fire"]), cmd))
    return rows


def build(phase: str, results_dir: Path) -> tuple[str, list[str]]:
    rows: list[tuple[str, str, str]] = []
    for path in sorted(results_dir.glob("*.json")):
        rows.extend(_rows(json.loads(path.read_text()), path.name))
    missing = [label for label, _, cmd in rows if not cmd]
    lines = [f"# {phase} — results", ""]
    for label, value, cmd in rows:
        lines.append(f"- **{label}**: {value}")
        lines.append(f"  - produced by: `{cmd}`")
    lines.append("")
    return "\n".join(lines), missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ol.report")
    parser.add_argument("phase")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--results", type=Path, default=None)
    args = parser.parse_args(argv)

    results_dir = args.results or Path("results") / args.phase
    if not results_dir.is_dir():
        print(f"no results directory: {results_dir}", file=sys.stderr)
        return 1
    note, missing = build(args.phase, results_dir)
    if missing:
        for label in missing:
            print(f"NUMBER-WITHOUT-PRODUCING-CMD: {label}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
