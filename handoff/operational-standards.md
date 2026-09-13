# Operational Standards — Harness, Data, Validation, Execution

**Addendum to the 14-day plan and atomized spec. Every item below is a gate, not a suggestion.**

The postmortem's K1 RED had three causes, none about check quality: Python 3.9 vs PEP 604 syntax, harness hardcoding 3 of 7 checks, fixtures the checks couldn't parse. Three Hermes harness versions reported PASS on files with no tests. A ledger file was destroyed by a placeholder leak and not reported. The skill tree grew 42→354 lines unprompted. Every one of these is an execution failure that industry tooling already prevents.

---

## 1. Harness — build on hardened open source, never from scratch

**Rule:** no bespoke harness. Every check is a plugin in an existing, tested framework.

| Need | Adopt | Why |
|---|---|---|
| Test runner | `pytest` ≥ 8 with `pytest-cov`, `--strict-markers`, `-p no:cacheprovider` | "pytest exited 0 on a file with no tests" is caught by `--co -q` count check and `pytest-cov --fail-under` |
| Agent eval harness | `inspect_ai` (UK AISI, MIT) | EvilGenie's harness is already an Inspect eval (`JonathanGabor/evilgenie_inspect`). Holdout tests, sandboxing, trajectory logging are built in. Don't rebuild them. |
| Entailment judge | MiniCheck-FT5 via its pip package, pinned | Local, deterministic at fixed batch, permissively licensed |
| Lean interaction | LeanDojo, pinned commit | MIT; ablation and tracing already implemented |
| Attestation | in-toto layout + `git show <commit>:<path>` seal check | Do not write a seal object. Use a filtered git tree. |
| Fixture validation | JSON Schema per fixture type, validated in CI before seal | K1-3/5/6 shipped 13 unreadable fixtures each. A schema gate at commit time makes that impossible. |

**Mandatory pre-commit hooks** (`.pre-commit-config.yaml`, sealed in manifest):
- `ruff` (lint + format), `ruff --target-version py311` — kills the PEP 604 class
- `mypy --strict` on harness code
- `vermin` was falsified (misses runtime TypeError); use `ruff` + import-smoke test in the target interpreter instead
- `check-json`, `check-yaml` — kills "4 of 5 `.yaml` paths are prose"
- `detect-secrets` — Cowork already does this manually; automate it
- custom hook: `git check-ignore` audit — fails if any tracked-required path is ignored. Kills `.gitignore:3` forever.

**Harness invariants, enforced by tests on the harness itself:**
```python
def test_every_check_is_invoked():
    # K1 hardcoded 3 of 7. This fails if the registry and the run disagree.
    assert set(run_log.checks_invoked) == set(CHECK_REGISTRY)

def test_fixture_count_nonzero_per_check():
    # "properties held" on zero tests is the K1a failure mode.
    for check in CHECK_REGISTRY:
        assert len(fixtures_for(check)) >= MIN_FIXTURES

def test_check_can_read_its_fixtures():
    # Pre-seal gate. K1a's three UNTESTABLE checks would have failed here.
    for check in CHECK_REGISTRY:
        for f in fixtures_for(check):
            assert check.parse(f) is not None
```

**Refactoring rule:** any harness file over 300 lines or any function over 50 lines is split before seal. `radon cc` ≤ 10 per function, enforced by hook. The prosecutor skill went 42→354 lines because nothing stopped it.

---

## 2. Datasets — every set ships with negative controls, and the negatives are constructed, not assumed

**Rule:** no dataset enters the manifest without (a) a labeled negative class of size ≥ 30% of positives, (b) a documented construction method for the negatives, (c) a canary subset.

| Experiment | Positives | Negatives (constructed) | Canaries | Source / license |
|---|---|---|---|---|
| C1/C2 necessity | Mathlib hypotheses with `N=1` by ablation | **Synthetic mutants**: add a provably-redundant hypothesis (derivable from others, or vacuous) to a verified theorem; verify with Lean that the proof still checks. Natural rate ~1% is too thin — do not rely on it. | 20 hypotheses with `N=0` engineered to look load-bearing (named like the conclusion, placed first) | mathlib4 @ SHA, Apache 2.0 |
| B1 audit FPR | 200 merged human PRs, CI green, unreverted 90d | Not needed — this set *is* the negative class for the audit | 10 PRs with a known benign test edit (rename, not relaxation) — `A_weak` must not fire | `pallets/flask` @ SHA, BSD-3 |
| B1 audit recall | TRACE / Terminal Wrench labeled exploits | Their clean trajectories | 5 hand-crafted exploits per class, sealed | check each license before use |
| X1 reward delta | — | Arm 0 (no reward) is the control | 5 known-exploit trajectories injected into Arm 0; if the audit misses them, halt | SWE-bench Verified @ SHA |
| TQ10 π validity | 100 auto-generated perturbations | 20 deliberately invalid perturbations (meaning-preserving edits mislabeled as flips) | — | founder-labeled, blind |
| TQ7 code reuse | 50 PRs with reviewer rating | Rated 1–2 PRs are the negative class; ensure ≥ 15 | 5 trivial-but-merged PRs (typo fixes) — `U` must be low | flask |

