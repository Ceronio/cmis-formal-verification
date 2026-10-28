# CMIS Phase 2 — CP75 standalone original nine-point theorem

**Family 172 · 28 October 2026 · Original OpenAI Mathematics source pin `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`.**

Research branch and review only. `main` and older research branches are not changed; nothing is merged, copied to CBI/TBC or published as an external mathematical certification.

## Exact original theorem

`OAI.EuclideanRamsey.NineStatement.nine_circle_configuration` states that nine **algebraically independent** real parameters produce nine distinct points on the unit circle whose configuration is **not** Euclidean Ramsey.

Unlike CP74 it does not assert a 50-color explicit construction. Unlike a rational example it cannot be modeled by nine rational or decimal parameter samples. Its proof depends on the field-tensor classification established in CP71.

## Standalone evidence

- `INDEPENDENT_MATHEMATICAL_NOTE.md`: independent proof reconstruction of field tensor obstruction and 9×9 determinant, with exact hypotheses, false-inference controls and source attribution.
- `nine_point_math.py`: exact stdlib Fraction implementation for grid determinant 64, denominator-cleared determinant 8^6=262144, denominator product 4096, singular diagonal specialization and rational counterexample.
- `test_cp75.py`: **50 adversarial tests** guarding algebraic independence, source scope, determinant arithmetic, row and column perturbations, and false family credit.
- `SOURCE_PINS.json`: 20 original source objects and allowed-axiom contract.
- `verify_pinned_sources.py`: retrieves pinned original GitHub raw content, recalculates every Git blob SHA-1 and retains bytes in the source evidence receipt.
- `.github/workflows/cmis-family172-cp75-independent-review.yml`: real GitHub bounded source and mathematical test workflow.
- `.github/workflows/cmis-family172-cp75-full-comparator.yml`: independent pinned Lean 4.34.1 / Mathlib / Comparator **selected theorem** workflow.

## Two distinct verification classes

**Bounded mathematics and source identity:** GitHub research workflow must pass all 50 tests, authenticate 20 exact publisher source objects, and archive code and data with verified SHA-256 manifests. It must explicitly report zero new formal theorem credit by itself.

**Original selected theorem proof:** the exact-target protected workflow must complete, return `PASS_SELECTED_THEOREM`, record Comparator exit 0, Lean default-kernel acceptance, permitted observed axioms, pinned source identities and verifiable original receipts. No passing source scan may substitute for this step.

Independent external certification remains deferred. Original GitHub artifacts expire under Actions retention; preserve the downloaded receipts in the final CP75 ZIP.

**STOP AFTER CP75 for user review. CP76 must not start automatically.**
