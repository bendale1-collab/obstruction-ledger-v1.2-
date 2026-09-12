# Proxy Architecture-Decorrelation Gate (Gate 1 for ML-IP Kill Tests)

**When to use:** A computational-chemistry or materials-science thesis proposes using multiple learned models (GNNs, equitransformer, etc.) as "independent" energy proxies, and the kill test checks whether their errors are decorrelated enough to count as independent witnesses. Gate 1 is the **proxy architecture-decorrelation check**: compute the effective rank of the error-correlation matrix and compare against a pre-registered threshold (typically 1.5).

## The core insight

Three GNNs trained on the **same training data** (OC20/OC22) share the same failure modes — their error patterns are almost certainly **rank-one** (all correlate with each other because they all learned from the same underlying bias). Running three same-family models is not a valid multiplexing strategy. The only way to get independent error signals is to use **proxies from different physical regimes**:

| Proxy type | Physics regime | Cost | All elements? |
|------------|---------------|------|---------------|
| Classical FF (EMT) | Embedded-atom metals | ~1ms/structure | ❌ (Au, Ag, Cu, Pt, Pd, Ni, Al only) |
| Classical FF (LJ) | Generic pair potential | ~30ms/structure | ✅ |
| Semi-empirical QM (GFN0-xTB) | Tight-binding | ~0.2-1s/structure | ✅ |
| Learned GNN (MACE-MP-0) | Equivariant MP, MP data | ~0.5-0.9s/structure | ✅ |
| Learned GNN (CHGNet) | Crystal Hamiltonian, MP data | ~1-2s/structure | ✅ |
| DFT (reference) | First-principles | hours/structure | ✅ |
| GNN (SchNet) | Learned OC20→OC22 transfer | ~300ms/structure | ✅ |

## Execution order (workflow correction from 2026-06-29 session)

**Correct order of operations for Gate 1:**

1. **Check for pre-computed predictions FIRST.** The OC22 evaluation server (EvalAI) and official model repos may have downloadable prediction files. If found → align on system/sample IDs, subtract DFT truth, compute eff_rank — no inference needed.

2. **IF pre-computed predictions are NOT available** (common — EvalAI is login-gated, fairchem repo has none, HuggingFace has only raw DFT data):
   - Do NOT run three same-family GNNs (same training data → almost certainly rank-one)
   - Instead, run **exactly one classical force-field proxy** (CPU, no checkpoint) over a few thousand structures
   - Pair it with **exactly one cheaply-obtained GNN prediction** (SchNet is the cheapest at 14MB checkpoint)
   - Compute eff_rank on these 2-3 decorrelated-by-physics proxies

3. **IF EMT fails** (it will — OC22 is oxides, every structure contains oxygen, and EMT only supports 7 metals): use **LennardJones** (generic pair potential, works for all elements, CPU-only) as the classical proxy instead. It's physically meaningless for oxides, which is exactly the point — its errors are completely decorrelated from any learned-model error.

