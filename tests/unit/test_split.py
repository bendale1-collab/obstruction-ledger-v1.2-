"""B1-01i red tests: the Terminal Wrench task split is seeded, disjoint, exhaustive, sealed."""

from __future__ import annotations

from pathlib import Path

from scripts.seal_digest import entries
from scripts.split_tw_tasks import SEED, main, split, task_ids

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SPLIT_A = "prereg/tw-split-A.txt"
SPLIT_B = "prereg/tw-split-B.txt"


def _fake_clone(tmp_path: Path, count: int) -> Path:
    root = tmp_path / "tw"
    for i in range(count):
        (root / "tasks" / str(1000 + i)).mkdir(parents=True)
    (root / "tasks" / "README.md").write_text("not a task\n")
    return root


def test_task_ids_are_sorted_task_directories_only(tmp_path: Path) -> None:
    ids = task_ids(_fake_clone(tmp_path, 5))
    assert ids == ["1000", "1001", "1002", "1003", "1004"]


def test_split_is_seeded_disjoint_exhaustive_and_sorted() -> None:
    ids = [str(i) for i in range(101)]
    a, b = split(ids, SEED)
    assert a == sorted(a) and b == sorted(b)
    assert not set(a) & set(b)
    assert sorted([*a, *b]) == sorted(ids)
    assert abs(len(a) - len(b)) <= 1
    assert (a, b) == split(ids, SEED)
    assert (a, b) != split(ids, SEED + 1)
    assert a != ids[: len(a)]


def test_seed_is_the_pre_registered_one() -> None:
    assert SEED == 20260914


def test_main_writes_both_files_one_id_per_line(tmp_path: Path) -> None:
    root = _fake_clone(tmp_path, 7)
    out = tmp_path / "prereg"
    assert main(["--root", str(root), "--out-dir", str(out)]) == 0
    a = (out / "tw-split-A.txt").read_text().splitlines()
    b = (out / "tw-split-B.txt").read_text().splitlines()
    assert len(a) + len(b) == 7
    assert all(line.isdigit() for line in [*a, *b])


def test_split_files_are_inside_the_seal() -> None:
    paths = [path for path, _ in entries(REPO_ROOT)]
    assert SPLIT_A in paths
    assert SPLIT_B in paths
