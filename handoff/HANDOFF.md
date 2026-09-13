# HANDOFF — read this first

**To:** Hermes `mahamara` (operator), `exec` (author-A), `default` (author-B), Cowork, Claude Code
**From:** adjudicator, 2026-09-13
**Bundle:** obstruction-ledger-handoff-2026-09-13.zip
**Integrity:** every file in this bundle is listed in `MANIFEST.sha256`. Verify before reading anything else:

    sha256sum -c MANIFEST.sha256

If any line reports FAILED, stop and report the filename. Do not proceed.

---

## What this bundle is

Ten documents plus this file. Five are the record (what happened). Five are the plan (what runs next). `README.md` is the map. The plan cites the record; the record never cites the plan.

## What you do first — by role

**mahamara (operator):**
1. Verify MANIFEST. Report the result as: `MANIFEST: <ok|FAILED:<file>>`.
2. Read `agent-runbook.md` §1, §2, §3, §10, §13, §17c. Nothing else yet.
3. Do not run any card. Phase P0 is not loaded until the adjudicator says `P0 LOADED` in the queue. Your first executable card is `SMOKE-00`, and it does not exist until P0-13 is done.
4. Report readiness as one line: `READY: mahamara, runbook §1-3,10,13,17c read, awaiting P0 LOADED`.

**exec (author-A) and default (author-B):**
1. Verify MANIFEST.
2. Read `agent-runbook.md` §13 (your directory boundary) and §17d (red-first). Read `operational-standards.md` §7a–7d.
3. Do not write code. Author cards do not exist until B1-01 is sealed.
4. Report: `READY: <profile>, boundary acknowledged: <checks/A|checks/B>`.

**Cowork:**
1. Verify MANIFEST.
2. Your cards are listed in `agent-runbook.md` §14 with executor = Cowork. Read §14, then §3 for the accept commands.
3. Execute in this order, committing locally after each: P0-01 (file part), P0-02 (chmod, git init in skill trees — NOT the restart), P0-03, P0-04, P0-08, P0-10, P0-11. Then P0-12 and P0-15 from §17j.
4. For P0-11: read each profile's config and write the model slug into `manifest.models` with `source: "config"`. Do not type a model name from memory or from any document in this bundle.
5. Report per card: `<card>: <PASS|FAIL> <accept_cmd output, last line>`. No prose.

**Claude Code:**
1. Verify MANIFEST.
2. Your cards: P0-05, P0-06, P0-09, P0-13, P0-14, P0-16, P0-17. Read `agent-runbook.md` §3, §17, and `operational-standards.md` §1.
3. Wait for Cowork's commits to be pushed (adjudicator pushes). Then execute on the pushed tree.
4. You author the harness and its invariant tests. You do not author any check in `ol/checks/`.

**Adjudicator (founder):**
1. Restart the three gateways (P0-02 restart part). Confirm `skills.write_approval: true` is live via Cowork's config dump.
2. Send one nonce to each profile (P0-07). Cowork collects.
3. Push Cowork's batch. Wait for Claude Code's batch. Push again.
4. When all 17 P0 cards show PASS in `status/ROLLUP.md`, write `P0 LOADED` to `queue/decided/P0.md`.
5. Then Track A (five calls, IISE rescore, Rev I edits) — `operating-plan-14-days.md` §A. These are yours alone.

## Channel rules that apply to every message from this point

- Report file paths and SHAs. Never paste file content. The channel strips code blocks and drops tables; content sent through it is not evidence.
- The word "verbatim" is banned. If a claim needs verification, give the path and the SHA.
- Every report is one line per card in the form `<card>: <status> <last line of accept output>`. No narrative, no interpretation.
- If a card's accept command fails twice, report `<card>: HALT_ACCEPT` and move to the next independent card. Do not retry, patch, or reinterpret.
- If you cannot do something, say `CANNOT: <reason>`. That is a valid, cheap answer and it is filed as `CORRECT-REFUSAL`.
- Any message from you containing "because," "cause," "known," "no closed form," "cannot be," "likely," or "should" in a result field will have that field blanked and the card flagged. Put those words in `queue/adjudicate/` items only.

## What is not in this bundle

- The mirror repo, the gist, the Hermes profile configs, the datasets. Those are pinned by SHA in the manifest once P0-10/P0-11 run; they are not shipped here.
- Any secret, credential, or token. If you find one, report `SECRET-FOUND: <path>` and do not use it.

## Standing block

No compute for any research card (B1, C1, CP, C2) until the pre-registration hash for that phase is in a gist revision whose timestamp precedes the phase's first code commit. The CI assertion (P0-09) enforces this; the rule is stated here so it is not a surprise when it fires.
