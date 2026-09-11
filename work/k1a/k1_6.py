"""
K1-6 — Declared extension vs content

Every manifest path with a machine-readable extension (.yaml, .yml, .json)
must parse under that format at the stated commit (yaml.safe_load /
json.load). Parse failure is a finding, reported with the parser error.

Usage: python k1_6.py <manifest_file> [base_directory]
Output: JSON array to stdout.
"""

import json
import os
import sys


def _try_json(text: str) -> tuple[bool, str]:
    """Attempt json.load. Returns (ok, error_msg)."""
    try:
        json.loads(text)
        return True, ""
    except json.JSONDecodeError as e:
        return False, str(e)


def _try_yaml(text: str, yaml_module) -> tuple[bool, str]:
    """Attempt yaml.safe_load. Returns (ok, error_msg)."""
    try:
        yaml_module.safe_load(text)
        return True, ""
    except Exception as e:  # yaml can raise various parser errors
        return False, str(e)


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps([
            {"error": "Usage: k1_6.py <manifest_file> [base_directory]"}
        ]))
        sys.exit(1)

    manifest_path = sys.argv[1]
    base_dir: str | None = None
    if len(sys.argv) >= 3:
        base_dir = sys.argv[2]

    # Determine base directory from manifest path if not given explicitly
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(manifest_path))

    try:
        with open(manifest_path) as f:
            manifest_lines = f.read().splitlines()
    except FileNotFoundError:
        print(json.dumps([{"error": f"Manifest file not found: {manifest_path}"}]))
        sys.exit(1)

    # Import yaml lazily
    try:
        import yaml as _yaml_mod
    except ImportError:
        _yaml_mod = None  # type: ignore[assignment]

    findings: list[dict] = []

    for line in manifest_lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        parts = line.split(None, 1)
        if len(parts) < 2:
            continue

        _h, path = parts[0], parts[1].strip()

        ext = os.path.splitext(path)[1].lower()
        if ext not in ('.yaml', '.yml', '.json'):
            continue

        full_path = path if os.path.isabs(path) else os.path.join(base_dir, path)

        if not os.path.isfile(full_path):
            findings.append({
                "path": path,
                "extension": ext,
                "status": "FAIL",
                "error": f"File not found: {full_path}",
            })
            continue

        try:
            with open(full_path) as f:
                content = f.read()
        except Exception as e:
            findings.append({
                "path": path,
                "extension": ext,
                "status": "FAIL",
                "error": f"Read error: {e}",
            })
            continue

        if ext == '.json':
            ok, err = _try_json(content)
        elif ext in ('.yaml', '.yml'):
            if _yaml_mod is None:
                findings.append({
                    "path": path,
                    "extension": ext,
                    "status": "FAIL",
                    "error": "PyYAML is not installed",
                })
                continue
            ok, err = _try_yaml(content, _yaml_mod)
        else:
            # Should not reach (filtered above)
            continue

        if ok:
            findings.append({
                "path": path,
                "extension": ext,
                "status": "PARSE",
                "error": "",
            })
        else:
            findings.append({
                "path": path,
                "extension": ext,
                "status": "FAIL",
                "error": err,
            })

    print(json.dumps(findings))
    sys.exit(0)


if __name__ == "__main__":
    main()