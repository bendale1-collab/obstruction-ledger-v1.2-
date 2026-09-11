#!/usr/bin/env python3
"""
K1-2 — divergence-declaration

For each manifest path: diff seal-commit vs HEAD. Report SAME or DIFFERS
with nature = APPEND / EDIT / RENUMBER / DELETE. Every DIFFERS must cite
a declaring ledger entry outside the diverging file. Undeclared divergence,
or declaration only by self-reference, is a finding.

Output: full per-path table. Count-only output is itself a finding.

Input: 
  Git mode: --git <seal_commit> [<head_commit>] (default HEAD)
  Fixture mode: <directory> containing seal/, head/, and MANIFEST

Output: JSON array to stdout; one object per path
Exit: 0 even when findings exist
"""

import sys
import json
import subprocess
from pathlib import Path


def git_show(commit: str, path: str) -> bytes | None:
    """Get file content at a specific commit."""
    try:
        result = subprocess.run(
            ['git', 'show', f'{commit}:{path}'],
            capture_output=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def diff_nature(old_content: bytes | None, new_content: bytes | None) -> tuple[str, str]:
    """Determine if content is SAME or DIFFERS, and the nature of change."""
    if old_content is None and new_content is None:
        return 'SAME', 'NEITHER'
    
    if old_content is None:
        return 'DIFFERS', 'APPEND'  # File added
    
    if new_content is None:
        return 'DIFFERS', 'DELETE'  # File removed
    
    if old_content == new_content:
        return 'SAME', 'UNCHANGED'
    
    # Content differs — determine nature
    old_lines = old_content.decode('utf-8', errors='replace').splitlines()
    new_lines = new_content.decode('utf-8', errors='replace').splitlines()
    
    # Check if it's an append (old content is prefix of new content)
    if len(new_lines) > len(old_lines):
        # Check if old lines are unchanged at start
        if old_lines == new_lines[:len(old_lines)]:
            return 'DIFFERS', 'APPEND'
    
    # Check for renumber (headers changed but content similar)
    # Simple heuristic: if line count changed and headers differ
    old_headers = [l for l in old_lines if l.startswith('#')]
    new_headers = [l for l in new_lines if l.startswith('#')]
    
    if old_headers != new_headers:
        # Headers changed — could be renumber or edit
        if len(old_headers) != len(new_headers):
            return 'DIFFERS', 'RENUMBER'
    
    # Default to EDIT
    return 'DIFFERS', 'EDIT'


def find_declaring_entry(path: str, ledger_dir: Path | None) -> str | None:
    """Find a ledger entry declaring the divergence for this path."""
    if ledger_dir is None or not ledger_dir.exists():
        return None
    
    # Look for ledger files that mention the path
    for ledger_file in ledger_dir.glob('*.md'):
        try:
            content = ledger_file.read_text(encoding='utf-8')
            if path in content:
                return str(ledger_file)
        except Exception:
            pass
    
    return None


def check_k1_2_git(seal_commit: str, head_commit: str, manifest_path: str) -> list[dict]:
    """Check K1-2 in git mode."""
    findings = []
    
    # Read manifest at HEAD
    manifest_content = git_show(head_commit, manifest_path)
    if manifest_content is None:
        return [{'error': f'Manifest {manifest_path} not found at {head_commit}'}]
    
    # Parse manifest (sha256sum format)
    lines = manifest_content.decode('utf-8').strip().split('\n')
    paths = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.split('  ', 1)
        if len(parts) == 2:
            paths.append(parts[1])
    
    # Check each path
    for path in paths:
        old_content = git_show(seal_commit, path)
        new_content = git_show(head_commit, path)
        
        status, nature = diff_nature(old_content, new_content)
        
        finding = {
            'path': path,
            'status': status,
            'nature': nature
        }
        
        if status == 'DIFFERS':
            # Look for declaring entry (would need ledger dir from git)
            finding['declaring_entry'] = None
            finding['reason'] = 'Undeclared divergence'
        
        findings.append(finding)
    
    return findings


def check_k1_2_fixture(fixture_dir: Path) -> list[dict]:
    """Check K1-2 in fixture mode."""
    findings = []
    
    seal_dir = fixture_dir / 'seal'
    head_dir = fixture_dir / 'head'
    manifest_file = fixture_dir / 'MANIFEST'
    ledger_dir = fixture_dir / 'ledger' if (fixture_dir / 'ledger').exists() else None
    
    if not manifest_file.exists():
        return [{'error': f'MANIFEST not found in {fixture_dir}'}]
    
    # Read manifest
    manifest_content = manifest_file.read_text(encoding='utf-8')
    lines = manifest_content.strip().split('\n')
    paths = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.split('  ', 1)
        if len(parts) == 2:
            paths.append(parts[1])
    
    # Check each path
    for path in paths:
        seal_file = seal_dir / path
        head_file = head_dir / path
        
        old_content = seal_file.read_bytes() if seal_file.exists() else None
        new_content = head_file.read_bytes() if head_file.exists() else None
        
        status, nature = diff_nature(old_content, new_content)
        
        finding = {
            'path': path,
            'status': status,
            'nature': nature
        }
        
        if status == 'DIFFERS':
            # Look for declaring entry
            declaring = find_declaring_entry(path, ledger_dir)
            finding['declaring_entry'] = declaring
            if declaring is None:
                finding['reason'] = 'Undeclared divergence'
            elif declaring.endswith(path):
                finding['reason'] = 'Self-referential declaration'
        
        findings.append(finding)
    
    return findings


def main():
    if len(sys.argv) < 2:
        print(json.dumps([]))
        sys.exit(0)
    
    all_findings = []
    
    # Check for git mode
    if '--git' in sys.argv:
        git_idx = sys.argv.index('--git')
        if git_idx + 1 >= len(sys.argv):
            print(json.dumps([{'error': '--git requires seal commit SHA'}]))
            sys.exit(0)
        
        seal_commit = sys.argv[git_idx + 1]
        head_commit = sys.argv[git_idx + 2] if git_idx + 2 < len(sys.argv) else 'HEAD'
        manifest_path = sys.argv[git_idx + 3] if git_idx + 3 < len(sys.argv) else 'MANIFEST.sha256'
        
        findings = check_k1_2_git(seal_commit, head_commit, manifest_path)
        all_findings.extend(findings)
    
    else:
        # Fixture mode: each argument is a fixture directory
        for arg in sys.argv[1:]:
            fixture_dir = Path(arg)
            if not fixture_dir.exists():
                all_findings.append({'error': f'Directory not found: {arg}'})
                continue
            
            if fixture_dir.is_dir():
                findings = check_k1_2_fixture(fixture_dir)
                for f in findings:
                    f['fixture'] = str(fixture_dir)
                all_findings.extend(findings)
    
    print(json.dumps(all_findings, indent=2))
    sys.exit(0)


if __name__ == '__main__':
    main()
