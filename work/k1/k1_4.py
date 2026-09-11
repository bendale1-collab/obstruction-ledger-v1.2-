#!/usr/bin/env python3
"""K1-4 — identifier well-formedness.

Implements K1-4 of checker-k1-prereg.md v0.3 §2:

    Any hex string that is a prefix-match (≥10 chars) of a canonical anchor
    value, or sits after a label (Gist ID:, FREEZE_HASH=, SHA, commit), must
    be exactly canonical length: SHA-256 = 64, git SHA = 40 or 7, gist ID =
    32. Any other length is a finding — including 31 (dropped character),
    10 (truncation), or 65 (inserted character). Where a canonical value is
    recorded in the bundle (STATE.yaml, SEAL-PACKET.md,
    seal-detached-v1.5.md), the full string must match it. Malformation,
    not only truncation.
    Scope: tracked files at the stated commit. Blocks under a QUOTED or
    DERIVED header (same convention as K1-1) are skipped — audit files that
    document malformed identifiers must carry the header or they fire.
    Output: (location, identifier, expected length, found length, anchor
    match).

Interface (task contract): file or directory paths as CLI arguments; JSON
array to stdout; one object per finding; exit 0 even when findings exist.
A git commit-ish is also accepted (scope: every tracked file at that
commit).

Mechanics, from the spec text:
  * Labels are matched exactly as written, case-sensitively, with word
    boundaries: "Gist ID:", "FREEZE_HASH" (the spec writes "FREEZE_HASH=";
    an immediately following colon is also accepted for YAML-style
    records), "SHA", "commit". The identifier is the first hex token after
    the label on the same line, separated only by whitespace or colons.
  * Canonical lengths by kind: gist ID = 32, SHA-256 = 64, git SHA = 40 or
    7. Label -> kind: "Gist ID:" -> gist ID; "FREEZE_HASH" -> SHA-256;
    "SHA" -> any SHA (SHA-256 or git); "commit" -> git.
  * Canonical anchor values are the hex tokens of length exactly 64, 40,
    or 32 found in files named STATE.yaml, SEAL-PACKET.md, or
    seal-detached-v1.5.md among the inputs (the bundle's canonical-value
    records, per the spec).
  * Prefix-match: a hex token sharing a common prefix of >= 10 characters
    with a canonical anchor value is presenting as that value and must
    equal it exactly. Canonical length with different content is still a
    finding (malformation, not only truncation). A token equal to some
    anchor value passes.
  * QUOTED/DERIVED skip: a line beginning with QUOTED or DERIVED (column
    zero) opens a skipped block. The block ends at the next markdown
    header line or at end of file — the R8c convention is one prepended
    line covering the evidence below, which this reproduces.

Exit codes: 0 = check ran (findings or not); 2 = usage or input error,
reported to stderr.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

HEX_TOKEN = re.compile(r'[0-9a-fA-F]+')
SKIP_OPEN = re.compile(r'^(QUOTED|DERIVED)\b')
BLOCK_END = re.compile(r'^ {0,3}#{1,6}(?:\s|$)')

ANCHOR_RECORDS = ('STATE.yaml', 'SEAL-PACKET.md', 'seal-detached-v1.5.md')
ANCHOR_KINDS = {64: 'sha256', 40: 'git_sha', 32: 'gist_id'}
CANONICAL = {'sha256': [64], 'git_sha': [7, 40], 'gist_id': [32]}

LABELS = (
    ('Gist ID:', ('gist_id',), re.compile(r'Gist ID:')),
    ('FREEZE_HASH=', ('sha256',),
     re.compile(r'(?<![A-Za-z0-9_])FREEZE_HASH[=:]')),
    ('SHA', ('sha256', 'git_sha'),
     re.compile(r'(?<![A-Za-z0-9_])SHA(?![A-Za-z0-9_])')),
    ('commit', ('git_sha',),
     re.compile(r'(?<![A-Za-z0-9_])commit(?![A-Za-z0-9_])')),
)
GAP = frozenset(' \t\r:')


def die(msg):
    print('k1_4: error: %s' % msg, file=sys.stderr)
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


def tracked_files(sha):
    rc, out, err = git(['ls-tree', '-r', '--name-only', sha])
    if rc != 0:
        die('cannot list tracked files at %s: %s' % (sha, err.strip()))
    return [l for l in dec(out).splitlines() if l]


def iter_input_files(args):
    """[(display_path, content)] in deterministic input order.

    File argument: the path as given. Directory: every file beneath it,
    keyed by path relative to the directory. Commit: every tracked file
    at that commit, keyed by repository-relative path.
    """
    files = []
    for arg in args:
        p = Path(arg)
        if p.is_file():
            files.append((str(p), read_text(p)))
        elif p.is_dir():
            for rel in sorted(str(q.relative_to(p))
                              for q in p.rglob('*') if q.is_file()):
                files.append((rel, read_text(p / rel)))
        else:
            sha = rev_commit(arg)
            if not sha:
                die('argument %r is not an existing file, directory, or '
                    'git commit' % arg)
            for rel in tracked_files(sha):
                rc, out, _ = git(['show', '%s:%s' % (sha, rel)])
                if rc == 0:
                    files.append((rel, dec(out)))
    return files


def active_lines(content):
    """(line_number, line) outside QUOTED/DERIVED blocks."""
    skip = False
    for n, line in enumerate(content.splitlines(), 1):
        if SKIP_OPEN.match(line):
            skip = True
            continue
        if skip:
            if BLOCK_END.match(line):
                skip = False
            else:
                continue
        yield n, line


def harvest_anchors(files):
    """Canonical anchor values from the bundle's canonical-value records.

    Hex tokens of exact canonical length (64/40/32) in files named
    STATE.yaml, SEAL-PACKET.md, or seal-detached-v1.5.md, outside
    QUOTED/DERIVED blocks (quoted evidence is not an assertion).
    """
    anchors = {}
    for display, content in files:
        if Path(display).name in ANCHOR_RECORDS:
            for _n, line in active_lines(content):
                for m in HEX_TOKEN.finditer(line):
                    tok = m.group()
                    kind = ANCHOR_KINDS.get(len(tok))
                    if kind and tok not in anchors:
                        anchors[tok] = kind
    return anchors


def common_prefix_len(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


def label_expected(kinds):
    out = []
    for k in kinds:
        for n in CANONICAL[k]:
            if n not in out:
                out.append(n)
    return out


def check_file(display, content, anchors):
    """Findings for one file: label-length violations and anchor-prefix
    malformations, one object per offending token instance."""
    findings = []
    for n, line in active_lines(content):
        tokens = [(m.start(), m.group()) for m in HEX_TOKEN.finditer(line)]
        if not tokens:
            continue
        hits = []
        for name, kinds, rx in LABELS:
            for m in rx.finditer(line):
                hits.append((name, m.end(), kinds))
        for start, tok in tokens:
            length = len(tok)
            expected = []
            triggers = []
            for name, end, kinds in hits:
                if end > start:
                    continue
                # Must be the first token after this label.
                if any(s >= end and s < start for s, _t in tokens):
                    continue
                # Only whitespace/colons may sit between label and token.
                if any(c not in GAP for c in line[end:start]):
                    continue
                for x in label_expected(kinds):
                    if x not in expected:
                        expected.append(x)
                triggers.append('label:' + name)
            label_violation = bool(expected) and length not in expected
            partial_kinds = []
            if length >= 10 and tok not in anchors:
                for anchor, kind in anchors.items():
                    if (kind not in partial_kinds
                            and common_prefix_len(tok, anchor) >= 10):
                        partial_kinds.append(kind)
            for kind in partial_kinds:
                for x in CANONICAL[kind]:
                    if x not in expected:
                        expected.append(x)
                triggers.append('prefix:' + kind)
            if not (label_violation or partial_kinds):
                continue
            expected.sort()
            if tok in anchors:
                match = 'exact'
            elif partial_kinds:
                match = 'partial'
            else:
                match = 'none'
            findings.append({
                'location': '%s:%d' % (display, n),
                'identifier': tok,
                'expected_length': expected,
                'found_length': length,
                'anchor_match': match,
                'trigger': triggers,
            })
    return findings


def main(argv):
    if not argv:
        die('usage: k1_4.py PATH...  (files, directories, or commit-ish)')
    files = iter_input_files(argv)
    anchors = harvest_anchors(files)
    findings = []
    for display, content in files:
        findings.extend(check_file(display, content, anchors))
    print(json.dumps(findings, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
