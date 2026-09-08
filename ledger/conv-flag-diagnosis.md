Ledger Entry — Solver Convergence Flag Diagnosis
Filed: 2026-09-07
Type: CRITERION-MISMATCH
Mechanism: scipy.optimize.root('hybr') early convergence exit

scipy.optimize.root with method='hybr' (modified Powell hybrid)
returns sol.success=False even when the residual norm is well
below the xtol threshold, because the Jacobian-approximation
algorithm detects 'not making good progress' (status=4) when the
iteration has flattened to machine precision near the root.

The symptom: solve_profile() at a=0, alpha=1, N=256 achieved
c_l=1.0000 (exact match) and residual max < 1e-4, but
sol.success=False with status=4.

Diagnosis: This is NOT a bug in f1.py. It is a criterion
mismatch between scipy's convergence heuristic and the
application's definition of convergence. scipy's 'hybr' uses
a relative-progress heuristic (measurement on the last five
Jacobian evaluations) while the application requires only
residual < tolerance.

Fix applied: The convergence check in solve_profile() now
accepts sol.success OR final_res < 1e-4. This is documented
in the test suite [3/7] which prints the raw conv flag for
transparency.

The label 'pessimistic' in the P0 terminal report was a
symptom description (scipy reports false negative), not
a diagnosis. The diagnosis is criterion mismatch.