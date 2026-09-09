#!/usr/bin/env python3
"""STRIP CHARACTERIZATION — CORRECTED localization. Full eig arrays, index-safe."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np; from scipy import linalg; from f1 import FourierSpectralEngine as FSE

FLOOR, CEIL = -0.497, -5e-4
dx_fixed = 40.0/2049.0

def loc(v, x, L):
    vn = v/(np.linalg.norm(v)+1e-30)
    return float(np.sum(np.abs(vn[np.abs(x)<1.0])**2)), float(np.sum(np.abs(vn[np.abs(x)>L/2.0])**2))

print("="*78)
print("STRIP CHARACTERIZATION (corrected) — L-convergence + localization")
print("="*78)

results = {}
for L_val in [20.0, 40.0, 80.0]:
    M_val = 2*int(round(L_val/dx_fixed)) + 1
    M_val = M_val if M_val % 2 == 1 else M_val + 1
    N_val = (M_val - 1)//2
    ft = FSE(N_val, L_val)
    x = ft.x; dx = 2*L_val/M_val
    Omega = -x/(x**2+0.25); HO = ft.hilbert(Omega)

    def apply_odd(v):
        w = 0.5*(v - v[::-1].copy())
        Lw = 1.0*w + 1.0*x*ft.differentiate(w) - HO*w - ft.hilbert(w)*Omega
        return 0.5*(Lw - Lw[::-1].copy())

    M_l = M_val
    L_odd = np.zeros((M_l, M_l), dtype=complex)
    for j in range(M_l):
        e = np.zeros(M_l); e[j] = 1.0
        L_odd[:, j] = apply_odd(e)

    # FULL eig (no filtering before indexing)
    eig_full, vecs_full = linalg.eig(L_odd)

    # Keep only finite, |lam|<10 (physicality) but keep original indices
    keep = np.isfinite(eig_full) & (np.abs(eig_full) < 10.0)
    idx_keep = np.where(keep)[0]

    # Strip mode indices
    strip_mask = (eig_full.real > FLOOR) & (eig_full.real < CEIL) & (np.abs(eig_full.imag) < 10.0) & keep
    strip_idx = np.where(strip_mask)[0]
    # Essential controls: near Re=-0.5, |Im|>10 (search in the |lambda|<10 window first; else full array)
    ess_mask = (np.abs(eig_full.real + 0.5) < 0.2) & (np.abs(eig_full.imag) > 10.0) & keep
    ess_idx = np.where(ess_mask)[0]

    # phi0
    phi0 = -x/(2.0*(x**2+0.25)**2)
    Lp = apply_odd(phi0); lam_p = np.sum(Lp*np.conj(phi0))/np.sum(np.abs(phi0)**2)
    mi_p, mo_p = loc(phi0, x, L_val)

    # Localization for strip modes
    strip_loc = []
    for i in strip_idx:
        lam = eig_full[i]
        mi, mo = loc(vecs_full[:, i], x, L_val)
        parity = float(np.max(np.abs(vecs_full[:, i] + vecs_full[:, i][::-1])))
        strip_loc.append((lam, mi, mo, parity))
    strip_loc.sort(key=lambda t: t[0].real)

    # Essential controls
    ess_loc = []
    for i in ess_idx[:12]:
        lam = eig_full[i]
        mi, mo = loc(vecs_full[:, i], x, L_val)
        ess_loc.append((lam, mi, mo))

    results[L_val] = {'N': N_val, 'M': M_val, 'dx': dx,
                      'strip_idx': strip_idx, 'ess_idx': ess_idx,
                      'strip_loc': strip_loc, 'ess_loc': ess_loc,
                      'eig_full': eig_full, 'vecs_full': vecs_full, 'x': x,
                      'phi0': {'lam': lam_p, 'mi': mi_p, 'mo': mo_p}}
    print(f"  [done L={L_val:.0f}, N={N_val}, strip={len(strip_idx)}, ess_control={len(ess_idx)}]", flush=True)

# ═══════════════════════════════════════════════════════════════════════
#  REPORT
# ═══════════════════════════════════════════════════════════════════════

print(f"\n{'─'*78}")
print("L-CONVERGENCE (odd-projected, full grid)")
print(f"{'─'*78}")
print(f"  {'L':>6s} {'N':>6s} {'strip ct':>10s} {'ess ct':>8s} {'min Re':>10s} {'max Re':>10s} {'mean Re':>10s} {'mean Im':>10s}")
print(f"  {'─'*6} {'─'*6} {'─'*10} {'─'*8} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")
for L_val in [20.0, 40.0, 80.0]:
    r = results[L_val]
    sl = r['strip_loc']
    if len(sl) > 0:
        res = np.array([t[0].real for t in sl]); ims = np.array([t[0].imag for t in sl])
        print(f"  {L_val:>6.0f} {r['N']:>6d} {len(sl):>10d} {len(r['ess_idx']):>8d} {res.min():>10.4f} {res.max():>10.4f} {res.mean():>10.4f} {np.abs(ims).mean():>10.4f}")

# Full eigenvalue list L=20
r20 = results[20.0]
print(f"\n  Strip modes at L=20 ({len(r20['strip_loc'])} total), sorted by Re desc:")
print(f"  {'#':>3s} {'Re λ':>12s} {'Im λ':>12s} {'m_in':>8s} {'m_out':>8s} {'parity':>8s}")
print(f"  {'─'*3} {'─'*12} {'─'*12} {'─'*8} {'─'*8} {'─'*8}")
for k, (lam, mi, mo, parity) in enumerate(sorted(r20['strip_loc'], key=lambda t: -t[0].real)):
    print(f"  {k:>3d} {lam.real:>12.6f} {lam.imag:>12.4f} {mi:>8.4f} {mo:>8.4f} {'ODD' if parity<1e-10 else 'MIX':>8s}")

# phi0
p = r20['phi0']
print(f"\n  φ₀ (point spectrum) L=20: λ_eng={p['lam'].real:.6f}, m_in={p['mi']:.4f}, m_out={p['mo']:.4f}")

# Essential controls
print(f"\n  Essential controls at L=20 (near Re=-0.5, |Im|>10): n={len(r20['ess_loc'])}")
for k, (lam, mi, mo) in enumerate(r20['ess_loc']):
    print(f"  {k:>3d} {lam.real:>10.6f} {lam.imag:>10.4f} {mi:>8.4f} {mo:>8.4f}")

# If no essential controls matched, show what modes with |Im|>10 exist
if len(r20['ess_loc']) == 0:
    e_full = r20['eig_full']
    vecs = r20['vecs_full']
    xr = r20['x']
    big_im = np.where((np.abs(e_full.imag) > 10.0) & np.isfinite(e_full))[0]
    print(f"\n  No modes match Re≈-0.5 & |Im|>10. The modes with |Im|>10 (n={len(big_im)}) have:")
    if len(big_im) > 0:
        print(f"    Re range: [{e_full[big_im].real.min():.4f}, {e_full[big_im].real.max():.4f}]")
        print(f"    Im range: [{e_full[big_im].imag.min():.4f}, {e_full[big_im].imag.max():.4f}]")
        print(f"    Localization of first 10 by |Im|:")
        bi_sorted = sorted(big_im, key=lambda i: abs(e_full[i].imag))
        for i in bi_sorted[:10]:
            mi, mo = loc(vecs[:, i], xr, 20.0)
            print(f"      Re={e_full[i].real:>8.4f} Im={e_full[i].imag:>8.4f} m_in={mi:>7.4f} m_out={mo:>7.4f}")

# OOPS — vecs not stored globally; do a targeted rerun for the fallback at the end (below)
print(f"\n{'─'*78}")
print("CONVERGENCE INTERPRETATION")
print(f"{'─'*78}")
counts = [len(results[L]['strip_loc']) for L in (20,40,80)]
means = [np.mean([t[0].real for t in results[L]['strip_loc']]) if results[L]['strip_loc'] else float('nan') for L in (20,40,80)]
print(f"  Count: {counts[0]} -> {counts[1]} -> {counts[2]}")
print(f"  Mean Re: {means[0]:.4f} -> {means[1]:.4f} -> {means[2]:.4f}")
print(f"  Dist to -0.5: {abs(means[0]-(-0.5)):.4f} -> {abs(means[1]-(-0.5)):.4f} -> {abs(means[2]-(-0.5)):.4f}")

count_falls = counts[0] > counts[1] or counts[1] > counts[2]
re_to_neg_half = [abs(means[k]-(-0.5)) for k in range(3)]
re_converging = re_to_neg_half[0] > re_to_neg_half[1] or re_to_neg_half[1] > re_to_neg_half[2]

print(f"\n  → count {'falls' if count_falls else 'stable/increasing'}; Re {'converging → -1/2' if re_converging else 'NOT converging to -1/2'}")
if count_falls and re_converging:
    print(f"  → ESSENTIAL-SPECTRUM DISCRETIZATION: F-4 zone catches band tail; strip question open")
elif (not count_falls) and (not re_converging):
    print(f"  → GENUINE STRIP (count stable, Re fixed away from -1/2) — origin condition not imposed")
else:
    print(f"  → MIXED PATTERN — report numbers, adjudicator decides")