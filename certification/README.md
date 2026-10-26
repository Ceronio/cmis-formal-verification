# CMIS claim-by-claim certification audit

**REVIEW BRANCH: ZERO NEW MATHEMATICAL CERTIFICATIONS.** This is a public-source evidence audit and a proposed fail-closed release policy. It does not certify all historical family claims, does not approve release and does not modify the original `main` verification register.

## Files

- [Claim register](claim-evidence-register.json) — exactly 42 historical Lean declarations, claim scopes, GitHub run/commit links, artifact IDs and artifact ZIP SHA-256 metadata; individual mathematical certification remains `UNCERTIFIED`.
- [Workflow inventory](github-run-inventory.json) — immutable snapshot of 70 GitHub Actions runs before this new branch's activity, including 26 runs referenced by the historical register and 44 other runs awaiting classification.
- [Mathematical certification standard](CLAIM_CERTIFICATION_POLICY.md) — formal proofs, exact statement hashes, legal/source pins, complete receipts, independent Lean replay, human mathematical scope review and retention.
- [Offline record audit](../scripts/verify_claim_certification.py) — checks claim and run crosswalk, exact original Git blob SHA, unsupported scope promotions and forged certifications.
- [Live receipt metadata audit](../scripts/audit_live_claim_artifacts.py) — read-only GitHub REST checks of all 26 historical runs and exact artifact metadata for all 42 declarations. **Does not download or inspect full receipt bytes.**
- [Adversarial tests](../tests/test_claim_certification.py) — 16 negative-control tests plus the positive no-credit baseline.
- [GitHub Actions check](../.github/workflows/cmis-claim-certification-audit.yml) — green provenance audit is NOT mathematical certification; certification-release gate intentionally reports HOLD until a genuine independently reviewed proof verifier is deployed.

## Run locally in a checkout

```bash
python3 -m unittest discover -s tests -p test_claim_certification.py -v
python3 scripts/verify_claim_certification.py --mode audit
# Read-only metadata queries, requires token with actions:read permission
GITHUB_TOKEN=YOUR_READ_ONLY_TOKEN python3 scripts/audit_live_claim_artifacts.py
# Must fail with RELEASE_HOLD (not an execution error):
python3 scripts/verify_claim_certification.py --mode release-gate
```

## Interpretation

| Result | What it means |
|---|---|
| `CLAIM_CONTRACT_AUDIT_PASS_ZERO_NEW_CERTIFICATION` | Registry is internally consistent and has not silently promoted claims |
| `LIVE_GITHUB_ARTIFACT_METADATA_PASS_NO_PROOF_CERTIFICATION` | Github currently reports pinned run and artifact identities; **receipt contents not authenticated** |
| `RELEASE_HOLD` | Required proof replay, independent scope review and broader family coverage not complete |
| A historical `PASS_SELECTED_THEOREM` | One exact selected statement was reportedly accepted by its original verification run; check its full proof receipt before stronger certification |
| Green CP70 | Family 171 typecheck, trust and release engineering checks passed, but the positive theorem was explicitly NOT proved |

Do not confuse the number of GitHub runs, proof declarations, families, conjectures, subclaims and independently reviewed mathematical certifications. They are different units.

## Release blocker

Actual positive certification requires separate approval and delivery of a trusted independent Lean/Comparator replay plus raw proof receipt and reviewer-attestation verification. This branch deliberately has no method to set a mathematical claim to `CERTIFIED` by editing JSON. Even if all 42 legacy statements were individually certified, the 44 additional historical runs and remaining corpus claims would still require reconciliation.

GitHub Action receipts can expire. Preservation into a durable evidence store requires separate explicit authorization of its destination. No automatic write to Mac, CBI, TBC, private archives, or public release occurs here.
