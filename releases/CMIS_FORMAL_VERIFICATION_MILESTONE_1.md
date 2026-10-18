# CMIS Formal Verification Milestone 1

This release publishes the first curated CMIS verification register.

## Published evidence

- **42** selected Lean theorem declarations passed the pinned formal-verification process.
- **18** mathematical families are validated at their complete recorded pure-mathematical scope.
- **9** additional family reviews are complete with bounded non-validation dispositions.
- **27** family reviews are resolved in total.

## Trust boundary

Each formal PASS represents the exact selected statement only. CMIS does not claim authorship of the underlying mathematics. Source claims are attributed to the pinned public source repository; CMIS contributes independent execution, statement checking, kernel replay, axiom auditing, receipt integrity, scope classification and reproducibility.

## Excluded from completed totals

Family 159's reciprocal-sum target was cancelled at the workflow's 350-minute limit while the large Lean build was still running. No Comparator or Lean-kernel verdict was reached. It is preserved as an execution hold, not a mathematical failure.

## Release contents

- living completed-verification catalogue;
- machine-readable verification register;
- family-level validation and non-validation register;
- verification methodology and trust model;
- current execution-hold report;
- immutable dependency pins;
- citation metadata;
- SHA-256 manifest.

Future progress will update the living register on `main` and be snapshotted in later tagged releases.
