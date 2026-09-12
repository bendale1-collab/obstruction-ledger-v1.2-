# Sweep Discipline and Instrument Defect Lessons

These lessons extend the core laws with experience from the
G1-02→G1-03 kill-rejection cycle.

## Sweep follows the constraint, not the plan

When a condition is binding (lowest count), the sweep parameter is the
one that could move that condition's count. Sweeping a non-binding
parameter is a violation of R1 (anti-correlation prior).

**Case:** G1-02 ran the sweep on the peer-relative multiplier (condition
d) while condition (a) was binding at 16/yr. Sweeping (d) cannot change
(a). The correct sweep is on the (a) detection method and its coverage
rate.

**Standing rule:** Identify the binding condition first. Then ask: what
parameter could move this condition across the threshold? Sweep that
parameter. If the answer is "none" (the instrument cannot produce a
different value), the instrument is defective — file
`UNMEASURED(instrument cannot resolve)`.

## Kill voided by instrument defect

A kill is void when:
1. The binding condition's count is based on a sample (not a full scan)
2. The expected base rate for that condition exceeds the kill threshold
3. The measured count is below the threshold

The zero-conjunction argument is circular: the zero is entailed by the
sampling defect, not by the world.

**Procedural rule:** Before filing a kill, verify that every condition
count is based on a full scan of the available universe, or that the
sampling rate is documented and the expected base rate has been checked.
A kill filed on a sampled binding condition is `UNTESTABLE(kill licensed
by <N>% sample on the binding condition)`.

## 720× fault — instrument defect caught inside the loop

On 2026-08-03, the executor found a 720× fault in the pipeline after
the user rejected the kill. The condition (a) measurement was 16/yr vs
expected ~11,500/yr. The executor sourced the base rate from the EFTS
API and confirmed the defect.

This was the **first substantive defect in this run caught inside the
loop** rather than by the reader. Record it as a milestone: the
anti-correlation prior (R1) can be automated as a pre-run check, and
once automated, it catches defects that previously escaped.

## Base-rate sanity check as a pre-run gate

Add to every pipeline: for each condition, emit the measured count
beside an independently-sourced expected count. A condition off by more
than an order of magnitude from its expected base rate **halts** the
run. This is the anti-correlation prior as code.

**Sources for base rates:**
- 8-K Item 5.02 (condition a): EFTS API, ~11,500/yr
- Other conditions without independent sources: set a loose floor and
  flag the absence as a limitation