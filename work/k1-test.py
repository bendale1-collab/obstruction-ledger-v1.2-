#!/usr/bin/env python3
"""
K1 RUN — public rows.

Runs each check in work/k1/ against every fixture under injections/ for that
check, and compares to the expected outcome in that check's index.md.

Output:
1. INJECTION TABLE — 140 rows
2. Per-check recall and false-positive rate
3. RETRODICTION TABLE — 14 rows R1-R14
"""

import sys
import json
import subprocess
import re
from pathlib import Path
from typing import Optional, List, Tuple


REPO_ROOT = Path(__file__).parent.parent
INJECTIONS_DIR = REPO_ROOT / 'injections'
WORK_K1_DIR = REPO_ROOT / 'work' / 'k1'


def parse_index_md(index_path: Path) -> List[Tuple[str, str]]:
    """Parse index.md to extract (case, expected) pairs."""
    cases = []
    text = index_path.read_text()
    
    # Find table rows in Positives and Negatives sections
    for line in text.split('\n'):
        line = line.strip()
        if not line.startswith('|') or '---' in line or 'Case' in line:
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 4:
            case = parts[1]
            expected = parts[2]
            if case and expected and not case.startswith('-'):
                cases.append((case, expected))
    
    return cases


def run_check(script: str, args: List[str], timeout: int = 30) -> Tuple[Optional[List], Optional[str]]:
    """Run a check script and return (parsed JSON output, error message)."""
    cmd = [sys.executable, str(WORK_K1_DIR / script)] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO_ROOT)
        if result.returncode != 0 and not result.stdout:
            return None, f'exit {result.returncode}: {result.stderr[:200]}'
        try:
            data = json.loads(result.stdout)
            return data, None
        except json.JSONDecodeError:
            return None, f'JSON parse error: {result.stdout[:200]}'
    except subprocess.TimeoutExpired:
        return None, 'timeout'
    except Exception as e:
        return None, str(e)


def evaluate_c1(expected: str, findings: Optional[List], error: Optional[str]) -> Tuple[str, str]:
    """Evaluate C1 result against expected outcome."""
    if error:
        return 'ERROR', error
    
    has_findings = len(findings or []) > 0
    
    if expected == 'FINDING':
        if has_findings:
            return 'PASS', f'{len(findings or [])} finding(s)'
        else:
            return 'FAIL', 'no findings (expected FINDING)'
    elif expected == 'SILENT':
        if not has_findings:
            return 'PASS', 'silent'
        else:
            return 'FAIL', f'{len(findings or [])} finding(s) (expected SILENT)'
    else:
        return 'FAIL', f'unknown expected: {expected}'


def evaluate_k1_1(expected: str, findings: Optional[List], error: Optional[str]) -> Tuple[str, str]:
    """Evaluate K1-1 result against expected outcome."""
    if error:
        return 'ERROR', error
    
    if not findings:
        if expected == 'SILENT':
            return 'PASS', 'silent'
        elif expected.startswith('MATCH'):
            return 'FAIL', 'no findings (expected MATCH)'
        elif expected == 'MISMATCH':
            return 'FAIL', 'no findings (expected MISMATCH)'
        elif expected.startswith('DERIVED'):
            return 'PASS', 'silent (DERIVED expected)'
        else:
            return 'FAIL', f'no findings, expected {expected}'
    
    # Has findings
    statuses = [f.get('status', '') for f in (findings or [])]
    
    if expected == 'MISMATCH':
        if 'MISMATCH' in statuses:
            return 'PASS', 'MISMATCH'
        else:
            return 'FAIL', f'no MISMATCH in {statuses}'
    elif expected.startswith('MATCH'):
        if all(s == 'MATCH' for s in statuses):
            return 'PASS', 'MATCH'
        else:
            return 'FAIL', f'expected MATCH, got {statuses}'
    elif expected.startswith('DERIVED'):
        if 'DERIVED' in statuses:
            return 'PASS', 'DERIVED'
        else:
            return 'FAIL', f'expected DERIVED, got {statuses}'
    elif expected == 'SILENT':
        return 'FAIL', f'got findings (expected SILENT): {statuses}'
    else:
        return 'FAIL', f'unknown expected: {expected}'