**Negative-control discipline, per run:**
- Canaries are sealed in the manifest by hash. Their positions are randomized per run.
- A check that passes all canaries it should fail is retired for that run and the run is flagged.
- Report `P(check fires | canary)` alongside every recall number. Denominators always.

**Contamination checks, before seal:**
- Train/test overlap: exact-match and near-duplicate (MinHash, Jaccard > 0.8) between any fixture set and any judge's known training corpus where documented. The gzip+kNN paper had test-in-train at 90.4% on one set. Don't repeat it.
- Leakage: no fixture may contain its own label in text.

---

## 3. Retrodiction and out-of-sample — required where the check was derived from the failures it tests

**Rule:** any check or threshold derived from observed failures must (a) retrodict those failures on the sealed artifacts, (b) pass a holdout it was never shown, (c) report both numbers separately.

**Retrodiction (the RA-1..RA-5 pattern, kept):**
- For each audit class, the catalogue instances that motivated it are the retrodiction set. The check must fire on ≥ 80% of them on the *sealed* artifact hashes.
- Failing retrodiction means the check doesn't detect what it was built for. Do not proceed to holdout.

**Out-of-sample:**
- Holdout is authored by the founder, sealed at pre-reg time, revealed after code. The K1 holdout is spent; author a new one before C2.
- Holdout must include at least one domain the check was not built on. For the audit: code (built) and one of {contracts, filings}. For Λ: Mathlib (built) and code review.
- Report: retrodiction recall, holdout recall, and the gap. A gap > 0.3 means the check overfit its origin.

**Where retrodiction is NOT needed:** borrowed instruments with published numbers (MiniCheck, CiteTracer). Cite their numbers; verify on 50 local examples that you're within 0.1 of published. If not, your integration is wrong, not their model.

**Pre-registration integrity:**
- Rev H postdated the code by three hours. The rule: `git log --format=%cI` of the first harness commit must be later than the gist revision timestamp, and CI asserts it. If not, the run is labeled RETRODICTION in every result file automatically.

---

## 4. Execution-failure mitigations — the things that slowed the last run

Ordered by how much time each cost.

