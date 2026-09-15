Replay of anchored split-B run; reproduces n=1920, union 231, per-class
64/9/41/133 exactly; original Phase C committed no invocations.log
(defect PHASE-C-MISSING-INVOCATIONS-LOG).

Files:

- `replay.invocations.log` — 1920 lines, one per trajectory, each carrying the
  four class verdicts for that case. These are the per-case vectors the
  retained-class union in `ledger/B1-verdict.md` was counted from.
- `replay.json` — the run's result file, carrying its `producing_cmd`,
  `started_at` and `finished_at`.

Produced by:

    python -m ol.audit run --classes A_weak,A_selfev,A_nonex,A_pad \
      --in ~/ol/repo/data/terminal-wrench --tree hack \
      --tasks prereg/tw-split-B.txt --out /tmp/retained/replay.json

This is a replay, not a second measurement: the anchored Phase C run at
7001cd3 remains the measurement of record.
