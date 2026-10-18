# Reproducing a CMIS formal-verification result

This guide describes the simplest independent reproduction path using a fresh GitHub-hosted runner.

## Before you begin

Choose one completed target from [COMPLETED_VERIFICATIONS.md](COMPLETED_VERIFICATIONS.md). Confirm that the target is classified as:

- family-validating;
- supporting only; or
- partial family coverage.

That classification must be preserved in your report.

## Run the workflow

1. Open the repository's **Actions** tab.
2. Select the workflow matching the target family.
3. Choose **Run workflow**.
4. Use the `main` branch unless you are deliberately testing another pinned revision.
5. Leave `execution_mode` as `full`.
6. Start the workflow and wait for a terminal result.

The workflow is fail-closed. It uploads a receipt whether it passes or stops at a controlled gate.

## Expected successful result

A completed formal PASS should contain:

- `FINAL_STATUS.txt` with `PASS_SELECTED_THEOREM`;
- Comparator exit code `0`;
- the marker `Your solution is okay!`;
- a Lean default-kernel acceptance record;
- an observed-axiom report within the permitted set;
- exact source, configuration, challenge and solution identities; and
- `99_receipt_sha256.txt` covering the receipt files.

## Verify the receipt

On Linux or macOS, after extracting the artifact:

```bash
cd <extracted-receipt-directory>
sha256sum -c 99_receipt_sha256.txt
```

On macOS systems without GNU `sha256sum`, verify with:

```bash
while read -r expected path; do
  path="${path#\*}"
  path="${path#./}"
  actual=$(shasum -a 256 "$path" | awk '{print $1}')
  test "$actual" = "$expected" || exit 1
done < 99_receipt_sha256.txt
```

A receipt may also contain a nested admission archive. Preserve it and report whether its internal manifest verifies after extraction.

## Interpret controlled stops correctly

- `ENVIRONMENT_HOLD`: toolchain, dependency, cache or compatibility problem.
- `SECURITY_HOLD`: required protected execution conditions were unavailable.
- `COMPARATOR_HOLD`: Comparator did not accept the configured target or could not complete.
- `UNCLASSIFIED_HOLD`: unexpected failure requiring inspection.
- cancelled or timed-out run: execution hold, not a mathematical verdict.

Do not convert a build failure, cancellation or timeout into a theorem rejection.

## Report the result

Open a [reproduction report](https://github.com/Ceronio/cmis-formal-verification/issues/new?template=reproduction-report.yml) and include:

- workflow name and run URL;
- family and selected theorem;
- final status;
- artifact SHA-256;
- manifest result;
- observed axioms;
- runner image;
- any discrepancies; and
- whether your result changes the family-level disposition.

## Local reproduction

Local execution is possible, but the GitHub-hosted workflow is the reference route because it recreates the pinned environment and preserves a public execution record. A local result should record the operating system, CPU architecture, toolchain, exact commit and all modified files.
