# CMIS mathematical claim certification policy — review candidate

**Status:** REVIEW ONLY. No mathematical claim is newly certified by this branch.
**Scope:** Current public repository \`Ceronio/cmis-formal-verification\`, 26 October 2026.
**Canonical source:** Historical public register on main, pinned to Git blob \`77a3906c00926b78f395382ca4823af1ca5ff19f\`.
**Data protection:** No changes to private CMIS, CBI, TBC, local Mac archives, or underlying public mathematical source objects.

## The governing distinction

GitHub Actions success is an execution outcome, not mathematical truth.

A selected formal theorem can be genuinely proven inside Lean while a larger manuscript headline remains uncovered. A source-only capture, typecheck, axiom inspection, static audit, dependency build or green release gate is not a positive proof of an unproved theorem.

Every positive mathematical claim must be traceable to a specific verified formal statement. A mathematical **family** may only be called fully certified when all claimed statements within its declared complete scope have their own valid proof chains and independent scope review.

## Historical records preserved, not promoted

The public main register reports 42 successful selected declarations / 26 distinct runs / 18 historically validated families, and nine completed unvalidated family reviews. These historical statuses remain untouched on main. The new claim-level index carries them as **reported formal passes**, never as new independent certification.

A separate GitHub Actions inventory covers all 70 pre-audit workflow runs: 52 success, 13 failure and five cancelled. Forty-four of those 70 runs are not among the 26 used by the historical main declaration register. They must be classified claim-by-claim, especially feature-branch results. No engineering or snapshot run gains proof credit just because it is green.

The 42-entry index does **not** certify all 372 original manuscript families, nor CP71–CP80. Those remain separate review obligations.

## Formal claim-to-proof contract

A FULLY_CERTIFIED claim requires all of the following, with identity-bound evidence:

1. **Statement identity.** Complete Lean proposition pretty-print and cryptographic hash of the normalized, elaborated target; explicit human-readable mathematical proposition including every quantifier, hypothesis, inequality, dimension and endpoint.
2. **Source pins and rights.** Exact OpenAI mathematics commit, target/config/challenge/solution object identities, imported theory and executable checker/toolchain pins; source attribution without unauthorized authorship claims.
3. **Real proof admission.** Exact target challenge/solution Comparator agreement, permitted observed axioms, and successful Lean default-kernel acceptance of the selected proof (not merely a \`#check\` or \`#print axioms\` command).
4. **Receipt completeness.** Raw proof logs, exit codes, selected target identifiers, full artifact bytes, outer and nested checksum manifests, downloaded artifact SHA-256 and durable retention, not just a GitHub summary or archive metadata.
5. **Independent replay.** Separate clean proof execution from pinned sources, independently verifiable run URL and new proof receipt, with no weakened statements, new axioms, \`sorry\`, \`admit\` or trust-boundary changes.
6. **Claim-scope review.** An independently accountable reviewer verifies equivalence between formal statement and actual public mathematical claim; the review cites proof artifacts and signs off every exception. It must not infer stronger claims from narrower proofs.
7. **Integration control.** Independent review of source, transitive assumptions and canonical project-gate applicability. Applications and commercial outcomes require their own empirical assessment and may not be auto-certified by a pure theorem.

\`FULLY_CERTIFIED\` is a **joint** state; a missing required gate means \`UNCERTIFIED\` or a narrower explicitly named result. Failed or timed-out proofs are HOLD, not mathematical disproof.

## Critical fail-closed implementation strategy

The current new verifier, \`scripts/verify_claim_certification.py\`, is intentionally limited to **record integrity**, with 16 adversarial negative controls. It cross-checks the exact 42 original declaration rows, source/main blob identity, all 70 historical GitHub runs, source-scope classifications, artifact ZIP digest *metadata* and zero false certification flags.

The audit may print \`CLAIM_CONTRACT_AUDIT_PASS_ZERO_NEW_CERTIFICATION\`. That means historical records have not been silently lost or upgraded. **It does not mean the mathematical claims are certified.**

The separate \`mathematical_release_gate\` job intentionally fails with \`RELEASE_HOLD\`. It cannot produce a green certification release until an independently reviewed verifier actually replays proofs, verifies receipts and scope attestations, and also closes coverage gaps. The current script *rejects any attempt to set a claim status to CERTIFIED through JSON alone*. Do not remove this restriction merely to obtain a green badge.

This branch does **not** rewrite the original public register, reassign historical proof credit, merge into main, publish a release, or create new canonical data.

## Known GitHub scope gaps

- Family 159: unresolved Lean resource and proof-admission hold; build progress is not theorem proof.
- Families 161, 162, 165, 167, 168, 169 and 170: follow-on feature-branch workflows need claim-specific comparison and archived receipts before promoting anything to the public claim registry.
- Family 171: CP67 source audit, CP68 typecheck, CP69 axiom/interface audit and CP70 release gate succeeded. CP70 explicitly records \`positive_target_proved=false\` and zero full-theorem credit.
- Family 172: seven comparator statements identified in source review, but independent formal admission and complete coverage not established by these GitHub audit files.
- Family 173: bounded finite checks do not prove the universal second-neighborhood statement.
- CP71–CP80: local research candidate artifacts and math examples do not replace source-faithful, published proof admissions.

## Evidence expiry and retention

GitHub Actions artifacts in this repository are temporary (often 30 days). Verified examples:
- Family 005 historical proof receipt: expected expiry 2026-11-16.
- Family 160 historical proof receipt: expected expiry 2026-11-17.
- Family 171 CP70 release gate: expected expiry 2026-11-25.

The historical claim index stores *artifact metadata* only; it does not pretend receipt ZIP contents have been copied to an immutable mirror. All original receipt bytes, internal manifests and hashes require separately authorized archival destinations. No automatic copying to CBI, TBC, the Mac or public release is authorized by this PR.

## Next acceptance gates (not claimed complete)

1. Independently download and validate all 42 indexed theorem declaration receipts, including shared-run artifacts.
2. Examine exact Lean statements and approved transitive axioms; map each to the paper's claimed theorem and document uncovered statements.
3. Replay each exact claim independently and preserve new immutable receipts with an audited retention plan.
4. Reconcile the 44 unregistered historical workflow runs and other source/branch changes as bounded claim records or explicit no-theorem-credit engineering events.
5. Resolve status for remaining mathematics families and CP71–CP80 without inventing missing proofs.
6. Implement a *separately reviewed positive-certification runner* that cryptographically validates proof and review attestations before allowing any positive CERTIFIED status.
7. Establish enforceable repository rulesets/required checks only under a separate scoped authorization and technical eligibility review. The existence of the new workflow alone is not branch protection.

**Release verdict in this PR:** \`RELEASE_HOLD / 0 newly independently certified mathematical claims\`.
