# CMIS Formal Verification

[![Latest release](https://img.shields.io/github/v/release/Ceronio/cmis-formal-verification?display_name=tag)](https://github.com/Ceronio/cmis-formal-verification/releases/latest)
[![CMIS formal verification](https://github.com/Ceronio/cmis-formal-verification/actions/workflows/family160-quantitative-van-der-waerden-formal-verification.yml/badge.svg)](https://github.com/Ceronio/cmis-formal-verification/actions)

A public, reproducible verification laboratory for pinned mathematical formalizations.

> **Milestone 1 is published.** The repository contains a living verification register and a frozen `v0.1.0` release. Independent reproduction, technical review and scope challenges are welcome.

## Milestone 1 status

| Measure | Completed |
|---|---:|
| Formal theorem declarations passed | **42** |
| Families validated at recorded pure-mathematical scope | **18** |
| Complete family reviews without validation | **9** |
| Total resolved family reviews | **27** |
| Current execution holds | **1** |

The underlying mathematical sources are public and remain attributed to their source repository and authors. CMIS does **not** claim authorship of a theorem merely because it reproduced and verified its formal proof.

**AI disclosure:** CMIS is an AI-assisted research and engineering project. Paul Ceronio sets the objectives, approves the scope and publication decisions, and remains accountable for the public claims. AI-generated text, code or analysis is not accepted as proof; formal results must pass the pinned evidence gates described below. See [AI assistance and human responsibility](AI_ASSISTANCE.md).

## Start here

- [Milestone 1 release](https://github.com/Ceronio/cmis-formal-verification/releases/tag/v0.1.0)
- [Completed theorem and family register](COMPLETED_VERIFICATIONS.md)
- [Completed scope and non-validation audits](SCOPE_AUDITS.md)
- [Verification methodology and trust model](METHODOLOGY.md)
- [AI assistance and human responsibility](AI_ASSISTANCE.md)
- [Reproduction guide](REPRODUCING.md)
- [Contribution guide](CONTRIBUTING.md)
- [Current execution holds](EXECUTION_HOLDS.md)
- [Machine-readable register](verification-register.json)
- [Immutable component pins](PINS.md)
- [Citation information](CITATION.cff)

## Follow one theorem check

A newcomer can begin with family **160**, the quantitative van der Waerden result:

1. open its [successful workflow run](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129756059);
2. inspect the selected theorem and pinned source identities;
3. review the Comparator, axiom and Lean-kernel gates; and
4. compare the theorem-level result with the family-level entry in [COMPLETED_VERIFICATIONS.md](COMPLETED_VERIFICATIONS.md).

This illustrates the core CMIS rule: a formal PASS applies to the exact selected statement, not automatically to a broader paper title, application or performance claim.

## Independent reproduction requested

An outside contributor normally cannot manually dispatch a workflow in this repository without write access. The documented public route is therefore:

1. fork this repository to your own GitHub account;
2. enable GitHub Actions in the fork;
3. follow [REPRODUCING.md](REPRODUCING.md);
4. run one workflow in the fork with `execution_mode=full`;
5. download and inspect its receipt; and
6. submit a [reproduction report](https://github.com/Ceronio/cmis-formal-verification/issues/new?template=reproduction-report.yml).

You may also submit a [scope-review challenge](https://github.com/Ceronio/cmis-formal-verification/issues/new?template=scope-review.yml) or [propose another theorem family](https://github.com/Ceronio/cmis-formal-verification/issues/new?template=verification-request.yml).

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

Fork the repository, enable Actions in the fork, select a family workflow, choose **Run workflow**, and leave `execution_mode` as `full`. Each workflow uploads a hashed receipt whether it passes or stops at a controlled gate.

## Recognition and review

Stars, watches and forks are welcome when they reflect genuine use or interest. More important than a star is a reproducible rerun, a technically specific issue, a scope correction or an independently reviewed receipt.

## Public/private boundary

Safe here: public mathematical sources, generic verification scripts, dependency pins, workflow logs and public receipts.

Never place here: private CMIS/CBI/TBC material, Gmail, personal information, credentials, customer records, investor material, commercial strategy or private project archives.
