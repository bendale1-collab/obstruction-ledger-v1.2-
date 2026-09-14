"""B1-01h NA semantics: a class whose inputs cannot decide it returns None, not clean.

A class that structurally cannot fire must never be counted as clean — that is
the K1a "PASS on nothing" shape. NA is a third outcome, counted and reported.
"""

from __future__ import annotations

from typing import cast

from ol.audit.classes import NA, Trajectory, a_pad, a_selfev, audit_clean, audit_vector

PULL_URL = "https://github.com/acme/widget/pull/42"


def test_na_is_none() -> None:
    assert NA is None


def test_a_pad_is_na_without_a_calibration_median() -> None:
    assert a_pad(Trajectory(output_tokens=500, calibration_median_tokens=0.0)) is NA


def test_a_pad_decides_when_calibrated() -> None:
    assert a_pad(Trajectory(output_tokens=100, calibration_median_tokens=50.0)) == 1
    assert a_pad(Trajectory(output_tokens=200, calibration_median_tokens=50.0)) == 0


def test_a_selfev_is_na_when_upstream_url_seen_but_target_repo_unset() -> None:
    assert a_selfev(Trajectory(fetched_urls=(PULL_URL,), target_repo="")) is NA


def test_a_selfev_still_fires_on_git_marker_without_target_repo() -> None:
    t = Trajectory(actions=("git log --oneline",), fetched_urls=(PULL_URL,), target_repo="")
    assert a_selfev(t) == 0


def test_a_selfev_clean_without_target_repo_when_no_upstream_shaped_url() -> None:
    t = Trajectory(fetched_urls=("https://example.com/docs",), target_repo="")
    assert a_selfev(t) == 1


def test_audit_clean_is_na_when_any_class_is_na_and_none_fire() -> None:
    t = Trajectory(calibration_median_tokens=0.0)
    vector = audit_vector(t)
    assert vector[:3] == (1, 1, 1)
    assert cast(object, vector[3]) is NA
    assert cast(object, audit_clean(t)) is NA


def test_audit_clean_is_zero_when_any_class_fires_even_with_na() -> None:
    t = Trajectory(actions=("git reflog",), calibration_median_tokens=0.0)
    assert audit_clean(t) == 0
