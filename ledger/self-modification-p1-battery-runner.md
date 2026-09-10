Ledger Entry — SELF-MODIFICATION (write-ahead)
Filed: 2026-09-08 (BEFORE the change takes effect)
Type: SELF-MODIFICATION
Object: harness/p1_battery.py (NEW file, P1 execution runner)

WHAT WILL CHANGE
Creation of harness/p1_battery.py — the P1 falsification battery runner.
This is a NEW file; it does NOT modify any sealed manifest file. It imports
engine/f1.py (sealed, read-only) and implements the pre-registered battery
tests with the pre-registered tolerances:
  FLOOR = -1/2 + 3e-3 = -0.497
  delta = 5e-4 (BORROWED-TOLERANCE)
  N = 1024 primary, N = 2048 doubling
  L = 20.0
  Strip zone: Re lambda in (FLOOR, -5e-4)
  F-5 threshold: eps*||(z-eps-L)^-1|| > 1e2 => UNTRUSTED

WHY
P1 authorization received. The sealed engine f1.py provides the operator
construction (RealizationPair._build_operator) but no battery harness. The
runner is the P1 measurement instrument. All tolerances are copied verbatim
from the pre-registration (specs/leg-a-p1-pre-registration-v1.5.txt, sealed
at c6a73ae8).

IMPACT ON P1 EXECUTION
None negative. The runner is required to execute P1. The sealed tree is
untouched. No TUNING adjustment of N, L, FLOOR, or any tolerance is made.

STANDING RULE COMPLIANCE
Write-ahead: filed BEFORE the file is created. No RULE-VIOLATION.