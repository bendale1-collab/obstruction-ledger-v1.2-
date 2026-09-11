#!/usr/bin/env python3
"""C1 — prose–table number mismatch check.

Every number in prose that also appears in a table or JSON in the same
packet must agree in value and unit. Tolerance: exact match after rounding
both values to the fewer significant digits of the pair, using Decimal
ROUND_HALF_UP on the string representation. Units must match literally.

Interface: packet directory as CLI argument. JSON array to stdout.
"""

from __future__ import annotations

import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


def count_sig_figs(value_str: str) -> int:
    """Count significant figures in a numeric string."""
    s = value_str.strip().lstrip("0")
    if not s or s == ".":
        return 1
    if "." in s:
        return len(s.replace(".", "").lstrip("0")) or 1
    return len(s) or 1


def sig_round(value_str: str, sig_digits: int) -> Decimal:
    """Round a numeric string to sig_digits significant figures."""
    d = Decimal(value_str)
    if d == 0:
        return d
    magnitude = int(d.adjusted())
    places = sig_digits - magnitude - 1
    if places >= 0:
        return d.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)
    else:
        factor = Decimal(10) ** abs(places)
        rounded = (d / factor).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return rounded * factor


def extract_numbers(text: str) -> list[tuple[str, str]]:
    """Extract (number, unit) pairs from text."""
    pattern = r"(-?\d+\.?\d*(?:[eE][+-]?\d+)?)\s*([a-zA-Z%/°²³]*)?"
    matches = []
    for m in re.finditer(pattern, text):
        num = m.group(1)
        unit = m.group(2) or ""
        matches.append((num, unit))
    return matches


def parse_packet(packet_dir: Path) -> tuple[list[tuple[str, str, str]], list[tuple[str, str, str]]]:
    """Parse packet into (prose_numbers, table_numbers).
    
    Returns:
        prose_numbers: [(file, number, unit), ...]
        table_numbers: [(file, number, unit), ...]
    """
    prose_nums = []
    table_nums = []
    
    for md_file in sorted(packet_dir.glob("*.md")):
        lines = md_file.read_text().splitlines()
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Table row: contains |
            if "|" in stripped and not stripped.startswith("#"):
                nums = extract_numbers(stripped)
                for num, unit in nums:
                    table_nums.append((str(md_file.name), num, unit))
            # Prose: not a header, not a table row, not empty
            elif stripped and not stripped.startswith("#"):
                nums = extract_numbers(stripped)
                for num, unit in nums:
                    prose_nums.append((str(md_file.name), num, unit))
    
    # JSON files
    for json_file in sorted(packet_dir.glob("*.json")):
        try:
            data = json.loads(json_file.read_text())
            json_str = json.dumps(data)
            nums = extract_numbers(json_str)
            for num, unit in nums:
                table_nums.append((str(json_file.name), num, unit))
        except (json.JSONDecodeError, OSError):
            pass
    
    return prose_nums, table_nums


def check_c1(packet_dir: Path) -> list[dict]:
    """Run C1 check on a packet directory."""
    findings = []
    prose_nums, table_nums = parse_packet(packet_dir)
    
    # For each number that appears in both prose and table, check agreement
    for prose_file, prose_val, prose_unit in prose_nums:
        for table_file, table_val, table_unit in table_nums:
            # Units must match literally
            if prose_unit != table_unit:
                findings.append({
                    "prose_location": prose_file,
                    "table_location": table_file,
                    "prose_value": prose_val,
                    "prose_unit": prose_unit,
                    "table_value": table_val,
                    "table_unit": table_unit,
                    "reason": "unit mismatch"
                })
                continue
            
            # Round both to fewer sig figs and compare
            try:
                prose_sig = count_sig_figs(prose_val)
                table_sig = count_sig_figs(table_val)
                min_sig = min(prose_sig, table_sig)
                
                prose_rounded = sig_round(prose_val, min_sig)
                table_rounded = sig_round(table_val, min_sig)
                
                if prose_rounded != table_rounded:
                    findings.append({
                        "prose_location": prose_file,
                        "table_location": table_file,
                        "prose_value": prose_val,
                        "table_value": table_val,
                        "unit": prose_unit,
                        "prose_rounded": str(prose_rounded),
                        "table_rounded": str(table_rounded),
                        "reason": "value mismatch after rounding"
                    })
            except Exception as e:
                findings.append({
                    "prose_location": prose_file,
                    "table_location": table_file,
                    "prose_value": prose_val,
                    "table_value": table_val,
                    "reason": f"rounding error: {e}"
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
    
    findings = check_c1(packet_path)
    print(json.dumps(findings, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
