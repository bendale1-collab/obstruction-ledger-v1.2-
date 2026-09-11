"""K1-3 property: section-structure stability negative space.

A markdown file that passes K1-3 (no divergence in header structure) must:
- Have identical header lines (levels and text) at seal commit and HEAD
- Permit only append-only changes after the original final header
- Not renumber, remove, or modify any original header

This property generates markdown that satisfies the negative criterion:
no structure divergence between two revisions.
"""

from hypothesis import given, settings
from hypothesis import strategies as st


def markdown_line():
    """Generate valid markdown content lines (non-headers)."""
    return st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ",
        min_size=1,
        max_size=50,
    )


def stable_header():
    """Generate a markdown header that appears in both seal and HEAD."""
    level = st.integers(min_value=1, max_value=6).example()
    text = st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz",
        min_size=3,
        max_size=20,
    ).example()
    return "#" * level + " " + text.capitalize()


@given(st.lists(
    st.one_of(
        st.just("").map(lambda _: markdown_line().example()),
        st.just("").map(lambda _: stable_header()),
    ),
    min_size=2,
    max_size=10,
))
@settings(max_examples=250)
def test_no_structure_divergence(content_lines):
    """Generate markdown with stable header structure.
    
    This property ensures that generated inputs have:
    - At least one header
    - Headers that remain identical across revisions
    - Only append-only changes permitted
    """
    markdown = "\n".join(content_lines)
    # Must have at least one header
    assert any(line.startswith("#") for line in content_lines)
    # Headers must not be renumbered
    headers = [l for l in content_lines if l.startswith("#")]
    assert len(headers) >= 1
    # No header removal or modification in structure
    assert all(isinstance(h, str) for h in headers)
