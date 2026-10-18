# Contributing to CMIS Formal Verification

Thank you for helping improve the accuracy, reproducibility and scope discipline of this project.

## Useful contribution types

### 1. Independent reproduction

Rerun a completed workflow from a clean GitHub-hosted runner and report:

- the workflow and run URL;
- the exact selected theorem declaration;
- the final workflow status;
- the downloaded artifact digest;
- the receipt-manifest result;
- the observed axioms; and
- any discrepancy from the published register.

Use the **Reproduction report** issue template.

### 2. Scope review

Challenge or refine the relationship between a verified theorem and its wider family claim. A useful scope review identifies:

- the exact family claim;
- the exact selected formal theorem;
- the missing, stronger or differently quantified statement;
- a pinned public source supporting the correction; and
- the proposed family disposition.

Use the **Scope review** issue template.

### 3. Verification request

Propose a public mathematical theorem or family for CMIS review. Include an immutable source reference, theorem statement, formalization location if available, and why the target is suitable for reproducible verification.

Use the **Verification request** issue template.

### 4. Harness and documentation improvements

Pull requests may improve:

- workflow reproducibility;
- source and dependency pinning;
- receipt portability;
- hash verification;
- failure classification;
- documentation clarity; or
- machine-readable registers.

A change must not silently broaden a theorem's scope or upgrade a family without evidence.

## Evidence rules

1. Preserve the original mathematical question.
2. Pin public source objects and dependency identities.
3. Distinguish theorem-level PASS from whole-family validation.
4. Preserve failed, cancelled and timed-out runs.
5. Do not treat successful compilation as proof acceptance.
6. Do not treat a permitted-axiom list as an observed-axiom report.
7. Do not claim novelty or authorship of externally sourced mathematics.
8. State limitations explicitly.

## Pull-request expectations

A pull request should include:

- a concise purpose statement;
- the exact files and claims affected;
- evidence or tests supporting the change;
- any changed counts in the public register;
- confirmation that private information is absent; and
- a note on whether the change affects a frozen release or only the living register.

## Public-data boundary

Do not submit private CMIS, CBI, TBC, Gmail, personal, customer, investor, credential or commercial material. All evidence in this repository must be suitable for permanent public disclosure.

## Conduct

Be precise, constructive and evidence-led. Technical disagreement is welcome; personal attacks, fabricated results and deliberate scope inflation are not.
