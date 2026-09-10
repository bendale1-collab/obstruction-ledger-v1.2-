# Ledger Entry — PUBLICATION-DELEGATION-FAILED
# Type: PUBLICATION-DELEGATION-FAILED
# Filed: 2026-09-10
# Gist: 6b6d2d42651ffe5b63ab6a54a603ca05

Publication of freeze hashes was attempted twice via an external-family
agent with gist OAuth scope:

  1. v1.3 hash (2026-09-06) — agent had gist:write scope configured.
     Gist save returned 403 (credentials invalid or expired). Nothing
     written. Asserted-only hash recorded in ledger/0000-genesis.yaml.
     The attempt is documented there as "agent publication failed on
     credentials."

  2. v1.4/v1.5 hash (2026-09-08) — agent retried with same credentials.
     Gist save returned 403 again. Nothing written in that session.
     v1.5 was later published by the founder manually as a fresh session.

  3. v1.6 hash (2026-09-10) — same credentials, same 403 on the agent.
     The founder published manually as a new session.

Independently confirmed: credential separation holds by construction.
The agent's PAT lacks gist scope and cannot write to the gist. The
founder's PAT (different session, different credential file) has the
gist scope. No single credential can both compute results and publish
hashes. This is the intended control — it is functioning as designed.

The 403 is the control, not a defect.

Consequence: every hash in this chain was published by the founder
in a separate session. No hash was self-published by the agent that
produced the results. This property should be recorded as a design
feature, not a workaround.