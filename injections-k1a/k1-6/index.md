# K1-6 Fixtures — Declared extension vs content

## MEASUREMENTS

file | parse result
---|---
p-json-comment | YAML_OK
p-json-missing-brace | PARSE_FAIL
p-json-nan-literal | YAML_OK
p-json-single | YAML_OK
p-json-trailing-comma | YAML_OK
p-json-unquoted | YAML_OK
p-yaml-bad-indent | PARSE_FAIL
p-yaml-dup | YAML_OK
p-yaml-multi-dash | PARSE_FAIL
p-yaml-tab-char | PARSE_FAIL
n-empty | YAML_OK
n-valid-json | YAML_OK
n-valid-yaml | YAML_OK

Positive fixtures (must fire): 10 cases where .yaml/.yml/.json files fail to parse.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-json-comment | FINDING | JSON with C-style comment (invalid); same file type structure as negatives | Y—same JSON object format, differs only in comment syntax |
| p-json-missing-brace | FINDING | JSON with unclosed brace (invalid); same structure as valid JSON negatives | Y—same JSON object format, differs only in completeness |
| p-json-nan-literal | FINDING | JSON with NaN literal (not valid JSON); same object structure as valid JSON | Y—same JSON format, differs only in value validity |
| p-json-single | FINDING | JSON with single quotes instead of double (invalid); same object structure | Y—same JSON object format, differs only in quote style |
| p-json-trailing-comma | FINDING | JSON with trailing comma (invalid); same file type structure as negatives | Y—same JSON object structure, differs only in syntax validity |
| p-json-unquoted | FINDING | JSON with unquoted key (invalid); same object structure as valid JSON | Y—same JSON object format, differs only in key quoting |
| p-yaml-bad-indent | FINDING | YAML with inconsistent indentation (invalid); same format as negatives | Y—same YAML key-value structure, differs only in indentation rules violated |
| p-yaml-dup | FINDING | YAML with duplicate keys (invalid in strict YAML); same key-value structure | Y—same YAML format, differs only in key uniqueness |
| p-yaml-multi-dash | FINDING | YAML with multiple document markers (invalid format); same YAML structure | Y—same YAML file format, differs only in document count |
| p-yaml-tab-char | FINDING | YAML with tab character in indentation (invalid); same YAML structure | Y—same YAML key-value format, differs only in tab vs space |

Negative fixtures (must stay silent): 3 cases where .yaml/.json files parse successfully.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-empty | SILENT | Empty YAML document (valid, parses as null); same YAML file type and structure | Y—same YAML file format, differs only in being empty (which is valid) |
| n-valid-json | SILENT | Well-formed JSON with valid syntax and double quotes; same object structure as positives | Y—same JSON object format and structure, differs only in syntax validity |
| n-valid-yaml | SILENT | Well-formed YAML with valid key-value pairs; same file type structure as positives | Y—same YAML key-value structure type as positives, differs only in being valid |

## Properties

**property_valid_json**: Generates JSON-serializable dictionaries that parse under json.load.
- Minimum 250 examples
- All keys are strings
- All values are strings, integers, or booleans
- Valid JSON when serialized with json.dumps
- Parses back with json.loads without error

**property_valid_yaml_structure**: Generates YAML-compatible data structures that parse under yaml.safe_load.
- Minimum 250 examples
- Key-value pairs with string keys
- Values are strings, integers, or booleans
- Consistent indentation (spaces, no tabs)
- Valid YAML when serialized (e.g., as key: value format)

Source incidents: MANIFEST.sha256 at 7d4aad7 records 5 .yaml/.yml paths. Only C1-exclusion-list.yaml parses successfully. Four others fail: chebyshev-mapping-rejection-2026-09-07.yaml, chebyshev-mapping-rejection.yaml, conv-flag-diagnosis-2026-09-07.yaml, conv-flag-diagnosis.yaml, fourier-diff-tolerance-2026-09-07.yaml, fourier-diff-tolerance.yaml, misidentification-by-acronym-collision-2026-09-08.yaml, misidentification-by-acronym-collision.yaml — all are prose with YAML-style commented headers, not structured YAML.
