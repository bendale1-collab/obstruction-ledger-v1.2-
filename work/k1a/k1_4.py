"""
K1-4 — Identifier well-formedness

Any hex string that is a prefix-match (>=10 chars) of a canonical anchor
value, or sits after a label (Gist ID:, FREEZE_HASH=, SHA, commit), must
be exactly canonical length: SHA-256 = 64, git SHA = 40 or 7, gist ID = 32.
Any other length is a finding. Blocks under a QUOTED or DERIVED header are
skipped.

Usage: python k1_4.py <file> [file ...]
Output: JSON array to stdout.
"""

import json
import re
import sys


# Labels and their expected lengths
LABEL_RULES = [
    # Gist ID: expects 32 hex chars
    (re.compile(r'Gist\s*ID\s*[:=]\s*([0-9a-fA-F]+)', re.IGNORECASE), 32, "gist_id"),
    # FREEZE_HASH= / FREEZE_HASH: expects SHA-256 = 64
    (re.compile(r'FREEZE_HASH\s*[:=]\s*([0-9a-fA-F]+)', re.IGNORECASE), 64, "sha256"),
    # SHA-256: expects 64
    (re.compile(r'SHA[-_]?256\s*[:=]\s*([0-9a-fA-F]+)', re.IGNORECASE), 64, "sha256"),
    # SHA followed by hex — expect 40 (full git SHA) or 64 (SHA-256)
    (re.compile(r'\bSHA\b\s*[:=]\s*([0-9a-fA-F]+)', re.IGNORECASE), 40, "git_sha"),
    # "commit" near hex — expect 40
    (re.compile(r'\bcommit\b\s*[=:]\s*([0-9a-fA-F]+)', re.IGNORECASE), 40, "commit"),
    # SHA256 after hash/sum without dash
    (re.compile(r'(?:sha|sha256)\s*[:=]\s*([0-9a-fA-F]+)', re.IGNORECASE), 64, "sha256"),
]


def find_quoted_derived_ranges(lines: list[str]) -> list[tuple[int, int]]:
    """Return (start_line, end_line) ranges that fall under QUOTED / DERIVED headers.

    A line starting with QUOTED or DERIVED (as a word) marks subsequent content
    as quoted/derived until EOF or a line starting with '#' (section heading).
    Lines before any marker are normal.
    """
    ranges: list[tuple[int, int]] = []
    in_block = False
    block_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^(QUOTED|DERIVED)\b', stripped, re.IGNORECASE):
            if not in_block:
                in_block = True
                block_start = i + 1  # content starts on the next line
        elif in_block:
            if stripped.startswith('#'):
                ranges.append((block_start, i))
                in_block = False

    if in_block:
        ranges.append((block_start, len(lines)))

    return ranges


def is_quoted_or_derived_line(
    line_idx: int,
    quoted_ranges: list[tuple[int, int]],
) -> bool:
    """Check if line_idx falls within any QUOTED/DERIVED range."""
    for start, end in quoted_ranges:
        if start <= line_idx < end:
            return True
    return False


def collect_canonical_anchors(
    file_texts: dict[str, str],
) -> set[str]:
    """Collect all known canonical anchor hex values from bundle files.

    Reads STATE.yaml, SEAL-PACKET.md, and seal-detached-*.md when present.
    """
    anchors: set[str] = set()
    anchor_pattern = re.compile(r'(?:FREEZE_HASH|SHA[-_]?256|Gist\s*ID)\s*[:=]\s*([0-9a-fA-F]{32,64})', re.IGNORECASE)

    for path, text in file_texts.items():
        basename = path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].lower()
        if basename in ("state.yaml", "seal-packet.md") or basename.startswith("seal-detached"):
            for m in anchor_pattern.finditer(text):
                anchors.add(m.group(1))

    return anchors


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps([{"error": "Usage: k1_4.py <file> [file ...]"}]))
        sys.exit(1)

    paths = sys.argv[1:]

    # ---- Read all files ----
    file_texts: dict[str, str] = {}
    for path in paths:
        try:
            with open(path) as f:
                file_texts[path] = f.read()
        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            print(json.dumps([{"error": f"Cannot read {path}: {e}"}]))
            sys.exit(1)

    # ---- Collect canonical anchors from bundle files ----
    canonical_anchors = collect_canonical_anchors(file_texts)

    findings: list[dict] = []

    # ---- Pattern for hex strings >= 10 chars ----
    hex_pattern = re.compile(r'[0-9a-fA-F]{10,}')

    for path, text in file_texts.items():
        lines = text.splitlines()
        quoted_ranges = find_quoted_derived_ranges(lines)

        for m in hex_pattern.finditer(text):
            hex_str = m.group()
            line_idx = text[:m.start()].count("\n")

            # Skip if within QUOTED/DERIVED block
            if is_quoted_or_derived_line(line_idx, quoted_ranges):
                continue

            # ---- Check label context (100 chars before) ----
            ctx_start = max(0, m.start() - 100)
            context_before = text[ctx_start:m.start()]

            expected_len: int | None = None
            match_label = ""
            for pattern, exp_len, label_type in LABEL_RULES:
                pm = pattern.search(context_before)
                if pm:
                    captured = pm.group(1)
                    # Verify the captured hex connects to this match
                    if hex_str.startswith(captured):
                        expected_len = exp_len
                        match_label = label_type
                        break

            # ---- Check prefix-match against canonical anchors ----
            anchor_match = ""
            if expected_len is None:
                for anchor in canonical_anchors:
                    if len(anchor) >= 10 and hex_str == anchor[:len(hex_str)]:
                        anchor_match = anchor
                        expected_len = len(anchor)
                        break

            # ---- Report if length mismatch ----
            if expected_len is not None and len(hex_str) != expected_len:
                findings.append({
                    "location": f"{path}:{line_idx + 1}",
                    "identifier": hex_str,
                    "expected_length": expected_len,
                    "found_length": len(hex_str),
                    "anchor_match": anchor_match,
                })

    print(json.dumps(findings))
    sys.exit(0)


if __name__ == "__main__":
    main()