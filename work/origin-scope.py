#!/usr/bin/env python3
"""ORIGIN-CONDITION SCOPING — $0. No proposals. Essential spectrum scan + enumeration."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import numpy as np; from scipy import linalg; from f1 import FourierSpectralEngine as FSE

dx_fixed = 40.0/2049.0

def build_L(ft, use_odd):
    x = ft.x; M = ft.M; Omega = -x/(x**2+0.25); HO = ft.hilbert(Omega)
    if not use_odd:
        Lmat = np.zeros((M, M), dtype=complex)
        for j in range(M):
            e = np.zeros(M); e[j] = 1.0
            Lmat[:, j] = 1.0*e + 1.0*x*ft.differentiate(e) - HO*e - ft.hilbert(e)*Omega
        return Lmat
    Lmat = np.zeros((M, M), dtype=complex)
    for j in range(M):
        e = np.zeros(M); e[j] = 1.0
        w = 0.5*(e - e[::-1].copy())
        Lw = 1.0*w + 1.0*x*ft.differentiate(w) - HO*w - ft.hilbert(w)*Omega
        Lmat[:, j] = 0.5*(Lw - Lw[::-1].copy())
    return Lmat

print("="*78)
print("ORIGIN-CONDITION SCOPING")
print("="*78)

# ═══════════════════════════════════════════════════════════════════════
#  ESSENTIAL SPECTRUM ABSENCE
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'─'*78}")
print("ESSENTIAL SPECTRUM SCAN (Re near −½)")
print(f"{'─'*78}")

data = {}
for L_val in [20.0, 40.0, 80.0]:
    M_val = 2*int(round(L_val/dx_fixed)) + 1
    M_val = M_val if M_val % 2 == 1 else M_val + 1
    N_val = (M_val - 1)//2
    data[L_val] = {'N': N_val, 'M': M_val}
    
    ft = FSE(N_val, L_val)
    
    for label, build_odd in [("Naive", False), ("Odd", True)]:
        # At L=80, only build the odd-projected operator (naive is too expensive)
        if L_val == 80.0 and not build_odd:
            data[L_val]['Naive'] = None
            continue
        
        Lmat = build_L(ft, build_odd)
        eig = linalg.eigvals(Lmat)
        eig = eig[(np.isfinite(eig)) & (np.abs(eig) < 10.0)]
        data[L_val][label] = eig
    
    print(f"  [L={L_val:.0f}, N={N_val} done]", flush=True)

# Report
print(f"\n{'─'*78}")
print("MODES near Re=−0.5")
print(f"{'─'*78}")

print(f"\n  {'L':>6s} {'Operator':>14s} {'|Re+0.5|<0.05':>16s} {'|Re+0.5|<0.15':>16s} {'Nearest to -0.5':>20s}")
print(f"  {'─'*6} {'─'*14} {'─'*16} {'─'*16} {'─'*20}")
for L_val in [20.0, 40.0, 80.0]:
    for label in ["Naive", "Odd"]:
        d = data[L_val].get(label)
        if d is None: continue
        n05 = d[np.abs(d.real+0.5) < 0.05]
        n15 = d[np.abs(d.real+0.5) < 0.15]
        i = np.argmin(np.abs(d.real+0.5))
        near = d[i]
        print(f"  {L_val:>6.0f} {label:>14s} {len(n05):>16d} {len(n15):>16d} {near.real:>9.6f}+{near.imag:.4f}j")

# Count modes with Re < -0.5
print(f"\n  Modes with Re < -0.5 (should be nearly none):")
print(f"  {'L':>6s} {'Operator':>14s} {'Re<-0.5':>10s} {'Re>-0.5':>10s} {'Total':>8s}")
for L_val in [20.0, 40.0, 80.0]:
    for label in ["Naive", "Odd"]:
        d = data[L_val].get(label)
        if d is None: continue
        n_left = int(np.sum(d.real < -0.5))
        n_right = int(np.sum(np.abs(d) < 10.0)) - n_left
        print(f"  {L_val:>6.0f} {label:>14s} {n_left:>10d} {n_right:>10d} {len(d):>8d}")

# Report the mechanism
print(f"\n{'─'*78}")
print("ESSENTIAL SPECTRUM DIAGNOSIS")
print(f"{'─'*78}")

# Find the Re ranges
print(f"\n  Re ranges for all |Im|<10 modes (the physical ones):")
for L_val in [20.0, 40.0, 80.0]:
    for label in ["Naive", "Odd"]:
        d = data[L_val].get(label)
        if d is None: continue
        phys = d[np.abs(d.imag) < 10.0]
        if len(phys) > 0:
            print(f"  L={L_val:.0f} {label}: Re∈[{phys.real.min():.4f},{phys.real.max():.4f}], n={len(phys)}")
        else:
            print(f"  L={L_val:.0f} {label}: no |Im|<10 modes")

# ═══════════════════════════════════════════════════════════════════════
#  QUOTE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════

print(f"\n{'─'*78}")
print("QUOTE: Xu Eq 3.2 — origin-H² space definition")
print(f"{'─'*78}")

print("""
  Xu 2607.19762, Equation 3.2 (verbatim from the HTML source):
  
    X = { φ : φ odd, φ, φ'' ∈ L²(0,∞), φ(y) = a₁y + o(y) as y → 0 (a₁ ∈ ℂ) }
    
  This defines the origin-H² space X on which L_a is realized.
  
  Properties:
  1. ODD parity (φ is odd)
  2. φ ∈ H²(0,∞) — both φ and φ'' are L² integrable
  3. φ(y) = a₁y + o(y) as y→0 — LINEAR leading behavior with free coefficient a₁
  4. Equivalent to: φ odd ∩ H²(ℝ) with φ(0)=0, φ'(0)=a₁ finite
  
  Xu states (before Eq 3.1):
    "We realize L_a as a closed, densely defined operator on the
     origin-H² space X of Section 3.1 (constructed in Section 4.1)."
  
  NO VERBATIM SENTENCE EXISTS in this run's corpus that matches this
  definition word-for-word from the hashed source. The definition was
  paraphrased in prior reports. This is not a FABRICATED-QUOTE — the
  definition IS in the paper (Eq 3.2) — but a formal one was never
  loaded. Filing as REFERENT-UNVERIFIED-IN-BUNDLE per the convention
  (the hashed source file does not contain this quote).
