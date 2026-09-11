#!/usr/bin/env python3
"""K1-6 — declared extension vs content.

Implements K1-6 of checker-k1-prereg.md v0.3 §2:

    Every manifest path with a machine-readable extension (.yaml, .yml,
    .json) must parse under that format at the stated commit
    (yaml.safe_load / json.load). Parse failure is a finding, reported
    with the parser error.
    Output: (path, extension, PARSE / FAIL + error).

Interface (task contract): file or directory paths as CLI arguments; JSON
array to stdout; one object per finding; exit 0 even when findings exist.
Findings are parse failures only (FAIL rows, each carrying the parser
error); paths that parse emit nothing, and a run with no failures emits
[].

A git commit-ish is also accepted: reads MANIFEST.sha256 at that commit
and checks its .yaml/.yml/.json paths at that commit. "COMMIT:PATH" uses
the manifest at PATH at COMMIT. Directory arguments check every
.yaml/.yml/.json file beneath them.

Files with other extensions are out of scope: no check, no finding.
.yaml and .yml parse via yaml.safe_load (PyYAML, imported lazily only
when a YAML path is actually checked); .json via json.load. Content is
decoded strictly as UTF-8; a decode failure is reported as a FAIL with
the decode error.
"""

import io
import json
import subprocess
import sys
from pathlib import Path

MACHINE_EXTS = ('.yaml', '.yml', '.json')


def die(msg):
    print('k1_6: error: %s' % msg, file=sys.stderr)
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


def read_bytes(path):
    try:
        with open(path, 'rb') as f:
            return f.read()
    except OSError as e:
        die('cannot read %s: %s' % (path, e))


def manifest_paths_from(text):
    """Paths column of a sha256sum-format manifest (second token onward)."""
    paths = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            paths.append(parts[1].strip())
    return paths


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


def check(path, raw):
    """One finding for a parse failure under the declared extension."""
    ext = Path(path).suffix.lower()
    if ext not in MACHINE_EXTS:
        return None
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError as e:
        return {'path': path, 'extension': ext, 'status': 'FAIL',
                'parser': 'utf-8 decode', 'error': str(e)}
    if ext == '.json':
        try:
            json.load(io.StringIO(text))
        except Exception as e:
            return {'path': path, 'extension': ext, 'status': 'FAIL',
                    'parser': 'json.load', 'error': str(e)}
        return None
    try:
        import yaml
    except ImportError:
        die('PyYAML is required to check .yaml/.yml paths '
            '(python3 -m pip install pyyaml)')
    try:
        yaml.safe_load(io.StringIO(text))
    except Exception as e:
        return {'path': path, 'extension': ext, 'status': 'FAIL',
                'parser': 'yaml.safe_load', 'error': str(e)}
    return None


def main(argv):
    if not argv:
        die('usage: k1_6.py PATH...  '
            '(files, directories, commit-ish, or COMMIT:PATH)')
    targets = []  # (path, raw bytes)
    for arg in argv:
        p = Path(arg)
        if p.is_file():
            targets.append((str(p), read_bytes(p)))
        elif p.is_dir():
            for q in sorted(p.rglob('*')):
                if q.is_file() and q.suffix.lower() in MACHINE_EXTS:
                    targets.append((str(q.relative_to(p)), read_bytes(q)))
        else:
            if ':' in arg:
                rev, sub = arg.split(':', 1)
            else:
                rev, sub = arg, None
            sha = rev_commit(rev)
            if not sha:
                die('argument %r is not an existing file, directory, or '
                    'git commit' % arg)
            _label, text = manifest_at_commit(sha, sub)
            for path in manifest_paths_from(text):
                if Path(path).suffix.lower() in MACHINE_EXTS:
                    rc, out, err = git(['show', '%s:%s' % (sha, path)])
                    if rc != 0:
                        die('manifest path %r not found at commit %s: %s'
                            % (path, sha, err.strip()))
                    targets.append((path, out))
    findings = []
    for path, raw in targets:
        f = check(path, raw)
        if f:
            findings.append(f)
    print(json.dumps(findings, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
