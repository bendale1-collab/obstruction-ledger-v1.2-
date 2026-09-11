"""K1-1 negative-space properties. Written from the sealed section 2 definition only.
No check code is imported or referenced. Each property yields (anchor_bytes,
report_text) that must produce no K1-1 finding.
"""
from hypothesis import strategies as st
MIN_EXAMPLES = 200
FENCE = "`" * 3
text_line = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",), blacklist_characters="`\r"),
    min_size=0, max_size=60)

@st.composite
def exact_quote(draw):
    """Quoted block byte-identical to the anchor, with or without trailing newline -> MATCH."""
    lines = draw(st.lists(text_line, min_size=1, max_size=8))
    anchor = "\n".join(lines) + draw(st.sampled_from(["\n", ""]))
    report = "Preamble.\n\nQUOTE-OF: anchor.txt\n" + FENCE + "\n" + anchor + FENCE + "\n\nAfter.\n"
    return anchor.encode("utf-8"), report

@st.composite
def derived_any(draw):
    """Any block under a DERIVED header is skipped regardless of content -> no finding."""
    anchor = draw(text_line) + "\n"
    body = draw(text_line) + "\n"
    report = "DERIVED 862219a3\nQUOTE-OF: anchor.txt\n" + FENCE + "\n" + body + FENCE + "\n"
    return anchor.encode("utf-8"), report

PROPERTIES = {"exact_quote": exact_quote(), "derived_any": derived_any()}
