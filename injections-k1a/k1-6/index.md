# K1-6 Fixtures — Declared extension vs content

## MEASUREMENTS (§2 parsers: python3 -c "import json,sys; json.load(open(sys.argv[1]))" / python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))")

file | parser | exit code
---|---|---
p-json-comment | json.load | 1
p-json-missing-brace | json.load | 1
p-json-single | json.load | 1
p-json-trailing-comma | json.load | 1
p-json-unclosed-string | json.load | 1
p-json-unquoted | json.load | 1
p-yaml-bad-indent | yaml.safe_load | 1
p-yaml-multi-dash | yaml.safe_load | 1
p-yaml-tab-char | yaml.safe_load | 1
p-yaml-unclosed-flow | yaml.safe_load | 1
n-empty | yaml.safe_load | 0
n-valid-json | json.load | 0
n-valid-yaml | yaml.safe_load | 0

Positive fixtures (must fire): 10 cases where .yaml/.yml/.json files fail to parse under the §2 parser.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| p-json-comment | FINDING | JSON with C-style comment; exit 1 under json.load | Y—same JSON object format as negatives, differs only in comment syntax |
| p-json-missing-brace | FINDING | JSON with unclosed brace; exit 1 under json.load | Y—same JSON object format as negatives, differs only in completeness |
| p-json-single | FINDING | JSON with single quotes instead of double; exit 1 under json.load | Y—same JSON object format as negatives, differs only in quote style |
| p-json-trailing-comma | FINDING | JSON with trailing comma; exit 1 under json.load | Y—same JSON object structure as negatives, differs only in syntax validity |
| p-json-unclosed-string | FINDING | JSON with unterminated string value; exit 1 under json.load | Y—same JSON object format as negatives, differs only in string termination |
| p-json-unquoted | FINDING | JSON with unquoted key; exit 1 under json.load | Y—same JSON object format as negatives, differs only in key quoting |
| p-yaml-bad-indent | FINDING | YAML with inconsistent indentation; exit 1 under yaml.safe_load | Y—same YAML key-value structure as negatives, differs only in indentation rules violated |
| p-yaml-multi-dash | FINDING | YAML with malformed multi-document marker sequence; exit 1 under yaml.safe_load | Y—same YAML file format as negatives, differs only in document marker validity |
| p-yaml-tab-char | FINDING | YAML with tab character in indentation; exit 1 under yaml.safe_load | Y—same YAML key-value format as negatives, differs only in tab vs space |
| p-yaml-unclosed-flow | FINDING | YAML with unclosed flow mapping (`a: {b: c`); exit 1 under yaml.safe_load | Y—same YAML flow-mapping structure as a valid mapping would use, differs only in closure |

Negative fixtures (must stay silent): 3 cases where .yaml/.json files parse successfully under the §2 parser.

| case | expected | rationale | hard Y/N |
|------|----------|-----------|----------|
| n-empty | SILENT | Empty YAML document (valid, parses to None); exit 0 under yaml.safe_load | Y—same YAML file type as positives, differs only in being empty (which is valid) |
| n-valid-json | SILENT | Well-formed JSON with valid syntax and double quotes; exit 0 under json.load | Y—same JSON object format as positives, differs only in syntax validity |
| n-valid-yaml | SILENT | Well-formed YAML with valid key-value pairs; exit 0 under yaml.safe_load | Y—same YAML key-value structure as positives, differs only in being valid |

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

## Source-incident paragraph (corrected)

MANIFEST.sha256 at 7d4aad7 records five `.yaml` paths: `known-bad-specs/C1-exclusion-list.yaml`, `ledger/chebyshev-mapping-rejection-2026-09-07.yaml`, `ledger/conv-flag-diagnosis-2026-09-07.yaml`, `ledger/fourier-diff-tolerance-2026-09-07.yaml`, `ledger/misidentification-by-acronym-collision-2026-09-08.yaml`. Only `C1-exclusion-list.yaml` parses successfully under `yaml.safe_load`. The other four — all dated `-2026-09-0X.yaml` — fail to parse; each is prose with a YAML-style commented header, not structured YAML. Their undated twins (`chebyshev-mapping-rejection.md`, `conv-flag-diagnosis.md`, `fourier-diff-tolerance.md`, `misidentification-by-acronym-collision.md`) are `.md` files, not `.yaml`; the previous round's paragraph incorrectly listed undated `.yaml` names that do not exist in MANIFEST.sha256.