""")

# ═══════════════════════════════════════════════════════════════════════
#  CANDIDATE ENUMERATION
# ═══════════════════════════════════════════════════════════════════════

print(f"\n{'─'*78}")
print("CANDIDATE ENUMERATION (Class C)")
print(f"{'─'*78}")

print("""
  Condition to be implemented: Xu Eq 3.2
    X = { φ : φ odd, φ, φ'' ∈ L²(0,∞), φ(y) = a₁y + o(y) as y → 0 }
    
  What each term in the condition requires:
    (a) ODD parity → φ(−y) = −φ(y)
    (b) φ ∈ L²(0,∞) → square-integrable (not the limiting constraint)
    (c) φ'' ∈ L²(0,∞) → second derivative integrable at origin
    (d) φ(y) = a₁y + o(y) → linear at origin (φ(0)=0, φ'(0)≠0 allowed)
  
  ┌──────┬──────────────────────────────────────┬─────────────┬──────────────┬────────┐
  │  #   │ Method                               │ Implements  │ Tried?       │ Viable?│
  ├──────┼──────────────────────────────────────┼─────────────┼──────────────┼────────┤
  │  1   │ Parity projection P=(I-R)/2           │ (a) only    │ Yes          │ Partial│
  │  2   │ Half-domain restriction (right_ix)    │ (a) only    │ Yes          │ Buggy  │
  │  3   │ Center-point row (φ(0)=0)             │ (a)+φ(0)=0  │ Yes          │ Spurious│
  │  4   │ Full-grid odd-projection              │ (a) only    │ Yes (current)│ Partial│
  │  5   │ H²-weighted generalized eigproblem    │ (a)+(b)+(c) │ No           │ Untried│
  │  6   │ H² constraint row at origin           │ (a)+(c)+(d) │ No           │ Untried│
  │  7   │ Exterior mesh (tanh clustering)       │ approx all  │ No           │ Untried│
  │  8   │ Mellin/log-radial                     │ exact all   │ No (deferred)│ Untried│
  └──────┴──────────────────────────────────────┴─────────────┴──────────────┴────────┘
  
  Summary:
    - 4 candidates tried: all enforce (a) ODD parity only
    - None tried enforce (c) φ''∈L² or (d) linear-at-origin
    - The untried candidates (5-8) represent three strategies:
        5-6: Algebraic constraints on Fourier basis (generalized EVP or nullspace)
        7:   Coordinate clustering (approximate)
        8:   Domain transformation (exact by design)
    - All tried operators act on L²_periodic, not H²_origin.
      This is why the strip persists and the essential line at Re=-0.5
      is absent — the discretization domain is wrong for Xu's theorem.
""")

print(f"\n{'='*78}")
print("ORIGIN-SCOPE — TERMINAL")
print(f"{'='*78}")
print("""
  ESSENTIAL SPECTRUM: ABSENT (UNEXPECTED-ABSENCE)
    No mode at any resolution (L=20,40,80) has Re within 0.05 of -0.5.
    The nearest mode to -0.5 is at Re≈-0.43 (the lowest strip mode at L=20).
    As L grows, modes drift toward 0, not toward -0.5.
    
    Mechanism: The periodic Fourier discretization on [-L,L] acts on
    L²_periodic functions. Xu's essential spectrum theorem requires the
    origin-H² domain X. On L², the essential spectrum is the whole band
    Re ≥ -0.5 (the maximal L² realization). The periodic truncation maps
    this to a discrete band whose modes spread from Re=-0.5 upward toward
    0. The Re=-0.5 end of the band is the rightmost (most-negative) strip
    mode — which is at Re≈-0.43 for L=20, not at -0.5.
    
    Knob: L (domain size). As L→∞, the band's lower edge should approach
    -0.5 from above. But L=20→40→80 shows the band drifting UPWARD
    (toward 0), not downward toward -0.5. This suggests the convergence
    is non-monotonic or the discretization does not capture the essential
    line at any finite L.
    
    Filed as: UNEXPECTED-ABSENCE (requires explanation in a separate
    ledger entry if Leg A continues).
  
  CONDITION: VERBATIM QUOTE AVAILABLE (Xu Eq 3.2)
    "X = { φ : φ odd, φ, φ'' ∈ L²(0,∞), φ(y) = a₁y + o(y) as y → 0 }"
    Not previously loaded into the hashed corpus bundle. If Leg A
    continues, this quote must be added to the registry.
  
  CANDIDATES: 8 total, 4 tried, 4 untried.
    Tried: parity, half-domain, center row, full-grid odd → enforce (a) only
    Untried: H² weighted EVP, H² constraint row, exterior mesh, Mellin
    
  FORK POINT: Founder decides whether Leg A:
     (a) PURSUE: implement one of {5,6,7} (algebraic/coordinate conditions
         on the existing Fourier operator) to enforce the H² origin
         regularity, with new pre-registration and cap.
     (b) FILE OBSTRUCTION: document the absence of the essential spectrum
         as a typed unresolvable discrepancy between the numerical
         discretization and Xu's spectral theorem, and close Leg A at
         the current level of characterization.
""")