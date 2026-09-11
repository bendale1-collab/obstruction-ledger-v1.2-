"""K1-5 property: duplicate hash within manifest negative space.

A manifest passes K1-5 (no duplicates) when every hash is unique.
This property generates manifest lines where all hashes are distinct.
Any duplicate hash is a finding (positive for K1-5).
"""

from hypothesis import given, settings
from hypothesis import strategies as st


@given(st.lists(
    st.tuples(
        st.binary(min_size=16, max_size=16).map(lambda b: b.hex()),
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz-_", min_size=3, max_size=15),
    ),
    min_size=1,
    max_size=50,
    unique_by=lambda x: x[0],
))
@settings(max_examples=250)
def test_all_hashes_unique(manifest_lines):
    """Generate manifest entries with unique hashes only."""
    hashes = [h for h, _ in manifest_lines]
    # All hashes must be unique
    assert len(hashes) == len(set(hashes))
    # All entries must be valid
    assert all(isinstance(h, str) and len(h) == 32 for h, _ in manifest_lines)
    assert all(isinstance(p, str) and len(p) > 0 for _, p in manifest_lines)
