#!/usr/bin/env python3
"""K1-5 — duplicate hash within manifest.

Implements K1-5 of checker-k1-prereg.md v0.3 §2:

    Every hash in MANIFEST.sha256 must be unique. Two paths with one hash
    is a finding, reported with both paths. Distinct-artifact count is
    reported alongside the line count.
    Output: (hash, [paths]); MANIFEST_LINES vs DISTINCT_ARTIFACTS.

Interface (task contract): file or directory paths as CLI arguments; JSON
array to stdout; one object per finding; exit 0 even when findings exist.
One finding per duplicated hash, carrying the hash, every path sharing it,
the manifest's line count (MANIFEST_LINES) and its distinct-artifact count
(DISTINCT_ARTIFACTS). A clean manifest emits [].

A git commit-ish is also accepted: reads MANIFEST.sha256 at that commit.
"COMMIT:PATH" reads the manifest at PATH at COMMIT (for manifests that are
not the root MANIFEST.sha256, e.g. K1-MANIFEST.sha256).

Directory arguments: every file beneath the directory is checked as a
manifest if its name contains MANIFEST and ends .sha256, or if its content
is sha256sum format (every non-empty line begins with a 64-hex digest).
Explicitly passed files are parsed as manifests regardless of name.

Lines are parsed leniently (first whitespace-separated token = hash, the
remainder = path); MANIFEST_LINES counts non-empty lines.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

SNIFF_LINE = re.compile(r'^[0-9a-fA-F]{64}(?:\s|$)')


def die(msg):
    print('k1_5: error: %s' % msg, file=sys.stderr)
    sys.exit(2)


def git(args):
    try:
        r = subprocess.run(['git'] + args, capture_output=True)
    except FileNotFoundError:
        die('git is not available')
    return r.returncode, r.stdout, r.stderr.decode('utf-8', 'replace')


def dec(raw):
    return raw.decode('utf-8', 'replace')


def rev_commit(arg):
    rc, out, _ = git(['rev-parse', '--verify', arg + '^{commit}'])
    if rc != 0:
        return None
    sha = dec(out).strip()
    return sha or None


def read_text(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except OSError as e:
        die('cannot read %s: %s' % (path, e))


def parse_entries(text):
    """[{line, hash, path}] for every non-empty line, in file order."""
    entries = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split(None, 1)
        entries.append({'line': n,
                        'hash': parts[0],
                        'path': parts[1].strip() if len(parts) > 1 else ''})
    return entries


def looks_like_manifest(text):
    """True when every non-empty line starts with a 64-hex digest
    (sha256sum output format)."""
    lines = [l for l in text.splitlines() if l.strip()]
    return bool(lines) and all(SNIFF_LINE.match(l.strip()) for l in lines)


def check(source, text):
    """One finding per hash carried by more than one manifest line."""
    entries = parse_entries(text)
    order = []
    by_hash = {}
    for e in entries:
        if e['hash'] not in by_hash:
            by_hash[e['hash']] = []
            order.append(e['hash'])
        by_hash[e['hash']].append(e)
    manifest_lines = len(entries)
    distinct = len(by_hash)
    findings = []
    for h in order:
        group = by_hash[h]
        if len(group) < 2:
            continue
        findings.append({
            'manifest': source,
            'hash': h,
            'paths': [e['path'] for e in group],
            'lines': [e['line'] for e in group],
            'manifest_lines': manifest_lines,
            'distinct_artifacts': distinct,
        })
    return findings


def manifest_at_commit(sha, sub):
    """(label, text) for the manifest at a commit.

    sub given: that path. sub None: root MANIFEST.sha256, else the single
    file named MANIFEST.sha256 in the tree; none or several is an error,
    never a guess.
    """
    if sub is not None:
        rc, out, err = git(['show', '%s:%s' % (sha, sub)])
        if rc != 0:
            die('manifest %r not found at commit %s: %s'
                % (sub, sha, err.strip()))
        return '%s:%s' % (sha, sub), dec(out)
    rc, out, _ = git(['show', '%s:MANIFEST.sha256' % sha])
    if rc == 0:
        return '%s:MANIFEST.sha256' % sha, dec(out)
    rc, out, err = git(['ls-tree', '-r', '--name-only', sha])
    if rc != 0:
        die('cannot list files at commit %s: %s' % (sha, err.strip()))
    cands = [l for l in dec(out).splitlines()
             if l and Path(l).name == 'MANIFEST.sha256']
    if len(cands) == 1:
        return manifest_at_commit(sha, cands[0])
    if len(cands) > 1:
        die('multiple MANIFEST.sha256 files at %s: %s'
            % (sha, ', '.join(cands)))
    die('no MANIFEST.sha256 found at commit %s' % sha)


def main(argv):
    if not argv:
        die('usage: k1_5.py MANIFEST...  '
            '(manifest file, directory, commit-ish, or COMMIT:PATH)')
    sources = []
    for arg in argv:
        p = Path(arg)
        if p.is_file():
            sources.append((str(p), read_text(p)))
        elif p.is_dir():
            found = []
            for q in sorted(p.rglob('*')):
                if not q.is_file():
                    continue
                text = read_text(q)
                if (('MANIFEST' in q.name and q.name.endswith('.sha256'))
                        or looks_like_manifest(text)):
                    found.append((str(q.relative_to(p)), text))
            if not found:
                die('no manifest files found under %s' % arg)
            sources.extend(found)
        else:
            if ':' in arg:
                rev, sub = arg.split(':', 1)
            else:
                rev, sub = arg, None
            sha = rev_commit(rev)
            if not sha:
                die('argument %r is not an existing file, directory, or '
                    'git commit' % arg)
            sources.append(manifest_at_commit(sha, sub))
    findings = []
    for source, text in sources:
        findings.extend(check(source, text))
    print(json.dumps(findings, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
