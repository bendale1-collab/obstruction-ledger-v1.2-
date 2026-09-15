"""`python -m ol.audit run` — score audit classes over a corpus.

--in takes a Terminal Wrench clone (trajectory.json files) or a git checkout
such as flask, whose merge commits are the cases. --prs/--seed sample
deterministically by hash. Canaries are scored on their own and never enter a
class denominator.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from ol.audit.classes import NA, Trajectory, Verdict, a_nonex, a_pad, a_selfev, a_weak
from ol.audit.corpus import Case, canary_cases, sample
from ol.audit.filters import TREES, read_ids, select_cases
from ol.audit.stats import wilson_ci

__all__ = ["Case", "canary_cases", "main", "sample", "score", "select_cases"]

CLASSES: dict[str, Callable[[Trajectory], Verdict]] = {
    "A_weak": a_weak,
    "A_selfev": a_selfev,
    "A_nonex": a_nonex,
    "A_pad": a_pad,
}


def score(cases: list[Case], names: list[str], cmd: str) -> tuple[dict[str, object], int]:
    """Per-class counts plus the number of cases vetoed by at least one class."""
    classes: dict[str, object] = {}
    vetoed: set[str] = set()
    for name in names:
        fires = clean = na = 0
        for label, trajectory in cases:
            verdict = CLASSES[name](trajectory)
            if verdict == 0:
                fires += 1
                vetoed.add(label)
            elif verdict is NA:
                na += 1
            else:
                clean += 1
        low, high = wilson_ci(fires, fires + clean)
        classes[name] = {
            "fires": fires,
            "clean": clean,
            "na": na,
            "cases": len(cases),
            "evaluable": fires + clean,
            "wilson_ci_low": low,
            "wilson_ci_high": high,
            "producing_cmd": cmd,
        }
    return classes, len(vetoed)


def _parse(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="ol.audit")
    parser.add_argument("command", choices=["run"])
    parser.add_argument("--classes", default=",".join(CLASSES))
    parser.add_argument("--in", dest="source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--prs", type=int, default=None)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--canaries", type=Path, default=None)
    parser.add_argument("--tasks", type=Path, default=None)
    parser.add_argument("--tree", choices=sorted(TREES), default="hack")
    parser.add_argument("--commits", type=Path, default=None)
    return parser.parse_args(argv)


def _show(verdict: Verdict) -> str:
    return "na" if verdict is NA else str(verdict)


def _write_outputs(
    out: Path, result: dict[str, object], cases: list[Case], names: list[str]
) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    lines = [
        label + "\t" + " ".join(f"{n}={_show(CLASSES[n](t))}" for n in names) for label, t in cases
    ]
    out.with_suffix(".invocations.log").write_text("\n".join(lines) + "\n")


def _selection(args: argparse.Namespace) -> tuple[str, list[Case]]:
    """The producing command string and the cases it selects."""
    cmd = (
        f"python -m ol.audit run --classes {args.classes} --in {args.source} "
        f"--prs {args.prs} --seed {args.seed} --tree {args.tree}"
        + (f" --tasks {args.tasks}" if args.tasks else "")
        + (f" --commits {args.commits}" if args.commits else "")
    )
    cases = select_cases(
        args.source,
        args.prs,
        args.seed,
        tree=args.tree,
        tasks=read_ids(args.tasks) if args.tasks else None,
        commits_dir=args.commits,
    )
    return cmd, cases


def main(argv: list[str] | None = None) -> int:
    started_at = datetime.now(UTC).isoformat()
    args = _parse(argv)
    names = [n.strip() for n in args.classes.split(",") if n.strip()]
    unknown = [n for n in names if n not in CLASSES]
    if unknown:
        print(f"unknown classes: {unknown}", file=sys.stderr)
        return 2

    cmd, cases = _selection(args)
    classes, vetoed = score(cases, names, cmd)
    canaries = canary_cases(args.canaries) if args.canaries else []
    canary_fires = sum(1 for _, t in canaries if any(CLASSES[n](t) == 0 for n in names))
    low, high = wilson_ci(vetoed, len(cases))
    _write_outputs(
        args.out,
        {
            "numerator": vetoed,
            "denominator": len(cases),
            "ci_low": low,
            "ci_high": high,
            "producing_cmd": cmd,
            "classes": classes,
            "canary_fire": f"{canary_fires}/{len(canaries)}",
            "started_at": started_at,
            "finished_at": datetime.now(UTC).isoformat(),
        },
        cases,
        names,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
