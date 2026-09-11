# K1-6 Fixtures — Declared extension vs content

Positive fixtures (must fire): 10 cases where .yaml/.yml/.json files fail to parse.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-yaml-invalid-colon | FINDING | YAML with invalid syntax (multiple colons) | Y |
| p-json-trailing-comma | FINDING | JSON with trailing comma (invalid) | Y |
| p-yaml-indent-error | FINDING | YAML with inconsistent indentation | Y |
| p-json-unclosed-brace | FINDING | JSON with unclosed object brace | Y |
| p-yaml-tab-character | FINDING | YAML with tab character (invalid indent) | Y |
| p-json-nan-value | FINDING | JSON with NaN (not valid JSON literal) | Y |
| p-yaml-bad-list | FINDING | YAML list with inconsistent indentation | Y |
| p-json-single-quotes | FINDING | JSON with single quotes (invalid, must use double) | Y |
| p-yaml-duplicate-key | FINDING | YAML with duplicate keys (last-value-wins behavior, but still invalid) | Y |
| p-json-comment-style | FINDING | JSON with C-style comment (not valid JSON) | Y |

Negative fixtures (must stay silent): 3 cases where .yaml/.json files parse successfully.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-valid-yaml | SILENT | Well-formed YAML, parses successfully | N |
| n-valid-json | SILENT | Well-formed JSON, parses successfully | N |
| n-empty-yaml | SILENT | Empty YAML document (valid, parses to null) | N |

## Properties

**property_valid_json**: Generates JSON-serializable dictionaries. Minimum 250 examples.
- All keys are strings
- All values are strings, integers, or booleans
- Result is valid JSON when serialized with json.dumps
- Parses back with json.loads

**property_valid_yaml_structure**: Generates data structures that form valid YAML. Minimum 250 examples.
- Key-value pairs with string keys
- Values are strings, integers, or booleans
- Serializable structure compatible with YAML spec
- Empty dictionaries are valid YAML

Source incidents: At 7d4aad7, MANIFEST.sha256 records 5 .yaml/.yml paths, but only one (C1-exclusion-list.yaml) parses successfully. Four others fail: chebyshev-mapping-rejection-*.yaml, conv-flag-diagnosis-*.yaml, fourier-diff-tolerance-*.yaml, misidentification-by-acronym-collision-*.yaml are prose with commented headers, not structured YAML.
