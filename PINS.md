# Immutable pins

The workflow intentionally pins source commits, verifier commits and GitHub Actions by full SHA. Changes require a new reviewed checkpoint.

| Component | Pin |
|---|---|
| actions/checkout | `11d5960a326750d5838078e36cf38b85af677262` |
| actions/setup-go | `40f1582b2485089dde7abd97c1529aa768e1baff` |
| actions/upload-artifact | `ea165f8d65b6e75b540449e92b4886f43607fa02` |
| OpenAI Mathematics | `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` |
| Lean release | `4.34.1` |
| Comparator | `d03acab154d269c06e60e4de7e4cc85deebff94b` |
| lean4export | `076e8e57707e813375e8f9da8bf989799ace9680` |
| Landrun | `ec104f6edc1e14d7fec6d31146f1ec6f9c192c5a` |
| Mathlib | `d13f23b723b8a846827a245b89c10fc7d3f11612` |

The project historically pins Lean and its mathematical dependencies. Comparator, lean4export and Landrun are additionally pinned by this CMIS execution harness so that each run has an auditable verifier identity.
