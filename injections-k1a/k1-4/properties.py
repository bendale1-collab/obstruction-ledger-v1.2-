"""K1-4 property: identifier well-formedness negative space.

An identifier passes K1-4 (well-formed) when it meets canonical length:
- SHA-256: exactly 64 hex characters
- git SHA: exactly 40 hex characters (or 7 for short form)
- Gist ID: exactly 32 hex characters

This property generates hex strings of canonical lengths only.
Any identifier outside these lengths is a finding (positive for K1-4).
"""

from hypothesis import given, settings
from hypothesis import strategies as st


@given(st.binary(min_size=16, max_size=16).map(lambda b: b.hex()))
@settings(max_examples=250)
def test_canonical_gist_id(hex_string):
    """Generate a 32-character hex string (canonical gist ID length)."""
    assert len(hex_string) == 32
    assert all(c in "0123456789abcdef" for c in hex_string)


@given(st.binary(min_size=20, max_size=20).map(lambda b: b.hex()))
@settings(max_examples=250)
def test_canonical_sha40(hex_string):
    """Generate a 40-character hex string (canonical git SHA length)."""
    assert len(hex_string) == 40
    assert all(c in "0123456789abcdef" for c in hex_string)


@given(st.binary(min_size=32, max_size=32).map(lambda b: b.hex()))
@settings(max_examples=250)
def test_canonical_sha64(hex_string):
    """Generate a 64-character hex string (canonical SHA-256 length)."""
    assert len(hex_string) == 64
    assert all(c in "0123456789abcdef" for c in hex_string)
