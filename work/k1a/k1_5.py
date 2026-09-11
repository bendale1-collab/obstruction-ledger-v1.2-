"""
K1-5 — Duplicate hash within manifest

Every hash in MANIFEST.sha256 must be unique. Two paths with one hash is
a finding, reported with both paths. Distinct-artifact count is reported
alongside the line count.

Usage: python k1_5.py <manifest_file>
Output: JSON array to stdout.
"""

import json
import re
import sys

_LINE_RE = re.compile(r'^([0-9a-fA-F]+)\s+(.+)$')


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps([]))
        sys.exit(0)

    manifest_path = sys.argv[1]

    with open(manifest_path) as f:
        raw_lines = f.read().splitlines()

    # Filter blank / comment lines
    all_lines: list[str] = []
    for line in raw_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            all_lines.append(stripped)

    hash_to_paths: dict[str, list[str]] = {}
    for line in all_lines:
        m = _LINE_RE.match(line)
        if m:
            h, path = m.group(1), m.group(2).strip()
            hash_to_paths.setdefault(h, []).append(path)

    findings: list[dict] = []
    for h, paths in sorted(hash_to_paths.items()):
        if len(paths) > 1:
            findings.append({
                "hash": h,
                "paths": paths,
            })

    total_lines = len(all_lines)
    distinct_artifacts = len(hash_to_paths)

    # Prepend a metadata object as the first element
    output = [
        {
            "_summary": {
                "MANIFEST_LINES": total_lines,
                "DISTINCT_ARTIFACTS": distinct_artifacts,
            }
        }
    ]
    output.extend(findings)

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()