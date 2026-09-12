# Execution workflow preferences

Emerged from the MVI program (clinical trial outcome classification, three-judge panel, 2026-07-24).

## Delivery format (Telegram)

Br's Telegram client does not render Markdown tables or code blocks reliably.
Default to writing report output to a file and delivering via `MEDIA:/path`
attachment rather than inline formatting. Write findings to `.txt` files in
the repo's `work/` directory; attach with `MEDIA:/absolute/path/to/file.txt`.
Inline tables in chat are a failed delivery, not a fallback.

## Commit-and-report-SHA pattern

When producing gate outputs, run reports, or measurement results during
a pre-registered run: **commit the output file, report the SHA, push
to origin.** The user reads outputs from the git mirror, not from
inline chat. The workflow is:

1. Write output to `work/<filename>.txt`
2. `git add` + `git commit` with descriptive message
3. Report the commit SHA (short form is fine)
4. `git push origin main`
5. Reply with SHA and brief summary (counts, pass/fail) — NOT the file contents

The user will read the committed file from the mirror. Do not paste
file contents into chat unless the user explicitly asks. Gate outputs
are artifacts, not chat messages.

**Violation example (2026-09-11):** User instruction: "Do not paste
tables in your reply; commit files and report SHAs. Outputs are read
from the mirror." The agent had been pasting G4 tables inline instead
of committing and reporting SHA.

## Output-block format

When the user provides a prompt with a typed `OUTPUT` section at the bottom (the ` ``` ` delimited block), that block IS the output contract for that run. Fill computed numbers into it. Do not add narrative commentary above or below the block unless the prompt explicitly asks for deeper analysis. The user will ask for decomposition if they want it.

The block typically contains:
- PART headers with computed numbers
- BAND: typed verdict + CI + state
- SEARCH WIDTH: classification/API call counts

Do not add section headers the prompt did not specify. Fill `[ ]` / `[Y/N]` placeholders. If a value cannot be computed, put `UNMEASURED(reason)` in the slot.

## Pre-flight before multi-call passes

Before any pipeline that makes 10+ API calls (recollection, reclassification, cross-model audit), run a pre-flight on 3 diverse items × 1-2 judges. Verify:

1. **Schema**: `response_format: json_object` produces valid JSON with expected keys. Check per model — different models may format differently.
2. **Span/offset resolution**: If using span_text or offsets, confirm they resolve deterministically from source strings. Models cannot count bytes precisely — span_text is more reliable than character offsets.
3. **No truncation**: Confirm max_tokens is set high enough that extended thinking before the label does not truncate the payload. A model that "refuses" may just be hitting the token ceiling.
4. **Systematic failures**: Check for PARSE_ERR / format failures across models. A model that PARSE_FAILs on 3 pre-flight items will fail on all 60 — fix the extraction or exclude the model before the full pass.

Fix failures and re-test before the full pass. A pre-flight failure on the full pass wastes 20+ minutes of API calls.

## Typed-arithmetic discipline

**Arithmetic is shown from logged inputs (H1 rule — no arithmetic in prose).** Every computed number must have its derivation shown:

```
ARITHMETIC:
  corrected = (disagreements - unsupported) / items
            = (18 - 12) / 52 = 6/52 = 11.5%
```

Do not assert a number without showing the arithmetic that produced it. If the user corrects arithmetic, the correction is accepted without argument — post-hoc drift is forbidden.

## Against-interest reporting

When an instrument convicts its own lineage (same model family, same provider), the finding is strengthened, not weakened. Explicitly report the pattern when it occurs. State "testimony against interest" in the output.

This is the strongest evidence available — the instrument acts against its own bias. Do not treat shared lineage as automatic weakness; the direction of the finding is what determines the discount.

## The recollection-first principle

Before building an inspection/verification layer, verify that the primary collection layer produces the data the inspection layer needs. A collection defect (narrative paraphrase instead of structured citations, free text instead of JSON) cannot be fixed by a better inspector — it must be fixed at the collection level.

In the MVI run: narrative paraphrase satisfied the judge prompt → inspection consumed narratives → B1 code had nothing to match. Fix: enforce structured citations at judge level (span_text, not free-form citation). Do not build inspection logic for data that was never formally collected.