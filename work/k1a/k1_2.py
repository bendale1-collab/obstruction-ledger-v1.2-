#!/usr/bin/env python3
"""K1-2 — divergence-declaration check.

For each manifest path: diff seal-commit vs HEAD. Report SAME or
DIFFERS with nature = APPEND / EDIT / RENUMBER / DELETE. Every DIFFERS
must cite a declaring ledger entry outside the diverging file.
Undeclared divergence, or declaration only by self-reference, is a finding.

Output: full per-path table. Count-only output is itself a finding.

Two modes:
- Git mode: repo root, seal commit vs HEAD over MANIFEST.sha256
- Fixture mode: directory with seal/, head/, MANIFEST

Interface: path as CLI argument. JSON array to stdout.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def detect_mode(input_path: Path) -> str:
    """Detect whether input is fixture mode or git mode."""
    if input_path.is_dir():
        if (input_path / "MANIFEST").exists() and (input_path / "seal").is_dir():
            return "fixture"
    return "git"


def read_manifest_fixture(fixture_dir: Path) -> list[str]:
    """Read MANIFEST file in fixture mode."""
    manifest_file = fixture_dir / "MANIFEST"
    if not manifest_file.exists():
        return []
    lines = manifest_file.read_text().strip().splitlines()
    return [line.strip() for line in lines if line.strip()]


def read_manifest_git(repo_root: Path) -> list[str]:
    """Read MANIFEST.sha256 in git mode."""
    manifest_file = repo_root / "MANIFEST.sha256"
    if not manifest_file.exists():
        return []
    paths = []
    for line in manifest_file.read_text().splitlines():
        line = line.strip()
        if line:
            # Format: hash  path
            parts = line.split(None, 1)
            if len(parts) >= 2:
                paths.append(parts[1])
    return paths


def get_seal_commit(repo_root: Path) -> str | None:
    """Get seal commit from git log or tags."""
    try:
        result = subprocess.run(
            ["git", "tag", "-l", "*seal*"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip():
            return result.stdout.strip().split()[0]
    except subprocess.CalledProcessError:
        pass

    # Fallback: look for commit message with "seal"
    try:
        result = subprocess.run(
            ["git", "log", "--all", "--grep=seal", "--format=%H", "-1"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip():
            return result.stdout.strip()
    except subprocess.CalledProcessError:
        pass

    return None


def get_file_content_git(repo_root: Path, commit: str, path: str) -> str | None:
    """Get file content at a git commit."""
    try:
        result = subprocess.run(
            ["git", "show", f"{commit}:{path}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def get_file_content_fixture(base_dir: Path, subdir: str, path: str) -> str | None:
    """Get file content from fixture directory."""
    file_path = base_dir / subdir / path
    if file_path.exists():
        return file_path.read_text()
    return None


def determine_nature(seal_content: str | None, head_content: str | None) -> str:
    """Determine the nature of the difference."""
    if seal_content is None and head_content is not None:
        return "INSERT"
    if seal_content is not None and head_content is None:
        return "DELETE"
    if seal_content is None and head_content is None:
        return "SAME"

    # Both exist
    assert seal_content is not None
    assert head_content is not None

    if seal_content == head_content:
        return "SAME"

    # Check if append-only
    if head_content.startswith(seal_content):
        return "APPEND"

    # Check if headers changed (RENUMBER)
    seal_headers = [
        line for line in seal_content.splitlines() if line.strip().startswith("#")
    ]
    head_headers = [
        line for line in head_content.splitlines() if line.strip().startswith("#")
    ]
    if seal_headers != head_headers:
        return "RENUMBER"

    # Otherwise it's an edit
    return "EDIT"


def find_declaring_entries_fixture(
    fixture_dir: Path, path: str
) -> list[str]:
    """Find declaring ledger entries in fixture mode."""
    declaring = []
    ledger_dir = fixture_dir / "head" / "ledger"
    if not ledger_dir.exists():
        return declaring

    for ledger_file in ledger_dir.glob("*"):
        if ledger_file.is_file():
            content = ledger_file.read_text()
            if path in content:
                declaring.append(f"ledger/{ledger_file.name}")

    return declaring


def find_declaring_entries_git(repo_root: Path, path: str) -> list[str]:
    """Find declaring ledger entries in git mode."""
    declaring = []
    ledger_dir = repo_root / "ledger"
    if not ledger_dir.exists():
        return declaring

    for ledger_file in ledger_dir.glob("*.md"):
        if ledger_file.is_file():
            content = ledger_file.read_text()
            if path in content:
                declaring.append(f"ledger/{ledger_file.name}")

    return declaring


def check_k1_2_fixture(fixture_dir: Path) -> list[dict]:
    """Run K1-2 in fixture mode."""
    findings = []
    manifest_paths = read_manifest_fixture(fixture_dir)

    if not manifest_paths:
        findings.append({
            "path": "MANIFEST",
            "status": "FINDING",
            "reason": "empty or missing MANIFEST",
        })
        return findings

    for path in manifest_paths:
        seal_content = get_file_content_fixture(fixture_dir, "seal", path)
        head_content = get_file_content_fixture(fixture_dir, "head", path)
        nature = determine_nature(seal_content, head_content)

        if nature == "SAME":
            findings.append({
                "path": path,
                "status": "SAME",
                "nature": "SAME",
            })
            continue

        # Find declaring entries
        declaring = find_declaring_entries_fixture(fixture_dir, path)

        # Filter out self-references
        declaring = [d for d in declaring if d != path]

        if not declaring:
            findings.append({
                "path": path,
                "status": "FINDING",
                "nature": nature,
                "reason": "undeclared divergence",
                "declaring_entries": [],
            })
        else:
            findings.append({
                "path": path,
                "status": "DIFFERS",
                "nature": nature,
                "declaring_entries": declaring,
            })

    return findings


def check_k1_2_git(repo_root: Path) -> list[dict]:
    """Run K1-2 in git mode."""
    findings = []
    manifest_paths = read_manifest_git(repo_root)

    if not manifest_paths:
        findings.append({
            "path": "MANIFEST.sha256",
            "status": "FINDING",
            "reason": "empty or missing MANIFEST.sha256",
        })
        return findings

    seal_commit = get_seal_commit(repo_root)
    if not seal_commit:
        findings.append({
            "path": "seal_commit",
            "status": "FINDING",
            "reason": "could not determine seal commit",
        })
        return findings

    for path in manifest_paths:
        seal_content = get_file_content_git(repo_root, seal_commit, path)
        head_content = get_file_content_git(repo_root, "HEAD", path)
        nature = determine_nature(seal_content, head_content)

        if nature == "SAME":
            findings.append({
                "path": path,
                "status": "SAME",
                "nature": "SAME",
            })
            continue

        # Find declaring entries
        declaring = find_declaring_entries_git(repo_root, path)

        # Filter out self-references
        declaring = [d for d in declaring if d != path]

        if not declaring:
            findings.append({
                "path": path,
                "status": "FINDING",
                "nature": nature,
                "reason": "undeclared divergence",
                "declaring_entries": [],
            })
        else:
            findings.append({
                "path": path,
                "status": "DIFFERS",
                "nature": nature,
                "declaring_entries": declaring,
            })

    return findings


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps([]))
        sys.exit(0)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(json.dumps([]))
        sys.exit(0)

    mode = detect_mode(input_path)

    if mode == "fixture":
        findings = check_k1_2_fixture(input_path)
    else:
        findings = check_k1_2_git(input_path)

    print(json.dumps(findings, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
