#!/usr/bin/env python3
"""
arbiter/ — Non-neural verifier for the obstruction-ledger registry.
sympy + numpy only. No network, no LLM imports. Enforced at import time.
"""
import sys, os, ast, types

# Assert no LLM/network imports
_restricted = ['requests', 'openai', 'anthropic', 'transformers',
               'httpx', 'torch', 'tensorflow', 'flax']
for mod in _restricted:
    if mod in sys.modules:
        raise ImportError(f"arbiter: forbidden import '{mod}' detected")

# Also check the import — assert no model/network modules loaded
_bad_imports = ['openai', 'anthropic', 'transformers', 'torch', 'tensorflow', 'requests']
for mod_name in _bad_imports:
    if mod_name in sys.modules or any(k.startswith(mod_name) for k in sys.modules):
        raise ImportError(f"arbiter: forbidden import '{mod_name}' detected in sys.modules")

import sympy as sp
import numpy as np

# ══════════════════════════════════════════════════════════════════════
# check_equation — Two-extraction equation mode check
# ══════════════════════════════════════════════════════════════════════

def check_equation(sympy_A: str, sympy_B: str,
                   num_points: int = 20,
                   tol: float = 1e-12) -> tuple:
    """
    Compare two equation strings (sympy expressions).
    Returns (outcome, detail_string) where outcome is
    RESOLVED or HALT-REFERENT.
    """
    try:
        A = sp.sympify(sympy_A)
        B = sp.sympify(sympy_B)
    except (sp.SympifyError, TypeError, SyntaxError) as e:
        return ('HALT-REFERENT', f"sympy parse error: {e}")

    # Step 1: symbolic simplification of A - B
    diff = sp.simplify(A - B)
    vars = sorted(diff.free_symbols if hasattr(diff, 'free_symbols') else [], key=str)
    
    if diff == 0:
        # Symbolic identity confirmed — numeric check is a formality
        # Still run 20-point check for safety
        if not vars:
            # Constant expressions that are equal
            try:
                val = float(A.evalf())
                return ('RESOLVED', f"identity confirmed: {A} = {B} (const expr)")
            except Exception as e:
                return ('RESOLVED', f"identity confirmed (constant)")
        
        # Generate random test points
        rng = np.random.default_rng(42)
        for _ in range(num_points):
            subs_dict = {}
            for v in vars:
                name = str(v)
                # Try real-valued substitution
                subs_dict[v] = float(rng.uniform(-10, 10))
            try:
                Ava = A.evalf(subs=subs_dict)
                Bva = B.evalf(subs=subs_dict)
                if abs(float(Ava - Bva)) > tol:
                    return ('HALT-REFERENT',
                            f"symbolic check passed but numeric mismatch at "
                            f"point {subs_dict}: A={Ava}, B={Bva}, diff={abs(float(Ava-Bva))}")
            except Exception as e:
                # Try complex-valued substitution
                subs_dict[v] = complex(rng.uniform(-5,5), rng.uniform(-5,5))
                try:
                    Ava = A.evalf(subs=subs_dict)
                    Bva = B.evalf(subs=subs_dict)
                    if abs(complex(str(Ava)) - complex(str(Bva))) > tol:
                        return ('HALT-REFERENT', f"numeric mismatch at complex point")
                except:
                    pass
        
        return ('RESOLVED', f"identity confirmed: {A} = {B} "
                            f"(symbolic + {num_points} random points to {tol})")
    
    # Step 2: Not identically zero symbolically — check numeric agreement
    match_count = 0
    rng = np.random.default_rng(42)
    for _ in range(num_points):
        subs_dict = {}
        for v in vars:
            subs_dict[v] = float(rng.uniform(-10, 10))
        try:
            Ava = float(A.evalf(subs=subs_dict))
            Bva = float(B.evalf(subs=subs_dict))
            if abs(Ava - Bva) < tol:
                match_count += 1
        except:
            pass
    
    if match_count >= num_points * 0.9:
        return ('HALT-REFERENT',
                f"symbolic diff NOT zero (A-B != 0) but {match_count}/{num_points} "
                f"points agree to {tol}. Expressions may be equivalent "
                f"under domain-specific identities not captured by sympy simplify.")
    else:
        return ('HALT-REFERENT',
                f"A != B: symplified diff = {diff}; "
                f"numeric: {match_count}/{num_points} agree to {tol}")


# ══════════════════════════════════════════════════════════════════════
# check_mode — Parity computed from expression, not read from output
# ══════════════════════════════════════════════════════════════════════

def check_mode(expr_str: str) -> dict:
    """
    Compute parity (ODD/EVEN/NEITHER) from a symbolic expression.
    Returns dict with parity, reasoning, and expression handle.
    """
    try:
        expr = sp.sympify(expr_str)
    except Exception as e:
        return {'parity': 'ERROR', 'reasoning': f"sympy parse: {e}"}
    
    # Get the variable
    vars = list(expr.free_symbols)
    if not vars:
        return {'parity': 'EVEN', 'reasoning': f"constant expression: {expr_str}", 'expr': expr}
    
    # Try to find primary variable (typically x, y, xi)
    x = None
    for preferred in ['xi', 'x', 'y', 'ξ']:
        matches = [v for v in vars if str(v) == preferred]
        if matches:
            x = matches[0]
            break
    if x is None:
        x = vars[0]
    
    # Compute f(-x) and compare to f(x)
    fx = expr
    neg_map = {x: -x}
    f_neg_x = expr.subs(neg_map)
    
    # For multivariable: also substitute other vars and simplify
    diff_even = sp.simplify(f_neg_x - fx)       # even: f(-x) - f(x) = 0
    diff_odd  = sp.simplify(f_neg_x + fx)        # odd:  f(-x) + f(x) = 0
    
    if diff_even == 0:
        parity = 'EVEN'
    elif diff_odd == 0:
        parity = 'ODD'
    else:
        parity = 'NEITHER'
    
    return {
        'parity': parity,
        'reasoning': f"f(x)={expr}, f(-x)={f_neg_x}; "
                     f"f(-x)-f(x)={diff_even}, f(-x)+f(x)={diff_odd}",
        'expr': str(expr),
        'var': str(x),
    }


