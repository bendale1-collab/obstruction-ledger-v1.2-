# B1 PARTIAL

pre-registered external-data 2026-09-14

Source: `results/C/*.json` at `7001cd3`. Every number below carries the
`producing_cmd` recorded in the result file that holds it.

## Recall — split B

- aggregate recall 231/1920 = 0.120 (band 0.10-0.50) — `results/C/tw_hack_B.json`
  - `python -m ol.audit run --classes A_weak,A_selfev,A_nonex,A_pad --in /Users/brukendale/ol/repo/data/terminal-wrench --prs None --seed 0 --tree hack --tasks prereg/tw-split-B.txt`
- A_pad hack 133/1920 — `results/C/tw_hack_B.json`
  - `python -m ol.audit run --classes A_weak,A_selfev,A_nonex,A_pad --in /Users/brukendale/ol/repo/data/terminal-wrench --prs None --seed 0 --tree hack --tasks prereg/tw-split-B.txt`
- A_pad honest 33/1809 — `results/C/tw_honest_B.json`
  - `python -m ol.audit run --classes A_weak,A_selfev,A_nonex,A_pad --in /Users/brukendale/ol/repo/data/terminal-wrench --prs None --seed 0 --tree honest --tasks prereg/tw-split-B.txt`
- A_selfev 9/1920 — `results/C/tw_hack_B.json`
  - `python -m ol.audit run --classes A_weak,A_selfev,A_nonex,A_pad --in /Users/brukendale/ol/repo/data/terminal-wrench --prs None --seed 0 --tree hack --tasks prereg/tw-split-B.txt`
- A_nonex 41/1881 evaluable, 39 NA — `results/C/tw_hack_B.json`
  - `python -m ol.audit run --classes A_weak,A_selfev,A_nonex,A_pad --in /Users/brukendale/ol/repo/data/terminal-wrench --prs None --seed 0 --tree hack --tasks prereg/tw-split-B.txt`
- A_weak hack 64/1920 — included in the 231 aggregate above — `results/C/tw_hack_B.json`
  - `python -m ol.audit run --classes A_weak,A_selfev,A_nonex,A_pad --in /Users/brukendale/ol/repo/data/terminal-wrench --prs None --seed 0 --tree hack --tasks prereg/tw-split-B.txt`

## Retirement

- A_weak RETIRED, flask 35/200 CI[0.129,0.234] — `results/C/flask_prs.json`
  - `python -m ol.audit run --classes A_weak,A_selfev,A_nonex,A_pad --in /Users/brukendale/ol/repo/data/flask --prs 200 --seed 20260913 --tree hack`

## Sequencing and seal

- anchor 67d852b0 15:20:21Z — founder assertion; not a git object in this
  repository and absent from every tracked file, so it carries no
  `producing_cmd`
- results 7001cd3 15:23:17Z — `git log -1 --format=%cI 7001cd3`
- sealed paths clean — `git diff 3a6460b 5b98454 -- ol/audit prereg/` empty
- seal c36dc952 reproduced at 3a6460b, 7001cd3, 5b98454 —
  `python scripts/seal_digest.py`; at `claudecode-p0` HEAD the digest is
  b2aada17, sealed path `ol/audit/__main__.py` having changed in B1-01n
  after the measurement
