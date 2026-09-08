#!/usr/bin/env python3
"""P1 Falsification Battery — LEG A (CLM Spectral, gCLM a=0).

Pre-registration: specs/leg-a-p1-pre-registration-v1.5.txt (sealed c6a73ae8)
Execution order: F-4 FIRST. Then F-1, F-2, F-3, F-5. Then two-grid floor.

Tolerances (verbatim from pre-registration):
  FLOOR = -1/2 + 3e-3 = -0.497
  delta = 5e-4 (BORROWED-TOLERANCE)
  Strip zone: Re lambda in (FLOOR, -5e-4)
  F-5: eps*||(z-eps-L)^-1|| > 1e2 => UNTRUSTED
  N = 1024 primary, N = 2048 doubling, L = 20.0

The engine (engine/f1.py) is SEALED — imported read-only, never modified.
"""
import sys, os, json, time
import numpy as np
from scipy import linalg

ENGINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine')
sys.path.insert(0, ENGINE_DIR)
from f1 import RealizationPair, gCLMSolver  # noqa: E402

FLOOR = -0.5 + 3e-3          # -0.497
DELTA = 5e-4                 # BORROWED-TOLERANCE
L = 20.0

RESULTS = {}


def spectrum_of(rp: RealizationPair, N: int, odd_basis: bool):
    """Return (L_mat, eigenvalues) for the linearized operator at a=0."""
    rp.N = N
    rp.ft = __import__('f1').FourierSpectralEngine(N, L)
    L_mat = rp._build_operator(a=0.0, odd_basis=odd_basis)
    eig = linalg.eigvals(L_mat)
    return L_mat, eig


def eig_zone_count(eig, lo, hi):
    """Count eigenvalues with Re in (lo, hi), excluding {0,1} by complex distance."""
    re = eig.real
    mask = (re > lo) & (re < hi)
    # Exclude anything within complex distance delta of 0 or 1
    for z in eig[mask]:
        if abs(z) < DELTA or abs(z - 1.0) < DELTA:
            mask[np.where(np.abs(eig - z) < 1e-15)[0]] = False
    return int(np.sum(mask)), eig[mask]


def resolvent_metric(L_mat, z, eps):
    """eps * ||(z - eps - L)^-1||_2 via smallest singular value."""
    n = L_mat.shape[0]
    B = (z - eps) * np.eye(n) - L_mat
    s = linalg.svdvals(B)
    sigma_min = s[-1]
    if sigma_min < 1e-300:
        return float('inf')
    return float(eps / sigma_min)


def run_F4():
    """F-4 POSITIVE CONTROL (run FIRST). Max-L2 strip, absent in origin-H2, stable under doubling."""
    t0 = time.time()
    rp = RealizationPair(N=1024, L=L)
    out = {}

    # Maximal-L2 at N=1024
    L_naive, eig_naive = spectrum_of(rp, 1024, odd_basis=False)
    n_naive, strip_naive = eig_zone_count(eig_naive, FLOOR, -DELTA)

    # Origin-H2 at N=1024
    L_clean, eig_clean = spectrum_of(rp, 1024, odd_basis=True)
    n_clean, _ = eig_zone_count(eig_clean, FLOOR, -DELTA)

    # Maximal-L2 at N=2048 (doubling)
    L_naive2, eig_naive2 = spectrum_of(rp, 2048, odd_basis=False)
    n_naive2, _ = eig_zone_count(eig_naive2, FLOOR, -DELTA)

    # Resolvent norms for strip eigenvalues (diagnostic)
    strip_resolvents = []
    for z in strip_naive[:10]:
        strip_resolvents.append(round(resolvent_metric(L_naive, z, 1e-3), 4))

    passed = (n_naive >= 2) and (n_clean == 0) and (n_naive2 >= 2)
    out.update(
        test='F-4',
        n_naive_1024=n_naive, n_clean_1024=n_clean, n_naive_2048=n_naive2,
        strip_eigs=[complex(round(z.real, 6), round(z.imag, 6)) for z in strip_naive[:5]],
        strip_resolvent_norm_eps1e3=strip_resolvents,
        passed=bool(passed),
        elapsed_s=round(time.time() - t0, 1),
    )
    return out


