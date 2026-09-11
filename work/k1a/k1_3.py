"""
K1-3 — Section-structure stability

For each sealed file: header text and numbering at HEAD must equal the
seal commit. Any inserted, removed, or renumbered header is a finding.
Appended headers after the original final header are permitted only if
the original headers are unchanged.

Usage: python k1_3.py <before_file> <after_file> <before_commit> <after_commit>
Output: JSON array to stdout.
"""

import json
import re
import sys


def extract_headers(text: str) -> list[dict]:
    """Extract markdown ATX headings with line number, level, and full text."""
    headers: list[dict] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            headers.append({
                "line": lineno,
                "level": len(m.group(1)),
                "text": m.group(2).strip(),
            })
    return headers


def main() -> None:
    if len(sys.argv) == 1:
        print(json.dumps([]))
        sys.exit(0)
    if len(sys.argv) != 5:
        print(json.dumps([
            {"error": "Usage: k1_3.py <before_file> <after_file> <before_commit> <after_commit>"}
        ]))
        sys.exit(1)

    before_file, after_file, before_commit, after_commit = sys.argv[1:5]

    with open(before_file) as f:
        before_text = f.read()
    with open(after_file) as f:
        after_text = f.read()

    before_headers = extract_headers(before_text)
    after_headers = extract_headers(after_text)

    findings: list[dict] = []

    # ---- Determine if original headers are unchanged as a prefix ----
    original_unchanged = True
    for idx, bh in enumerate(before_headers):
        if idx >= len(after_headers):
            original_unchanged = False
            break
        if bh["text"] != after_headers[idx]["text"]:
            original_unchanged = False
            break

    original_last_line = before_headers[-1]["line"] if before_headers else 0

    # ---- Build lookup maps ----
    before_texts = {bh["text"] for bh in before_headers}
    after_texts = {ah["text"] for ah in after_headers}

    # ---- Removed headers ----
    for bh in before_headers:
        if bh["text"] not in after_texts:
            findings.append({
                "path": after_file,
                "header_diff": (
                    f"REMOVED: \"{bh['text']}\" (line {bh['line']}) "
                    f"present in seal ({before_commit}) but absent from HEAD ({after_commit})"
                ),
            })

    # ---- Inserted / appended headers ----
    for ah in after_headers:
        if ah["text"] not in before_texts:
            inserted = {
                "path": after_file,
                "header_diff": (
                    f"INSERTED: \"{ah['text']}\" (line {ah['line']}) "
                    f"in HEAD ({after_commit}), not present in seal ({before_commit})"
                ),
            }
            is_append = ah["line"] > original_last_line
            if is_append and original_unchanged:
                # Appended after original headers and originals unchanged — permitted
                continue
            findings.append(inserted)

    # ---- Changed headers (same position, different text) ----
    for idx, bh in enumerate(before_headers):
        if idx < len(after_headers):
            ah = after_headers[idx]
            if bh["text"] != ah["text"]:
                findings.append({
                    "path": after_file,
                    "header_diff": (
                        f"CHANGED: \"{bh['text']}\" (line {bh['line']}) "
                        f"-> \"{ah['text']}\" (line {ah['line']}): "
                        f"in seal ({before_commit}) vs HEAD ({after_commit})"
                    ),
                })

    print(json.dumps(findings))
    sys.exit(0)


if __name__ == "__main__":
    main()