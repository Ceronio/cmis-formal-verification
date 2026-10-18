# CMIS Verification Methodology and Trust Model

## Purpose

CMIS is a provenance-controlled verification programme. It independently reproduces and checks pinned public mathematical formalizations; it does not claim authorship of the underlying theorems merely because a verification run succeeds.

## Evidence sequence

1. **Pin the source** — repository, commit, configuration, challenge statement and solution object.
2. **Reproduce in a clean runner** — “fixed Ubuntu image, Lean toolchain and dependency graph.
3. **Check the statement contract** — Comparator compares the selected challenge and solution statement.
4. **Control assumptions** — the post-check records the observed axioms and compares them with the permitted set.
5. **Replay through Lean’s kernel** — successful acceptance is required for a formal PASS.
6. **Preserve a receipt** — versions, hashes, logs, status and manifests are retained as an immutable workflow artifact.
7. **Apply scope discipline** — theorem-level success upgrades a family only when the verified targets cover the complete recorded claim.

## Pinned verifier identity

| Component | Pin |
|---|---|
| OpenAI Mathematics | `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` |
| Lean |  4.34.1` |
| Mathlib | `d13f23b723b8a846827a245b89c10fc7d3f11612` |
| Comparator | `d03acab154d269c06e60e4de7e4cc85deebff94b` |
| lean4export | `076e8e57707e813375e8f9da8bf989799ace9680` |
| Landrun |...efailed...