def run_F1(rp):
    """F-1 POINT SPECTRUM. Above FLOOR must be exactly {0,1}, stable under doubling."""
    t0 = time.time()
    out = {'test': 'F-1'}

    for N in (1024, 2048):
        L_mat, eig = spectrum_of(rp, N, odd_basis=True)
        above = eig[eig.real > FLOOR]
        re = sorted(above.real, reverse=True)
        out[f'n_above_floor_N{N}'] = int(len(above))
        out[f'evals_above_floor_N{N}'] = [round(complex(z).real, 6) for z in re[:8]]
        # Identify {0,1} by complex distance
        has_0 = any(abs(z) < DELTA for z in above)
        has_1 = any(abs(z - 1.0) < DELTA for z in above)
        # Any OTHER eigenvalue above floor?
        others = [complex(z) for z in above
                  if not (abs(z) < DELTA or abs(z - 1.0) < DELTA)]
        out[f'has_0_N{N}'] = bool(has_0)
        out[f'has_1_N{N}'] = bool(has_1)
        out[f'n_others_N{N}'] = int(len(others))
        out[f'others_N{N}'] = [round(z.real, 6) for z in others[:5]]

    passed = (
        out.get('n_others_N1024', 99) == 0 and out.get('n_others_N2048', 99) == 0
        and out.get('has_0_N1024', False) and out.get('has_1_N1024', False)
        and out.get('n_above_floor_N1024', -1) == 2 and out.get('n_above_floor_N2048', -1) == 2
    )
    out['passed'] = bool(passed)
    out['elapsed_s'] = round(time.time() - t0, 1)
    return out


def run_F2(rp):
    """F-2 ESSENTIAL SPECTRUM. Cluster mean at -1/2 +/- 2e-3; no member >= FLOOR."""
    t0 = time.time()
    out = {'test': 'F-2'}

    for N in (1024, 2048):
        L_mat, eig = spectrum_of(rp, N, odd_basis=True)
        cluster = eig[eig.real < FLOOR]
        mean_re = float(np.mean(cluster.real)) if len(cluster) else float('nan')
        max_member = float(np.max(cluster.real)) if len(cluster) else float('nan')
        out[f'cluster_size_N{N}'] = int(len(cluster))
        out[f'cluster_mean_re_N{N}'] = round(mean_re, 6)
        out[f'cluster_max_member_N{N}'] = round(max_member, 6)

    passed = all(
        abs(out[f'cluster_mean_re_N{N}'] - (-0.5)) <= 2e-3 and out[f'cluster_max_member_N{N}'] < FLOOR
        for N in (1024, 2048)
    )
    out['passed'] = bool(passed)
    out['elapsed_s'] = round(time.time() - t0, 1)
    return out


