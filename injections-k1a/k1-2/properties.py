"""K1-2 negative-space properties. Written from the sealed section 2 definition only.
No check code is imported or referenced. Each property yields a fixture-mode
directory description (dict: MANIFEST, seal, head, ledger) that must produce
no K1-2 finding.
"""
from hypothesis import strategies as st
MIN_EXAMPLES = 200
name = st.from_regex(r"[a-z]{1,8}\.md", fullmatch=True)
body = st.text(alphabet=st.characters(whitelist_categories=("L", "N", "Zs")),
               min_size=0, max_size=80).map(lambda s: s + "\n")

@st.composite
def all_same(draw):
    """head == seal for every manifest path -> all SAME, no finding."""
    paths = draw(st.lists(name, min_size=1, max_size=6, unique=True))
    files = {p: draw(body) for p in paths}
    return {"MANIFEST": paths, "seal": files, "head": dict(files), "ledger": {}}

@st.composite
def append_declared(draw):
    """One path appended-to at head, declared by a ledger file naming it -> no finding."""
    paths = draw(st.lists(name, min_size=1, max_size=6, unique=True))
    files = {p: draw(body) for p in paths}
    target = draw(st.sampled_from(paths))
    head = dict(files)
    head[target] = files[target] + draw(body)
    return {"MANIFEST": paths, "seal": files, "head": head,
            "ledger": {"ledger/decl.md": f"File {target} diverges from seal: APPEND.\n"}}

PROPERTIES = {"all_same": all_same(), "append_declared": append_declared()}
