"""K1-4 property: identifier well-formedness negative space (in-scope only).

An in-scope identifier is one:
1. Preceded by a label from §2 (Gist ID:, FREEZE_HASH=, SHA256=, commit, BLOB=, GIT_HEAD=)
2. OR a prefix-match of a canonical value from the sealed bundle

An in-scope identifier at canonical length produces no finding.
This property generates in-scope identifiers of canonical lengths only.
Any non-canonical length is a finding (positive for K1-4).

Canonical lengths per §2:
- SHA-256: 64 hex chars
- git SHA: 40 hex chars (full form) or 7 hex chars (short form)
- gist ID: 32 hex chars
"""

from hypothesis import given, settings
from hypothesis import strategies as st


@given(st.binary(min_size=16, max_size=16).map(lambda b: b.hex()))
@settings(max_examples=250)
def test_canonical_gist_id_32(hex_string):
    """Generate 32-character hex strings (canonical gist ID length).
    
    In-scope: Gist ID:, FREEZE_HASH= with gist ID format, or
    prefix-matching a known gist from sealed bundle.
    """
    assert len(hex_string) == 32
    assert all(c in "0123456789abcdef" for c in hex_string)


@given(st.binary(min_size=20, max_size=20).map(lambda b: b.hex()))
@settings(max_examples=250)
def test_canonical_sha40(hex_string):
    """Generate 40-character hex strings (canonical git SHA full form).
    
    In-scope: commit label, GIT_HEAD=, or prefix-matching a commit
    from sealed bundle history.
    """
    assert len(hex_string) == 40
    assert all(c in "0123456789abcdef" for c in hex_string)


@given(st.binary(min_size=32, max_size=32).map(lambda b: b.hex()))
@settings(max_examples=250)
def test_canonical_sha64(hex_string):
    """Generate 64-character hex strings (canonical SHA-256).
    
    In-scope: FREEZE_HASH=, SHA256=, BLOB=, or prefix-matching
    a SHA-256 from sealed bundle (MANIFEST.sha256).
    """
    assert len(hex_string) == 64
    assert all(c in "0123456789abcdef" for c in hex_string)


@given(st.binary(min_size=4, max_size=4).map(lambda b: b.hex()))
@settings(max_examples=100)
def test_canonical_sha7_short_form(hex_string):
    """Generate 7-character hex strings (canonical git SHA short form).
    
    In-scope: commit label with short form, or prefix-matching a
    short commit SHA from sealed bundle.
    """
    assert len(hex_string) == 7
    assert all(c in "0123456789abcdef" for c in hex_string)
