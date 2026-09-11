# K1-6 — Declared extension vs content: injection index

10 positive (must fail parse) + 10 negative (must parse or be out of scope).
Each fixture is a single file with a specific extension.
Check runs yaml.safe_load on .yaml/.yml and json.load on .json.

## Positives (must FAIL parse)

| Case | Extension | Expected | Rationale | Hard-neg |
|------|-----------|----------|-----------|----------|
| pos-01 | .yaml | FAIL | Comment-header prose (ledger convention); unquoted colon in prose body | N |
| pos-02 | .yaml | FAIL | Comment headers then prose with unquoted colons throughout | N |
| pos-03 | .json | FAIL | Plain free text, not JSON at all | N |
| pos-04 | .yaml | FAIL | Unquoted colons in values: "key: value with: colons" | Y |
| pos-05 | .yaml | FAIL | Markdown headings + broken list nesting + unclosed bracket | N |
| pos-06 | .yml | FAIL | Comment headers then bad indentation + extra colons | N |
| pos-07 | .json | FAIL | Truncated JSON object (missing closing brace and value) | Y |
| pos-08 | .yaml | FAIL | Over-indented key without parent mapping | Y |
| pos-09 | .json | FAIL | Trailing comma in JSON object | Y |
| pos-10 | .yaml | FAIL | Tab character for indentation (YAML forbids tabs) | Y |

## Negatives (must PARSE or be out of scope)

| Case | Extension | Expected | Rationale | Hard-neg |
|------|-----------|----------|-----------|----------|
| neg-01 | .yaml | PARSE | Valid YAML key-value pairs | Y |
| neg-02 | .yaml | PARSE | Valid YAML list | Y |
| neg-03 | .json | PARSE | Valid JSON object | Y |
| neg-04 | .json | PARSE | Valid JSON array | Y |
| neg-05 | .yaml | PARSE | Valid nested YAML mapping | Y |
| neg-06 | .md | SILENT | Not a checked extension (.md) | N |
| neg-07 | .txt | SILENT | Not a checked extension (.txt) | N |
| neg-08 | .py | SILENT | Not a checked extension (.py) | N |
| neg-09 | (none) | SILENT | No extension; not in scope | N |
| neg-10 | .yaml | PARSE | Empty file; valid YAML (parses as None) | N |

Hard-negative count: 5/10 positives are hard (pos-04, pos-07 through pos-10
share file type and structure with the negative YAML/JSON files, differing
only in the parse-breaking property). 5/10 negatives are hard (neg-01
through neg-05 are valid YAML/JSON of the same format as the positives).