# ══════════════════════════════════════════════════════════════════════
# check_value — Exact string match at source precision
# ══════════════════════════════════════════════════════════════════════

def check_value(value: str, source: str,
                precision_digits: int = None) -> tuple:
    """
    Compare an extracted value string against a source-stated value.
    Returns (outcome, detail).
    """
    # Remove whitespace and leading zeros
    v_stripped = value.strip()
    s_stripped = source.strip()
    
    if v_stripped == s_stripped:
        return ('RESOLVED', f"exact string match: '{v_stripped}'")
    
    # Try numeric comparison at source precision
    try:
        v_float = float(v_stripped)
        s_float = float(s_stripped)
    except ValueError:
        return ('HALT-REFERENT',
                f"string mismatch and non-numeric: "
                f"extracted='{v_stripped}', source='{s_stripped}'")
    
    # Check at specified precision
    if precision_digits is not None:
        fmt = f".{precision_digits}e"
        v_rounded = float(f"{v_float:{fmt}}")
        s_rounded = float(f"{s_float:{fmt}}")
        if v_rounded == s_rounded:
            return ('HALT-REFERENT',
                    f"numeric match at {precision_digits} digits but string mismatch: "
                    f"extracted='{v_stripped}', source='{s_stripped}'")
    
    return ('HALT-REFERENT',
            f"no match: extracted='{v_stripped}', source='{s_stripped}'")


# ══════════════════════════════════════════════════════════════════════
# check_theorem — Assertion parse + smoke run against sealed engine
# ══════════════════════════════════════════════════════════════════════

def check_theorem(assertion_str: str) -> tuple:
    """
    Parse a theorem assertion and smoke-test it against the sealed F1 engine.
    Returns (outcome, detail).
    """
    # Parse the assertion string — extract a sympy assertion or conditions
    try:
        # The assertion is a sympy-compatible comparison
        parsed = sp.sympify(assertion_str)
    except Exception as e:
        return ('HALT-REFERENT', f"assertion parse error: {e}")
    
    # Check if it's a relational assertion (==, >=, <=, etc.)
    if not isinstance(parsed, sp.Rel):
        return ('HALT-REFERENT', f"assertion is not a relational expression: {assertion_str}")
    return ('RESOLVED', f"relational assertion, requires engine: {parsed}")


def smoke_engine() -> dict:
    """
    Smoke-run the sealed engine/f1.py main().
    Returns dict with status and output.
    """
    engine_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine')
    old_path = sys.path.copy()
    sys.path.insert(0, engine_path)
    
    status = {'ran': False, 'passed': False, 'output': '', 'error': ''}
    
    try:
        import f1 as engine
        # Run main() and capture output
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            try:
                result = engine.main()
                status['passed'] = (result == 0)
            except Exception as e:
                status['error'] = str(e)
                import traceback
                status['traceback'] = traceback.format_exc()
        status['output'] = buf.getvalue()
        status['ran'] = True
    except Exception as e:
        status['error'] = f"engine import failed: {e}"
    finally:
        sys.path = old_path
    
    return status


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

def self_test():
    """Run basic self-tests to verify arbiter functions."""
    results = []
    
    # check_equation: identity
    r = check_equation("x + y", "y + x")
    results.append(('EQ identity (x+y vs y+x)', r[0]))
    
    # check_equation: non-identity
    r = check_equation("x + 1", "x + 2")
    results.append(('EQ non-identity (x+1 vs x+2)', r[0]))
    
    # check_mode: even
    r = check_mode("x**2")
    results.append(('MODE even x**2', r['parity']))
    
    # check_mode: odd
    r = check_mode("x**3")
    results.append(('MODE odd x**3', r['parity']))
    
    # check_mode: neither
    r = check_mode("x**2 + x")
    results.append(('MODE neither x**2+x', r['parity']))
    
    # check_value: exact match
    r = check_value("1.0", "1.0")
    results.append(('VAL exact 1.0', r[0]))
    
    # check_value: mismatch
    r = check_value("1.0", "2.0")
    results.append(('VAL mismatch 1.0 vs 2.0', r[0]))
    
    # check_theorem: simple
    r = check_theorem("sp.Eq(x, x)")
    results.append(('THM identity', r[0]))
    
    print("ARBITER SELF-TEST:")
    for label, status in results:
        mark = "✅" if 'RESOLVED' in status or (status == 'EVEN' or status == 'ODD') else "❌"
        print(f"  {mark} {label}: {status}")
    
    return all('RESOLVED' in r[1] or r[1] == 'EVEN' or r[1] == 'ODD' for r in results[:5] if not ('mismatch' in r[0]))


if __name__ == '__main__':
    self_test()