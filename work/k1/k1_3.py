#!/usr/bin/env python3
"""K1-3 — section-structure stability.

Implements K1-3 of checker-k1-prereg.md v0.3 §2:

    For each sealed file: header text and numbering at HEAD must equal the
    seal commit. Any inserted, removed, or renumbered header is a finding.
    Appended headers after the original final header are permitted only if
    the original headers are unchanged.
    Output: (path, header diff).

Interface (task contract): file or directory paths as CLI arguments; JSON
array to stdout; one object per finding; exit 0 even when findings exist.
K1-3 additionally accepts a git commit pair.

Usage:
    k1_3.py BEFORE_FILE AFTER_FILE     file pair (before, after)
    k1_3.py BEFORE_DIR AFTER_DIR       directory pair, files matched by
                                       relative path
    k1_3.py SEAL_COMMIT HEAD_COMMIT    git commit pair; the file set is the
                                       manifest at the BEFORE commit (all
                                       tracked files if there is none)

Mechanics, from the spec text:
  * A header is a markdown ATX heading line: up to three leading spaces,
    one to six '#', then a space or end of line. Every file in scope is
    scanned; the sealed set is not extension-filtered.
  * Header identity is the raw heading line with trailing whitespace
    stripped. The before/after header lists are compared in order.
  * If the after-side list begins with the entire before-side list, the
    original headers are unchanged and anything beyond them is the
    permitted append case: no finding. (A before-side file with no
    headers that gains headers is therefore silent; all additions are
    trailing appends.)
  * Any other difference is one finding per file, classified per header:
    inserted / removed / renumbered (leading section number changed while
    level and title are unchanged) / changed (title or level edited).
  * A file present on the before side and absent on the after side
    reports its before-side headers as removed. A headerless absent file
    reports nothing; file-level divergence is K1-2's scope, not K1-3's.

Exit codes: 0 = check ran (findings or not); 2 = usage or input error,
reported to stderr.
"""

import json
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

ATX = re.compile(r'^ {0,3}(#{1,6})(?:\s+(.*))?$')
SECTION_NUM = re.compile(r'^(?:§\s*)?(\d+)\s*[.)]?\s*(.*)$')


def die(msg):
    print('k1_3: error: %s' % msg, file=sys.stderr)
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