def run_F3():
    """F-3 MODULATION ROWS. (a) no eigenvalue within complex distance 5e-4 of 0 or 1;
    (b) spectral abscissa <= FLOOR. Uses modulated Jacobian (N1, N2 constraint rows)."""
    t0 = time.time()
    out = {'test': 'F-3'}

    solver = gCLMSolver(0.0, N=512, L=L)
    Omega, c_l, conv = solver.solve_profile(1.0, tol=1e-8, max_iter=50)
    out['profile_converged'] = bool(conv)
    out['c_l'] = round(float(c_l), 6)

    # Build the balanced residual Jacobian (ODE + 2 mod rows) around converged solution
    ft = solver.ft
    M = ft.M

    def residual(x):
        return solver._residual_balanced(x, 1.0)

    x0 = solver._pack(Omega, c_l)
    J = np.zeros((M + 1, M + 1))
    eps_fd = 1e-5
    r0 = residual(x0)
    for j in range(M + 1):
        xp = x0.copy()
        xp[j] += eps_fd
        J[:, j] = (residual(xp) - r0) / eps_fd

    eig = linalg.eigvals(J)
    eig = eig[np.isfinite(eig)]
    re = eig.real
    out['n_eig'] = int(len(eig))
    out['spectral_abscissa'] = round(float(np.max(re)), 6)

    # (a) no eigenvalue within complex distance 5e-4 of 0 or 1
    near_0 = [complex(z) for z in eig if abs(z) < DELTA]
    near_1 = [complex(z) for z in eig if abs(z - 1.0) < DELTA]
    out['n_near_0'] = int(len(near_0))
    out['n_near_1'] = int(len(near_1))
    out['near_0'] = [round(abs(z), 8) for z in near_0[:3]]
    out['near_1'] = [round(abs(z - 1.0), 8) for z in near_1[:3]]

    passed = (len(near_0) == 0) and (len(near_1) == 0) and (out['spectral_abscissa'] <= FLOOR)
    out['passed'] = bool(passed)
    out['elapsed_s'] = round(time.time() - t0, 1)
    return out


def run_F5(rp):
    """F-5 RESOLVENT-NORM / PSEUDOSPECTRAL. eps*||(z-eps-L)^-1|| > 1e2 => UNTRUSTED."""
    t0 = time.time()
    out = {'test': 'F-5', 'eigenvalues_checked': []}

    L_mat, eig = spectrum_of(rp, 1024, odd_basis=True)
    above = eig[eig.real > FLOOR]
    targets = []
    for z in above:
        if abs(z) < DELTA or abs(z - 1.0) < DELTA:
            targets.append(complex(z))
    out['n_targets'] = len(targets)

    for z in targets:
        m3 = resolvent_metric(L_mat, z, 1e-3)
        m4 = resolvent_metric(L_mat, z, 1e-4)
        untrusted = m3 > 1e2
        out['eigenvalues_checked'].append({
            'z': round(complex(z).real, 6),
            'eps1e3_metric': round(m3, 4),
            'eps1e4_metric': round(m4, 4),
            'UNTRUSTED': bool(untrusted),
        })

    out['n_untrusted'] = int(sum(1 for e in out['eigenvalues_checked'] if e['UNTRUSTED']))
    out['passed'] = bool(out['n_untrusted'] == 0)
    out['elapsed_s'] = round(time.time() - t0, 1)
    return out


def two_grid_floor(rp):
    """Observed two-grid eigenvalue difference for point eigenvalues and cluster mean."""
    t0 = time.time()
    out = {'test': 'TWO-GRID-FLOOR'}

    # Point eigenvalues (0,1) at N=1024 and N=2048
    _, e1024 = spectrum_of(rp, 1024, odd_basis=True)
    _, e2048 = spectrum_of(rp, 2048, odd_basis=True)

    def get_pair(eig, target):
        idx = np.argmin(np.abs(eig - target))
        return complex(eig[idx])

    p0_1024 = get_pair(e1024, 0.0)
    p0_2048 = get_pair(e2048, 0.0)
    p1_1024 = get_pair(e1024, 1.0)
    p1_2048 = get_pair(e2048, 1.0)

    d0 = abs(p0_1024 - p0_2048)
    d1 = abs(p1_1024 - p1_2048)

    c1024 = e1024[e1024.real < FLOOR].real
    c2048 = e2048[e2048.real < FLOOR].real
    d_cluster = abs(np.mean(c1024) - np.mean(c2048))

    out.update(
        lambda0_1024=round(p0_1024.real, 8), lambda0_2048=round(p0_2048.real, 8),
        lambda1_1024=round(p1_1024.real, 8), lambda1_2048=round(p1_2048.real, 8),
        d_lambda0=round(float(d0), 8), d_lambda1=round(float(d1), 8),
        cluster_mean_1024=round(float(np.mean(c1024)), 8),
        cluster_mean_2048=round(float(np.mean(c2048)), 8),
        d_cluster_mean=round(float(d_cluster), 8),
        observed_floor=max(round(float(d0), 8), round(float(d1), 8), round(float(d_cluster), 8)),
        borrowed_delta=DELTA,
        floor_ratio=round(max(float(d0), float(d1), float(d_cluster)) / DELTA, 3),
        elapsed_s=round(time.time() - t0, 1),
    )
    return out


