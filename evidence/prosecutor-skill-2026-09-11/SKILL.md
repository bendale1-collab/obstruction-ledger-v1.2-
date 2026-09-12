---
name: prosecutor
description: Adversarial-falsification framework for quantitative thesis testing. Laws, typed verdicts, pre-registration discipline, planted controls, and the three-tier execution pattern (gate → build → falsify). Seal-check v2, anchor rendering discipline.
---

# PROSECUTOR — Adversarial-Falsification Framework

**When to load:** Any thesis/claim/hypothesis test — measurement, falsification, or pre-registered kill screens.

---

## Core laws

*(ref:instrument-verification-techniques.md)* — mutation, split, span, testimony.
*(ref:gate-execution-lessons.md)* — budget, substrate, sweep, thresholds.
*(ref:pre-registration-battery-design.md)* — anchor-loss, control-first, ambiguous-middle, cap-derivation.
*(ref:precision-guard-rule.md)* — source-stated precision, UNSOURCED-PRECISION tagging.
*(ref:standing-rules-18-22.md)* — payoff before forecast; population before cut; cross-check verdict; CANNOT-QUOTE stays unticked.
*(ref:operator-convention-and-discretization-audit.md)* — sign, half-domain, term-by-term, truncation convergence, Hilbert formulas.
*(ref:referent-resolution-control.md)* — referent identity vs circular justification; demote never delete.
*(ref:k0-checker-design.md)* — K0 adversarial report verification (C3/C6/R1), injection-set validation, K1 candidate extensions. K0 v0.1 implements C3/C6/R1 ONLY; C1 designed-not-built; C2/C4/C5/C7/C8/C9/R2 names only (scope correction in k0-checker-validation.md).
*(ref:closed-record-discipline.md)* — closed result documents are immutable after seal: no edits/insertions, EOF pointers only; corrections live in the ledger; replay limitation; divergence-report cadence.
*(ref:k1-pre-registration-assembly.md)* — K1 input survey: commit-range UTC conversion, K0 interface (code implements C3/C6/R1 only; C1 designed not built), candidate-count mismatch handling, replay-limitation awareness.
*(ref:gist-id-audit-2026-09-10.md)* — gist-ID truncation audit across commits; K1 candidate 4 provenance; ANCHORS.md gap.
*(ref:seal-check-v2.md)* — commit-based seal verification (sha256(git show SEAL_COMMIT:path) vs manifest entry).
*(ref:subset-digest-sealing.md)* — git-based manifest subset integrity: whole-repo tree hashes diverge on every commit (falsified 2026-09-11); use subset digest instead (sha256 of sorted blob-sha+path pairs per git rev-parse <commit>:<path>). Subset digest stable across outside-manifest edits, tree hash is not.
*(ref:seal-object-definition-2026-09-11.md)* — Seal object falsification & correction: commits 437c58f vs HEAD (outside-manifest edits only) show tree-hash divergence but subset-digest identity; whole-repo tree hashes cannot seal subsets; subset digest is correct object. Construction, stability property, procedure change, falsification test.
*(ref:anchor-rendering-discipline.md)* — DERIVED vs VERBATIM anchor representation rule; RENDERING-AS-RECORD defect class.
*(ref:control-repair-procedure.md)* — continuous-vs-discrete eigenfunction verification protocol (5 steps).
*(ref:control-repair-protocol.md)* — coordinate map, index space, engine control, overlap/residual.
*(ref:mechanical-grep-report-contract.md)* — frozen-section grep/pickaxe report contract: section-completeness placeholder rule, tracked-vs-untracked classification, dual truncated/full pickaxe procedure, anchor-registry negative check, exact-reply-contract override.
*(ref:git-provenance-audit.md)* — force-add detection (`git check-ignore --no-index` pitfall), multi-writer attribution audit, QUOTED header convention, manifest duplicate-hash scan, session attribution from Hermes state DB.
*(ref:session-attribution-forensics.md)* — cross-profile session DB queries to verify which session/model produced a commit; common misattribution patterns (user claim vs database reality); zombie session caveat.
*(ref:injection-fixture-discipline.md)* — hard-negative 5/10 rule, write-before-code ordering, class-level organization, threshold pre-statement (recall=1.0, FP=0.0), adjudication branches for ambiguous cases.
*(ref:divergence-report-precondition.md)* — standing rule 7 procedure: diff seal vs HEAD, classify nature (append/edit/renumber/delete), cite declaring entries, full table output, gate result (clean/fully-declared/undeclared).
*(ref:seal-preparation-pattern.md)* — two-stage seal (pre-registration + run), manifest write/commit/seal-check-v2/gist-block template, founder-only publication, append-only gist.
*(ref:split-authorship-protocol.md)* — code authorship split: Agent A (C1/K1-1/K1-2) and Agent B (K1-3–K1-6) each read §2 only; neither reads other's code or fixtures; contamination bounded to definitions. Pre-run standing-rule statement required. Split-breach: when fixture author modifies code under test, the guard is breached regardless of risk level; file as wrong-invariant verdict (session identity ≠ authorship identity).
*(ref:k1-test-harness-pattern.md)* — K1 run phase: test harness output contract (injection table + per-check stats + retrodiction table), evaluation logic, NO_CODE handling for unwritten checks.
*(ref:k1a-fixture-measurement-discipline.md)* — Operationalization of planted controls for check fixtures: MEASUREMENTS.txt (run code to generate, not assert); index.md rationales must match measurements character-for-character; hard-negative distinctness verification; property file label scoping per §2.
*(ref:k1a-gate-procedure.md)* — K1a G0–G4 gates: import smoke (IMPORT-OK + empty-input []), static syntax (ruff FA,UP), pytest collect-only, clean tree, divergence report. Halt conditions, failure modes, publication requirement. G4 canonical: 7d4aad7 vs HEAD (19 manifest paths), not K1a-seal comparisons.
*(ref:anchor-postdates-artifact.md)* — Public gist anchor postdates code commits: repo seal commit is binding timestamp, not public publication timestamp. Procedure finding, not disqualification.
*(ref:tarball-handoff-pattern.md)* — Multi-agent fixture delivery via tarball: hash-verify, extract, count entries, remove tarball, commit with provenance message. No reading other agent's fixtures.

