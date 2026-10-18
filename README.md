# CMIS Formal Verification

[![CMIS formal verification](https://github.com/Ceronio/cmis-formal-verification/actions/workflows/family160-quantitative-van-der-waerden-formal-verification.yml/badge.svg)](https://github.com/Ceronio/cmis-formal-verification/actions)

A public, reproducible verification laboratory for pinned mathematical formalizations.

## Milestone 1 status

| Measure | Completed |
|---|---:|
| Formal theorem declarations passed | **42** |
| Families validated at recorded pure-mathematical scope | **18** |
| Complete family reviews without validation | **9** |
| Total resolved family reviews | **27** |
| Current execution holds | **1** |

The underlying mathematical sources are public and remain attributed to their source repository and authors. CMIS does **not** claim authorship of a theorem merely because it reproduced and verified its formal proof.

## Living registers

- [Completed theorem and family register](COMPLETED_VERIFICATIONS.md)
- [Completed scope and non-validation audits](SCOPE_AUDITS.md)
- [Verification methodology and trust model](METHODOLOGY.md)
- [Current execution holds](EXECUTION_HOLDS.md)
- [Machine-readable register](verification-register.json)
- [Immutable component pins](PINS.md)
- [Citation information](CITATION.cff)

## What a green formal run means

A `PASS_SELECTED_THEOREM` result requires:

1. pinned source, configuration, challenge and solution identities;
2. Comparator acceptance of the configured statement;
3. an observed-axiom report within the permitted set; and
4. Lean default-kernel acceptance.

A green theorem run does not automatically validate a wider paper title, operational application, performance claim or CBI deployment.

## Pinned evidence contract

- OpenAI Mathematics: `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`
- Lean: `4.34.1`
- Mathlib: `d13f23b723b8a846827a245b89c10fc7d3f11612`
- Comparator: `d03acab154d269c06e60e4de7e4cc85deebff94b`
- lean4export: `076e8e57707e813375e8f9da8bf989799ace9680`
- Landrun: `ec104f6edc1e14d7fec6d31146f1ec6f9c192c5a`
- Permitted axioms: `propext`, `Quot.sound`, `Classical.choice`

## Reproduction

Open the **Actions** tab, select a family workflow, choose **Run workflow**, and leave `execution_mode` as `full`. Each workflow uploads a hashed receipt whether it passes or stops at a controlled gate.

## Public/private boundary

Safe here: public mathematical sources, generic verification scripts, dependency pins, workflow logs and public receipts.

Never place here: private CMIS/CBI/TBC material, Gmail, personal information, credentials, customer records, investor material, commercial strategy or private project archives.
