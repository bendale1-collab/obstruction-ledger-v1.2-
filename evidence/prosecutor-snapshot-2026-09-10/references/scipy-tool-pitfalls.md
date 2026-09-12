## Scipy 'hybr' convergence handling (tool-usage pitfall)

`scipy.optimize.root(method='hybr')` can return `success=False` (status=4: "not making good progress") even when the solution is correct (c_l ≈ 1.0, residual < 1e-4). This is a known scipy quirk with flat convergence.

**Fix:** Accept if `sol.success or np.max(np.abs(sol.fun)) < 1e-4`

**Pitfall:** Do not relax the residual threshold beyond 1e-4 on a 2N+1 grid — that's already generous relative to machine precision. If the residual is > 1e-4, the solver genuinely failed.