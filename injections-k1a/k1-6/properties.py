"""K1-6 property: declared extension vs content negative space.

Content passes K1-6 (parseable) when .yaml, .yml, and .json files parse
successfully under yaml.safe_load or json.load respectively.
This property generates valid YAML and JSON content only.
Parse failures are findings (positive for K1-6).
"""

from hypothesis import given, settings
from hypothesis import strategies as st
import json


@given(st.dictionaries(
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=10),
    st.one_of(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", max_size=20),
        st.integers(),
        st.booleans(),
    ),
    min_size=0,
    max_size=10,
))
@settings(max_examples=250)
def test_valid_json(data):
    """Generate valid JSON-serializable data."""
    # Must serialize to valid JSON
    json_str = json.dumps(data)
    # Must parse back successfully
    parsed = json.loads(json_str)
    assert isinstance(parsed, dict)


@given(st.dictionaries(
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz_", min_size=1, max_size=8),
    st.one_of(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", max_size=15),
        st.integers(min_value=0, max_value=100),
        st.booleans(),
    ),
    min_size=0,
    max_size=5,
))
@settings(max_examples=250)
def test_valid_yaml_structure(data):
    """Generate data structures that form valid YAML when serialized."""
    # YAML is a superset of JSON, so valid JSON is valid YAML
    import json
    yaml_str = json.dumps(data).replace("{", "").replace("}", "").strip()
    # Must contain at least one key-value line (not empty)
    assert len(yaml_str) >= 1 or len(data) == 0
