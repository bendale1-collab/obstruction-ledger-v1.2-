"""Which tokens in agent shell keystrokes are file paths (B1-01m).

A token is a path only if it is an argument to a file-mutating command
(rm/unlink/git rm, mv, sed -i, truncate, >, >>, tee, or open(..., 'w'|'a') in
Python) AND it either contains "/" or matches ^[A-Za-z0-9_.-]+\\.[A-Za-z0-9]+$
with no trailing punctuation. Dotted attributes, method calls and prose never
qualify: they are not arguments to anything that writes.
"""

from __future__ import annotations

import re

SEGMENT_RE = re.compile(r"[\n;&|]+")
PATHLIKE_RE = re.compile(r"^[A-Za-z0-9_.-]+\.[A-Za-z0-9]+$")
OPEN_WRITE_RE = re.compile(r"""open\(\s*['"]([^'"]+)['"]\s*,\s*['"][wa]""")
REMOVE = {"rm", "unlink"}
WRITE_ALL_ARGS = {"mv", "tee", "truncate"}
QUOTES = "'\""


def is_pathlike(token: str) -> bool:
    token = token.strip(QUOTES)
    return "/" in token or bool(PATHLIKE_RE.match(token))


def _tokens(segment: str) -> list[str]:
    return [t.strip(QUOTES) for t in segment.split()]


def _command(tokens: list[str]) -> tuple[str, list[str]]:
    """(command word, its arguments) after skipping sudo and VAR=value prefixes."""
    i = 0
    while i < len(tokens) and (tokens[i] == "sudo" or re.match(r"^\w+=", tokens[i])):
        i += 1
    if i >= len(tokens):
        return "", []
    return tokens[i], tokens[i + 1 :]


def _args(argv: list[str]) -> list[str]:
    return [a for a in argv if not a.startswith("-")]


def _redirect_targets(tokens: list[str]) -> list[str]:
    out = []
    for i, tok in enumerate(tokens):
        if tok in (">", ">>") and i + 1 < len(tokens):
            out.append(tokens[i + 1])
        elif tok.startswith(">") and len(tok.lstrip(">")) > 0:
            out.append(tok.lstrip(">"))
    return out


def _segment(segment: str) -> tuple[list[str], list[str]]:
    """(removed candidates, written candidates) before the path-likeness filter."""
    tokens = _tokens(segment)
    cmd, argv = _command(tokens)
    removed: list[str] = []
    written: list[str] = _redirect_targets(tokens) + OPEN_WRITE_RE.findall(segment)
    if cmd in REMOVE or (cmd == "git" and argv[:1] == ["rm"]):
        removed = _args(argv[1:] if cmd == "git" else argv)
    elif cmd in WRITE_ALL_ARGS:
        written += _args(argv)
    elif cmd == "sed" and any(a.startswith("-i") for a in argv):
        written += _args(argv)[1:]
    return removed, written


def _collect(text: str, index: int) -> list[str]:
    out: list[str] = []
    for segment in SEGMENT_RE.split(text):
        for candidate in _segment(segment)[index]:
            if is_pathlike(candidate) and candidate not in out:
                out.append(candidate.strip(QUOTES))
    return out


def removed_paths(text: str) -> list[str]:
    return _collect(text, 0)


def written_paths(text: str) -> list[str]:
    return _collect(text, 1)


def mutated_paths(text: str) -> list[str]:
    out = removed_paths(text)
    out += [p for p in written_paths(text) if p not in out]
    return out
