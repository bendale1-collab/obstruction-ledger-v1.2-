#!/usr/bin/env python3
"""
K1-1 — quote-vs-anchor

Any block presented as quoting an anchored file (gist, sealed path) must
byte-match the anchor at the stated revision, or carry the header
`DERIVED <revision-sha>`. Unlabeled non-matching text is a finding.

Output: (block location, anchor, revision, MATCH / DERIVED / MISMATCH).
Network: one fetch per anchor, raw URL, cached per run.

Input: file paths as CLI arguments
Output: JSON array to stdout; one object per finding
Exit: 0 even when findings exist
"""

import sys
import json
import re
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError


# Cache for fetched anchors (per run)
_anchor_cache = {}


def fetch_anchor(url: str) -> bytes:
    """Fetch anchor content from URL, cached per run."""
    if url in _anchor_cache:
        return _anchor_cache[url]
    
    try:
        with urlopen(url) as response:
            content = response.read()
            _anchor_cache[url] = content
            return content
    except URLError as e:
        _anchor_cache[url] = None
        raise


def extract_gist_id(text: str) -> str | None:
    """Extract gist ID from text (32 hex chars)."""
    # Look for gist ID pattern (32 hex characters)
    match = re.search(r'\b([0-9a-f]{32})\b', text)
    if match:
        return match.group(1)
    return None


def extract_anchored_blocks(text: str, file_path: Path) -> list[dict]:
    """Extract blocks that claim to quote anchored files."""
    blocks = []
    lines = text.split('\n')
    
    # Patterns for anchored content
    gist_pattern = re.compile(r'gist\.github(?:usercontent)?\.com/[^/]+/([0-9a-f]+)')
    anchor_pattern = re.compile(r'ANCHOR:?\s*(.+)', re.IGNORECASE)
    derived_pattern = re.compile(r'^DERIVED\s+([0-9a-f]+)', re.MULTILINE)
    
    current_block = None
    block_start = None
    in_code_block = False
    
    for line_num, line in enumerate(lines, 1):
        # Track code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                if current_block:
                    current_block['end_line'] = line_num
                    current_block['content'] = '\n'.join(lines[block_start:line_num-1])
                    blocks.append(current_block)
                    current_block = None
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
                block_start = line_num
            continue
        
        if in_code_block and current_block is None:
            # Check if this line references an anchor
            gist_match = gist_pattern.search(line)
            anchor_match = anchor_pattern.search(line)
            
            if gist_match:
                gist_id = gist_match.group(1)
                # Construct raw URL
                url = f'https://gist.githubusercontent.com/bendale1-collab/{gist_id}/raw'
                current_block = {
                    'start_line': block_start,
                    'anchor': url,
                    'gist_id': gist_id,
                    'revision': None,  # Will be extracted if present
                    'has_derived': False
                }
            elif anchor_match:
                anchor_ref = anchor_match.group(1).strip()
                current_block = {
                    'start_line': block_start,
                    'anchor': anchor_ref,
                    'revision': None,
                    'has_derived': False
                }
        
        # Check for DERIVED header
        if current_block:
            derived_match = derived_pattern.match(line)
            if derived_match:
                current_block['has_derived'] = True
                current_block['revision'] = derived_match.group(1)
    
    return blocks


def check_k1_1(file_path: Path) -> list[dict]:
    """Check K1-1 for a single file."""
    findings = []
    
    try:
        text = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return [{'error': f'Cannot read {file_path}: {e}'}]
    
    blocks = extract_anchored_blocks(text, file_path)
    
    for block in blocks:
        anchor = block['anchor']
        has_derived = block['has_derived']
        
        # Fetch anchor content
        try:
            anchor_content = fetch_anchor(anchor)
            if anchor_content is None:
                findings.append({
                    'block_location': f"lines {block['start_line']}-{block.get('end_line', '?')}",
                    'anchor': anchor,
                    'revision': block.get('revision'),
                    'status': 'FETCH_FAILED',
                    'reason': 'Could not fetch anchor'
                })
                continue
        except Exception as e:
            findings.append({
                'block_location': f"lines {block['start_line']}-{block.get('end_line', '?')}",
                'anchor': anchor,
                'revision': block.get('revision'),
                'status': 'FETCH_FAILED',
                'reason': str(e)
            })
            continue
        
        # Compare block content against anchor (byte-level)
        block_bytes = block['content'].encode('utf-8')
        
        if block_bytes == anchor_content:
            # Byte-exact match
            findings.append({
                'block_location': f"lines {block['start_line']}-{block.get('end_line', '?')}",
                'anchor': anchor,
                'revision': block.get('revision'),
                'status': 'MATCH'
            })
        elif has_derived:
            # Has DERIVED header, so mismatch is acceptable
            findings.append({
                'block_location': f"lines {block['start_line']}-{block.get('end_line', '?')}",
                'anchor': anchor,
                'revision': block.get('revision'),
                'status': 'DERIVED',
                'reason': 'Content differs but DERIVED header present'
            })
        else:
            # Mismatch without DERIVED header
            findings.append({
                'block_location': f"lines {block['start_line']}-{block.get('end_line', '?')}",
                'anchor': anchor,
                'revision': block.get('revision'),
                'status': 'MISMATCH',
                'reason': 'Content differs and no DERIVED header'
            })
    
    return findings


def main():
    if len(sys.argv) < 2:
        print(json.dumps([]))
        sys.exit(0)
    
    all_findings = []
    
    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.exists():
            all_findings.append({'error': f'File not found: {arg}'})
            continue
        
        if path.is_file():
            findings = check_k1_1(path)
            for f in findings:
                f['file'] = str(path)
            all_findings.extend(findings)
        elif path.is_dir():
            # Recursively check all files in directory
            for file_path in path.rglob('*'):
                if file_path.is_file() and file_path.suffix in ['.md', '.txt']:
                    findings = check_k1_1(file_path)
                    for f in findings:
                        f['file'] = str(file_path)
                    all_findings.extend(findings)
    
    print(json.dumps(all_findings, indent=2))
    sys.exit(0)


if __name__ == '__main__':
    main()
