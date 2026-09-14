"""Extractors that build Trajectory records from real corpora."""

from __future__ import annotations

import re

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


class ExtractError(Exception):
    """A trajectory could not be built without guessing a required field."""


def split_sentences(text: str) -> tuple[str, ...]:
    out: list[str] = []
    for chunk in SENTENCE_RE.split(text.strip()):
        cleaned = " ".join(chunk.split())
        if cleaned:
            out.append(cleaned)
    return tuple(out)
