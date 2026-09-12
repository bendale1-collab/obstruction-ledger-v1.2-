# Telegram Delivery Format

## Rule

Deliver raw output files as MEDIA attachments (`MEDIA:/path/to/file.txt`). Do NOT embed run output inline in prose or wrap it in commentary. The user wants the raw file, not a summary of it.

If the file is short (< 500 chars, e.g., a single typed verdict), you may inline it in a code block. Otherwise, prefer the attachment.

**Never say:** "looks good," "all pass," "the run shows," "as you can see," "the results indicate" — the file is the output, the user reads it.

## Why

The user ("Br") operates the PROSECUTOR framework for all quantitative research. The output contract specifies exactly one typed verdict plus supporting data. Narrative wrapping is noise. The user copies the file, not the prose.

## Exceptions

- A one-line summary of the verdict (e.g., "K0: FAIL — 0.8276 vs 0.20") is acceptable as context before the file attachment.
- If the command produced no output (empty file), say so directly rather than attaching an empty file.
- If the run failed with an error, attach the error output.