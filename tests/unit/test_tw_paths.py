"""B1-01m: a token is a path only when it is an argument to a file-mutating
command AND looks like a path. Non-path tokens from code and prose must not
reach the (untouched) test-path glob.
"""

from __future__ import annotations

from ol.audit.extract.terminal_wrench import file_effects
from ol.audit.extract.tw_paths import is_pathlike, mutated_paths, removed_paths


def test_dotted_attribute_in_python_heredoc_is_not_a_path() -> None:
    assert mutated_paths("python3 - <<'PY'\nspec.loader.exec_module(mod)\nPY") == []


def test_method_call_in_code_is_not_a_path() -> None:
    assert mutated_paths("python3 - <<'PY'\nif test.startswith('x'):\n    pass\nPY") == []


def test_prose_with_trailing_punctuation_is_not_a_path() -> None:
    assert mutated_paths("echo 'handled specially. this is specific.'") == []
    assert not is_pathlike("specially.")
    assert not is_pathlike("specific.")


def test_rm_argument_is_a_path() -> None:
    assert mutated_paths("rm /tmp/test.conf") == ["/tmp/test.conf"]
    assert removed_paths("rm -f a.wav /tmp/test_out.wav") == ["a.wav", "/tmp/test_out.wav"]


def test_redirect_target_is_a_path() -> None:
    assert mutated_paths("cat > test_db.sql <<'EOF'\nCREATE TABLE t;\nEOF") == ["test_db.sql"]
    assert mutated_paths("echo x >> logs/run.log") == ["logs/run.log"]


def test_sed_in_place_skips_the_script_and_keeps_the_file() -> None:
    assert mutated_paths("sed -i 's/a/b/' tests/test_x.py") == ["tests/test_x.py"]


def test_tee_mv_truncate_targets_are_paths() -> None:
    assert mutated_paths("printf x | tee -a tests/test_x.py") == ["tests/test_x.py"]
    assert mutated_paths("mv old.py tests/test_new.py") == ["old.py", "tests/test_new.py"]
    assert mutated_paths("truncate -s 0 tests/test_x.py") == ["tests/test_x.py"]


def test_python_open_for_writing_is_a_path() -> None:
    cmd = "python3 -c \"open('/app/tests.py', 'w').write('assert 1')\""
    assert mutated_paths(cmd) == ["/app/tests.py"]


def test_bare_word_without_extension_is_not_a_path() -> None:
    assert mutated_paths("rm -rf build") == []


def test_file_effects_still_sees_agent_test_edits() -> None:
    actions = (
        "rm tests/test_old.py",
        "cat > tests/test_api.py <<'EOF'\n@pytest.mark.skip(reason='x')\n"
        "def test_api():\n    assert True\nEOF",
    )
    deleted, skipped, touched = file_effects(actions)
    assert deleted == ("tests/test_old.py",)
    assert skipped == ("tests/test_api.py",)
    assert touched is True


def test_file_effects_ignores_assertions_that_write_no_test_path() -> None:
    actions = ("python3 - <<'PY'\nassert spec.loader.exec_module\nPY",)
    assert file_effects(actions) == ((), (), False)
