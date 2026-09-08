#!/usr/bin/env python3
"""
Eigenvector localization — mass fractions m_in, m_out.
Pre-registered:
  populations:
    P1: 20 odd residuals (origin-H2 strip modes)
    P2: 22 naive positive-Re strip modes
    P3: {0} mode (both operators) and {1} mode (naive only) — controls, known point spectrum
    P4: 10 essential-cluster modes (|Im|>10, Re near -1/2 on origin-H2) — controls, essential discretization
  Expected under H-A (20 = essential artifacts): P1 ~ P4 (m_out large), P2 ~ P3 (m_in large)
  Expected under H-B (20 = odd half of strip, engine incomplete): P1 ~ P2 ~ P3 (all m_in large)
L=20, N=1024. No engine edits. $0.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np
from scipy import linalg
from f1 import RealizationPair, FourierSpectralEngine

L = 20.0; N = 1024
P0_THRESH = -0.5 + 1e-3
M = 2*N + 1
center = M // 2  # index of x=0

rp = RealizationPair(N=N, L=L)
ft = FourierSpectralEngine(N, L)
x = ft.x  # [-L, L], length M=2049

# Inner region: |xi| < 1
inner_mask = np.abs(x) < 1.0
# Outer region: |xi| > L/2
outer_mask = np.abs(x) > L/2
# Right-half indices for origin-H2 eigenvectors
center = M // 2
right_ix = np.arange(center, M)
x_right = x[right_ix]
inner_mask_right = np.abs(x_right) < 1.0
outer_mask_right = np.abs(x_right) > L/2

def mass_fractions(v, domain='full'):
    """Compute m_in, m_out for eigenvector v on given domain."""
    n = np.linalg.norm(v)
    if n < 1e-15:
        return (0.0, 0.0)
    vn = v / n
    if domain == 'full':
        m_in = float(np.sum(np.abs(vn[inner_mask])**2))
        m_out = float(np.sum(np.abs(vn[outer_mask])**2))
    elif domain == 'right_half':
        m_in = float(np.sum(np.abs(vn[inner_mask_right])**2))
        m_out = float(np.sum(np.abs(vn[outer_mask_right])**2))
    return (m_in, m_out)

# Build operators and get eigendecompositions
L_naive = rp._build_operator(a=0.0, odd_basis=False)
L_h2 = rp._build_operator(a=0.0, odd_basis=True)

e_n, v_n = linalg.eig(L_naive)
e_h, v_h = linalg.eig(L_h2)

# Filter |eig| < 10
filt_n = np.abs(e_n) < 10.0
e_nf = e_n[filt_n]; v_nf = v_n[:, filt_n]
filt_h = np.abs(e_h) < 10.0
e_hf = e_h[filt_h]; v_hf = v_h[:, filt_h]

# ── Classify populations ──

# P1: 20 odd residuals (origin-H2 strip modes, P0 zone)
re_h = e_hf.real
mask_h_strip = (re_h > P0_THRESH) & (np.abs(e_hf) > 1e-2) & (np.abs(e_hf - 1.0) > 1e-2)
p1_eig = e_hf[mask_h_strip]
p1_vec = v_hf[:, mask_h_strip]

# Remove {0} if present
p1_nonzero_idx = np.abs(p1_eig) > 5e-4
p1_eig = p1_eig[p1_nonzero_idx]
p1_vec = p1_vec[:, p1_nonzero_idx]

# P2: 22 naive positive-Re strip modes (P0 zone, Re > 0)
re_n = e_nf.real
mask_n_strip = (re_n > P0_THRESH) & (np.abs(e_nf) > 1e-2) & (np.abs(e_nf - 1.0) > 1e-2)
p2_all_eig = e_nf[mask_n_strip]
p2_all_vec = v_nf[:, mask_n_strip]
# Separate positive-Re and negative-Re
p2_pos_idx = p2_all_eig.real > 0
p2_eig = p2_all_eig[p2_pos_idx]
p2_vec = p2_all_vec[:, p2_pos_idx]
# Negative-Re naive modes (the ones also in H2)
p2neg_eig = p2_all_eig[~p2_pos_idx]
p2neg_vec = p2_all_vec[:, ~p2_pos_idx]

# P3: {0} mode (both operators) and {1} mode (naive only)
# {0} on origin-H2
p3_0_h = e_hf[np.argmin(np.abs(e_hf))]
# {0} on naive
p3_0_n = e_nf[np.argmin(np.abs(e_nf))]
# {1} on naive (nearest eigenvalue to 1)
p3_1_idx = np.argmin(np.abs(e_nf - 1.0))
p3_1_n = e_nf[p3_1_idx]
p3_1_v = v_nf[:, p3_1_idx]

# P4: 10 essential-cluster modes (|Im|>10, Re near -1/2 on origin-H2)
# These are high-imaginary modes — discretization of the essential spectrum
im_h = np.abs(e_hf.imag)
mask_ess = (im_h > 10) & (np.abs(e_hf.real + 0.5) < 0.1)
p4_eig = e_hf[mask_ess]
p4_vec = v_hf[:, mask_ess]

def report_pop(label, eig, vecs, domain='full'):
    if len(eig) == 0:
        print(f"{label}: NO MODES")
        return
    print(f"\n{label} ({len(eig)} modes)")
    mins_in = []; mins_out = []
    for k in range(min(len(eig), 20)):
        v = vecs[:, k]
        # For full-domain eigenvectors (naive), use full-domain mass fraction
        m_in, m_out = mass_fractions(v, domain)
        mins_in.append(m_in); mins_out.append(m_out)
    print(f"  m_in  (|xi|<1):  mean={np.mean(mins_in):.4f}  min={np.min(mins_in):.4f}  max={np.max(mins_in):.4f}")
    print(f"  m_out (|xi|>L/2): mean={np.mean(mins_out):.4f}  min={np.min(mins_out):.4f}  max={np.max(mins_out):.4f}")
    return {'n': len(eig), 'm_in_mean': float(np.mean(mins_in)), 'm_out_mean': float(np.mean(mins_out)),
            'm_in_min': float(np.min(mins_in)), 'm_in_max': float(np.max(mins_in)),
            'm_out_min': float(np.min(mins_out)), 'm_out_max': float(np.max(mins_out))}

print("="*80)
print("EIGENVECTOR LOCALIZATION — mass fractions at L=20, N=1024")
print("="*80)

r1 = report_pop("P1: Odd residuals (origin-H2 strip)", p1_eig, p1_vec, 'right_half')
r2 = report_pop("P2: Naive positive-Re strip modes", p2_eig, p2_vec, 'full')
r2n = report_pop("P2neg: Naive negative-Re strip modes", p2neg_eig, p2neg_vec, 'full')

# P3: individual controls
print("\nP3: Control modes")
for label, ev, vec, dom in [("{0} on H2", p3_0_h, v_hf[:, np.argmin(np.abs(e_hf))], 'right_half'),
                         ("{0} on naive", p3_0_n, v_nf[:, np.argmin(np.abs(e_nf))], 'full'),
                         ("{1} on naive", p3_1_n, p3_1_v, 'full')]:
    mi, mo = mass_fractions(vec, dom)
    print(f"  {label}: λ={ev.real:.6f}{ev.imag:+.6f}j  m_in={mi:.4f}  m_out={mo:.4f}")

r4 = report_pop("P4: Essential-cluster controls (|Im|>10)", p4_eig, p4_vec, 'right_half')

# ── Hypothesis test ──
print(f"\n{'='*80}")
print("HYPOTHESIS TEST")
print("="*80)

# If H-A holds: P1 ~ P4 (m_out large, delocalized), P2 ~ P3 (m_in large, localized)
# If H-B holds: P1 ~ P2 ~ P3 (all localized)

mean_in_p1 = r1['m_in_mean'] if r1 else 0
mean_in_p2 = r2['m_in_mean'] if r2 else 0
mean_in_p4 = r4['m_in_mean'] if r4 else 0
mean_out_p1 = r1['m_out_mean'] if r1 else 0
mean_out_p2 = r2['m_out_mean'] if r2 else 0
mean_out_p4 = r4['m_out_mean'] if r4 else 0

print(f"  P1 (odd residuals): m_in={mean_in_p1:.4f}, m_out={mean_out_p1:.4f}")
print(f"  P2 (pos-Re strip):  m_in={mean_in_p2:.4f}, m_out={mean_out_p2:.4f}")
print(f"  P4 (ess controls):  m_in={mean_in_p4:.4f}, m_out={mean_out_p4:.4f}")

if abs(mean_in_p1 - mean_in_p4) < abs(mean_in_p1 - mean_in_p2):
    h_verdict = "H-A holds: odd residuals resemble essential-spectrum discretization (delocalized)"
elif abs(mean_in_p1 - mean_in_p2) < 0.1 and abs(mean_in_p1 - mean_in_p4) > 0.1:
    h_verdict = "H-B holds: odd residuals resemble point-spectrum modes (localized)"
else:
    h_verdict = "INCONCLUSIVE — distributions not clearly separated"

print(f"\n  Verdict: {h_verdict}")

# Detailed: look at per-mode distribution
print(f"\n{'='*80}")
print("PER-MODE BREAKDOWN")
print("="*80)

print(f"\nP1 odd residuals — m_in distribution:")
for k in range(min(len(p1_eig), 20)):
    v = p1_vec[:, k]
    mi, mo = mass_fractions(v, 'right_half')
    print(f"  [{k:>2d}] λ={p1_eig[k].real:+.6f}{p1_eig[k].imag:+.4f}j  m_in={mi:.4f}  m_out={mo:.4f}")

print(f"\nP2 pos-Re strip — m_in distribution:")
for k in range(min(len(p2_eig), 22)):
    v = p2_vec[:, k]
    mi, mo = mass_fractions(v, 'full')
    print(f"  [{k:>2d}] λ={p2_eig[k].real:+.6f}{p2_eig[k].imag:+.4f}j  m_in={mi:.4f}  m_out={mo:.4f}")

out = {
    'P1_odd_residuals_H2': {
        'n': len(p1_eig),
        'm_in_mean': float(np.mean([mass_fractions(p1_vec[:,k], 'right_half')[0] for k in range(len(p1_eig))])),
        'm_out_mean': float(np.mean([mass_fractions(p1_vec[:,k], 'right_half')[1] for k in range(len(p1_eig))])),
    },
    'P2_pos_Re_naive_strip': {
        'n': len(p2_eig),
        'm_in_mean': float(np.mean([mass_fractions(p2_vec[:,k], 'full')[0] for k in range(len(p2_eig))])),
        'm_out_mean': float(np.mean([mass_fractions(p2_vec[:,k], 'full')[1] for k in range(len(p2_eig))])),
    },
    'P4_essential_controls': {
        'n': len(p4_eig),
        'm_in_mean': float(np.mean([mass_fractions(p4_vec[:,k], 'right_half')[0] for k in range(len(p4_eig))])),
        'm_out_mean': float(np.mean([mass_fractions(p4_vec[:,k], 'right_half')[1] for k in range(len(p4_eig))])),
    },
    'verdict': h_verdict,
}
with open('work/eigenvector-localization-results.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nResults saved to work/eigenvector-localization-results.json")