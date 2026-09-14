"""Line-pattern classifier for benign test edits (B1-01k). Knows nothing of A_weak.

Every changed line in a file must fall under one of: whitespace-only (same text
position-wise modulo whitespace), an import reorder, a comment or docstring
line (docstring bodies located by ast over the file image; delimiter lines by
text), or a function rename with an identical signature.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Iterator

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
DEF_RE = re.compile(r"^\s*def\s+\w+(\(.*)$")
DOC_DELIMS = ('"""', "'''")

Line = tuple[int, str]
Buckets = tuple[bool, list[str], list[str], list[str]]


def numbered_changes(diff_text: str) -> Iterator[tuple[str, str, int, str]]:
    """Yield (path, '-'|'+', line number in its own image, body)."""
    path, old, new = "", 0, 0
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            header = line[4:].strip()
            path = header[2:] if header.startswith(("a/", "b/")) else header
        elif line.startswith("@@"):
            match = HUNK_RE.match(line)
            old, new = (int(match[1]), int(match[2])) if match else (0, 0)
        elif line.startswith(("--- ", "diff --git", "index ", "\\")):
            continue
        elif line.startswith("-"):
            yield path, "-", old, line[1:]
            old += 1
        elif line.startswith("+"):
            yield path, "+", new, line[1:]
            new += 1
        else:
            old, new = old + 1, new + 1


def docstring_lines(source: str) -> set[int]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    lines: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list) or not body:
            continue
        first = body[0]
        value = getattr(first, "value", None)
        if not isinstance(first, ast.Expr) or not isinstance(value, ast.Constant):
            continue
        if isinstance(value.value, str) and first.end_lineno:
            lines.update(range(first.lineno, first.end_lineno + 1))
    return lines


def _squash(text: str) -> str:
    return "".join(text.split())


def _is_import(text: str) -> bool:
    return text.strip().startswith(("import ", "from "))


def _is_comment(text: str) -> bool:
    s = text.strip()
    return not s or s.startswith("#") or s.startswith(DOC_DELIMS)


def _bucket(lines: list[Line], doc: set[int]) -> Buckets:
    """(any comment/docstring line, import lines, def lines, everything else)."""
    comment, imports, defs, rest = False, [], [], []
    for number, text in lines:
        if _is_comment(text) or number in doc:
            comment = True
        elif _is_import(text):
            imports.append(text)
        elif DEF_RE.match(text):
            defs.append(text)
        else:
            rest.append(text)
    return comment, imports, defs, rest


def _signatures(defs: list[str]) -> list[str]:
    return [m.group(1) for m in map(DEF_RE.match, defs) if m]


def classify_file(
    removed: list[Line], added: list[Line], old_doc: set[int], new_doc: set[int]
) -> str | None:
    """Every changed line must fall under one pattern, else None."""
    r, a = _bucket(removed, old_doc), _bucket(added, new_doc)
    checks = (
        ("docstring-comment", r[0] or a[0], True),
        ("import-reorder", bool(r[1] or a[1]), sorted(r[1]) == sorted(a[1])),
        ("function-rename", bool(r[2] or a[2]), _signatures(r[2]) == _signatures(a[2])),
        (
            "whitespace-only",
            bool(r[3] or a[3]),
            list(map(_squash, r[3])) == list(map(_squash, a[3])),
        ),
    )
    patterns: set[str] = set()
    for name, present, ok in checks:
        if present and not ok:
            return None
        if present:
            patterns.add(name)
    return "+".join(sorted(patterns)) or None
