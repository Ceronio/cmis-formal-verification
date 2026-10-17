# CMIS Family 132 — Free GitHub Actions formal verification

This small public execution harness checks one explicitly selected formal theorem from the pinned OpenAI Mathematics repository:

`OAI.Paper320.quantitative_separation`

It contains **no private CMIS, CBI, TBC, Gmail or personal data**. It fetches only public source repositories and returns a hashed execution receipt.

## Why this repository is public

Standard GitHub-hosted Actions runners are free for public repositories. The workflow uses a fresh Ubuntu virtual machine and uploads the result as a workflow artifact.

## Run it

1. Open this repository's **Actions** tab.
2. Select **CMIS Family 132 Formal Verification**.
3. Choose **Run workflow**.
4. Leave `execution_mode` as `full`.
5. Download the `cmis-family132-formal-receipt-...` artifact after completion.

The workflow is fail-closed. A green run means either:

- `ADMISSION_PASS` when admission-only mode was chosen; or
- `PASS_SELECTED_THEOREM` after Comparator success and the post-check axiom report.

Any environment, security, build or Comparator problem fails the workflow and still uploads the diagnostic receipt.

## Pinned evidence contract

- OpenAI Mathematics commit: `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`
- Lean: `4.34.1`
- Official Lean Linux asset SHA-256: `47bf4bbd78f70c2e9670598ab7124d92b6efb7330ff33e5fbb4030f6fd72e4e4`
- Mathlib: `d13f23b723b8a846827a245b89c10fc7d3f11612`
- Comparator: `d03acab154d269c06e60e4de7e4cc85deebff94b`
- lean4export: `076e8e57707e813375e8f9da8bf989799ace9680`
- Landrun: `ec104f6edc1e14d7fec6d31146f1ec6f9c192c5a`
- Selected theorem: `OAI.Paper320.quantitative_separation`
- Permitted axioms: `propext`, `Quot.sound`, `Classical.choice`

## Scope

A successful run verifies the theorem selected by the Comparator configuration. It does not automatically verify the separately tracked unbounded or fixed-power endpoint claims, and it does not validate an operational CMIS/CBI application.

## Public/private boundary

Safe here: public mathematical sources, generic verification scripts, public dependency pins, workflow logs and formal receipts.

Never place here: CBI or TBC content, Gmail, personal information, commercial strategy, credentials, private AIREM/BWIS material, or internal project archives.
