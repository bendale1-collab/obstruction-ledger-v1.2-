# K1-4 — Identifier well-formedness: injection index

10 positive (must fire) + 10 negative (must stay silent).
Each fixture is a single .md file containing identifier strings.
Check validates hex identifier length and canonical match.

Canonical values used in fixtures:
- Gist ID: 6b6d2d42651ffe5b63ab6a54a603ca05 (32 chars)
- SHA-256: 34f06514419c660174e6ae0c3b4e828595681d72c31e355cf366a634bae7dacd (64 chars)
- Git SHA: a8e11c813a4828e1ee5d57ccde0ae926671287ff (40 chars)
- Short SHA: 7d4aad7 (7 chars)

## Positives (must fire)

| Case | Expected | Rationale | Hard-neg |
|------|----------|-----------|----------|
| pos-01 | FINDING | Gist ID 31 chars (dropped "1" at pos 11): 6b6d2d4265ffe5b63ab6a54a603ca05 | N |
| pos-02 | FINDING | SHA-256 63 chars (dropped trailing char): ...178c00a | N |
| pos-03 | FINDING | Gist ID 33 chars (inserted "a"): ...03ca05a | N |
| pos-04 | FINDING | SHA 65 chars (two trailing zeros): ...7dacd00 | N |
| pos-05 | FINDING | git SHA 9 chars after "commit": abc12def0 (expected 40 or 7) | N |
| pos-06 | FINDING | Gist ID 10 chars after label: 6b6d2d4265 (prefix match ≥10, expected 32) | N |
| pos-07 | FINDING | SHA-256 correct length (64) but value mismatch: last two chars "ce" vs canonical "cd" | N |
| pos-08 | FINDING | 31-char gist ID inside URL path: .../6b6d2d4265ffe5b63ab6a54a603ca05 | N |
| pos-09 | FINDING | git SHA 8 chars after "commit": 5a6d9c8a (expected 40 or 7) | N |
| pos-10 | FINDING | SHA-1 41 chars (inserted trailing "0"): a8e11c813a4828e1ee5d57ccde0ae926671287ff0 | N |

## Negatives (must stay silent)

| Case | Expected | Rationale | Hard-neg |
|------|----------|-----------|----------|
| neg-01 | SILENT | Correct 32-char gist ID after "Gist ID:" label | Y |
| neg-02 | SILENT | Correct 64-char SHA-256 after "FREEZE_HASH=" label | Y |
| neg-03 | SILENT | Correct 40-char git SHA after "commit" label | Y |
| neg-04 | SILENT | Correct 7-char short SHA after "commit" label | Y |
| neg-05 | SILENT | Correct 32-char gist ID in URL path | Y |
| neg-06 | SILENT | 31-char malformed ID but under QUOTED header — block skipped | N |
| neg-07 | SILENT | 63-char malformed SHA but under DERIVED header — block skipped | N |
| neg-08 | SILENT | Short hex "abc123" (6 chars) after unlabeled "hash:" — <10 chars, no recognized label | N |
| neg-09 | SILENT | Non-hex string "not-a-sha-value" after "commit:" — not hex | N |
| neg-10 | SILENT | Empty file — nothing to check | N |

Hard-negative count: 5/10 (neg-01 through neg-05).
