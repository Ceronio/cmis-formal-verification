# CMIS Phase 2 / CP74 — independent twelve-point spherical Ramsey obstruction

**Standalone checkpoint · 28 October 2026 · Family 172 · Review only**

## Original formal target

**OAI.GrahamSpherical.full_main** from OpenAI Mathematics, source commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`.

The exact claim includes: (i) 12 distinct points, (ii) unit sphere, (iii) for each positive ambient dimension a 50-color avoiding map for this literal witness, and (iv) not Euclidean Ramsey. No weaker substitution is allowed.

## CP74 independently checked mathematics

- Exact polynomial derivation of the three weighted moment identities from three rotated coordinate squares.
- Algebraic rotation/derivation identities and strict parameter bounds; source-dependent real derivation construction explicitly distinguished from finite rational tests.
- Reconstruction of the copy-invariant weighted energy identity, then independently checked floor-modulo-50 obstruction.
- A proposed conventional **16-color strengthening** derived from the same universal energy identity; no original selected theorem or independent human/Lean certification is claimed for this sharpening.
- Negative controls for t=0, missing energy hypothesis, false assumption that rational t proves transcendence, incorrect assumption that numerical samples construct real-global colorings.

## Reproducible files

- `math_audit.py`: standard-library exact Z[t] moment equations, rational witness samples and exact floor arithmetic.
- `test_cp74.py`: 40 separate adversarial mathematical tests.
- `SOURCE_PINS.json`: 25 immutable original source objects, exact comparator names and allowed axioms.
- `verify_pinned_sources.py`: recomputes source Git blob hashes and verifies original theorem/solution interfaces.
- `INDEPENDENT_MATHEMATICAL_NOTE.md`: mathematical derivations, limitations, proof dependencies and 16-color conjecture-review scope.
- GitHub Actions workflows: independent bounded research and **separate exact Lean/Comparator** theorem admission.

## Trust and release

Successful Python calculations are not proof of the original universal theorem. Positive selected-theorem credit is permitted only if `OAI.GrahamSpherical.full_main` passes its separate original Comparator and Lean kernel run and both original receipts pass an independent integrity audit. This is one of seven Family172 comparator statements; full-family and external certification remain deferred.

Artifacts should be preserved in the CP74 downloadable ZIP independently of GitHub Actions retention. `main`, other PRs, CBI, TBC, Mac archives, and canonical records must remain unmodified.

**Stop after CP74. Do not begin CP75 before the user reviews CP74.**
