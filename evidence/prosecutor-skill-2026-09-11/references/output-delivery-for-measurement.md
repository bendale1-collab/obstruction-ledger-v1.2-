# Output Delivery for Measurement Work

**Core rule: Numbers must be visible in chat, not hidden in file paths.**

When delivering measurement results, verdict data, or numerical findings:

1. **Paste all critical numbers inline first** — in code blocks, tables, or structured format within the chat message
2. **Then attach the file path** — MEDIA: path as secondary reference

**Wrong pattern:**
```
"Report: /Users/.../r31-results.txt"
```
The user cannot verify invisible content inside a file they can only see referenced.

**Right pattern:**
```
Digest at 7d4aad7: 020bb559e6f712892dec0c91...
Digest at HEAD:    3d9c8dec14e62e78b7afefbb...

MEDIA:/Users/.../r31-results.txt
```

**Applies to:**
- Hashes, digests, SHAs (full 64/40 chars, never truncated in chat)
- Verdicts, gate results, thresholds
- Tables where every row carries decision logic
- Fixture counts, fixture coverage, control results
- Any measurement where the reader needs to verify the verdict rests on visible data

**Exception:** Intermediate scaffolding (logs, raw tool output, auxiliary data) can be file-only if the verdict itself is visible in chat.

---

**Session origin:** 2026-09-11, K1a fixtures and manifest integrity verification. User corrected twice: "The file path isn't the data" and "every number in that file is still invisible to me." The core principle: adversarial-falsification verdicts are only auditable when the numbers are front-and-center.
