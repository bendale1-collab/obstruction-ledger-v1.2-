# K1-6 Fixtures — Declared extension vs content

Positive fixtures (must fire): 10 cases where .yaml/.yml/.json files fail to parse.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-yaml-bad-colon-syntax | FINDING | YAML with multiple colons on line (invalid); same file type as negatives | Y—same YAML file structure and format, differs only in validity |
| p-json-trailing-comma-invalid | FINDING | JSON with trailing comma (invalid); same file type structure as negatives | Y—same JSON object structure, differs only in syntax validity |
| p-yaml-indentation-error | FINDING | YAML with inconsistent indentation (invalid); same format as negatives | Y—same YAML key-value structure, differs only in indentation rules violated |
| p-json-missing-brace | FINDING | JSON with unclosed brace (invalid); same structure as valid JSON negatives | Y—same JSON object format, differs only in completeness |
| p-yaml-tab-in-indent | FINDING | YAML with tab character in indentation (invalid); same YAML structure | Y—same YAML key-value format, differs only in tab vs space |
| p-json-not-a-value | FINDING | JSON with NaN literal (not valid JSON); same object structure as valid JSON | Y—same JSON format, differs only in value validity |
| p-yaml-list-bad-indent | FINDING | YAML list with inconsistent indentation (invalid); same list structure | Y—same YAML list format as valid negatives, differs only in indentation |
| p-json-wrong-quotes | FINDING | JSON with single quotes instead of double (invalid); same object structure | Y—same JSON object format, differs only in quote style |
| p-yaml-duplicate-keys | FINDING | YAML with duplicate keys (invalid in strict YAML); same key-value structure | Y—same YAML format, differs only in key uniqueness |
| p-json-c-comment | FINDING | JSON with C-style comment (invalid); same object structure as valid JSON | Y—same JSON object format, differs only in comment syntax |

Negative fixtures (must stay silent): 3 cases where .yaml/.json files parse successfully.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-valid-yaml-structure | SILENT | Well-formed YAML with valid key-value pairs; same file type structure as positives | Y—same YAML key-value structure type as positives, differs only in being valid |
| n-valid-json-object | SILENT | Well-formed JSON with valid syntax and double quotes; same object structure as positives | Y—same JSON object format and structure, differs only in syntax validity |
| n-empty-yaml-doc | SILENT | Empty YAML document (valid, parses as null); same YAML file type and structure | Y—same YAML file format, differs only in being empty (which is valid) |

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
