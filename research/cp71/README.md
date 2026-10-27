# CMIS Phase 2 CP71 — full standalone bounded research review

**Family 172: exact Euclidean Ramsey definitions and tensor-field substrate**

Public/source evidence only. Preserve historic CP70/CP71 files; this new standalone review does not overwrite any canonical archive or `main` branch.

## Mathematical deliverables

1. `INDEPENDENT_MATHEMATICAL_NOTE.md`: exact quantifier audit, complete conventional two-point theorem proof, dimension-one two-color obstruction, exact field-tensor certificate and deliberate false-tensor negative control.
2. `math_audit.py`: dependency-free exact rational and sparse-polynomial computation covering all small simplex colorings, geometric isometries, affine span rank and tensor conditions.
3. `test_cp71.py`: 19 adversarial mathematical tests.
4. `SOURCE_PINS.json`: six exact pinned publisher source objects (paper sections, theorem comparator, config, solution and scope).
5. `verify_pinned_sources.py`: read-only live public GitHub source acquisition, recomputed blob-identity verification, comparator scope checks, and source snapshots for the workflow receipt.

## Source and proof boundaries

- The `Ramsey a` property is `∀ r≥2, ∃ D≥1, ∀ c:ℝ^D→Fin r, ∃ monochromatic b congruent at original scale`.
- The full classification target is `OAI.EuclideanRamsey.classification` requiring s≥2, d≥1, injective a and full affine span. It states `Ramsey a ↔ FieldCriterion a`.
- The seven comparator results are separate targets. Only the main classification definition/interface is reviewed here; no family-level or formal proof credit is awarded.
- The author/source claims about deeper classification, equivalence, sufficiency and necessity remain in the publisher's work; no independent Lean kernel replay of the full theorem was undertaken by this CP71 workflow.

## GitHub Actions — full CP71 execution

`.github/workflows/cmis-family172-cp71-independent-review.yml` runs all 19 mathematical controls and the exact finite-audit script, fetches and authenticates six immutable public source objects, enforces the requested quantifier, tensor and config contract, and uploads immutable-ish SHA-256 documented receipts (GitHub artifacts themselves expire; durable evidence retention remains separately authorised).

Expected terminal marker: `PASS_CP71_BOUNDED_MATH_AND_PINNED_SOURCE` (the spelling is deliberate in the currently pinned workflow contract). This is a **research execution** marker and MUST NOT be interpreted as `PASS_SELECTED_THEOREM`.

## Quality/release gate

- Code, source, and generated receipts must pass in the real GitHub Actions run.
- Result metadata must retain `family_whole_scope_validated=false` and `additional_formal_credit=0`.
- Distinguish the GitHub run conclusion from the mathematical conclusion.
- A review-ready GitHub PR is allowed; do not merge to main or publish release without separate approval.
- CP72 and subsequent checkpoints are STOPPED until the user reviews the CP71 ZIP.

Source: https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/172.md