### Independent-ref rule

Coverage audit reference MUST be from a DIFFERENT source family than the extraction source. Same press release / PDF on both sides → circular void.

### Output contract

Every run returns exactly one typed verdict. Plus: frozen dataset, statistic with bootstrap CIs, control-behavior table, coverage/audit table, one-paragraph statement of what would have changed the verdict.

**Delivery preference (this user):** txt file attachments over inline chat tables/code blocks. Telegram strips inline formatting; tables don't render. Default to writing findings to a file and delivering via `MEDIA:` path rather than inline formatting. Report the path only; do not paste file content into chat.

## Pitfalls — corrections from this project

### Negatives must be distinct from each other, not just from positives

When writing 10 negatives, each must be structurally distinct from the others. A negative that is a near-duplicate of another negative (e.g. both single-entry manifests with different hashes) wastes a slot and inflates the hard-negative count. The user caught neg-07 being a structural duplicate of neg-03 at `ea7236a`; replaced with last-hex-char-differ (same path, hashes differ only in final hex char, expected SILENT because distinct). Review all 10 negatives against each other before committing.

**Application (2026-09-11, K1a round 3):** K1-4 had two gist-31 positives (one truncated, one "exactly short") — redundant. Replaced second with gist-33 (one char over). Also had two sha256-65 positives — redundant. Replaced second with sha256-63 (one char under). **Distinct variants, not copies with different paths.**

### Verify injection commit contains ONLY injection files

After committing injections, run: `git show --stat <sha> | grep -v '^ injections/'` — expect only the commit header and summary line. Any surviving file line means a non-injection file leaked into the commit. Report output in full.

### Pre-code spec ambiguities → standing-rules append, not spec edit

When a spec ambiguity is identified before code exists (e.g. "does K1-4 check `hash:` labels or only the illustrative list in §2?"), append a standing rule to `ledger/standing-rules.md` under the K1 section noting the ambiguity and its adjudication path. Do NOT resolve by editing the sealed spec. The standing rule records that disagreement between code and fixture will be adjudicated under §4, not resolved by editing either.

### Sealed closed records are append-only, never edited

`leg-a-closed-*.md` and similar closed result documents receive **no edits and no insertions after seal**. Corrections and commentary about them live in the ledger (e.g. `ledger/sealed-file-append-only.md`, `ledger/rendering-as-record.md`). EOF pointers only: a standing-rule cross-reference at the end is the maximum permitted modification. Any mid-file insertion into a sealed closed record is a violation — file it in RULE-IN-CLOSED-RECORD instead. Standing rule 8 in `ledger/standing-rules.md` governs this.

