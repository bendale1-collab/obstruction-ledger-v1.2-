"""Property tests for seal_check.verdict (agent-runbook.md §17g).

Paired inverse: a code commit at or before the gist revision is always
RETRODICTION; strictly after, never. derandomize=True per P0-17 so a
failing example replays from the test name alone.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from hypothesis import given, settings
from hypothesis import strategies as st

from harness.ci.seal_check import verdict

base_times = st.datetimes(
    min_value=datetime(2000, 1, 1),
    max_value=datetime(2100, 1, 1),
    timezones=st.just(UTC),
)
non_negative_seconds = st.integers(min_value=0, max_value=10_000_000)


@settings(max_examples=200, deadline=None, derandomize=True)
@given(base_times, non_negative_seconds)
def test_code_at_or_before_gist_is_retrodiction(gist_dt: datetime, lead_seconds: int) -> None:
    code_dt = gist_dt - timedelta(seconds=lead_seconds)
    result = verdict(code_dt.isoformat(), gist_dt.isoformat())
    assert result["label"] == "RETRODICTION"


@settings(max_examples=200, deadline=None, derandomize=True)
@given(base_times, st.integers(min_value=1, max_value=10_000_000))
def test_code_strictly_after_gist_is_not_retrodiction(gist_dt: datetime, lag_seconds: int) -> None:
    code_dt = gist_dt + timedelta(seconds=lag_seconds)
    result = verdict(code_dt.isoformat(), gist_dt.isoformat())
    assert result["label"] is None