4. **IF LJ also fails** (it's noise, not signal — corr with DFT ≈ -0.07 for oxides): upgrade to **GFN0-xTB** (semi-empirical QM, real chemistry, broad element coverage, ~0.2s/structure on CPU). Install via micromamba (see GFN0-xTB setup section below).

## Anti-correlation correction (IMPORTANT — eff_rank blind spot)

eff_rank treats +0.78 and -0.78 correlation identically, but they are **fundamentally different for ensemble construction**:

- **Positively correlated errors (r ≈ +0.8):** both proxies over/under-shoot in the same direction. Redundant — combining offers minimal improvement. eff_rank ≈ 1.2 genuinely signals rank-one collapse.
- **Anti-correlated errors (r ≈ -0.8):** errors cancel when combined. This is the **ideal ensemble configuration**, not a redundancy signal. eff_rank ≈ 1.25 is misleading here.

**Decision rule:** When eff_rank < 1.5, check the sign of the off-diagonal:
- If r > 0 (positively correlated errors) → eff_rank is meaningful. Continue as normal: RANK_ONE_KILL.
- If r < 0 (anti-correlated errors) → eff_rank is a FALSE NEGATIVE. Run the variance-minimizing linear combination test below instead.

## Variance-minimizing linear combination test (for anti-correlated pairs)

When errors are anti-correlated, the correct test is: does combining the two proxies beat the best single proxy?

### Method

1. **Split** data into training (e.g. 200) and test (e.g. 100) sets
2. **On the training set**, solve for the weight w that minimizes the ensemble error variance:

   ```
   w = (Var(err_b) - Cov(err_a, err_b)) / (Var(err_a) + Var(err_b) - 2*Cov(err_a, err_b))
   ```

   where the combined prediction is: `y_hat = w * proxy_a + (1-w) * proxy_b`

   Clamp w to [0, 1] for interpretability.

3. **On the held-out test set**, compare RMSE of four estimators:
   - Proxy A alone
   - Proxy B alone
   - 50/50 average
   - Optimal-w combination

4. **PASS condition:** The optimal-w combination's RMSE is meaningfully lower (≥5% reduction) than the best single proxy's RMSE, out-of-sample.

### Example result (GFN0-xTB + SchNet on 300 OC22 val_id structures, 200/100 split)

| Estimator | RMSE (eV) | vs best single |
|-----------|-----------|----------------|
| xtb alone | 5979.97 | — |
| SchNet alone | 547.03 | baseline |
| 50/50 avg | 2725.77 | **+398%** ✗ |
| **optimal-w (w=0.077)** | **127.69** | **−76.66%** ✓ |

Even though eff_rank was only 1.25 (below the 1.5 threshold), the optimal combination produced a **4× RMSE reduction** (127.7 vs 547.0 eV). The tiny xtb weight (7.7%) was enough to cancel SchNet's error because the two errors anti-correlate at r = -0.79.

**Important:** The 50/50 average FAILS here (makes things worse) because xtb has much larger variance than SchNet. The variance-minimizing w correctly finds the 7.7% sweet spot.

## Data source: OC22 validation set

Available as HuggingFace dataset `nimashoghi/oc22`:

| Split | Rows | Ground truth |
|-------|------|-------------|
| train | 8.23M | yes |
| val_id | 395k | **yes** (column `y`) |
| val_ood | 451k | **yes** |
| test_id | 398k | NaN |
| test_ood | 385k | NaN |

Download a single parquet shard (299MB for 98k structures) and use only `val_id` (has `y` — DFT ground truth energy):
```
https://huggingface.co/datasets/nimashoghi/oc22/resolve/main/data/val_id-00000-of-00004.parquet
```

## Parquet parsing (critical — the data format is nested)

The parquet stores cell and positions as **object arrays of arrays**. Standard `pd.read_parquet()` or `pq.read_table()` gives you 1D object arrays with length=1 for cell and length=num_atoms for positions:

```python
import pyarrow.parquet as pq
import numpy as np
from ase import Atoms

table = pq.read_table("val_id_shard.parquet")
df = table.to_pandas()

for idx, row in df.iterrows():
    # CELL: object array wrapping a single 3x3 ndarray
    cell_raw = row["cell"]                     # ndarray(1,) dtype=object
    cell = cell_raw[0]                         # ndarray(3,3) — the actual cell matrix

    # POSITIONS: object array of per-atom coordinate arrays
    pos_raw = row["pos"]                       # ndarray(N,) dtype=object
    pos = np.stack(pos_raw).astype(float)      # ndarray(N,3)

    # ATOMIC NUMBERS
    nums = np.array(row["atomic_numbers"]).astype(int)  # ndarray(N,)

    atoms = Atoms(positions=pos, numbers=nums, cell=cell, pbc=True)
```

A **pre-parsed cache** (1000 structures as ASE Atoms objects) exists at `data/oc22_val_cache.pkl` with shape `{'atoms': list[Atoms], 'y': list[float], 'sid': list[int]}`.

⚠️ **Tags are STRIPPED from the cached Atoms objects.** The cache was built by `cache_val_data.py` which does not set `atoms.set_tags()` from the parquet's `tags` column. If you need tags for structure classification (bare slab vs slab+adsorbate), rebuild from the raw parquet:

```python
import pyarrow.parquet as pq
from ase import Atoms
import numpy as np

df = pq.read_table("val_id_shard.parquet").to_pandas()
for i, row in df.iterrows():
    cell = row["cell"][0]                # ndarray(3,3)
    pos = np.stack(row["pos"]).astype(float)  # ndarray(N,3)
    nums = np.array(row["atomic_numbers"]).astype(int)
    tags = row["tags"]
    atoms = Atoms(positions=pos, numbers=nums, cell=cell, pbc=True)
    atoms.set_tags(tags)
```

**OC22 tag convention:** tag=0 (bulk/fixed), tag=1 (surface/relaxed), tag=2 (adsorbate). In a 200-structure subset from val_id: ~45 bare slabs (tags ∈ {0,1}), ~155 slab+adsorbate (tags ∈ {0,1,2}).

## Running inference (fairchem + OCPCalculator)

Models available via fairchem-core v1.10.0:

| Model | Checkpoint size | OC22 val_id MAE (direct) | Notes |
|-------|----------------|--------------------------|-------|
| SchNet | 14MB | 3.424 eV | Cheapest, ~300ms/structure on CPU |
| DimeNet++ | 33MB | 2.739 eV | Medium |
| PaiNN | 80MB | 2.700 eV | Medium |
| GemNet-dT | 14MB | 2.380 eV | Better but same training data |

All from fairchem `OCPCalculator(model_name="SchNet-IS2RE-OC20-All", cpu=True, local_cache=path, seed=42)`.

⚠️ **Fairchem checkpoints must be on disk** — the `local_cache` parameter downloads on first load. Checkpoints exist at `data/checkpoints/schnet_all.pt` etc. if previously downloaded.

## CHGNet setup

```bash
pip install chgnet
```

This installs the CHGNet package and its ASE calculator. CHGNet (Crystal Hamiltonian Graph Neural Network) is a universal MLIP trained on Materials Project trajectories, similar to MACE-MP-0 but with a different architecture (crystal-symmetry-aware vs equivariant).

**Performance on 114-atom OC22 oxide slabs (Apple M-series CPU):**
- ~1-2s per structure (CPU, auto-detect device)
- Uses torch backend — may use GPU if available

**As trust-detection signal:** s1 = |MACE_ads - CHGNet_ads|. Two different learned neural potentials trained on overlapping but not identical MP datasets, with different architectures → different OOD failure patterns.

### CHGNet ASE calculator

```python
from chgnet.model import CHGNetCalculator
from ase import Atoms

# Initialize
calc = CHGNetCalculator(device='cpu')  # or 'cuda' if GPU available

# Use as standard ASE calculator
atoms = Atoms(...)
atoms.calc = calc
energy = atoms.get_potential_energy()
```

**Pitfall:** CHGNet may fail on structures with elements not in its training set. Test on one structure first. On OC22 val_id with 57 elements, it had no element compatibility issues.

## MACE ensemble uncertainty (strongest incumbent)

When a trust-detection kill test compares cross-mechanism disagreement against single-model uncertainty, the strongest incumbent is a multi-model MACE ensemble using different pre-trained variants:

| Variant | Architecture | Size | Speed (114-atom slab, CPU) |
|---------|-------------|------|--------------------------|
| L0_energy | 1-layer, energy-only | 33 MB | ~0.14s/struct |
| MPtrj (L1) | 1-layer, forces+energies | 134 MB | ~0.6s/struct |
| L2 | 2-layer, forces+energies | 64 MB | ~0.9s/struct |

All downloadable from `https://github.com/ACEsuit/mace-foundations/releases/tag/mace_mp_0`

```python
from mace.calculators import MACECalculator
models = {'MPtrj': 'MACE_MPtrj_2022.9.model',
          'L0_energy': '2023-12-10-mace-128-L0_energy_epoch-249.model',
          'L2': '2024-01-07-mace-128-L2_epoch-199.model'}
predictions = {}
for name, path in models.items():
    calc = MACECalculator(model_paths=path, device='cpu', default_dtype='float32')
    predictions[name] = [float(atoms.copy().calc(calc).get_potential_energy()) for atoms in structures]
ensemble_std = np.std([predictions[k] for k in models], axis=0)
```

**Warning:** These are NOT true random seeds — different architectures trained on potentially different MP subsets. The ensemble std is a weaker bar than a proper seed-ensemble (which requires days of GPU training). State this explicitly in any kill-test header.

## Structural-family OOD holdout

When testing OOD failure detection, define the T2 holdout by a held-out structural family independent of train-distance (to avoid circularity with signal s3).

For slab+adsorbate systems (OC22): families are defined by adsorbate composition (tag-2 elements). Suitable holdouts from system 0 (1000 structures):

| Adsorbate | Count | Notes |
|-----------|-------|-------|
| CO (C,O) | 84-97 | **Best — chemically distinct binding** |
| H2O (H,H,O) | 114 | Good |
| HO2 (H,O,O) | 65 | Good |
| OH (H,O) | 39 | OK |
| C (atomic) | 35 | OK |
| H (atomic) | 34 | OK |

**Rule:** Hold out exactly one family, pre-registered with structural-definition justification before any OOD errors are computed. CO is preferred because C-metal back-donation is a fundamentally different binding mechanism than O/OH/H adsorption.

## GFN0-xTB setup on macOS ARM (no conda)

```bash
# Install micromamba (one-shot binary, no conda needed)
curl -Ls "https://github.com/mamba-org/micromamba-releases/releases/latest/download/micromamba-osx-arm64" -o /tmp/micromamba
chmod +x /tmp/micromamba

# Create xtb environment
/tmp/micromamba create -y -p /tmp/xtb_env xtb -c conda-forge

# Test: param file must be in CWD (XTBHOME env var doesn't pass through micromamba)
cp /tmp/xtb_env/share/xtb/param_gfn0-xtb.txt .
/tmp/micromamba run -p /tmp/xtb_env --cwd . xtb --gfn 0 --sp input.xyz
```

**Key pitfalls:**
- XTBHOME env var is NOT propagated through micromamba's process isolation. The `--env` / `-e` flag and `export XTBHOME=` inside `bash -c` both fail to reach the xtb binary. **Workaround:** copy `param_gfn0-xtb.txt` to the CWD before running xtb; xtb searches CWD as a fallback.
- The `--xtbhome` flag also doesn't work reliably through micromamba.
- xtb's RPATH is set correctly — all dylibs (libxtb.6.dylib, libmctc-lib.0.dylib, libgfortran.5.dylib, libomp.dylib) are at `/tmp/xtb_env/lib/` and found via `@loader_path/../lib/`.
- xtb v6.7.1 works for all OC22 elements (tested 300 structures, 100% convergence, 0.2s average per 114-atom slab).

### xtb Python subprocess template

```python
import subprocess, re

xtb_cmd = ["/tmp/micromamba", "run", "-p", "/tmp/xtb_env", "--cwd", work_dir,
           "xtb", "--gfn", "0", "--sp", xyz_path]

result = subprocess.run(xtb_cmd, capture_output=True, text=True, timeout=300)

if result.returncode == 0:
    for line in result.stdout.split('\n'):
        if 'TOTAL ENERGY' in line:
            m = re.search(r'(-?\d+\.\d+)\s*Eh', line)
            if m:
                energy_eh = float(m.group(1))
                energy_ev = energy_eh * 27.211386  # Hartree to eV
```

## Eff_rank computation

```python
import numpy as np
import pandas as pd

# error matrix: each column = proxy_error = proxy_prediction - dft_truth
err = pd.DataFrame({
    "proxy_lj": lj_preds - targets,
    "proxy_schnet": schnet_preds - targets,
})
C = err.corr().values                            # (N_proxies, N_proxies)
ev = np.linalg.eigvalsh(C)
ev = ev[ev > 1e-12]
eff_rank = float((ev.sum()**2) / (ev**2).sum())  # participation ratio
```

### Interpretation with N proxies

| N | Max eff_rank | eff_rank ≈ N means | eff_rank ≈ 1 means |
|---|-------------|--------------------|--------------------|
| 2 | 2.0 | Errors are nearly decorrelated → proxies count as independent witnesses | Errors highly correlated → rank-one collapse |
| 3 | 3.0 | Three independent error signals | All three share the same failure mode |
| 4+ | N | Strong proxy diversity | Redundant proxies |

**IMPORTANT CORRECTION — eff_rank treats +r and -r identically, but they are NOT the same for ensemble purposes:**

- **Positively correlated errors (+r ≈ 1):** both proxies over/under-shoot in the same direction. Redundant — combining offers minimal improvement (rank-one collapse).
- **Anti-correlated errors (−r ≈ −0.8):** errors cancel when combined. This is the **ideal ensemble configuration**, not a kill. eff_rank near 1.25 is misleading here: it flags anti-correlation as "correlated" when it's actually complementarity.

**Testing anti-correlated pairs:** When eff_rank < 1.5 and the off-diagonal is negative, do NOT kill immediately. Instead, run the **variance-minimizing linear combination test** (see section above). Only kill if the combined prediction fails to beat the best single proxy out-of-sample.

**Pre-registered threshold (symmetric case):** eff_rank ≥ 1.5 → PASS (proxies are sufficiently decorrelated to proceed to Gate 2). **Exception for anti-correlated pairs (r < 0):** use the combination test instead.

## Gate 1 decision tree (corrected)

```
                    ┌──────────────────────┐
                    │ Have ≥2 informative   │
                    │ proxies (|corr|≥0.2)? │
                    └──────┬───────────────┘
                           │
              ┌────────────┴────────────┐
              │ YES                     │ NO
              │                         │
    ┌─────────▼─────────┐     ┌─────────▼──────────┐
    │ Compute eff_rank   │     │ Free path dead.    │
    │ of error-corr mat  │     │ Need another proxy │
    └─────────┬─────────┘     │ source (xTB/MP).   │
              │               └────────────────────┘
    ┌─────────┴─────────┐
    │ eff_rank ≥ 1.5?   │
    └──────┬────────────┘
           │
   ┌───────┴───────────────┐
   │ YES                   │ NO — check sign
   │                       │
   │ PASS                  ▼
   │ (decorrelated)   ┌──────────────┐
   │                  │ r < 0?       │
   │                  │ (anti-corr?) │
   │                  └──┬───────────┘
   │             ┌───────┴───────┐
   │             │ YES           │ NO (r > 0)
   │             │               │
   │     ┌───────▼───────┐   ┌───▼────────┐
   │     │ Run var-min   │   │ RANK_ONE   │
   │     │ combination   │   │ KILL       │
   │     │ test          │   └────────────┘
   │     └───────┬───────┘
   │             │
   │     ┌───────▼───────────┐
   │     │ Combo beats best  │
   │     │ single proxy?     │
   │     └──┬────────────────┘
   │   ┌────┴────┐
   │   │ YES     │ NO
   │   │         │
   │   │ PASS    │ KILL
   │   │(denoise)│ (real)
   │   └─────────┘
```

### Total-energy vs adsorption-energy artifact (updated 2026-06-29, 691 properly-matched pairs)

The total-energy error correlations between proxies can differ DRAMATICALLY from the adsorption-energy error correlations. This is because total energies are dominated by per-element baselines (sum of per-atom reference energies), which can manufacture or suppress correlations that don't exist in the chemically meaningful quantity.

**Measured on 691 properly-matched slab+adsorbate pairs (52 slab-size categories) from OC22 val_id:**

| Error corr | Total energy | Adsorption energy (proper pair-matched) | Change |
|------------|-------------|-----------------------------------------|--------|
| SchNet x xTB | -0.7584 | -0.0954 | **Anti-correlation was a baseline artifact** |
| MACE x SchNet | +0.0719 | +0.1505 | Modest positive (genuine decorrelation) |
| MACE x xTB | +0.0456 | +0.0452 | **Unchanged — genuine near-zero decorrelation** |

**eff_rank on total energy: 2.16** (below Gate 2 threshold of 2.3)  
**eff_rank on adsorption energy: 2.93** (above Gate 2 threshold)

**Implications:**
- The SchNet-xTB anti-correlation (-0.76 on total) was a **total-energy baseline artifact driven by per-element reference energies**, NOT a genuine error-structure property. On properly-matched adsorption energy, SchNet-xTB errors are nearly zero (-0.10). The entire "anti-correlated ensemble" narrative was an artifact of measuring the wrong quantity.
- MACE-xTB decorrelation (0.05 on both) is genuine and survives across energy quantities — two entirely different physical methods producing independent errors.
- MACE-SchNet decorrelation (0.07 -> 0.15) is genuine but modest.
- If Gate 2 asks about adsorption energy specifically, the 3-proxy ensemble passes (eff_rank 2.93 > 2.3). If the target is total energy (OC22 task definition), the Gate verdict remains HOLD (eff_rank 2.16 < 2.3).

**Always report both total-energy and decomposition-level correlations when the data supports it. Use proper bond-line matching for E_ads computation (mean of matching bare-slab references by non-adsorbate atom count) — the single-minimum-bare-slab reference introduces large systematic errors.**

### Pre-registered mechanism prediction pattern (3+ proxy ensembles)

When expanding from a 2-proxy ensemble to 3+ proxies, the user requires a **pre-registered prediction** committed before any computation. This is a meta-process validation: does mechanism reasoning predict decorrelation correctly?

### Bottleneck-coordinate analysis (the framework for 3rd proxy prediction)

Before predicting decorrelation, analyze each proxy along THREE orthogonal axes:

| Axis | Strength | Examples |
|------|----------|----------|
| **Theory** | Strongest | learned-neural vs semi-empirical-QM vs DFT vs classical-FF |
| **Representation** | Medium | graph-equivariant vs continuous-filter vs pairwise-potential vs tight-binding |
| **Data** | Weakest | OC20-trained vs Materials-Project-trained vs solid-state vs molecular |

**Axis ranking: theory > representation > data.** A proxy that varies the STRONGEST axis (e.g., adding QM to a neural-only set) is PREDICTED to produce strongly decorrelated errors. A proxy that varies only the WEAKEST axis (e.g., MP-trained GNN to an OC20-trained GNN — same theory, same general representation class) is PREDICTED to produce partially collinear errors.

**How to apply:**
1. For each existing proxy, state (theory, representation, data) triples
2. For the NEW proxy, state its triple
3. Compare axis-by-axis: which axes are shared vs different?
4. Predict pairwise error-correlation sign and approximate magnitude based on which axes differ
5. The single-axis-difference case (only data differs) gives a CLEAR opposite-sign prediction from the multi-axis-difference case (theory differs)

### Pattern

1. **Mechanism analysis:** For each existing proxy, state the fundamental error source (data bias, QM approximation, functional choice, etc.) — or more precisely, the (theory, representation, data) bottleneck-coordinate triple
2. **Mechanism independence prediction:** For the NEW proxy, predict whether its errors will be decorrelated from each existing proxy based on mechanism COMPARISON (bottleneck-axis overlap), not prior measurement
3. **Commit an eff_rank band** (e.g. "predict 2.1-2.5") for the 3x3 error-correlation matrix, with target midpoint
4. **State the KNOWN RISK** — the specific mechanism assumption that could be wrong (e.g. "cheap-DFT shares DFT-class error with reference → partial collinearity with truth itself", or "MACE shares theory+representation with SchNet → data-only variation is weak")
5. **State the FALSIFICATION CONDITION** — the specific measurement that would prove the theory wrong (e.g. "if corr(MACE_err, SchNet_err) < 0.2, data-variation alone manufactures independence and the axis hierarchy is falsified")
6. **Run measurement** — convergence rate, pairwise error correlations, 3x3 eff_rank
7. **Two verdicts:**
   - Meta-process verdict: did measured eff_rank land in the predicted band? If YES → mechanism independence is PREDICTIVE (validated a-priori diagnostic). If NO → mechanism-reasoning was post-hoc (the identified risk materialized).

---

## Proper E_ads computation for slab+adsorbate systems

When working with OC22 (or any slab+adsorbate) structures, the decision-relevant quantity is **adsorption energy**, not total energy. Total-energy correlations are contaminated by shared per-element baselines — two models can show r=0.999 simply by predicting the right number of atoms, masking chemical accuracy.

### OC22-specific structure classification

The OC22 parquet has a `tags` field for each atom:
- tag=0 → bulk/fixed (subsurface atoms)
- tag=1 → surface (relaxed surface atoms)
- tag=2 → adsorbate (added molecule/radical)

The `id` field has format `{system}_{fragment}` (e.g. `0_0`, `0_1` for system 0, fragments 0 and 1). All fragments sharing the same system prefix are from the same base slab with different adsorbate configurations.

No gas-phase reference structures exist in the OC22 val_id split. E_ads = E_slab+ads − E_clean_slab (no gas-phase subtraction needed within this split).

### Bond-line matching by non-adsorbate atom count

```
For each structure in the dataset:
     1. Read tags from raw parquet (NOT from cached ASE Atoms objects — tags are stripped)
     2. Classify: bare_slab if 2 ∉ tags, else slab+adsorbate
     3. For slab+adsorbate:
        n_ads = count(tag == 2)
        n_non_ads = natoms - n_ads
     4. For bare slab:
        n_non_ads = natoms  (all atoms are slab)

   Build lookup: bare_slabs_by_non_ads_count[n_non_ads] = [indices...]

   For each slab+adsorbate:
     match = bare_slabs_by_non_ads_count[n_non_ads]
     if match is not empty and has ≥1 valid entry:
       bare_ref_y = mean([dft_total[b] for b in match])
       bare_ref_mace = mean([mace_pred[b] for b in match])
       bare_ref_xtb = mean([xtb_pred[b] for b in match])
       bare_ref_schnet = mean([schnet_pred[b] for b in match])
       E_ads_dft = total_y[sa] - bare_ref_y
       E_ads_mace = mace_pred[sa] - bare_ref_mace
       etc.
   ```

   **DO NOT use a single global minimum-energy bare slab as reference for all slab+ads structures** — slab+ads structures may have different numbers of non-adsorbate atoms (different slab configurations), and using the wrong bare slab introduces large systematic errors. The resulting pseudo-E_ads range will be hundreds of eV rather than a chemically plausible ±5 eV. The bond-line matching by non-adsorbate atom count is mandatory.

   ### Expected E_ads range on OC22

   With proper pairwise matching on OC22 val_id system 0 (1000 structures, 52 slab-size categories):
   - E_ads range: approximately −10 to +10 eV (chemically sensible)
   - ~691 matchable pairs out of ~792 slab+ads structures
   - ~101 slab+ads structures cannot be matched (no bare slab of that size in the available cache)
   - Report N of valid pairs AND number of slab-size categories covered

   ### Known results (from 2026-06-29 session, updated with proper pair-matching on 691 structures)

   | Metric | Total energy | Adsorption energy (properly matched, 691 pairs, 52 slab-size cats) |
   |--------|-------------|---------------------------------------------------------------------|
   | corr(MACE, DFT) | 0.9999 | 0.9948 (genuine — validated via leakage check and E_ads test) |
   | corr(SchNet, DFT) | 0.2398 | 0.7134 (**improved** — was suppressed by shared baseline) |
   | corr(xTB, DFT) | 0.7588 | 0.1764 (CRASHED — near-useless on E_ads) |
   | corr(MACE_err, SchNet_err) | 0.0719 | **0.1505** (modestly decorrelated) |
   | corr(MACE_err, xTB_err) | 0.0456 | **0.0452** (genuinely decorrelated — survives) |
   | corr(SchNet_err, xTB_err) | -0.7584 | **-0.0954** (CRASHED — WAS a total-energy artifact) |
   | 3-proxy eff_rank | 2.161 | **2.934** (ABOVE Gate 2 threshold of 2.3) |
   | MACE RMSR | 4.07 eV | 29.86 eV |
   | SchNet RMSR | 9.36 eV | 114.65 eV |
   | xTB RMSR | 6.06 eV | 1166.54 eV |
   | Best single proxy | MACE | MACE |
   | Ensemble gain | 76% reduction (2-proxy S+x) | NONE — MACE dominates all combos (30x better) |

   **Key finding:** The SchNet-xTB anti-correlation (-0.76 on total energy) was a **total-energy baseline artifact driven by per-element reference energies**. On properly-matched adsorption energy, SchNet-xTB errors are nearly uncorrelated (-0.10). The MACE-SchNet decorrelation (0.07 on total, 0.15 on adsorption) is genuine but modest. MACE-xTB errors remain effectively zero-correlated (0.05) across both energy quantities — two entirely different physical methods (learned neural vs semi-empirical QM) producing completely independent errors.

   **SchNet's E_ads correlation improved dramatically (0.24 -> 0.71)** because the adsorption energy removes the per-atom baseline that was dominating SchNet's total-energy error signal. SchNet is actually quite good at adsorption chemistry on OC22 — its total-energy performance was misleadingly poor.

   **MACE dominates on E_ads** because its error variance (16 eV2) is 2-3 orders of magnitude smaller than SchNet (13,221 eV2) or xTB (1,273,502 eV2). The variance-minimizing weighted combination collapses to w≈1 on MACE, meaning the ensemble adds nothing beyond MACE alone. This is not a failure of the ensemble concept — it's a discovery that MACE is near-definitive for this particular system. The ensemble is only helpful when proxies have comparable accuracy but decorrelated errors.

   **xTB on E_ads:** corr = 0.18 (borderline below 0.2 floor). xTB does not provide useful adsorption-energy information on its own. Its errors are decorrelated from MACE (0.05) but its variance is 80,000x MACE's, making it useless for weighted combination. The earlier finding that xTB had corr = -0.16 on 83 pairs was a small-sample artifact — with 691 pairs the stable number is +0.18.

   ## Proxy substitution protocol (when the committed proxy is infeasible)

When the committed proxy becomes computationally infeasible (e.g., GPAW on laptop — >5 min/structure for 114-atom slabs), the substitution follows strict provenance rules to avoid goalpost-laundering:

1. **Retire the original prediction as UNTESTED** — not confirmed, not falsified, just infeasible. Log the specific blocker (which tool, what timed out, at what size).
2. **Do NOT inherit the original prediction** for the new proxy — the new proxy is on a different bottleneck-coordinate position and gets a NEW, independently-committed prediction.
3. **The new prediction should have the OPPOSITE predicted sign** from the original when the new proxy lands on the opposite side of the bottleneck-coordinate analysis (deliberate — proves the framework isn't post-hoc cherry-picking).
4. **Log the substitution provenance** in the report header so the substitution is fully transparent.

### Reporting output contract (6 computation items + 2 verdicts)

A complete NODE-C style report must contain, in order:

1. Committed predictions (in a report header, written before computation)
2. Convergence rate for the new proxy
3. corr(new_proxy, dft_truth)  — informativeness (report raw vs the arbitrary 0.2 floor)
4. Full 3x3 error-correlation matrix [proxy1, proxy2, new_proxy]
5. Individual pairwise error correlations: corr(new_err, existing_err_1) and corr(new_err, existing_err_2)
6. eff_rank of the 3x3 matrix

Then two verdicts:
- **Theory verdict** (meta-process): confirmed / falsified / partial, with the specific measurement that determined it
- **Gate verdict** (ensemble): pass / hold / kill, with eff_rank relative to ~2.3 threshold

### MACE-MP-0 as a third proxy for OC22

MACE-MP-0 (Materials Project universal MLIP) is the most practical 3rd proxy for OC22 kill tests on CPU-only hardware:

**Setup:**
```bash
pip install mace-torch
# Download model (133 MB)
wget https://github.com/ACEsuit/mace-foundations/releases/download/mace_mp_0/MACE_MPtrj_2022.9.model
```

**Performance on 114-atom OC22 oxide slabs (Apple M-series CPU):**
- ~0.8s per structure (CPU, float32)
- Good agreement on bare structures: first test showed -728.67 eV (MACE) vs -725.38 eV (DFT) — ~3.3 eV difference on 114 atoms
- May be slow on large structures (>300 atoms) — test on one structure first

**Bottleneck-coordinate analysis (pre-registered prediction from 2026-06-29 session):**
- SchNet  = (theory: LEARNED-NEURAL, representation: GRAPH, data: OC20)
- xTB     = (theory: SEMI-EMPIRICAL-QM, representation: TIGHT-BINDING, data: n/a)
- MACE-MP-0 = (theory: LEARNED-NEURAL, representation: GRAPH/equivariant, data: MATERIALS-PROJECT)

MACE shares theory+representation with SchNet, varying only the WEAKEST axis (data). Bottleneck theory predicts: corr(MACE_err, SchNet_err) SUBSTANTIALLY POSITIVE (+0.4 to +0.7), 3-proxy eff_rank < 2.0. See session `electrocat_handoff` for the actual measured values.

**Known risk for MACE-MP-0 as OC22 proxy:** Since MACE is trained on bulk Materials Project structures (not surfaces/slabs), its errors on 2D slab configurations may have a systematic bias (missing surface relaxation physics) that could couple or anti-couple with SchNet's OC20-surface bias in unpredictable ways.

See SKILL.md "Pre-registered mechanism prediction" section for the workflow and step-by-step requirements.

## Trust-detection kill test (cross-mechanism disagreement as OOD failure signal)

When the thesis claims that cross-mechanism disagreement detects a primary model's adsorption-energy failures better than the model's own (ensemble) uncertainty, use this staged kill test.

### Stage 0 — Setup (pre-register before scoring)

**A. Incumbent:** MACE 3-model ensemble variance (MPtrj, L0_energy, L2). Load via pre-trained checkpoints from ACEsuit/mace-foundations. No retraining needed (~5 min download, ~15 min compute on 800 structures). If pre-trained variants not loadable, fall back to kNN-distance in MACE latent space (weaker bar — state explicitly).

**B. OOD holdout (T2):** Define by held-out structural family independent of train-distance. For slab+adsorbate systems, families are defined by adsorbate composition (tag-2 elements). Pre-register the family before computing OOD errors. Record N(T1) and N(T2).

**C. Failure threshold:** 80th percentile of |MACE_ads − DFT_ads| on IN-DISTRIBUTION (T1). Compute BEFORE scoring T2. On 607 non-CO structures from OC22 val_id: threshold ≈ 5.02 eV.

**D. Gate condition:** mean(AUC(s1) − AUC(incumbent)) > 0 AND t > 1.0 across 5-fold stratified CV on T2, where s1 = |MACE_ads − CHGNet_ads|.

### Stage 1 — Cheap gate

Install and run CHGNet on T1+T2+bare structures. Compute E_ads with proper pair-matching. Signal s1 = |MACE_ads − CHGNet_ads|. Incumbent = MACE 3-model ensemble std. 5-fold stratified CV on T2, compare AUC and P@20%.

**Stage 1 sample-size arithmetic — pre-requisite check before scoring:** Before running the gate, verify that the OOD (T2) set has enough failures for 5-fold stratified CV. A minimum of ~5 failures per fold (i.e., 25+ total failures) is needed for stable AUC estimation. With the typical ~17% failure rate on OC22 (80th %ile threshold), this means T2 should have **at least ~150 structures** (25/0.17). Target 250-400 OOD structures for comfortable power (~8-14 failures/fold). If T2 cannot reach these counts on available data, the gate is UNDERPOWERED by design and should be stated as such, not scored as a clean kill.

**OOD expansion rules (one re-run protocol):** When the initial Stage 1 gate FAILS with t < 1.0 but the point estimate is directionally positive (delta > 0), the pre-registered protocol allows exactly ONE expansion re-run. Two expansion routes exist — choose one and state it before re-running:

   - **Route (a) — enlarge the SAME held-out family:** Pull more structures of the exact same structural family (e.g., CO adsorbate) from the full dataset (e.g., the full OC22 parquet instead of just the cached subset). This keeps the OOD DEFINITION unchanged — only the sample size increases. The ID set (T1) also stays the same. This is the correct route if the goal is to stabilize an underpowered statistic on the same OOD concept.

   - **Route (b) — hold out additional structural families:** Add 2-3 more families to the OOD set (e.g., O₂ and H₂O alongside CO). This CHANGES the OOD definition — the test is now about broader OOD coverage, not the same boundary. It also reduces the ID set (T1 shrinks by the removed families), which can shift the failure threshold if recomputed. Use this route only if the thesis question is about "general OOD" rather than "this specific OOD boundary."

   **Critical invariant:** The failure threshold is FROZEN at the original value across the re-run. The 5-fold stratified CV and the gate condition (mean delta > 0 AND t > 1.0) are frozen. This is the ONE re-run, not a tuning loop.

   **Three possible re-run outcomes:**
   1. **PASS** (delta > 0, t > 1.0) ↔ original was underpowered; cross-mechanism signal is real at the OOD frontier. Proceed to Stage 2.
   2. **FAIL — advantage SHRINKING toward 0** (delta near 0 or negative) ↔ the original signal was noise; clean kill stands.
   3. **FAIL — advantage still ~+0.15 but t still < 1.0** even at the enlarged sample ↔ the effect may be real but this domain can't power the test. Verdict: INCONCLUSIVE, not a kill. Do not run a third time.

   **Also report the signal ranking** (independent of t-stat): on the expanded set, is s1 still the best single signal? Does the incumbent remain near-worst? If the ranking holds with more data, it corroborates the thesis even if the t-stat doesn't clear the bar.

**Known result (OC22 val_id, T2=CO, 84 structures, original run):** GATE FAIL. s1 beats incumbent directionally (AUC 0.786 vs 0.629, delta +0.157) but t = 0.865 < 1.0. High fold variance from small T2 (84 structs, 14 failures, ~2.8/fold — insufficient for stable AUC). Individual signal AUCs: s1=0.786, s2(|MACE-xTB|)=0.715, s3(|MACE-SchNet|)=0.635, incumbent=0.629.

**Expanded re-run (Route a, 280 CO structures from full parquet, executed 2026-06-29):** GATE FAIL — advantage SHRINKING TOWARD ZERO. T2 = 280 CO structures (83 original + 197 new from full OC22 parquet). 70 failures (~14/fold at 25% failure rate — stable CV). Results:

| Fold | AUC(s1) | AUC(inc) | P@20(s1) | P@20(inc) |
|------|---------|----------|----------|-----------|
| 1 | 0.753 | 0.662 | 0.636 | 0.364 |
| 2 | 0.441 | 0.391 | 0.182 | 0.182 |
| 3 | 0.629 | 0.507 | 0.545 | 0.182 |
| 4 | 0.441 | 0.675 | 0.273 | 0.455 |
| 5 | 0.556 | 0.427 | 0.364 | 0.273 |
| Mean | 0.564 | 0.532 | 0.400 | 0.291 |

Benefit: s1 lost advantage from +0.157 (84 structs) to +0.032 (280 structs). The original was small-sample noise. Signal ranking held (s1 best, incumbent worst) but both AUCs < 0.60 — practically useless regardless of ranking. Verdict: KILL — noise confirmed, relocation thesis dead.

Empirical validation of sample-size pre-check: 84 structs (14 failures, ~3/fold) → undependable; 280 structs (70 failures, ~14/fold) → resolved. The ~25-failure threshold for stable 5-fold CV is validated.

### Stage 2 — Full ensemble (only if Stage 1 passes)

Add s2 (|MACE-xTB|), s3 (train-distance). Leakage guard: report T2 with and without s3 separately. Logistic regression ensemble. Win bar: mean(AUC_trust − AUC_inc) > 0 AND t > 1.0 AND max-fold-share < 0.5. OOD win without s3 is the target result (the primitive has a real job at the frontier).

## 3-proxy ensemble: dimension requirements for Gate 2

Gate 2 (RMT vs raw-disagreement) requires enough dimensional structure in the error matrix to be meaningful — 2 proxies provide no structure. The minimum for Gate 2 is eff_rank meaningfully > 2 on a 3x3 matrix.

### 3-proxy eff_rank interpretation

| eff_rank | Meaning |\n|----------|---------|\n| ~1.0–1.5 | One shared failure mode dominates; other proxies add no independent dimension |\n| ~1.5–2.2 | Two effective dimensions; third proxy partially collinear with one existing |\n| ~2.3–3.0 | Three substantially independent error dimensions → Gate 2 is dimensionally ready |\n\n### Typical expansion paths (from 2-proxy base)

After establishing a 2-proxy ensemble that passes (SchNet + xTB on OC22: anti-correlated, 4× RMSE improvement):

1. **Cheap GGA-DFT (PBE at loose settings):** Adds DFT-class error structure, different from both data-driven (SchNet) and tight-binding (xTB) on all THREE bottleneck axes. Predicts STRONG decorrelation across all pairs — candidate for eff_rank 2.1-2.5. **Known risk:** shares DFT-family error with the OC22 REFERENCE DFT itself — errors may be partially collinear with truth, not with the other proxies, which paradoxically reduces eff_rank because one dimension goes to redundancy-with-truth rather than decorrelation-with-another-proxy. **Implementation constraint:** GPAW PW/FD is too slow for 100+ atom oxide slabs on single-core CPU (>300s/structure); LCAO mode needs proper basis file installation. Not feasible on laptop without GPU — see proxy substitution protocol below for when this proxy is retired as infeasible.

2. **MP-trained GNN (MACE-MP-0, CHGNet, etc.):** GNN architecture trained on Materials Project (bulk, not catalysis). **Bottleneck analysis:** shares theory+representation with SchNet, varies only the WEAKEST axis (data). Predicts PARTIAL collinearity with SchNet errors (r +0.4 to +0.7), eff_rank < 2.0. **Not** strongly decorrelated — data-only variation is the weakest bottleneck. **Known risk:** MACE's bulk training vs SchNet's surface training could produce different systematic biases that partially counteract the shared-architecture prediction. **Implementation path:** pip install mace-torch + download model from ACEsuit/mace-foundations releases.

3. **Another semi-empirical method (DFTB+, MOPAC/PM7):** Different QM approximation from GFN0-xTB. **Known risk:** may share tight-binding-class errors with xTB. **Likely outcome:** informative but partially redundant with xTB dimension.\n\n## Typical results (from 2026-06-29 run on OC22 val_id structures)
| Proxy | Corr with DFT | Paired with | Error-corr | eff_rank | Ensemble RMSE vs best single |
|-------|---------------|-------------|-----------|----------|------------------------------|
| LJ (classical) | -0.07 | SchNet | 0.072 | 1.99 | Not tested (LJ is noise) |
| SchNet + DimeNet++ | +0.30 / +0.19 | same-data GNNs | 0.996 | **1.004** | RANK_ONE — as expected |
| GFN0-xTB + SchNet | +0.77 / +0.30 | different physics | **-0.78** | **1.25** | **−76.6%** (PASS on combo test) |

**3-proxy attempts (validated results from 2026-06-29 session):**
- **Cheap GGA-DFT (pre-registered prediction: eff_rank 2.1–2.5):** Not executed — GPAW too slow on CPU for 114-atom oxide slabs (timed out at 300-600s per structure in both PW and FD modes at any practical setting). **Retired as UNTESTED.** Design and prediction are documented as a template for when GPU resources are available.
- **MACE-MP-0 (substitute third proxy, opposite-signed prediction):** Pre-registered prediction: corr(MACE_err, SchNet_err) +0.4 to +0.7, 3-proxy eff_rank < 2.0. Executed on 200 OC22 val_id structures. **Results (validated):**
  - corr(MACE_total, DFT_total) = 0.9999 (suspiciously perfect — triggered validation protocol)
  - **Validated on adsorption energy:** corr(MACE_ads, DFT_ads) = 0.9990 — GENUINE (not a baseline artifact)
  - Leakage check: LOW risk (surface slabs ≠ MP bulk crystals; bare/slab+ads accuracy ratio 0.87)
  - corr(MACE_err, SchNet_err)_total = 0.0719 → 0.2304 on adsorption (modest decorrelation)
  - corr(MACE_err, xTB_err)_total = 0.0456 → 0.2360 on adsorption
  - eff_rank (total energy) = 2.16, eff_rank (adsorption) = 2.66
  - **Theory verdict: FALSIFIED** — data-variation alone manufactured near-independence; axis hierarchy (theory>representation>data) was wrong
  - **Gate verdict: HOLD** (eff_rank 2.16 < 2.3 for total-energy task)

### OC22-specific constraints (from 2026-06-29 empirical tests)
- **100% xtb convergence** on 300 val_id structures across all tested OC22 elements (O, Rb, Al, Ag, Co, Sc, Ba, Si, Cr, Cu, Ti, Cs, Rh, Mo, Ga, Bi, Sr, Nb, Sb, Mg, plus 40+ others). Average 0.2s per 114-atom slab on Apple M-series CPU.
- **xtb is informative:** corr(xtb_energy, DFT_truth) = +0.774 on 300 OC22 structures.
- **Same-data GNNs produce rank-one error:** SchNet × DimeNet++ error-correlation = 0.996. Architecture difference without training-data difference is useless.
- **GPAW on OC22 is computationally prohibitive on laptop CPU.** PW mode with ecut=200eV timed out at 600s. FD mode with h=0.30 timed out at 300s. LCAO mode needs complete PAW basis file installation. A single OC22 slab (114 atoms) takes >5 minutes even with the most aggressive settings. 200-structure batch would take ~16+ hours.

### CHGNet MPS/CPU performance trajectory

CHGNet uses the torch backend and may select `mps` (Apple Metal Performance Shaders) when available. **Performance degrades significantly with runtime** — the slowdown is not linear and does NOT reflect structure size alone:

| Structures processed | Rate | Total elapsed |
|---------------------|------|---------------|
| 50 | 1.39/s | 36s |
| 100 | 1.04/s | 96s |
| 200 | 0.57/s | 349s |
| 400 | 0.39/s | 1034s |
| 700 | 0.24/s | 2884s |

The slowdown is consistent (~0.4% per additional structure processed) and independent of structure size variation. Likely causes include MPS memory fragmentation or MACE-like internal array growth. For large batches (800+ structures), expect average ~4s/structure despite starting at ~0.7s/structure. Use checkpointing (save every 50-100 structures) to avoid losing progress on timeout.

**CHGNet warning messages:** CHGNet may emit warnings like `"Structure graph_id=None has 2 isolated atom(s) with atom_graph_cutoff=6. CHGNet calculation will likely go wrong"`. These appear for structures with atoms far from periodic neighbors (large vacuum gap in slab+z direction). The calculation still completes and the energy values are usable.

### Parquet row conversion beyond the 1000-structure cache

When reading structures from the OC22 parquet BEYOND the first 1000 rows (the pre-built cache), the position and cell arrays have a different nesting structure:

```python
# For structures indices 0-999 (matches cache):
pos = np.array(row['pos'], dtype=float)   # works — direct array

# For structures indices 1000+:
pos_raw = row['pos']                       # object array of (3,) float32 arrays
pos = np.array([list(p) for p in pos_raw], dtype=float)  # must flatten per-atom arrays
```

The cell field similarly may be stored as object arrays or flattened 9-element arrays rather than (3,3) matrices. The robust conversion function:

```python
def row_to_atoms(row):
    pos_raw = row['pos']
    if isinstance(pos_raw, np.ndarray) and pos_raw.dtype == object:
        pos = np.array([list(p) for p in pos_raw], dtype=float)
    else:
        pos = np.array(pos_raw, dtype=float)
    if pos.ndim > 2:
        pos = pos.reshape(-1, 3)
    
    cell_raw = row['cell']
    if isinstance(cell_raw, np.ndarray):
        if cell_raw.dtype == object or cell_raw.ndim > 2:
            cell_raw = np.array([list(c) for c in cell_raw], dtype=float).flatten()
        else:
            cell_raw = cell_raw.flatten()
    
    if len(cell_raw) == 9:
        cell = np.array(cell_raw, dtype=float).reshape(3, 3)
    elif len(cell_raw) == 6:
        from ase.cell import Cell
        cell = Cell.new(cell_raw)
    else:
        cell = np.eye(3) * 20.0
    return Atoms(positions=pos, numbers=row['atomic_numbers'], cell=cell, pbc=[True, True, True])
```

### OOD expansion route selector

When the initial Stage 1 gate FAILS with t < 1.0 but delta > 0 (underpowered, not dead), choose BETWEEN route (a) and route (b) based on what the thesis asks:

| Condition | Recommended route | Rationale |
|-----------|-----------------|-----------|
| Thesis asks about a SPECIFIC OOD boundary (e.g., "does cross-mechanism signal detect CO-adsorbate failures?") | **(a)** Enlarge the same held-out family — pull more CO structures from the full dataset | Preserves the OOD definition; only sample size changes |
| Thesis asks about GENERAL OOD (e.g., "does cross-mechanism signal detect OOD failures broadly?") | **(b)** Hold out additional families | Tests broader OOD coverage; changes T2 definition and reduces T1 |
| Re-run shows advantage SHRINKING vs the original point estimate | **FAIL — was noise** | With more power the signal doesn't stabilize — it collapses |
| Re-run shows advantage PERSISTING at ~original magnitude but t still < 1.0 | **INCONCLUSIVE** | Effect may be real but domain can't power the test; no third re-run |

The failure threshold is FROZEN across all re-runs regardless of route chosen. The route selection must be stated BEFORE the re-run begins — post-hoc route choice is goalpost drift.

## Pitfalls

1. **EMT does NOT support OC22 elements.** EMT is hard-coded for Au, Ag, Cu, Pt, Pd, Ni, Al. OC22 is composed of oxide electrocatalysts (O + dozens of transition metals + metalloids). Every structure fails with `NotImplementedError: No EMT-potential for <element>`. Use LJ or GFN0-xTB instead.
2. **Don't batch 3 same-training-domain GNNs.** SchNet, DimeNet++, PaiNN, GemNet-dT all trained on OC20/OC22 — their errors are structurally correlated despite architectural differences. The gate only tests architecture-decorrelated proxies.
3. **eff_rank blind spot for anti-correlation.** eff_rank treats +0.78 and -0.78 identically. For anti-correlated pairs (r < 0), use the variance-minimizing combination test instead.
4. **2 proxies give eff_rank bounded to [1, 2].** A result of 1.99 looks good but the scale is very compressed. With N=2, any pair with error-correlation < 0.5 gives eff_rank > 1.6. A true test of proxy diversity requires N ≥ 3.
5. **CPU inference is slow.** SchNet takes ~300ms/structure on CPU → 1000 structures = ~5 minutes. Add a second or third model and it scales linearly.
6. **OC22 checkpoint compatibility:** The fairchem-core v1.10.0 OCPCalculator auto-downloads checkpoints by model name string. The checkpoints from the original OCP repo may not match the fairchem API. Use the model names listed in the `_MODEL_MAP` of the installed fairchem version.
7. **xtb param file must be in CWD when using micromamba.** XTBHOME env var does not propagate through micromamba's process isolation. Always copy `param_gfn0-xtb.txt` to the working directory before running xtb via micromamba.
8. **50/50 average is NOT the correct combination for heteroscedastic proxies.** When one proxy has much higher variance than the other (e.g., xtb variance 4,459,511 vs SchNet variance 45,535), the 50/50 average can be WORSE than either alone. Always solve for the variance-minimizing w.
9. **MACE default dtype warning:** MACE-MP-0 models are saved as float64, but MACECalculator defaults to float32 on CPU. The model auto-converts, which may slightly affect precision. Pass `default_dtype='float64'` if double precision is needed, but this doubles memory and may slow inference. On the test run with 114-atom slabs, float32 gave energies consistent to ~0.01 eV with the float64 model — acceptable for error-correlation purposes.
10. **MACE download URL moved:** The MACE-MP-0 model is hosted under `ACEsuit/mace-foundations` (not `mace-mp`). The URL is `https://github.com/ACEsuit/mace-foundations/releases/download/mace_mp_0/MACE_MPtrj_2022.9.model` — if that 404s, check the releases page at `/ACEsuit/mace-foundations/releases` for newer model files.
11. **Total-energy correlation does NOT imply adsorption-energy correlation.** Error correlations between proxies can change sign between total energy and adsorption energy (SchNet xTB goes from -0.76 to -0.10 on OC22), and eff_rank can differ substantially (2.16 total vs 2.93 adsorption). The two quantities have different chemical meaning — total energy includes per-atom baselines, adsorption energy isolates the surface-adsorbate interaction. Always report which energy quantity the error correlations refer to, and acknowledge when a finding is specific to one quantity. **Use proper bond-line matching for E_ads — the single-minimum-bare-slab reference method produces systematically wrong error correlations.**
