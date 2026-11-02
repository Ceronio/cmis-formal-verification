# CMIS CP05 public bounded evidence

This branch contains a separate exact-rational finite certificate checker and synthetic tests. It does not contain historical archive bytes, private records, original CP05 source or undocumented public releases.

Local historical CP05 archive SHA-256 (not uploaded): `e6c35b0f460e15d71e9cc5f2cf20b310b9cb2ad4221d803e11bb9e821405e4da`.
All source and regression tests in the historical archive remain in the cumulative in-chat checkpoint review package.

The GitHub CI verifies sharp 1-bit exact probability optima, Farkas infeasibility, tiny rational probabilities to 10^-150, and deliberately invalid certificate controls. The CI **does not** execute the complete original CP05 2,882-check suite or authenticate all original dependencies. Therefore a green CI result is G18 supporting bounded evidence, *not* full source-to-claim acceptance; further full-checkpoint GitHub replay needs a separate vetted public-safe source packaging/reconciliation plan.

No merging into main, PR, public release, or private upload is approved in this change.