### Verbatim command output, not prose

When the user asks for a commit list or a specific command's output: **run the exact command given and paste the output verbatim**. Do not reformat into a prosified table, do not convert timezones unless asked, do not summarise. `git log --format='%h %cI %s'` is the canonical format for this project — if the user gives it, run it exactly. A prose reformulation that drops the actual output is an error ("reported empty").

### "Verbatim" claims require byte-level comparison, not diff

When reporting that published text is "verbatim" against a source, `diff` is
insufficient — it compares logical lines and is blind to continuation-line
indentation changes, trailing whitespace, and reflow. A mobile editor flattening
indentation on continuation lines will pass `diff` unchanged while the bytes
differ. Use `sha256sum` on both byte sequences (or `xxd | diff`) to prove byte
identity. A `diff` exit 0 is content-match, not verbatim-match. This is a live
K1-1 target: any check claiming verbatim match must prove it byte-for-byte.
(r21 incident, 2026-09-10: gist Rev E item 10 confirmed indentation was
flattened; the report had claimed "verbatim, no reflow" on `diff` alone.)

**Extension (r27 incident):** the agent's own report output can commit this
violation. When a report says "verbatim from gist" and presents text with
continuation-line indentation intact, but the fetched gist has flattened
indentation, the report is lying — it reconstructed or re-indented the text.
Rule: when you report "verbatim" output, the text in your report must be
byte-identical to what was fetched. Do not add indentation, reformat, or
reconstruct. If the source has flattened lines, quote them flattened.

### Critical data legibility: all numbers must be visible at delivery

When a report contains critical numbers (hashes, digests, thresholds, verdicts), those numbers must be **readable at delivery time** in the channel. File paths alone are not legible to the user — verdicts that rest on invisible backing data violate audit discipline. If the communication channel truncates, hides, or renders tables/code unreadably, paste the raw data as plain text directly into the chat. The rule: if you cannot read the number in the chat window right now, it does not count as part of the verdict. Invisible backing = failed report. This is an integrity gate, not a convenience preference. (r32 incident, 2026-09-11: user could not read a manifest-blob table or digests because Telegram stripped inline formatting; had to paste the file contents verbatim.)

### Canonical-length fixture requirement for K1-4 (identifier check)

When writing K1-4 fixtures, every hex string must be at an exact canonical length, not approximate:
- Gist IDs: exactly 32 characters
- SHA-256: exactly 64 characters
- Commit (full form): exactly 40 characters
- Commit (short form): exactly 7 characters

A 31-char gist string is valid for the positive case (one short), but a string of 28 or 29 chars looks like a prefix and confuses the fixture intent. Use exact lengths. Generate them with Python if needed: hex_string = 'a' * 32 for gist canonical. This prevents measurements from being ambiguous and rationales from drifting. (2026-09-11, K1a round 3: fixture generation used leftover partial strings from prior commits, causing measurements to not match rationales.)

### Never insert unauthorized content into append-only ledger entries

When the user specifies "append Instance N" to a ledger entry, append ONLY
that instance. Do not fabricate additional instances, add "helpful" context,
or insert sections that weren't requested. The ledger is append-only and every
insertion is a permanent record — an unauthorized insertion is the same class
of defect as an unauthorized edit. If you catch yourself adding content the
user didn't specify, stop, remove it, and commit only what was requested.
(ead0fa0 incident: Instance 2 was fabricated and inserted alongside the
user-requested Instance 3; required a second patch to remove.)

### Patch tool trailing-newline artifact

When appending to a file whose last line lacks a trailing newline, the `patch`
tool deletes and re-adds that line (producing a `-` line in `git show` diff)
even though only an append was intended. The content is unchanged but the diff
shows a spurious deletion. Verify with `git show <sha> -- <path> | tail -20`
to confirm the `-` line is identical to the `+` line (content unchanged,
newline added). If the user asks to verify deleted lines, report both the `-`
and `+` lines verbatim and note the artifact. (437c58f incident: patch
re-added the K1-6 labelling-method line with a trailing newline, producing a
false "deleted line" in the diff.)

### Exhaustive search yielding zero → report the gap immediately

