# Telegram Delivery Format

## Rule

Deliver raw output files as MEDIA attachments (`MEDIA:/path/to/file.txt`). Do NOT embed run output inline in prose or wrap it in commentary. The user wants the raw file, not a summary of it.

**Confirmed 2026-09-10 (explicit correction):** Br stated directly — "Txt file attachments preferred... the tables don't render." This applies beyond literal grep/pickaxe tables: ANY multi-item structured answer (numbered items, bullet lists, inline markdown headers, ad-hoc "Item 1 / Item 2" prose blocks) should be written to a file under `work/` and delivered via `MEDIA:` rather than typed inline in the chat reply, even when no markdown table is involved. The old "< 500 chars, inline in a code block is OK" exception is now the exception, not the default — reach for it only for a single short typed verdict line, not for anything with multiple sections/items. When in doubt, write the file.

**Reaffirmed later same session:** when the user says "Give me the txt file" / "give me the attachment" for a report that was previously delivered as inline chat prose (even a well-formatted one with markdown tables), the correct response is to write that exact content to a `work/*.txt` file and re-deliver as `MEDIA:` — not to ask what they want in it, not to re-summarize. Re-litigating whether a table "rendered fine" this time is itself the violation; the standing preference is file-first, always, for this user, no exceptions pending further correction.

**Never say:** "looks good," "all pass," "the run shows," "as you can see," "the results indicate" — the file is the output, the user reads it.

## Why

The user ("Br") operates the PROSECUTOR framework for all quantitative research. The output contract specifies exactly one typed verdict plus supporting data. Narrative wrapping is noise. The user copies the file, not the prose.

## Unsupported file types

Telegram rejects certain file extensions outright with `Unsupported document type '.ext'`. Known rejections: `.gz` (including `.tar.gz`). Supported: `.txt`, `.md`, `.pdf`, `.zip`, `.csv`, `.json`, `.yaml`, `.py`, `.sh`, `.xml`, `.docx`, `.xlsx`, `.pptx`. When the user needs to deliver a tarball, use `.zip` or deliver the raw path for manual retrieval. Never retry a rejected extension — it will fail identically every time.

## MEDIA attachment failures

If a `MEDIA:/path` attachment is not arriving after 1–2 attempts, DO NOT keep re-sending the same file. Instead:

1. Split the file into chunks of ~2500–3000 chars and send each as a separate `MEDIA:` (e.g. `gist-id-audit-pt1.txt`, `gist-id-audit-pt2.txt`).
2. If splitting also fails, deliver the file path as plain text in the message (e.g. `/Users/brukendale/Desktop/gist-id-audit-2026-09-10.txt`) and let the user fetch it themselves.
3. Do NOT paste the file content inline as code blocks unless asked — Telegram strips content in transit.

## Exceptions

- A one-line summary of the verdict (e.g., "K0: FAIL — 0.8276 vs 0.20") is acceptable as context before the file attachment.
- If the command produced no output (empty file), say so directly rather than attaching an empty file.
- If the run failed with an error, attach the error output.

## Exact reply-template override (rank above the MEDIA-attachment default)

If the task itself specifies the literal reply format (e.g. "Reply with exactly two
lines: FILE: <path> LINES: <n>" / "print the file path and its line count. Nothing
else."), that literal template wins — do NOT also send a `MEDIA:` attachment, do
NOT add a verdict summary line, do NOT add commentary. The default "attach as
MEDIA + one-line verdict" habit in this file is the fallback for open-ended
delivery, not a floor that must always be met. When the user gives an exact
reply contract, the contract IS the deliverable; anything extra is a violation
of "nothing else," not generosity.