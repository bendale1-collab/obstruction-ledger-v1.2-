# Obstruction Ledger — Makefile (scaffold stubs)
# RUNBOOK §4 rules: all targets exist, return NOT IMPLEMENTED or work

SHELL := /bin/bash
PHASE ?= UNKNOWN

help:
	@echo "Obstruction Ledger — targets:"
	@echo "  resume         RUNBOOK §1 cold-start / resume drill"
	@echo "  ledger-verify  Verify ledger hash chain"
	@echo "  seal-prepare   P6 seal artifact assembly"
	@echo "  determinism    H-F determinism test"
	@echo "  golden         H-A analytic goldens"
	@echo "  battery        H-G ghost battery"
	@echo "  g0             G0 extractor retrodiction"
	@echo "  g1             G1 α(a)-law discovery"

resume:
	@echo "NOT IMPLEMENTED: BOOTSTRAP — scaffolding in progress"

ledger-verify:
	bash env/ledger-verify.sh

seal-prepare:
	bash env/seal-prepare.sh

determinism:
	@echo "NOT IMPLEMENTED: P0"

golden:
	@echo "NOT IMPLEMENTED: P0"

battery:
	@echo "NOT IMPLEMENTED: P3"

g0:
	@echo "NOT IMPLEMENTED: P4"

g1:
	@echo "NOT IMPLEMENTED: P5"