# Standing rules — addendum

Rules earned after the handoff bundle was frozen. `handoff/` is hash-pinned by
`handoff/MANIFEST.sha256` and is not edited; these are written here instead and
are meant to read alongside `operational-standards.md` §7.

### 7m. An append names its section, not just its file.

*Failure:* appending a defect to the end of `ledger/defects.md` would have
filed it under the trailing "Correct behaviour" heading, inverting its meaning.
Filed as APPEND-TARGETS-SECTION-NOT-FILE.

*Rule:* every append states the section it targets, and lands in that section
even when that is not the end of the file. The last section of a ledger is not
always the section an entry belongs to.