def extract_headers(text):
    """[(line_number, raw_heading_line)], trailing whitespace stripped."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if ATX.match(line):
            out.append((n, line.rstrip()))
    return out


def header_parts(raw):
    """(level, number-or-None, title) for renumber-vs-edit classification."""
    m = ATX.match(raw)
    level = len(m.group(1))
    rest = (m.group(2) or '').strip()
    nm = SECTION_NUM.match(rest)
    if nm:
        return level, nm.group(1), nm.group(2).strip()
    return level, None, rest


def classify(old, new):
    """renumbered vs changed for an aligned pair of differing headers."""
    lo, no, to = header_parts(old)
    ln, nn, tn = header_parts(new)
    if (lo == ln and no is not None and nn is not None
            and no != nn and to == tn):
        return 'renumbered'
    return 'changed'


def compare(path, before_text, after_text, before_src, after_src):
    """One finding per file whose header structure is not stable, else None."""
    bh = extract_headers(before_text)
    ah = extract_headers(after_text)
    b = [raw for _, raw in bh]
    a = [raw for _, raw in ah]
    if a[:len(b)] == b:
        # Originals unchanged; anything beyond them is a permitted
        # trailing append (also covers the fully-equal case).
        return None
    entries = []
    sm = SequenceMatcher(a=b, b=a, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        if tag == 'replace':
            paired = min(i2 - i1, j2 - j1)
            for k in range(paired):
                entries.append({
                    'op': classify(b[i1 + k], a[j1 + k]),
                    'before_header': bh[i1 + k][1],
                    'before_line': bh[i1 + k][0],
                    'after_header': ah[j1 + k][1],
                    'after_line': ah[j1 + k][0]})
            for k in range(i1 + paired, i2):
                entries.append({
                    'op': 'removed',
                    'before_header': bh[k][1], 'before_line': bh[k][0],
                    'after_header': None, 'after_line': None})
            for k in range(j1 + paired, j2):
                entries.append({
                    'op': 'inserted',
                    'before_header': None, 'before_line': None,
                    'after_header': ah[k][1], 'after_line': ah[k][0]})
        elif tag == 'delete':
            for k in range(i1, i2):
                entries.append({
                    'op': 'removed',
                    'before_header': bh[k][1], 'before_line': bh[k][0],
                    'after_header': None, 'after_line': None})
        elif tag == 'insert':
            for k in range(j1, j2):
                entries.append({
                    'op': 'inserted',
                    'before_header': None, 'before_line': None,
                    'after_header': ah[k][1], 'after_line': ah[k][0]})
    if not entries:
        return None
    return {'path': path,
            'before_source': before_src,
            'after_source': after_src,
            'header_diff': entries}


def removed_file(path, before_text, before_src, after_src):
    """File gone on the after side: all of its before-side headers removed."""
    bh = extract_headers(before_text)
    if not bh:
        return None
    entries = [{'op': 'removed',
                'before_header': raw, 'before_line': n,
                'after_header': None, 'after_line': None} for n, raw in bh]
    return {'path': path,
            'before_source': before_src,
            'after_source': after_src,
            'header_diff': entries}


def tracked_files(sha):
    rc, out, err = git(['ls-tree', '-r', '--name-only', sha])
    if rc != 0:
        die('cannot list tracked files at %s: %s' % (sha, err.strip()))
    return [l for l in dec(out).splitlines() if l]


def parse_manifest_paths(text):
    """Paths column of a sha256sum-format manifest (second token onward)."""
    paths = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            paths.append(parts[1].strip())
    return paths


def manifest_paths(sha):
    """Sealed-file set at a commit: MANIFEST.sha256 paths, else all tracked.

    Root MANIFEST.sha256 first; otherwise a single file named
    MANIFEST.sha256 anywhere in the tree; ambiguity is an error, never a
    guess.
    """
    rc, out, _ = git(['show', '%s:MANIFEST.sha256' % sha])
    if rc == 0:
        return parse_manifest_paths(dec(out))
    files = tracked_files(sha)
    cands = [f for f in files if Path(f).name == 'MANIFEST.sha256']
    if len(cands) > 1:
        die('multiple MANIFEST.sha256 files at %s: %s'
            % (sha, ', '.join(cands)))
    if len(cands) == 1:
        rc, out, _ = git(['show', '%s:%s' % (sha, cands[0])])
        return parse_manifest_paths(dec(out))
    return files


class CommitSource(object):
    """File views of one git commit, manifest-scoped."""

    def __init__(self, sha):
        self.sha = sha

    def paths(self):
        return manifest_paths(self.sha)

    def get(self, path):
        rc, out, _ = git(['show', '%s:%s' % (self.sha, path)])
        return dec(out) if rc == 0 else None

    def desc(self):
        return self.sha


class DirSource(object):
    """File views of a directory tree, keyed by relative path."""

    def __init__(self, root):
        self.root = Path(root)

    def paths(self):
        return sorted(str(p.relative_to(self.root))
                      for p in self.root.rglob('*') if p.is_file())

    def get(self, rel):
        try:
            return (self.root / rel).read_text(encoding='utf-8',
                                               errors='replace')
        except OSError:
            return None

    def desc(self):
        return str(self.root)


def resolve(arg):
    """('file'|'dir'|'commit', value) for one CLI argument."""
    p = Path(arg)
    if p.is_file():
        return 'file', p
    if p.is_dir():
        return 'dir', p
    sha = rev_commit(arg)
    if sha:
        return 'commit', sha
    die('argument %r is not an existing file, directory, or git commit'
        % arg)


def main(argv):
    if len(argv) != 2:
        die('usage: k1_3.py BEFORE AFTER  '
            '(file pair, directory pair, or commit pair)')
    bkind, bval = resolve(argv[0])
    akind, aval = resolve(argv[1])
    findings = []
    if bkind == 'file' and akind == 'file':
        f = compare(str(aval), read_text(bval), read_text(aval),
                    str(bval), str(aval))
        if f:
            findings.append(f)
    elif bkind == 'file' or akind == 'file':
        other = 'directory' if (bkind == 'dir' or akind == 'dir') else 'commit'
        die('a file argument must be paired with a file, not a %s' % other)
    else:
        before = CommitSource(bval) if bkind == 'commit' else DirSource(bval)
        after = CommitSource(aval) if akind == 'commit' else DirSource(aval)
        for rel in before.paths():
            btext = before.get(rel)
            if btext is None:
                # Listed on the before side but not present there; nothing
                # to compare.
                continue
            atext = after.get(rel)
            if atext is None:
                f = removed_file(rel, btext, before.desc(), after.desc())
            else:
                f = compare(rel, btext, atext, before.desc(), after.desc())
            if f:
                findings.append(f)
    print(json.dumps(findings, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
