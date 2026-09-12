# Output-contract discipline

**When to reference:** Comparing models on classification tasks — F1 batteries, reader qualification, or any label-extraction work.

## Always apply, in order

1. **Payload parity first** — payload hash per item per model. Byte-identical inputs or PIPELINE DEFECT.
2. **Sufficient max_tokens** — models that produce reasoning before labels need 100+ tokens. 30 tokens truncates preamble before label (GPT-4o, Claude, Gemini all do this).
3. **Permissive extraction** — use `rfind` (last occurrence) of each label string in the raw completion. Extract even through preamble, JSON, reasoning blocks.
4. **Structured output where supported** — JSON schema or response_format with an enum field. Supported by OpenAI, Anthropic, Google via OpenRouter.
5. **Failure classification** — every failure gets one of:
   - `SAFETY_REFUSAL`: explicit decline (medical guardrail, etc.)
   - `PREAMBLE`: correct label present but wrapped in prose
   - `REASONING_FIRST`: chain-of-thought then label
   - `SCHEMA_MISMATCH`: JSON when bare expected, or inverse
   - `WRONG_LABEL`: clean single label, semantically wrong — **only real capability finding**
   - `EMPTY/ERROR`: API-level failure (retry, log)

## The decisive number

**WRONG_LABEL** count per model. Report raw completions for every failure — the string, not a summary. A model that always outputs preamble but includes the correct label is a format problem, not a capability failure.

## Hermes-specific: API key handling

The `***` key placeholder gets replaced by the actual API key across ALL Hermes tools (write_file, terminal heredocs, inline Python -c). This replacement happens BEFORE any interpreter sees the code, so it breaks:
- Python f-strings containing `{key}` — the replacement injects the key value as literal characters
- String concatenation with `'Bearer ' + key` — same issue
- Bash heredocs with `$KEY` — the `***` is replaced before bash expands the variable

**Only reliable pattern:**
1. Save key to temp file: `echo -n "$KEY" > /tmp/openrouter_key.txt`
2. Read from file at Python runtime: `key = open('/tmp/openrouter_key.txt').read().strip()`
3. Build auth header as a separate variable: `hdr = 'Bearer ' + key`
4. Pass to subprocess: `'-H', 'Authorization: ' + hdr`

Never embed the key in the same string literal that appears in a tool call. Avoid f-strings with `{key}` in any code sent through Hermes tools.

## Source

Session 2026-07-24, `OUTPUT CONTRACT REPAIR PROMPT.md`: 5 frontier models (Claude Opus 5, Claude Sonnet 5, GPT-4o, Gemini 3.5 Flash, Llama 4 Maverick) initially labelled "fail F1" but the majority were format issues. After permissive extraction and proper max_tokens, GPT-4o improved from 3/6 to 4/6. Amendment 06 formalizes the rule.