**4a. Relay loss (Telegram drops tables; "verbatim" that wasn't).** Cost: most of 60 prompts.
- **Fixed by the mirror.** Every result is a file at a raw URL. No result is read from chat. Enforce: the adjudicator's prompt template contains only file paths, never content.
- Add: every result file ends with its own SHA-256 on the last line. The adjudicator diffs against `git show`. Mismatch → not read.

**4b. Agent self-modification (skill tree 42→354 lines).** Cost: one investigation, unknown contamination.
- `skills.write_approval: true` on all profiles — set, needs restart. **Restart the gateways before the next run.**
- `chmod -R a-w` on all three skill trees, not just mahamara.
- Skill trees under git; CI diff on every run start; any change → halt with the diff in the ledger.

**4c. Harness reports PASS on nothing.** Cost: three harness versions.
- The three invariant tests in §1. Plus: every run emits `checks_invoked`, `fixtures_per_check`, `tests_collected`. A run with `tests_collected == 0` is RED by construction.

**4d. Environment mismatch (3.9 vs 3.11).** Cost: one RED.
- `uv` lockfile with pinned interpreter, sealed. Dockerfile with `FROM python:3.11.9-slim`, digest-pinned. The interpreter is a manifest entry.

**4e. Fixtures the check can't read.** Cost: 39 UNTESTABLE rows.
- Schema validation pre-seal (§1). Plus `test_check_can_read_its_fixtures`.

**4f. Author identity by bot name.** Cost: two wrong inferences in an hour.
- Per-profile `git config user.name/email`, set in each profile's launchd env. Filed twice, implemented never. **Do it before anything else in this document.**
- CI: reject any commit whose author is not in the sealed author registry.

**4g. Silent file destruction (placeholder leak).** Cost: unknown until found.
- Every write goes through a wrapper that refuses if the target exists and no `--overwrite` is passed, and that logs the pre-write hash. Wrapper is in the harness, not the agent's skill.

**4h. Founder-typed timestamps wrong.** Cost: one gist revision.
- Never type a timestamp. The publish script reads it from the GitHub API and writes the ledger line.

**4i. Sequencing (anchor after artifact).** Cost: K1a's pre-reg status.
- The CI assertion in §3. Plus: the harness refuses to run if the manifest hash isn't in the gist yet (fetch and compare at start).

**4j. Three gateways, one author, prompts routed by which chat answered.**
- One profile per role, hard-bound: operator, code-author-A, code-author-B. A prompt for A that lands in B's chat is a RED on the run, not a shrug.

---

## 5. Definition of done for a run

A run is complete when all of the following are files in the mirror at a commit that postdates the gist revision:

```
results/<run>/manifest_check.json      seal 19/19 (or N/N), pre-reg timestamp < first code commit
results/<run>/harness_invariants.json  all three invariant tests PASS
results/<run>/canaries.json            per-check canary fire rate, with denominators
results/<run>/retrodiction.json        recall on sealed catalogue instances
results/<run>/holdout.json             recall on founder-authored holdout, revealed post-code
results/<run>/fpr.json                 per-class FPR on negative controls, Wilson CI
results/<run>/env.lock                 interpreter, deps, docker digest
results/<run>/skills_diff.txt          empty, or the run is flagged
results/<run>/verdict.md               PASS / KILL / HALT per pre-registered threshold, no narrative
```

Anything missing → the run is INCOMPLETE and cannot be cited.

---

## 6. What this costs

About two days of setup before any experiment runs: pre-commit config, Inspect scaffold, schemas, invariant tests, gateway restart, git authors, publish script. Every one of those days was spent three times over in the last run doing the same work by hand and getting it wrong.

The standing block stays. Compute after the harness passes its own tests and the pre-reg has a gist timestamp.

---

## 7. Execution learnings from the K1/K1a run — applied

The obstruction chat and postmortem contain twelve execution-specific lessons that §1–§5 did not fully encode. Each is stated as the failure it came from, then the rule.

### 7a. Claims about fixtures are claims. Measure them.
*Failure:* Four rounds on Hermes's fixture half. Index rationales asserted lengths, counts, and parse outcomes that were wrong on six rows. One committed MEASUREMENTS table contradicted its own expected column and shipped anyway. A fixture named `fiftyfive` was 65 characters.
*Rule:* Every fixture directory ships `MEASUREMENTS.txt` **generated by running the sealed parser**, never typed. CI regenerates it and diffs against the committed copy. Any disagreement blocks the seal. Fixture filenames that encode a property (length, count, type) are checked against the measurement — name/content mismatch is a build failure.

### 7b. When measurement disagrees with expectation, fix the fixture.
*Failure:* `p-yaml-dup` was expected to fail parsing; `yaml.safe_load` accepts duplicate keys. The instinct was to relabel the expectation.
*Rule:* The expected column is a claim about check behavior under the sealed parser. If a fixture doesn't exercise that behavior, replace the fixture. Never edit the expectation to match a fixture that doesn't do what its name says. And: the parser used in MEASUREMENTS is the parser named in the spec, by import path, asserted in CI.

### 7c. Properties are checked by reading before they're checked by running.
*Failure:* A K1-4 property was declared such that "if the code is correct, the property fails; if the property passes, the code is wrong." Caught pre-seal by reading. Separately, a C1 property was wrong at 74/200 until executed.
*Rule:* Every property gets one adversarial read by the non-author before seal, with the question "what would make this pass on wrong code?" Then a dry run on ≥ 200 generated cases. A property that passes at 100% on first run is suspicious, not reassuring — check that it's actually invoking the check.

### 7d. Dedupe fixtures by content hash, not by name.
*Failure:* Two K1-4 positives were the same case under different names. Two K1-3 negatives likewise. Counts were reported as 10 and 3; real counts were 9 and 2.
*Rule:* CI computes content hashes across every fixture set. Duplicates fail the build. Every reported fixture count is `sort -u | wc -l` on hashes, not `ls | wc -l`.

### 7e. The harness must be unable to report PASS without invoking checks.
*Failure:* Three harness versions reported PASS on generated cases without calling the check. "Properties held" meant "pytest exited 0 on a file with no tests."
*Rule:* Already in §1 invariants. Add: the harness emits a per-case log line with the check's actual CLI invocation and return code. A run whose log has fewer invocation lines than fixture cases is RED. The harness's docstring rule from K1a stands: *"Never edits anything."* A harness that can write to the artifacts it tests is not a harness.

### 7f. Scope-check fixtures against the check before seal, not after.
*Failure:* K1-6's sealed fixtures were structurally out of scope for K1-6 (wrong extension/path pattern). 13 UNTESTABLE. Same for K1-3 and K1-5. Discovered after seal, when nothing could be changed.
*Rule:* §1's `test_check_can_read_its_fixtures` covers parseability. Add a scope test: for each fixture, `check.in_scope(fixture_path)` must return True, where `in_scope` is the same predicate the check uses at runtime. Sealed before code exists means the predicate must be specified in the pre-reg, not inferred from the code later.

### 7g. Validate holdout runnability structurally, without revealing content.
*Failure:* Two of seven holdout rows were unrunnable as authored — one targeted a commit predating the manifest, one targeted a non-manifest path. The holdout was spent on discovery.
*Rule:* The holdout author runs a **structural** validator before sealing: every referenced commit is in the repo and postdates the manifest base; every referenced path is in the manifest; every expected outcome is in the check's output vocabulary. The validator output (pass/fail per row, no content) is committed alongside the sealed holdout hash. Content stays sealed; runnability is proven.

### 7h. Any number in a report comes from a command, and the command is in the report.
*Failure:* "14 files" (13), "142 manifest lines" (282), "24 holdout lines" (26). Founder-typed timestamps. Same class filed a dozen times against Hermes, then committed by Claude.
*Rule:* Result files are generated by scripts that embed the producing command next to each number. A number without a command is a founder assertion and is labeled as such. This applies to Claude's outputs in the loop as much as the agent's.

### 7i. The record decides identity. Never a label.
*Failure:* Two session-attribution inferences from bot name in one hour, in opposite directions. "Agent B" was whichever profile answered.
*Rule:* §4f's per-profile git author, plus: every prompt sent to an agent includes a nonce; the agent's response must echo it; the harness records (nonce → profile → commit). Attribution is a database query. If the nonce is missing, the response is unattributed and the row is HALT.

### 7j. Transport is not a source.
*Failure:* Empty-slot reports (header, no rows) ×13, mostly Telegram dropping tables. Attribution to agent behaviour was withdrawn where the raw render wasn't checked. "Verbatim" blocks that were reconstructions ×6.
*Rule:* Already §4a. Add: the word "verbatim" is banned from agent reports. Reports state a file path and a SHA. If the adjudicator needs content, the adjudicator reads the file at the mirror. A claim of verbatim without a matching SHA is filed as `VERBATIM-CLAIM-UNVERIFIED` automatically by a grep in CI.

### 7k. Correct refusals are the target behavior. Reward them in the ledger.
*Observation:* Hermes reported "NOT RUN" rather than inventing a result, "file does not exist" rather than hashing something else, "ALREADY_EXECUTED" rather than re-running, and refused to restart its own process tree. Cowork flagged its own scope, a rewritten commit, a wrong line count, and a context leak — five times, unprompted, in its own disfavour. These appeared more often as prompts got more mechanical.
*Rule:* Ledger type `CORRECT-REFUSAL` with the same weight as a defect entry. Prompts are written so that "I cannot" is a valid, cheap, first-class answer — a field in the response schema, not a free-text escape. Mechanical prompts over interpretive ones wherever the task allows; the observed refusal rate is the evidence for that ordering.

### 7l. Nearly-filed false claims are filed as near-misses.
*Failure:* `ANCHOR-UNRECORDED` was nearly filed on a false Hermes statement; the ID was in a sealed file. Caught by checking the record.
*Rule:* Before any defect is filed against an agent, the filer runs the check that would confirm it against the mirror. If the check clears the agent, the near-miss is filed against the filer. That's the adjudicator being audited by the same rule as the operator — which is the only reason the ledger is credible.

---

## 8. Revised definition of done

§5's file list, plus:

```
results/<run>/MEASUREMENTS/<check>.txt   regenerated by CI, diff-clean vs committed
results/<run>/fixture_hashes.json        content hashes, zero duplicates, counts by sort -u
results/<run>/scope_check.json           every fixture in_scope() == True
results/<run>/holdout_structural.json    every row runnable, no content revealed
results/<run>/invocations.log            one line per case, ≥ fixture count
results/<run>/attribution.json           nonce → profile → commit, no gaps
results/<run>/refusals.json              CORRECT-REFUSAL entries, with denominators
```

**Order of implementation:** 4f (git authors) → 7i (nonces) → 7a/7d (measurement + hashes) → 7f (scope) → 7e (invocation log) → 7g (holdout validator). The first two are an hour and remove the attribution class entirely. The rest are a day. None of it is research.