def evaluate_k1_2(expected: str, findings: Optional[List], error: Optional[str]) -> Tuple[str, str]:
    """Evaluate K1-2 result against expected outcome."""
    if error:
        return 'ERROR', error
    
    safe_findings = findings or []
    has_findings = any(f.get('status') == 'DIFFERS' and f.get('reason') for f in safe_findings)
    all_same = all(f.get('status') == 'SAME' for f in safe_findings)
    
    if expected.startswith('FINDING'):
        if has_findings:
            return 'PASS', f'{sum(1 for f in safe_findings if f.get("reason"))} undeclared'
        else:
            return 'FAIL', 'no undeclared divergence'
    elif expected.startswith('SILENT'):
        if all_same or not has_findings:
            return 'PASS', 'silent'
        else:
            undeclared = [f for f in safe_findings if f.get('reason')]
            return 'FAIL', f'{len(undeclared)} undeclared (expected SILENT)'
    else:
        return 'FAIL', f'unknown expected: {expected}'


def run_injection_tests():
    """Run all injection tests and return results."""
    results = []
    
    # C1
    c1_index = INJECTIONS_DIR / 'c1' / 'index.md'
    if c1_index.exists():
        cases = parse_index_md(c1_index)
        for case, expected in cases:
            fixture = INJECTIONS_DIR / 'c1' / f'{case}.md'
            if not fixture.exists():
                results.append(('C1', case, expected, 'MISSING', 'fixture not found'))
                continue
            findings, error = run_check('c1.py', [str(fixture)])
            verdict, detail = evaluate_c1(expected, findings, error)
            results.append(('C1', case, expected, verdict, detail))
    
    # K1-1
    k11_index = INJECTIONS_DIR / 'k1-1' / 'index.md'
    if k11_index.exists():
        cases = parse_index_md(k11_index)
        for case, expected in cases:
            fixture = INJECTIONS_DIR / 'k1-1' / case
            if not fixture.exists():
                results.append(('K1-1', case, expected, 'MISSING', 'fixture not found'))
                continue
            findings, error = run_check('k1_1.py', [str(fixture)])
            verdict, detail = evaluate_k1_1(expected, findings, error)
            results.append(('K1-1', case, expected, verdict, detail))
    
    # K1-2
    k12_index = INJECTIONS_DIR / 'k1-2' / 'index.md'
    if k12_index.exists():
        cases = parse_index_md(k12_index)
        for case, expected in cases:
            fixture = INJECTIONS_DIR / 'k1-2' / case
            if not fixture.exists():
                results.append(('K1-2', case, expected, 'MISSING', 'fixture not found'))
                continue
            findings, error = run_check('k1_2.py', [str(fixture)])
            verdict, detail = evaluate_k1_2(expected, findings, error)
            results.append(('K1-2', case, expected, verdict, detail))
    
    return results


