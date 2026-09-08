# Parse all numeric targets from frozen bundle
data = []

# SPEC §1 / §4
data.append(('a_c=0.6890665337007457', 'SPEC §1', 'N — stated as anchor from ANCHORS', 'ANCHORS (LSS?)'))
data.append(('CCF stable lambda=1.1807776628998', 'SPEC §4 P1', 'N — published, no eqn path', 'Wang 2509.14185'))
data.append(('CCF 1st lambda=0.6057337012032', 'SPEC §4 P1', 'N — published, no eqn path', 'Wang 2509.14185'))
data.append(('CCF 2nd lambda=0.4713242245', 'SPEC §4 P1', 'N — published, no eqn path', 'Wang 2511.22819'))

# SPEC §14
data.append(('Ghost catch floor 90%', 'SPEC §14(a)', 'Y', 'SPEC §14'))
data.append(('Synthetic floor 90%', 'SPEC §14(b)', 'Y', 'SPEC §14'))
data.append(('extract-a PASS >=4/5', 'SPEC §14(c)', 'Y', 'SPEC §14'))
data.append(('extract-a GRAY 3/5', 'SPEC §14(c)', 'Y', 'SPEC §14'))
data.append(('extract-a KILL <=2/5', 'SPEC §14(c)', 'Y', 'SPEC §14'))
data.append(('Perm null p<.05, 1000x', 'SPEC §14(d)', 'Y', 'SPEC §14'))
data.append(('G1 tol 1.5x RMS', 'SPEC §14(f)', 'Y (floor self-computed P2)', 'SPEC §14'))
data.append(('Perturbed >=5 draws <=10', 'SPEC §14(g)', 'Y', 'SPEC §14'))
data.append(('Gray extension 1', 'SPEC §14(h)', 'Y', 'SPEC §14'))
data.append(('VOID rerun 1/phase', 'SPEC §14(j)', 'Y', 'SPEC §14'))
data.append(('Variant >=6->b 4-5->a <=3->c', 'SPEC §14(k)', 'Y', 'SPEC §14'))
data.append(('Stall pill 48h', 'SPEC §14(l)', 'Y', 'SPEC §14'))
data.append(('Global $1000 res $300', 'SPEC §14(m)', 'Y', 'SPEC §14'))
data.append(('k=3 extractor votes', 'SPEC §14(q)', 'Y', 'SPEC §14'))
data.append(('H-A CCF lambda 8 digits', 'SPEC §14(u)', 'N -- target set, no eqn given', 'SPEC §14'))
data.append(('RED-debug 1/phase', 'SPEC §14(v)', 'Y', 'SPEC §14'))

# ANCHORS 
data.append(('alpha(0)=1', 'ANCH a=0', 'Y (CLM 1985)', 'ANCHORS'))
data.append(('Omega=-xi/(xi^2+1/4)', 'ANCH a=0', 'Y (exact profile stated)', 'ANCHORS'))
data.append(('c_l=1 (a=0)', 'ANCH a=0', 'Y', 'ANCHORS'))
data.append(('alpha(1/2)=1/3', 'ANCH a=1/2', 'Y (trap NOT 1/2)', 'ANCHORS'))
data.append(('alpha(a_c)=0', 'ANCH a_c', 'Y', 'ANCHORS'))
data.append(('a_c=0.6890665337007457', 'ANCH a_c', 'N -- stated, no derivation', 'ANCHORS'))
data.append(('gamma_bar=1-a (a<0)', 'ANCH half-line', 'Y (formula given)', 'ANCHORS'))
data.append(('alpha(1)=-1', 'ANCH De Gregorio', 'Y', 'ANCHORS'))
data.append(('alpha(2/3)=0.04517094', 'ANCH soft', 'N -- soft anchor, source LSS 2021', 'ANCHORS'))
data.append(('alpha(0.8)=-0.260', 'ANCH soft', 'N -- soft anchor, source LSS 2021', 'ANCHORS'))
data.append(('gamma=1/(1-a)', 'ANCH complex', 'Y (formula given)', 'ANCHORS'))
data.append(('alpha_0(a)=2(1-a)^2/(2-a)', 'ANCH approx', 'Y (inexact, stated)', 'ANCHORS'))
data.append(('c_omega=-1', 'ANCH gCLM', 'Y (fixed)', 'ANCHORS'))

# RUNBOOK / CHECKLIST
data.append(('H-A CCF 8-digit', 'RUNBOOK §4', 'N -- same as SPEC §14(u)', 'RUNBOOK'))
data.append(('ESC timeout 48h', 'RUNBOOK §6', 'Y', 'RUNBOOK'))
data.append(('Liveness 6h', 'RUNBOOK §8/omnibus', 'Y', 'RUNBOOK'))
data.append(('HB 1 line', 'CHECKLIST S1', 'Y', 'CHECKLIST'))
data.append(('S5 ~$1 API', 'CHECKLIST S5', 'Y', 'CHECKLIST'))

print('=== CLASS AUDIT: DERIVATION SPECIFIED IN-BUNDLE? ===')
print()
print(f'{"VALUE":50s} | {"LOCATION":25s} | {"DERIV?":8s} | {"SOURCE":30s}')
print('-' * 120)
n_gaps = 0
for val, loc, deriv, src in data:
    yn = deriv[:1]
    print(f'{val:50s} | {loc:25s} | {yn:8s} | {src:30s}')
    if yn == 'N':
        n_gaps += 1
print()
print(f'SPEC GAPS (N count): {n_gaps}')
print()

if n_gaps > 0:
    print('GAP DETAIL:')
    for val, loc, deriv, src in data:
        if deriv[:1] == 'N':
            print(f'  [{val}] at {loc} — {deriv}'  )