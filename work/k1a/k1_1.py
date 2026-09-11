#!/usr/bin/env python3
"""K1-1 — quote-vs-anchor check.

Any block presented as quoting an anchored file (gist, sealed path) must
byte-match the anchor at the stated revision, or carry the header
`DERIVED <revision-sha>`. Unlabeled non-matching text is a finding.

Interface: packet directory as CLI argument. JSON array to stdout.
Network: one fetch per anchor URL, cached per run.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Global cache for fetched anchors
_anchor_cache: dict[str, str] = {}


def fetch_gist_content(gist_url: str) -> str | None:
    """Fetch raw content from a gist URL. Cached per run."""
    if gist_url in _anchor_cache:
        return _anchor_cache[gist_url]
    
    # Extract raw URL from gist URL
    # Pattern: https://gist.githubusercontent.com/.../raw/...
    if "raw" in gist_url:
        raw_url = gist_url
    else:
        # Convert gist URL to raw URL
        # https://gist.github.com/user/id -> https://gist.githubusercontent.com/user/id/raw
        raw_url = gist_url.replace("gist.github.com", "gist.githubusercontent.com")
        if not raw_url.endswith("/raw"):
            raw_url = raw_url.rstrip("/") + "/raw"
    
    try:
        import urllib.request
        with urllib.request.urlopen(raw_url, timeout=10) as response:
            content = response.read().decode("utf-8")
            _anchor_cache[gist_url] = content
            return content
    except Exception:
        return None


def extract_quoted_blocks(report_md: Path) -> list[dict]:
    """Extract quoted blocks and their anchor references from report.md.
    
    Returns list of:
        {
            "anchor_ref": "gist URL or sealed path",
            "quoted_content": "the quoted text",
            "has_derived": bool,
            "derived_sha": str or None
        }
    """
    blocks = []
    lines = report_md.read_text().splitlines()
    
    # Find gist URLs and sealed paths
    gist_pattern = r"https://gist\.github(?:usercontent)?\.com/[^\s\)]+"
    sealed_pattern = r"(?:sealed|anchor):([^\s\)]+)"
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for gist URL reference
        gist_match = re.search(gist_pattern, line)
        sealed_match = re.search(sealed_pattern, line)
        
        if gist_match:
            anchor_ref = gist_match.group(0)
        elif sealed_match:
            anchor_ref = sealed_match.group(1)
        else:
            i += 1
            continue
        
        # Look for quoted content in next lines
        quoted_lines = []
        has_derived = False
        derived_sha = None
        
        j = i + 1
        while j < len(lines):
            next_line = lines[j]
            
            # Check for DERIVED header
            if next_line.strip().startswith("DERIVED "):
                has_derived = True
                derived_sha = next_line.strip()[len("DERIVED "):].strip()
                j += 1
                continue
            
            # Quoted line (starts with > or is in a code block)
            if next_line.startswith(">"):
                quoted_lines.append(next_line[1:].lstrip())
            elif next_line.startswith("```"):
                # Code block
                j += 1
                while j < len(lines) and not lines[j].startswith("```"):
                    quoted_lines.append(lines[j])
                    j += 1
                break
            elif next_line.strip() == "":
                j += 1
                continue
            else:
                break
            j += 1
        
        if quoted_lines:
            blocks.append({
                "anchor_ref": anchor_ref,
                "quoted_content": "\n".join(quoted_lines),
                "has_derived": has_derived,
                "derived_sha": derived_sha
            })
            i = j
        else:
            i += 1
    
    return blocks


def load_anchor_content(packet_dir: Path, anchor_ref: str) -> str | None:
    """Load anchor content from packet (fixture mode) or fetch (live mode)."""
    # Check for local anchor.txt
    anchor_txt = packet_dir / "anchor.txt"
    if anchor_txt.exists():
        return anchor_txt.read_text()
    
    # Fetch from gist URL
    if "gist" in anchor_ref:
        return fetch_gist_content(anchor_ref)
    
    return None


def check_k1_1(packet_dir: Path) -> list[dict]:
    """Run K1-1 check on a packet directory."""
    findings = []
    
    # Find report.md
    report_md = packet_dir / "report.md"
    if not report_md.exists():
        return findings
    
    blocks = extract_quoted_blocks(report_md)
    
    for block in blocks:
        anchor_ref = block["anchor_ref"]
        quoted_content = block["quoted_content"]
        has_derived = block["has_derived"]
        derived_sha = block["derived_sha"]
        
        # Load anchor content
        anchor_content = load_anchor_content(packet_dir, anchor_ref)
        
        if anchor_content is None:
            findings.append({
                "block_location": str(report_md.name),
                "anchor": anchor_ref,
                "verdict": "MISMATCH",
                "reason": "anchor not found or fetch failed"
            })
            continue
        
        # Check byte match
        if quoted_content == anchor_content:
            verdict = "MATCH"
        elif has_derived:
            verdict = "DERIVED"
        else:
            verdict = "MISMATCH"
        
        if verdict == "MISMATCH":
            findings.append({
                "block_location": str(report_md.name),
                "anchor": anchor_ref,
                "revision": derived_sha or "HEAD",
                "verdict": verdict,
                "reason": "unlabeled non-matching text"
            })
    
    return findings


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps([]))
        sys.exit(0)
    
    packet_path = Path(sys.argv[1])
    if not packet_path.is_dir():
        print(json.dumps([]))
        sys.exit(0)
    
    findings = check_k1_1(packet_path)
    print(json.dumps(findings, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