When searching for a founder-specified phrase or section name across tracked
files returns zero matches, report "not found in any tracked file" and stop.
Do NOT expand the search to untracked files, variant phrasings, or broader
patterns in the same turn — the user asked for a specific string and it does
not exist. A 5-turn escalating search that ends at "not found" wastes the
user's time and patience. The correct next step is to ask the user to clarify
the target, not to keep widening the net.

### MEASUREMENTS table must agree with expected column before commit

When an index.md carries both a MEASUREMENTS table (generated by running code
on fixtures) and an expected column (FINDING / SILENT), every row must be
verified to agree before commit. A MEASUREMENTS row showing "YAML_OK" or
exit code 0 for a fixture whose expected column says FINDING is a
measurement-vs-expectation contradiction — the fixture is wrong, not the
expectation, and must be replaced with one that actually fails under the
declared parser. Committing a contradictory table is the same class as
committing an unverified verbatim claim: a judgment reported as a measurement.
(K1a round 3, 2026-09-11: six K1-6 positives measured YAML_OK but expected
FINDING, because yaml.safe_load was used as fallback instead of json.load
for JSON-typed fixtures. Corrected at round 4 by replacing fixtures that
failed to fire under the §2-mandated parser.)

### Subset digest seal object (corrected 2026-09-11)

**Falsified:** `git rev-parse HEAD^{tree}` as a seal object.

Whole-repo tree hashes diverge on every commit, whether manifest paths change or not. They cannot serve as seals for a subset of tracked files. **Correct seal object:** sorted list of `(path, blob_sha)` pairs (from `git rev-parse <commit>:<path>` for each manifest path), digested with sha256. Stable across commits that edit only files outside the manifest.

**Test:** commits 437c58f and HEAD touched only files outside the 19-path manifest, yet tree hashes differ (`e44577...` vs `a64bcf...`). Subset digest is identical at both (`3d9c8de...`). Tree hash failed; subset digest held. Use subset digest henceforth.

**Reference:** `ledger/seal-object-decision.md`, `ledger/subset-digest-sealing.md`, `work/r31-subset-digest-2026-09-11.txt`, `work/r32-manifest-blob-falsifier-2026-09-11.txt`.

### Verify cited filenames exist in the manifest before listing them

When writing a source-incident paragraph or any prose that lists specific filenames (e.g., "four .yaml paths fail: chebyshev-mapping-rejection.yaml, conv-flag-diagnosis.yaml, ..."), **verify each filename exists in the manifest** before citing it. Run `grep <name> MANIFEST.sha256` for each filename. If a cited filename does not exist in the manifest, the paragraph is factually wrong even if the narrative is correct.

**Violation example (2026-09-11, K1a round 3):** The K1-6 source-incident paragraph listed four undated `.yaml` filenames (chebyshev-mapping-rejection.yaml, conv-flag-diagnosis.yaml, fourier-diff-tolerance.yaml, misidentification-by-acronym-collision.yaml) that do not exist in MANIFEST.sha256. The actual undated twins are `.md` files. The dated `.yaml` files (with -2026-09-0X suffixes) do exist and are the ones that fail to parse. Corrected at round 4 by listing only the four dated .yaml paths that exist in the manifest, with the .md twins named as .md.

**Rule:** Before citing a filename in prose, grep the manifest for it. If it's not there, don't cite it — find the correct filename or state that the file does not exist.

### "No-execution instruction" means exactly that

When the operator says "no compute except the gates named" or "no code execution", that means **no py_compile, no test runs, no syntax checks, nothing**. Only the explicitly named gates are permitted. Running `python3 -m py_compile` to verify syntax is still execution and violates the constraint, even though it doesn't import or run the checks. The constraint is procedural (no agent-side execution), not functional (no check execution).

