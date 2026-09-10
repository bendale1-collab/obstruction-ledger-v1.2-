# Ledger Entry — LEDGER-IGNORED (mechanism finding)
# Filed: 2026-09-10
# Type: MECHANISM-FINDING

## Finding

`.gitignore:3` ignores `ledger/` in full. Every tracked file under `ledger/`
was force-added (`git add -f`) past this rule — confirmed via
`git check-ignore -v --no-index` on all tracked ledger paths, which matches
the `ledger/` rule regardless of tracked status.

13 files existed on disk under `ledger/`, ignored and uncommitted, until
COMMIT 1 (fc08b6f, 2026-09-10) force-added them unchanged.

This is the mechanism behind SEAL-DETACHED: the 5 v1.5 files reported as
"never committed" (per `ledger/seal-detached-v1.5.md`) were never
committable by default under this `.gitignore` rule. They required an
explicit `git add -f`, same as these 13. The v1.6 recovery (commit
5f49023) fixed the missing files by reconstructing and force-adding them —
it did not fix the rule that caused the gap. The rule remained active and
produced this second, independent backlog of 13 ignored files.

## The 13 files force-added in COMMIT 1 (fc08b6f), with sizes

| Path | Size (bytes) |
|---|---|
| ledger/0000-genesis.yaml | 643 |
| ledger/anchor-gap-v1.3-2026-09-08.yaml | 1219 |
| ledger/anchor-gap-v1.3.md | 1213 |
| ledger/p1-engine-red-f4-2026-09-08.yaml | 2450 |
| ledger/p1-engine-red-f4.md | 2424 |
| ledger/runner-test | 0 |
| ledger/self-modification-p1-battery-runner-2026-09-08.yaml | 1321 |
| ledger/self-modification-p1-battery-runner.md | 1267 |
| ledger/self-modification-research-bundle-execution-2026-09-08.yaml | 2212 |
| ledger/self-modification-research-bundle-execution.md | 1781 |
| ledger/self-modification-rule-violation-2026-09-08.yaml | 2442 |
| ledger/self-modification-rule-violation.md | 2270 |
| ledger/verifier/fabricated-quote-xu-phi0.md | 1818 |

## Ledger convention finding

The `.md`/`.yaml` ledger convention is prose with commented (`#`) headers,
not structured data. Confirmed: 4 of the 5 `.yaml`-extension paths in
`MANIFEST.sha256` fail to parse as YAML at commit 7d4aad7
(`yaml.scanner.ScannerError: mapping values are not allowed here`). Only
`known-bad-specs/C1-exclusion-list.yaml` is real, parseable YAML. The
`.yaml` extension on the other 4 manifest paths (chebyshev-mapping-
rejection, conv-flag-diagnosis, fourier-diff-tolerance,
misidentification-by-acronym-collision — all `-2026-09-0X.yaml` variants)
is a naming artifact, not a format guarantee.

## Byte-identity finding

The byte-identical `.md`/`.yaml` pair
(`ledger/misidentification-by-acronym-collision.md` and
`-2026-09-08.yaml`, hash `53ca0569...`) is a defect specific to the
2026-09-09 reconstruction (commit 5f49023) — both twins were generated
from the same recovery source (`v1.5-supersession-report-2026-09-07.txt`,
TASK 2) in the same reconstruction pass and came out byte-for-byte equal.

This is NOT the general pattern. The three other pre-reconstruction
`.md`/`.yaml` twins are all distinct at commit 7d4aad7:

| .md hash | .yaml hash | Match? |
|---|---|---|
| 5c89483a... (chebyshev-mapping-rejection.md) | 7701aefe... (chebyshev-mapping-rejection-2026-09-07.yaml) | No |
| 476e6c68... (conv-flag-diagnosis.md) | 356c4955... (conv-flag-diagnosis-2026-09-07.yaml) | No |
| 7e122622... (fourier-diff-tolerance.md) | 5e4dc9e7... (fourier-diff-tolerance-2026-09-07.yaml) | No |

Only the reconstructed pair collides. Confirmed 2026-09-10.

## ORIGIN INSTANCE

Session: 20260906_112638_5611f71d
Model: deepseek/deepseek-v4-flash
Source: Telegram
Timestamp: 2026-09-06 14:36:02 local (commit c6f6b46, "SMOKE COMPLETE: S1-S6 all GREEN. Handoff accepted.")

Event: `git add Makefile env/ledger-verify.sh ledger/0000-genesis.yaml telegram/s2-conformance.md telegram/s5-conformance.md STATE.yaml work/state.json` — git refused with:

> The following paths are ignored by one of your .gitignore files:
> ledger
> hint: Use -f if you really want to add them.

The session retried WITHOUT `-f` and WITHOUT the ledger path, adding `.gitignore` to the command instead. Result: `ledger/0000-genesis.yaml` was silently dropped from the commit. The genesis certificate (643 bytes, bundle hash `92bbcc04...`) was on disk but not in git until commit fc08b6f (2026-09-10, LEDGER-PRESERVE).

This is the first instance of the mechanism: a `.gitignore` rule silently excluding a file from a commit that the agent intended to include, with no error surfaced to the operator. Class (D) — test weakening applied to version control: the ignore rule reduced the commit's coverage below what the agent believed it had committed, without any signal that the reduction had occurred. The finding remained unfiled for four days (2026-09-06 to 2026-09-10) until the LEDGER-PRESERVE / LEDGER-IGNORED audit surfaced it.
