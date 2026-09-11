#!/usr/bin/env python3
"""
C1 — prose–table number mismatch

Compare numbers in prose against numbers in tables or JSON in the same file.
Tolerance: exact match after rounding both values to the fewer significant
digits of the pair. Rounding via Python decimal with ROUND_HALF_UP on the
string representation, never on binary floats. Integers compare exactly.
Units must match literally.

Input: file paths as CLI arguments
Output: JSON array to stdout; one object per finding
Exit: 0 even when findings exist
"""

import sys
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


def extract_prose_numbers(text: str) -> list[dict]:
    """Extract numbers from prose with location."""
    findings = []
    lines = text.split('\n')
    
    # Number pattern: optional sign, digits, optional decimal, optional units
    # Matches: 123, -45.67, +8.9, 12.34MB, 56.78%, etc.
    number_pattern = re.compile(r'([+-]?\d+(?:\.\d+)?)\s*([a-zA-Z%]*)')
    
    for line_num, line in enumerate(lines, 1):
        # Skip table rows (lines with | separators) and JSON structures
        if '|' in line and line.count('|') >= 2:
            continue
        if '{' in line or '}' in line or line.strip().startswith('"'):
            continue
        
        for match in number_pattern.finditer(line):
            value = match.group(1)
            unit = match.group(2) if match.group(2) else None
            findings.append({
                'value': value,
                'unit': unit,
                'location': f'line {line_num}',
                'context': line.strip()[:100]
            })
    
    return findings


def extract_table_json_numbers(text: str) -> list[dict]:
    """Extract numbers from tables and JSON structures."""
    findings = []
    lines = text.split('\n')
    
    # Table pattern: lines with | separators
    table_pattern = re.compile(r'\|.*\|')
    
    for line_num, line in enumerate(lines, 1):
        if table_pattern.search(line):
            # Extract numbers from table cells
            cells = line.split('|')
            for cell in cells[1:-1]:  # Skip empty first/last from split
                cell = cell.strip()
                # Try to parse as number
                try:
                    # Check if it's a pure number (possibly with unit)
                    num_match = re.match(r'^([+-]?\d+(?:\.\d+)?)\s*([a-zA-Z%]*)$', cell)
                    if num_match:
                        value = num_match.group(1)
                        unit = num_match.group(2) if num_match.group(2) else None
                        findings.append({
                            'value': value,
                            'unit': unit,
                            'location': f'line {line_num}',
                            'context': line.strip()[:100]
                        })
                except ValueError:
                    pass
        
        # JSON-like structures
        if '{' in line or '"' in line:
            # Try to extract key-value pairs
            json_num_pattern = re.compile(r'["\']([^"\']+)["\']:\s*([+-]?\d+(?:\.\d+)?)\s*([a-zA-Z%]*)')
            for match in json_num_pattern.finditer(line):
                key = match.group(1)
                value = match.group(2)
                unit = match.group(3) if match.group(3) else None
                findings.append({
                    'value': value,
                    'unit': unit,
                    'location': f'line {line_num}',
                    'context': f'{key}: {value}'
                })
    
    return findings


def round_to_fewer_sig_figs(val1: str, val2: str) -> tuple[Decimal, Decimal]:
    """Round both values to the fewer significant digits of the pair."""
    d1 = Decimal(val1)
    d2 = Decimal(val2)
    
    # Count significant digits
    def sig_figs(d: Decimal) -> int:
        # Convert to string, remove leading zeros and decimal point
        s = format(d, 'f')
        if '.' in s:
            integer_part, decimal_part = s.split('.')
        else:
            integer_part, decimal_part = s, ''
        
        # Remove leading zeros from integer part
        integer_part = integer_part.lstrip('0') or '0'
        
        # Count significant digits
        if d == 0:
            return 1
        
        # All digits in integer part are significant (except leading zeros)
        # Leading zeros in decimal part are not significant
        sig = len(integer_part) if integer_part != '0' else 0
        
        if decimal_part:
            # Find first non-zero digit
            for i, ch in enumerate(decimal_part):
                if ch != '0':
                    sig += len(decimal_part) - i
                    break
        
        return max(sig, 1)
    
    sf1 = sig_figs(d1)
    sf2 = sig_figs(d2)
    min_sf = min(sf1, sf2)
    
    # Round to min_sf significant figures
    def round_sig_figs(d: Decimal, sig_figs: int) -> Decimal:
        if d == 0:
            return d
        
        # Use quantize with appropriate precision
        # This is approximate; for production we'd need more careful handling
        magnitude = len(str(abs(d)).split('.')[0].lstrip('0') or '0')
        if magnitude >= sig_figs:
            # Round to integer
            return d.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        else:
            # Round to decimal places
            places = sig_figs - magnitude
            quant = Decimal('0.' + '0' * places)
            return d.quantize(quant, rounding=ROUND_HALF_UP)
    
    return round_sig_figs(d1, min_sf), round_sig_figs(d2, min_sf)


def check_c1(file_path: Path) -> list[dict]:
    """Check C1 for a single file."""
    findings = []
    
    try:
        text = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return [{'error': f'Cannot read {file_path}: {e}'}]
    
    prose_nums = extract_prose_numbers(text)
    table_nums = extract_table_json_numbers(text)
    
    # Compare each prose number against each table number
    for prose in prose_nums:
        for table in table_nums:
            # Check if units match (both None or both equal)
            if prose['unit'] != table['unit']:
                continue
            
            # Try to compare values
            try:
                p_val = prose['value']
                t_val = table['value']
                
                # Check if both are integers
                if '.' not in p_val and '.' not in t_val:
                    # Integer comparison: exact match
                    if int(p_val) != int(t_val):
                        findings.append({
                            'prose_location': prose['location'],
                            'table_location': table['location'],
                            'prose_value': p_val,
                            'table_value': t_val,
                            'prose_unit': prose['unit'],
                            'table_unit': table['unit'],
                            'reason': 'integer mismatch'
                        })
                else:
                    # Decimal comparison: round to fewer significant digits
                    p_rounded, t_rounded = round_to_fewer_sig_figs(p_val, t_val)
                    if p_rounded != t_rounded:
                        findings.append({
                            'prose_location': prose['location'],
                            'table_location': table['location'],
                            'prose_value': p_val,
                            'table_value': t_val,
                            'prose_rounded': str(p_rounded),
                            'table_rounded': str(t_rounded),
                            'prose_unit': prose['unit'],
                            'table_unit': table['unit'],
                            'reason': 'decimal mismatch after rounding'
                        })
            except Exception as e:
                # Skip values that can't be parsed
                pass
    
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
            findings = check_c1(path)
            for f in findings:
                f['file'] = str(path)
            all_findings.extend(findings)
        elif path.is_dir():
            # Recursively check all files in directory
            for file_path in path.rglob('*'):
                if file_path.is_file() and file_path.suffix in ['.md', '.txt', '.json', '.yaml', '.yml']:
                    findings = check_c1(file_path)
                    for f in findings:
                        f['file'] = str(file_path)
                    all_findings.extend(findings)
    
    print(json.dumps(all_findings, indent=2))
    sys.exit(0)


if __name__ == '__main__':
    main()