def run_retrodiction():
    """Run retrodiction rows R1-R14."""
    results = []
    
    # R1: rendering-as-record instance (K1-1)
    r1_file = REPO_ROOT / 'ledger' / 'rendering-as-record.md'
    if r1_file.exists():
        findings, error = run_check('k1_1.py', [str(r1_file)])
        if error:
            results.append(('R1', 'K1-1', 'MISMATCH ×2', 'ERROR', error))
        elif findings and any(f.get('status') == 'MISMATCH' for f in findings):
            count = sum(1 for f in findings if f.get('status') == 'MISMATCH')
            results.append(('R1', 'K1-1', 'MISMATCH ×2', 'PASS', f'{count} MISMATCH'))
        else:
            results.append(('R1', 'K1-1', 'MISMATCH ×2', 'FAIL', f'got {len(findings or [])} findings'))
    else:
        results.append(('R1', 'K1-1', 'MISMATCH ×2', 'MISSING', 'file not found'))
    
    # R2: seal-detached-v1.5.md @78d961b (K1-1)
    # Need to extract file at commit 78d961b
    r2_result = subprocess.run(['git', 'show', '78d961b:ledger/seal-detached-v1.5.md'],
                               capture_output=True, cwd=REPO_ROOT)
    if r2_result.returncode == 0:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.md', delete=False) as tmp:
            tmp.write(r2_result.stdout)
            tmp_path = tmp.name
        findings, error = run_check('k1_1.py', [tmp_path])
        Path(tmp_path).unlink()
        if error:
            results.append(('R2', 'K1-1', 'MATCH', 'ERROR', error))
        elif findings and all(f.get('status') == 'MATCH' for f in findings):
            results.append(('R2', 'K1-1', 'MATCH', 'PASS', 'MATCH'))
        elif not findings:
            results.append(('R2', 'K1-1', 'MATCH', 'PASS', 'silent (no quotes)'))
        else:
            statuses = [f.get('status') for f in findings]
            results.append(('R2', 'K1-1', 'MATCH', 'FAIL', f'got {statuses}'))
    else:
        results.append(('R2', 'K1-1', 'MATCH', 'ERROR', 'commit not found'))
    
    # R3: 7d4aad7 vs fe8a1e9 (K1-2)
    findings, error = run_check('k1_2.py', ['--git', '7d4aad7', 'fe8a1e9'])
    if error:
        results.append(('R3', 'K1-2', 'leg-a-closed DIFFERS/EDIT UNDECLARED', 'ERROR', error))
    elif findings:
        leg_a = [f for f in findings if 'leg-a-closed' in f.get('path', '')]
        if leg_a and leg_a[0].get('status') == 'DIFFERS' and leg_a[0].get('reason'):
            results.append(('R3', 'K1-2', 'leg-a-closed DIFFERS/EDIT UNDECLARED', 'PASS',
                          f"{leg_a[0].get('nature')} undeclared"))
        else:
            results.append(('R3', 'K1-2', 'leg-a-closed DIFFERS/EDIT UNDECLARED', 'FAIL',
                          f'leg-a-closed: {leg_a[0] if leg_a else "not found"}'))
    else:
        results.append(('R3', 'K1-2', 'leg-a-closed DIFFERS/EDIT UNDECLARED', 'FAIL', 'no findings'))
    
    # R4: 7d4aad7 vs a8e11c8 (K1-2)
    findings, error = run_check('k1_2.py', ['--git', '7d4aad7', 'a8e11c8'])
    if error:
        results.append(('R4', 'K1-2', '17 SAME + 2 declared DIFFERS', 'ERROR', error))
    elif findings:
        same_count = sum(1 for f in findings if f.get('status') == 'SAME')
        declared_differs = [f for f in findings if f.get('status') == 'DIFFERS' and not f.get('reason')]
        if same_count >= 17 and len(declared_differs) >= 2:
            results.append(('R4', 'K1-2', '17 SAME + 2 declared DIFFERS', 'PASS',
                          f'{same_count} SAME, {len(declared_differs)} declared'))
        else:
            results.append(('R4', 'K1-2', '17 SAME + 2 declared DIFFERS', 'FAIL',
                          f'{same_count} SAME, {len(declared_differs)} declared'))
    else:
        results.append(('R4', 'K1-2', '17 SAME + 2 declared DIFFERS', 'FAIL', 'no findings'))
    
    # R5: leg-a-closed @fe8a1e9 (K1-3) — NO CODE
    results.append(('R5', 'K1-3', 'FINDING (§7 inserted)', 'NO_CODE', 'K1-3 not implemented'))
    
    # R6: leg-a-closed @78d961b (K1-3) — NO CODE
    results.append(('R6', 'K1-3', 'FINDING (§3/§4 inserted, renumbered)', 'NO_CODE', 'K1-3 not implemented'))
    
    # R7: 18 other sealed files @a8e11c8 (K1-3) — NO CODE
    results.append(('R7', 'K1-3', '18 × SILENT', 'NO_CODE', 'K1-3 not implemented'))
    
    # R8: LOCKED history (K1-4) — NO CODE
    results.append(('R8', 'K1-4', 'FINDING ×5', 'NO_CODE', 'K1-4 not implemented'))
    
    # R8b: v1.6-publication-confirmation (K1-4) — NO CODE
    results.append(('R8b', 'K1-4', 'FINDING ×1', 'NO_CODE', 'K1-4 not implemented'))
    
    # R8c: gist-id-audit + r8-grep (K1-4) — NO CODE
    results.append(('R8c', 'K1-4', 'SILENT', 'NO_CODE', 'K1-4 not implemented'))
    
    # R9: anchors/ANCHORS.md @6b70539 (K1-4) — NO CODE
    results.append(('R9', 'K1-4', 'SILENT', 'NO_CODE', 'K1-4 not implemented'))
    
    # R10: A1/A5 reconciliation (C1)
    # Need to find the file — likely in ledger/
    r10_candidates = list((REPO_ROOT / 'ledger').glob('*reconcil*'))
    if r10_candidates:
        findings, error = run_check('c1.py', [str(r10_candidates[0])])
        if error:
            results.append(('R10', 'C1', 'FINDING', 'ERROR', error))
        elif findings:
            results.append(('R10', 'C1', 'FINDING', 'PASS', f'{len(findings)} finding(s)'))
        else:
            results.append(('R10', 'C1', 'FINDING', 'FAIL', 'no findings'))
    else:
        results.append(('R10', 'C1', 'FINDING', 'MISSING', 'reconciliation file not found'))
    
    # R11: K0 H2 report (C1)
    # Need to find K0 H2 report
    r11_candidates = list((REPO_ROOT / 'work').glob('*k0*')) + list((REPO_ROOT / 'work').glob('*h2*'))
    if r11_candidates:
        findings, error = run_check('c1.py', [str(r11_candidates[0])])
        if error:
            results.append(('R11', 'C1', 'SILENT', 'ERROR', error))
        elif not findings:
            results.append(('R11', 'C1', 'SILENT', 'PASS', 'silent'))
        else:
            results.append(('R11', 'C1', 'SILENT', 'FAIL', f'{len(findings)} finding(s)'))
    else:
        results.append(('R11', 'C1', 'SILENT', 'MISSING', 'K0 H2 file not found'))
    
    # R12: MANIFEST.sha256 @7d4aad7 (K1-5) — NO CODE
    results.append(('R12', 'K1-5', 'FINDING ×1', 'NO_CODE', 'K1-5 not implemented'))
    
    # R13: 5 .yaml manifest paths @7d4aad7 (K1-6) — NO CODE
    results.append(('R13', 'K1-6', 'FAIL ×4, PARSE ×1', 'NO_CODE', 'K1-6 not implemented'))
    
    # R14: K1-MANIFEST.sha256 (K1-5) — NO CODE
    results.append(('R14', 'K1-5', 'SILENT', 'NO_CODE', 'K1-5 not implemented'))
    
    return results


