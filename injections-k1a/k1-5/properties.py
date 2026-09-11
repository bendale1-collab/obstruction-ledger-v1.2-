"""K1-5 property: duplicate hash within manifest negative space.

A manifest passes K1-5 (no duplicates) when every hash is unique.
This property generates manifest entries with all hashes distinct.
Hashes are 64-character hex strings (sha256sum format).
Any duplicate hash is a finding (positive for K1-5).
"""

from hypothesis import given, settings
from hypothesis import strategies as st


@given(st.lists(
    st.tuples(
        st.binary(min_size=32, max_size=32).map(lambda b: b.hex()),
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz-_/.", min_size=3, max_size=20),
    ),
    min_size=1,
    max_size=50,
    unique_by=lambda x: x[0],
))
@settings(max_examples=250)
def test_all_hashes_distinct(manifest_entries):
    """Generate manifest entries with all unique hashes (sha256 format).
    
    All hashes must be:
    - Exactly 64 hex characters (sha256sum output format)
    - Unique across all entries
    - No duplicate paths
    """
    hashes = [h for h, _ in manifest_entries]
    paths = [p for _, p in manifest_entries]
    
    # All hashes must be unique
    assert len(hashes) == len(set(hashes)), "Hashes must be unique"
    # All paths must be unique
    assert len(paths) == len(set(paths)), "Paths must be unique"
    # All hashes must be exactly 64 chars
    assert all(len(h) == 64 for h in hashes), "All hashes must be 64 chars"
    # All hashes must be valid hex
    assert all(all(c in "0123456789abcdef" for c in h) for h in hashes), "All hashes must be hex"
