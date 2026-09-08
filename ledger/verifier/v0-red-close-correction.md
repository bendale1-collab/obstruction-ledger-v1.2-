event: RED-CLOSE-CORRECTION
type: CORRECTION
order: OL-v1.5-P1-RED-CLOSE
date: 2026-09-08
authority: Founder-requested consequence re-evaluation

detail: |
  The RED-CLOSE report claimed the λ=1 eigenvalue is "structurally absent
  from the odd-basis operator" because "dΩ/dξ is EVEN and the odd basis
  cannot span it." This was PARTIALLY WRONG and requires correction.

  CORRECT statements:
  - dΩ/dξ (the translation mode, Xu Eq 3.7) IS EVEN (verified: f(-ξ)+f(ξ)=0).
  - The engine's odd-basis construction does NOT produce λ=1.

  INCORRECT statement:
  - "λ=1 is structurally absent from the odd-basis operator."
  
  Xu Theorem 2 (2607.19762): "Its full point spectrum over ℂ, on the odd
  realization, is exactly {0,1}." Therefore λ=1 DOES exist in the odd
  basis. The odd-basis eigenfunction at λ=1 is the ODD time-shift mode,
  distinct from the EVEN translation mode φ=dΩ/dξ (Eq 3.7). The engine
  failing to produce it is an ENGINE CONSTRUCTION problem, not a
  structural limitation.

  CONSEQUENCE:
  The RED-CLOSE rescope premise ("preserve the even half of the domain
  so that {1} survives") was predicated on the wrong claim and is hereby
  WITHDRAWN. The problem is not that the odd-basis restriction structurally
  excludes λ=1, but that the engine construction fails to realize it.
  The correct fix direction is: fix the odd-basis operator construction
  (or use a constrained approach per Options A/B/C in the rescope
  proposal) rather than abandoning the odd-basis restriction entirely.

  UNCHANGED findings:
  - F-4 strip reduction (~2×, not eliminated) remains correct
  - P0 golden was correct for its own criterion
  - Engine-RED verdict stands
  - The residual 20 strip modes characterization stands
  - The {0,1} finding in naive (0.375 not 1.0, finite-domain effect) stands

  Correction filed as ledger entry.