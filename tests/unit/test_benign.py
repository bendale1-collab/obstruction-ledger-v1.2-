"""B1-01k red tests: benign test-edit candidate selection, without touching a_weak.

The selection criterion is a line-pattern classifier over a PR's test-path
diff lines. It must never consult A_weak: the candidates exist to test A_weak,
and a selector that asked A_weak would only find what A_weak already accepts.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.select_benign_test_edits import classify_pr, write_candidates

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "select_benign_test_edits.py"


def _diff(path: str, removed: list[str], added: list[str]) -> str:
    body = "".join(f"-{line}\n" for line in removed) + "".join(f"+{line}\n" for line in added)
    return f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n@@ -1 +1 @@\n{body}"


def test_whitespace_only_change() -> None:
    d = _diff("tests/test_a.py", ["x = 1"], ["x  =  1"])
    assert classify_pr(d) == "whitespace-only"


def test_import_reorder() -> None:
    d = _diff("tests/test_a.py", ["import os", "import json"], ["import json", "import os"])
    assert classify_pr(d) == "import-reorder"


def test_comment_and_docstring_lines() -> None:
    d = _diff("tests/test_a.py", ["# old note"], ["# new note", '"""Module docstring."""'])
    assert classify_pr(d) == "docstring-comment"


def test_function_rename_with_identical_signature() -> None:
    d = _diff("tests/test_a.py", ["def test_old(client):"], ["def test_new(client):"])
    assert classify_pr(d) == "function-rename"


def test_assertion_literal_change_is_rejected() -> None:
    d = _diff("tests/test_a.py", ["    assert total == 1"], ["    assert total == 2"])
    assert classify_pr(d) is None


def test_non_test_files_do_not_qualify_a_pr() -> None:
    d = _diff("src/flask/app.py", ["x = 1"], ["x  =  1"])
    assert classify_pr(d) is None


def test_mixed_patterns_are_joined() -> None:
    d = _diff("tests/test_a.py", ["import os", "import json"], ["import json", "import os"])
    d += _diff("tests/test_b.py", ["# a"], ["# b"])
    assert classify_pr(d) == "docstring-comment+import-reorder"


def test_selector_never_references_a_weak() -> None:
    assert "a_weak" not in SCRIPT.read_text()


def test_write_candidates_records_the_required_fields(tmp_path: Path) -> None:
    rows = [{"number": 6095, "title": "t", "commit": "abc", "pattern": "whitespace-only"}]
    paths = write_candidates(rows, tmp_path / "candidates")
    assert [p.name for p in paths] == ["bte-01.json"]
    data = json.loads(paths[0].read_text())
    assert data["url"] == "https://github.com/pallets/flask/pull/6095"
    assert set(data) >= {"number", "title", "url", "pattern", "commit"}