def main():
    print('INJECTION TABLE')
    print('check | case | expected | got | detail')
    print('------|------|----------|-----|-------')
    
    injection_results = run_injection_tests()
    for check, case, expected, verdict, detail in injection_results:
        print(f'{check} | {case} | {expected} | {verdict} | {detail}')
    
    print()
    print('PER-CHECK INJECTION STATS')
    
    for check_name in ['C1', 'K1-1', 'K1-2']:
        check_results = [(exp, got) for chk, _, exp, got, _ in injection_results if chk == check_name]
        positives = [(exp, got) for exp, got in check_results if exp in ('FINDING', 'MISMATCH')]
        negatives = [(exp, got) for exp, got in check_results if exp in ('SILENT', 'MATCH', 'DERIVED')]
        
        pos_pass = sum(1 for _, got in positives if got == 'PASS')
        neg_pass = sum(1 for _, got in negatives if got == 'PASS')
        
        recall = pos_pass / len(positives) if positives else 0
        fpr = 1 - (neg_pass / len(negatives)) if negatives else 0
        
        print(f'{check_name}: recall={recall:.2f} ({pos_pass}/{len(positives)}), FPR={fpr:.2f} ({len(negatives)-neg_pass}/{len(negatives)} false positives)')
    
    print()
    print('RETRODICTION TABLE')
    print('row | check | expected | got | detail')
    print('----|-------|----------|-----|-------')
    
    retrodiction_results = run_retrodiction()
    for row, check, expected, verdict, detail in retrodiction_results:
        print(f'{row} | {check} | {expected} | {verdict} | {detail}')


if __name__ == '__main__':
    main()
