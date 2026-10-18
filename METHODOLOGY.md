# CMIS Verification Methodology and Trust Model

## Purpose

CMIS is a provenance-controlled verification programme. It independently reproduces and checks pinned public mathematical formalizations; it does not claim authorship of the underlying theorems merely because a verification run succeeds.

## Evidence sequence

1. **Pin the source** - repository, commit, configuration, challenge statement and solution object.
2. **Reproduce in a clean runner** - fixed Ubuntu image, Lean toolchain and dependency graph.
3. **Check the statement contract** - Comparator compares the selected challenge and solution statement.
4. **Control assumptions** - the post-check records the observed axioms and compares them with the permitted set.
5. **Replay through Lean's kernel** - successful acceptance is required for a formal PASS.
6. **Preserve a receipt** - versions, hashes, logs, status and manifests are retained as a workflow artifact.
7. **Apply scope discipline** - theorem-level success upgrades a family only when the verified targets cover the complete recorded claim.

## Pinned verifier identity

| Component | Pin |
|---|---|
| OpenAI Mathematics | `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` |
| Lean | `4.34.1` |
| Mathlib | `d13f23b723b8a846827a245b89c10fc7d3f11612` |
| Comparator | `d03acab154d269c06e60e4de7e4cc85deebff94b` |
| lean4export | `076e8e57707e813375e8f9da8bf989799ace9680` |
| Landrun | `ec104f6edc1e14d7fec6d31146f1ec6f9c192c5a` |
| Permitted axioms | `propext`, `Quot.sound`, `Classical.choice` |

## Formal PASS

A target receives `PASS_SELECTED_THEOREM` only when:

- the pinned target objects match their expected identities;
- Comparator accepts the configured statement;
- the solution export is accepted by Lean's default kernel;
- the observed axioms are within the permitted set; and
- the workflow creates a complete evidence receipt.

## Family-level validation

A family is validated only when the successful formal targets cover the complete recorded mathematical scope. A narrower supporting result may pass formally while the wider family remains not validated.

## Evidence classes

- **Family-validating:** contributes to complete coverage of a family.
- **Supporting only:** true selected theorem, but narrower than the family claim.
- **Partial family coverage:** covers some advertised subclaims, with others outside the target set.
- **Complete, not validated:** review is resolved by an evidence gap, scope mismatch or absent formal target.
- **Execution hold:** no mathematical verdict was reached because the environment, build or time gate stopped first.

## What CMIS does not claim

A formal theorem receipt does not by itself establish:

- authorship or novelty of the underlying mathematics;
- validation of a broader paper title;
- empirical performance of software;
- validation of a real-world application;
- CBI production readiness; or
- correctness outside the pinned source, theorem and dependency contract.

## Reproduction

Each family workflow is available under `.github/workflows/`. Run it from the GitHub **Actions** tab with `execution_mode=full`. The workflow is fail-closed and uploads a receipt whether it succeeds or stops at a controlled gate.