def main():
    print("=" * 72)
    print("P1 FALSIFICATION BATTERY — LEG A (CLM SPECTRAL, gCLM a=0)")
    print(f"FLOOR = {FLOOR}  delta = {DELTA}  L = {L}")
    print("Execution order: F-4 FIRST, then F-1, F-2, F-3, F-5, then two-grid floor")
    print("=" * 72)

    rp = RealizationPair(N=1024, L=L)

    # ── F-4 FIRST ──
    print("\n[F-4] POSITIVE CONTROL (max-L2 strip) — run FIRST")
    r4 = run_F4()
    print(json.dumps(r4, indent=2, default=str))
    RESULTS['F-4'] = r4
    if not r4['passed']:
        print("\n*** ENGINE RED — F-4 FAILED. Do not evaluate F-1/F-2/F-3/F-5 as scored tests. ***")
        RESULTS['terminal'] = 'ENGINE-RED'
        save()
        return 1

    # ── F-1 ──
    print("\n[F-1] POINT SPECTRUM")
    r1 = run_F1(rp)
    print(json.dumps(r1, indent=2, default=str))
    RESULTS['F-1'] = r1

    # ── F-2 ──
    print("\n[F-2] ESSENTIAL SPECTRUM")
    r2 = run_F2(rp)
    print(json.dumps(r2, indent=2, default=str))
    RESULTS['F-2'] = r2

    # ── F-3 ──
    print("\n[F-3] MODULATION ROWS")
    r3 = run_F3()
    print(json.dumps(r3, indent=2, default=str))
    RESULTS['F-3'] = r3

    # ── F-5 ──
    print("\n[F-5] RESOLVENT-NORM / PSEUDOSPECTRAL")
    r5 = run_F5(rp)
    print(json.dumps(r5, indent=2, default=str))
    RESULTS['F-5'] = r5

    # ── Two-grid floor ──
    print("\n[TWO-GRID FLOOR] observed vs borrowed 5e-4")
    r6 = two_grid_floor(rp)
    print(json.dumps(r6, indent=2, default=str))
    RESULTS['TWO-GRID-FLOOR'] = r6

    # ── Battery verdict ──
    battery_pass = r1['passed'] and r2['passed'] and r3['passed']
    print("\n" + "=" * 72)
    print(f"F-4 (positive control): {'PASS' if r4['passed'] else 'FAIL'}")
    print(f"F-1 (point spectrum):   {'PASS' if r1['passed'] else 'FAIL'}")
    print(f"F-2 (essential spectrum): {'PASS' if r2['passed'] else 'FAIL'}")
    print(f"F-3 (modulation):       {'PASS' if r3['passed'] else 'FAIL'}")
    print(f"F-5 (resolvent):        {'PASS' if r5['passed'] else 'FAIL'}")
    if battery_pass:
        RESULTS['terminal'] = 'BATTERY-GREEN'
        print("BATTERY GREEN — proceeding to PALC + deflation and a=0.1 continuation")
    else:
        RESULTS['terminal'] = 'GOLD-MISS'
        print("GOLD-MISS — battery failure; terminal state (no continuation)")
    save()
    return 0 if battery_pass else 2


def save():
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work', 'p1-battery-results.json')
    with open(out_path, 'w') as f:
        json.dump(RESULTS, f, indent=2, default=str)
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    sys.exit(main())