**Violation example (2026-09-11):** Agent B ran `python3 -m py_compile` on work/k1a/*.py before committing code, despite the instruction "no compute except the gates named." The py_compile step does not import or run the checks; it only verifies syntax. It would not have caught the K1 import failure (PEP 604 `X | None` is valid syntax but fails at runtime on Python 3.9). Filed, not disqualifying, but recorded as a procedure deviation.

**Rule:** When in doubt, ask the operator. Do not run any Python, shell, or compilation command unless it is explicitly named in the gate list or the operator authorizes it.

### write_file destroys content when placeholder leaks in

When using `write_file` to append to an existing file, if the tool's auto-generated placeholder content (e.g., "[truncated]") leaks into the file, it **destroys the original content**. The tool replaces the entire file, not appends. If you see a truncated placeholder in a write_file response, immediately check the file with `cat` or `head` and recover from git history if needed:

```bash
git show HEAD~1:<path> > /tmp/recovered.md
# Then re-do the append correctly
```

Better approach: use `patch` tool for appends, or read the file first, then use write_file with the full content (original + new). Never trust that write_file will preserve existing content if you don't provide it in full. (2026-09-11: verbatim-claim-unverified.md was destroyed when write_file leaked placeholder; recovered from 3d92e6b.)

### Empty-input contract for CLI tools

When a check/validator tool receives no arguments or empty input, it should
produce `[]` and exit 0 — an empty result set is a valid response, not an
error. An error object with exit 1 is a code defect (the tool failed to
implement the empty-input case), not an import failure.

**Pattern:** At the top of `main()`, before any argument parsing:
```python
if len(sys.argv) < 2:  # or == 1 for tools requiring positional args
    json.dump([], sys.stdout)
    sys.exit(0)
```

Gate G0 empty-input test catches this: `for f in work/k1a/*.py; do uv run --python 3.11 python "$f"; echo "exit: $?"; done`.
Expected: 7/7 emit `[]` exit 0. (Agent B k1_3..k1_6 failed at 0511785,
fixed at rev 2 by adding early-return branch.)

**Pitfall:** `len(sys.argv) != N` (exact count check) will reject empty input
and emit an error object. Use `len(sys.argv) < 2` or `len(sys.argv) == 1` for
the empty-input branch, then `len(sys.argv) != N` for the partial-args error
branch. Order matters: empty-input check first, then argument-count check.

### Wrong-invariant verdict — testing the wrong split

When an attribution or isolation test passes, verify it tested the **correct
invariant**. A test that confirms "different sessions produced the commits"
may pass while the actual guard ("fixture author did not modify code under
test") fails — the test tested session identity instead of authorship
contamination. The verdict is wrong even though the test passed.

**Pattern:** Before reporting a pass, ask: "What invariant was this test
designed to verify? Does the test actually measure that invariant, or does
it measure a proxy that can pass while the invariant fails?" If the test
measures a proxy, report it as a **wrong-invariant verdict** — the test
passed but the guard it was supposed to enforce is still breached.

**Example (2026-09-11 K1a):** The session attribution report confirmed that
0511785 and 163f11b were produced by different sessions/profiles/models and
reported "split holds." But the split-authorship guard requires that the
fixture author not modify code under test. Both the fixtures (3cebd19/898c566)
and the code revision (0511785) were from the same mahamara session
(20260911_124250_f1624c, qwen/qwen3.7-max). The test verified session
identity between Agent A and Agent B, not fixture-vs-code authorship.
Filed as wrong-invariant verdict in `ledger/split-breach-2026-09-11.md`.

**Split-breach filing:** When fixture author and code author share the same
session/profile, the split-authorship guard is breached regardless of risk
level (9 insertions / 10 deletions, empty-input branch only — risk low,
breach absolute). File in ledger as `split-breach-<date>.md` with: session ID,
profile, model, commit SHAs, diff size, scope, risk assessment, breach
classification (absolute), remaining guard (holdout row).

### Session attribution via state.db queries

To verify which Hermes session produced a commit, query the session databases:

```bash
# Find all state.db files
find ~/.hermes -name 'state.db' -type f | sort

# Search for commit SHA or message text in messages table
for db in ~/.hermes/state.db ~/.hermes/profiles/*/state.db; do
  echo "=== $db ==="
  sqlite3 "$db" "SELECT s.id, s.source, s.model, s.title, 
    datetime(s.started_at, 'unixepoch') as started
    FROM sessions s WHERE s.id IN (
      SELECT DISTINCT session_id FROM messages 
      WHERE content LIKE '%COMMIT_SHA%' OR content LIKE '%MESSAGE_TEXT%'
    ) ORDER BY s.started_at;"
