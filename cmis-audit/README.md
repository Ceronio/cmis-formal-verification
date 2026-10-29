# CP09/CP10 bounded source audit

CP09 and CP10 remain **HOLD**. This additive audit preserves every existing
repository file and formal-verification requirement.

Read [the reconciliation report](reports/RECONCILIATION_REPORT.txt),
[mathematical findings](reports/MATHEMATICAL_VERIFICATION_FINDINGS.json), and
[all 16 acceptance gates](reports/UNIVERSAL_ACCEPTANCE_GATES.csv).
[Source references](SOURCE_REFERENCES.json) identify the exact upstream paths,
commit, Git blobs and SHA-256 values. The 11 public source files are unchanged.

## Reproduction

From the repository root, using Python 3.12 and the standard library:

```sh
python3 cmis-audit/scripts/reconstruct_cp09.py
python3 cmis-audit/scripts/reconstruct_cp10.py
```

These write generated results under `cmis-audit/results/`. Reference bounded
outputs are retained under `cmis-audit/evidence/`. Tests include all published
pivots, digit carry boundaries and invalid denominator-shortcut controls.
They do not build the full growing source matrix or prove the complete theorem.

The workflow `cmis-cp09-cp10-bounded-audit.yml` has **only workflow_dispatch**.
It has not been executed as part of publication. Dispatch requires separate
owner authorisation. Its only success label is
`PASS_BOUNDED_COMPUTATIONS_ONLY`; no formal or family credit follows.

## Integrity and trust

`PAYLOAD_SHA256.json` is the authoritative SHA-256 manifest for all added files
except itself. Paths are relative to the repository root; the Git tree binds the
manifest itself. Source Git blobs are independently recorded in
`evidence/pinned_sources/SOURCE_HASH_AUDIT.json`.

Existing Comparator, kernel, observed-axiom, source pinning, preservation and
independent-review gates remain unchanged. Licensing alone may be deferred.
Family 159 and the unreadable original CP62 archive remain unresolved.
No private inventories, local paths, credentials or large archives are included.
No existing register or frozen release is changed.

This work is substantially AI-assisted. It claims no authorship or novelty for
the externally sourced mathematics and no newly certified checkpoint.
