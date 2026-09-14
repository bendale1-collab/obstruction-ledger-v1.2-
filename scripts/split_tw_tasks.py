#!/usr/bin/env python3
"""Seeded A/B split of Terminal Wrench task ids (B1-01i).

Every directory under tasks/ is a task id; ids are not assumed numeric.
Sorted, shuffled with random.Random(SEED), halved, each half written sorted,
one id per line. Split A is the design set; split B is sealed and evaluated
once, per the pre-registered interpretation in prereg/K1-five-experiments-v0.2.md.

Run: python scripts/split_tw_tasks.py [--root <clone>] [--out-dir prereg]
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

SEED = 20260914
DEFAULT_ROOT = Path.home() / "ol" / "repo" / "data" / "terminal-wrench"


def task_ids(root: Path) -> list[str]:
    tasks = root / "tasks"
    return sorted(p.name for p in tasks.iterdir() if p.is_dir())


def split(ids: list[str], seed: int) -> tuple[list[str], list[str]]:
    order = sorted(ids)
    random.Random(seed).shuffle(order)
    half = len(order) // 2
    return sorted(order[:half]), sorted(order[half:])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="split_tw_tasks")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out-dir", type=Path, default=Path("prereg"))
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args(argv)

    ids = task_ids(args.root)
    a, b = split(ids, args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "tw-split-A.txt").write_text("\n".join(a) + "\n")
    (args.out_dir / "tw-split-B.txt").write_text("\n".join(b) + "\n")
    print(f"SPLIT: {len(a)} {len(b)} (seed {args.seed}, {len(ids)} task ids)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