done
```

**Key tables:**
- `sessions`: id, source, model, title, started_at, ended_at
- `messages`: session_id, role, content, timestamp

**Common misattribution patterns:**
- User claims session X produced commit Y, but database shows session Z
- Session received prompt but ended without output; prompt re-issued to different session
- Zombie sessions (ended_at IS NULL) appear in "active at commit time" queries

**Verification:** Cross-reference message timestamps with commit timestamps. A session that received the prompt at 18:49:54 but ended at 18:51:45 did not produce a commit at 18:55:38 — the prompt was re-issued.

### UNTESTABLE-FIXTURE-DEFECT verdict

When fixture structure does not match the check interface, the fixture set is
structurally untestable. Score all affected injection rows as
**UNTESTABLE-FIXTURE-DEFECT** — not PASS, not FAIL, not SKIP.

**Pattern:** The check requires `(before_file, after_file, before_commit,
after_commit)` but fixtures are single files with no before state. No
harness patch can fix this without the fixture author writing the fix — and
the fixture author writing the harness patch is the same contamination as
the fixture author modifying code under test.

**Filing:** Document in `ledger/<check>-fixture-defect.md`:
- Defect type: injection defect (§4)
- Check interface vs fixture structure mismatch
- No before state exists in sealed set
- Authorship (who wrote fixtures, who wrote harness patch)
- Verdict: UNTESTABLE-FIXTURE-DEFECT for all affected rows
- Remaining evaluation surface (real commits, holdout)

**Harness update:** Change the check branch to emit
`{"verdict": "UNTESTABLE-FIXTURE-DEFECT", "fixture": "<path>"}` with exit -1.
The test function skips with reason, not assertion failure.

**Example (2026-09-11 K1a K1-3):** All 13 K1-3 injection fixtures were
single .md files; k1_3.py requires before/after pairs. The 591d638 harness
patch (negatives as before==after, positives as needs-pair) was written by
the fixture author and withdrawn as a scoring path. Filed in
`ledger/k1a-k1-3-fixture-defect.md`. K1-3 still evaluated on R5/R6/R7 (real
commits) and seven-row holdout.

### properties.py completeness check

When a check directory contains `positive/` and `negative/` subdirs, verify
`properties.py` exists. This file declares the negative-space property
(generator of inputs that must NEVER produce a finding, minimum 200 examples).

**Verification:**
```bash
for d in c1 k1-1 k1-2 k1-3 k1-4 k1-5 k1-6; do
  count=$(find "injections-k1a/$d" -name 'properties.py' -type f | wc -l)
  echo "$d: $count"
done
```

**Missing properties.py is a delivery defect.** Report in the fixture-defect
filing or in a separate completeness audit. The negative-space property is
part of the §2 specification; its absence means the check cannot be evaluated
on the property dimension.

**Example (2026-09-11 K1a):** k1-3 and k1-6 had no properties.py in the
sealed set. Both checks missing the negative-space property. Reported in
fixture-defect filings and harness documentation.

### Parser-per-filetype for K1-6 (yaml.safe_load is too permissive)

When checking K1-6 (declared extension vs content), **use the §2-mandated parser per file type**:
- `.json` files → `json.load` (or `python3 -c "import json,sys; json.load(open(sys.argv[1]))"`)
- `.yaml` / `.yml` files → `yaml.safe_load` (or `python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))"`)

**Do not use yaml.safe_load as a universal fallback for JSON files.** YAML's permissive grammar accepts most malformed JSON as a scalar or mapping, masking the intended failure. A JSON file with trailing commas, single quotes, or unquoted keys will parse successfully under yaml.safe_load but fail under json.load. Using the wrong parser produces false negatives (YAML_OK when the fixture should FAIL).

**Measurement procedure:** Run each fixture through its declared parser (based on the file extension or intended type), not through both parsers with fallback. Record exit code 0 (parse OK) or 1 (parse FAIL). The MEASUREMENTS table must use the correct parser per row, and the expected column must match. (K1a round 3, 2026-09-11: six K1-6 positives measured YAML_OK but expected FINDING because yaml.safe_load was used as fallback; corrected at round 4 by using json.load for JSON-typed fixtures and replacing fixtures that failed to fire under the §2-mandated parser.)

### Three-tier execution pattern (gate → build → falsify)

- **Gate:** Pre-registered freeze. Hash published. No compute until hash is founder-published.
- **Build:** Engine construction. Write-ahead for manifest changes.
- **Falsify:** Battery execution. Cheapest-fatal-first. F-4 (negative control) runs before F-1 (positive test).

### Standing rules (cross-reference)

Canonical address: `ledger/standing-rules.md` in the active project. Rules in sealed files are indexed by reference; nothing is moved from sealed files.

Closed result documents (e.g. `leg-a-closed-*.md`) receive NO edits or mid-file insertions after seal — corrections and commentary about them live in the ledger; EOF pointers only (see ref:closed-record-discipline.md).