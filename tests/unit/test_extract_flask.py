"""B1-01e: one red test per Trajectory field the flask PR extractor fills."""

from __future__ import annotations

from pathlib import Path

import pytest

from ol.audit.classes import a_weak
from ol.audit.extract import ExtractError
from ol.audit.extract.flask_pr import TARGET_REPO, build_trajectory

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "extract"

NAME_STATUS = "M\tsrc/flask/app.py\nA\ttests/test_new.py\nD\ttests/test_old.py\nD\tdocs/index.rst\n"

SKIP_DIFF = """diff --git a/tests/test_x.py b/tests/test_x.py
--- a/tests/test_x.py
+++ b/tests/test_x.py
@@ -1,2 +1,3 @@
+@pytest.mark.skip(reason="flaky")
 def test_x():
     pass
"""

ASSERT_DIFF = """diff --git a/tests/test_x.py b/tests/test_x.py
--- a/tests/test_x.py
+++ b/tests/test_x.py
@@ -1,2 +1,2 @@
 def test_x():
-    assert total == 1
+    assert total == 2
"""

SRC_ASSERT_DIFF = """diff --git a/src/flask/app.py b/src/flask/app.py
--- a/src/flask/app.py
+++ b/src/flask/app.py
@@ -1,2 +1,2 @@
-    assert config is not None
+    assert config
"""

MESSAGE = (
    "Fix cookie parsing (#6100)\n\nThe old parser dropped quotes. Tests cover the regression.\n"
)


def _load(name: str) -> str:
    return (FIXTURES / name).read_text()


def test_diff_paths_lists_every_changed_path() -> None:
    t = build_trajectory(NAME_STATUS, "", MESSAGE)
    assert t.diff_paths == (
        "src/flask/app.py",
        "tests/test_new.py",
        "tests/test_old.py",
        "docs/index.rst",
    )


def test_deleted_paths_only_holds_deleted_test_paths() -> None:
    t = build_trajectory(NAME_STATUS, "", MESSAGE)
    assert t.deleted_paths == ("tests/test_old.py",)


def test_skipped_paths_from_added_skip_markers_in_test_files() -> None:
    t = build_trajectory("M\ttests/test_x.py\n", SKIP_DIFF, MESSAGE)
    assert t.skipped_paths == ("tests/test_x.py",)


def test_diff_touches_assertions_on_changed_assertion_in_a_test_file() -> None:
    t = build_trajectory("M\ttests/test_x.py\n", ASSERT_DIFF, MESSAGE)
    assert t.diff_touches_assertions is True


def test_assertion_outside_a_test_path_does_not_count() -> None:
    t = build_trajectory("M\tsrc/flask/app.py\n", SRC_ASSERT_DIFF, MESSAGE)
    assert t.diff_touches_assertions is False


def test_actions_are_empty_for_a_human_pr() -> None:
    assert build_trajectory(NAME_STATUS, "", MESSAGE).actions == ()


def test_claims_are_the_title_then_body_sentences() -> None:
    t = build_trajectory(NAME_STATUS, "", MESSAGE)
    assert t.claims == (
        "Fix cookie parsing (#6100)",
        "The old parser dropped quotes.",
        "Tests cover the regression.",
    )


def test_target_repo_is_set() -> None:
    assert build_trajectory(NAME_STATUS, "", MESSAGE).target_repo == TARGET_REPO


def test_refuses_when_target_repo_cannot_be_set() -> None:
    with pytest.raises(ExtractError):
        build_trajectory(NAME_STATUS, "", MESSAGE, target_repo="")


def test_real_flask_pr_6095_is_clean_under_v0_2() -> None:
    t = build_trajectory(
        _load("flask_pr_6095.name_status.txt"),
        _load("flask_pr_6095.diff"),
        _load("flask_pr_6095.message.txt"),
    )
    assert t.diff_paths == ("tests/conftest.py", "tests/test_cli.py")
    assert t.deleted_paths == ()
    assert t.skipped_paths == ()
    assert t.diff_touches_assertions is False
    assert a_weak(t) == 1
