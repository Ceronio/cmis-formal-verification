# Family 171 full-target specification

This directory records the exact positive target for the hypercube Ramsey manuscript:

`∃ C : ℝ, 0 < C ∧ ∀ n : ℕ, (ramseyNumber (cube n) : ℝ) ≤ C * (2 : ℝ) ^ n`.

## Current formal status

- The target type is specified using the pinned source definitions.
- Definitional equivalences map it to the manuscript statement and to the negated hypothesis used by the existing source theorem `counterexample_sequence_of_not_linear`.
- The positive target is **not proved** here.
- No `sorry`, `admit`, new `axiom`, private project data, or claim of mathematical acceptance is permitted.
- Successful source audit or Lean typechecking is specification evidence only and adds zero proof credit.

## Source contract

- Source repository: `openai/math`
- Source commit: `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`
- Source module: `OAI.Combinatorics.Ramsey.Hypercube`
- Lean version: `4.34.1`

AI-assisted specification and engineering; not independent human peer review.
