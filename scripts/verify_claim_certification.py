#!/usr/bin/env python3
"""Fail-closed CMIS historical claim and GitHub-run consistency audit.

This script checks record integrity. It CANNOT prove mathematics and MUST NOT
issue a certificate based on a green workflow, an artifact SHA or self-reported
metadata. The separate release gate remains closed until a trusted,
independent proof-replay and human scope-attestation route exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


class AuditError(ValueError):
    """A required claim-evidence invariant is missing or inconsistent."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def verify_contract(
    claim_register: dict,
    legacy_register: dict,
    run_inventory: dict,
    legacy_bytes: bytes | None = None,
) -> dict:
    """Check exact legacy coverage, provenance shape, scope and zero false credits."""
    require(claim_register.get("schema_version") == "1.0.0", "Unsupported claim schema")
    require(run_inventory.get("schema_version") == "1.0.0", "Unsupported run schema")
    require(
        claim_register.get("repository") == run_inventory.get("repository")
        == "Ceronio/cmis-formal-verification",
        "Repository identity mismatch",
    )
    source = claim_register.get("source_registry") or {}
    require(source.get("path") == "verification-register.json", "Wrong legacy source path")
    require(source.get("branch") == "main", "Legacy evidence must refer to main")
    require(
        source.get("blob_sha") == run_inventory.get("legacy_main_registry_sha"),
        "Inconsistent historical register Git blob",
    )
    if legacy_bytes is not None:
        require(
            source.get("blob_sha") == git_blob_sha(legacy_bytes),
            "Historical register bytes do not match pinned Git blob SHA",
        )
    require(
        source.get("base_commit") == run_inventory.get("base_main_commit"),
        "Different historical branch baselines",
    )
    require(
        claim_register.get("source_openai_commit")
        == "fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb",
        "OpenAI source pin was altered",
    )
    legacy_rows = legacy_register.get("formal_theorem_declarations")
    require(isinstance(legacy_rows, list) and len(legacy_rows) == 42, "Expected 42 legacy declarations")
    claims = claim_register.get("claims")
    require(isinstance(claims, list) and len(claims) == len(legacy_rows), "Legacy claim loss or duplicate count")
    require(claim_register.get("total_legacy_claims") == len(legacy_rows), "Claim count does not match data")
    require(claim_register.get("uncertified_by_new_standard") is True, "Global certification warning removed")
    run_entries = run_inventory.get("entries")
    require(isinstance(run_entries, list) and len(run_entries) == 70, "Run inventory is incomplete")
    require(run_inventory.get("count") == len(run_entries), "Run count disagrees with entries")
    run_map = {run.get("run_id"): run for run in run_entries}
    require(len(run_map) == len(run_entries), "Duplicated GitHub workflow run")
    legacy_ids = {row[4] for row in legacy_rows}
    require(len(legacy_ids) == 26, "Unexpected legacy proof run coverage")
    for run in run_entries:
        run_id = run.get("run_id")
        require(isinstance(run_id, int) and run_id > 0, "Invalid run ID")
        require(
            run.get("run_url") == f"https://github.com/Ceronio/cmis-formal-verification/actions/runs/{run_id}",
            f"Non-canonical run URL: {run_id}",
        )
        require(bool(re.fullmatch(r"[a-f0-9]{40}", str(run.get("commit_sha", "")))), f"Run {run_id} missing commit pin")
        require(
            run.get("historical_formal_claim_registered") is (run_id in legacy_ids),
            f"Run {run_id} historical declaration mapping is incorrect",
        )
        require(
            run.get("certification_status") == "NOT_CERTIFIED_BY_THIS_INVENTORY",
            f"Run {run_id} unlawfully promotes workflow status",
        )
    by_id = {claim.get("claim_id"): claim for claim in claims}
    require(len(by_id) == len(claims), "Duplicate claim identifier")
    families = set()
    for row in legacy_rows:
        ordinal, family_id, declaration, scope, run_id = row
        claim_id = f"CMIS-LEGACY-{ordinal:03d}"
        require(claim_id in by_id, f"Missing historical claim {claim_id}")
        claim = by_id[claim_id]
        require(claim.get("family_id") == family_id, f"Family mismatch in {claim_id}")
        require(claim.get("source_declaration") == declaration, f"Declaration mismatch in {claim_id}")
        require(claim.get("historical_scope_label") == scope, f"Scope mismatch in {claim_id}")
        require(claim.get("historical_main_registry_run_id") == run_id, f"Run mismatch in {claim_id}")
        require(scope in ("family-validating", "supporting-only", "partial-family"), f"Unknown scope {claim_id}")
        run = run_map.get(run_id)
        require(run is not None, f"Evidence run not found for {claim_id}")
        require(run.get("branch") == "main" and run.get("status") == "completed" and run.get("conclusion") == "success", f"Historical run not successful for {claim_id}")
        p = claim.get("primary_github_run") or {}
        require(p.get("run_id") == run_id and p.get("url") == run["run_url"], f"Evidence URL mismatch in {claim_id}")
        require(p.get("head_sha") == run["commit_sha"], f"Commit mismatch in {claim_id}")
        require(p.get("reported_conclusion") == "success", f"False historical success in {claim_id}")
        require(p.get("terminal_selected_theorem_pass_reported") is True, f"Selected-theorem record missing in {claim_id}")
        art = claim.get("github_artifact_metadata") or {}
        require(isinstance(art.get("artifact_id"), int) and art["artifact_id"] > 0, f"Missing artifact id in {claim_id}")
        require(art.get("metadata_source") == "GITHUB_ACTIONS_ARTIFACT_METADATA", f"Unrecognized artifact metadata provenance in {claim_id}")
        require(bool(re.fullmatch(r"sha256:[a-f0-9]{64}", str(art.get("github_artifact_zip_sha256", "")))), f"Malformed artifact SHA256 in {claim_id}")
        require(art.get("archive_contents_independently_verified") is False, f"Unsupported claim of artifact inspection in {claim_id}")
        require(claim.get("historical_proof_status") == "REPORTED_FORMAL_PASS_NOT_INDEPENDENTLY_REPRODUCED", f"Unapproved historical proof promotion in {claim_id}")
        statement = claim.get("exact_claim_statement") or {}
        require(
            statement.get("independent_statement_equivalence_review") == "NOT_DONE",
            f"Unreviewed statement has been promoted in {claim_id}",
        )
        provenance = claim.get("evidence_integrity") or {}
        require(provenance.get("nested_manifest_independently_checked") is False, f"Unsupported manifest-checked assertion in {claim_id}")
        require(provenance.get("long_term_immutable_mirror_verified") is False, f"Unsupported permanence claim in {claim_id}")
        reproduce = claim.get("independent_reproduction") or {}
        require(reproduce.get("status") == "NOT_DONE", f"Unattested independent reproduction in {claim_id}")
        peer = claim.get("peer_scope_review") or {}
        require(peer.get("status") == "NOT_DONE", f"Unattested independent scope review in {claim_id}")
        certification = claim.get("certification") or {}
        # A static JSON entry, even with plausible URLs, can never certify a theorem.
        # Positive certification requires an additional independently reviewed, trusted
        # end-to-end proof runner and attestation validator (NOT present in this PR).
        require(
            certification.get("status") == "UNCERTIFIED"
            and certification.get("certificate_id") is None,
            f"UNAUTHORIZED CERTIFICATION in {claim_id}",
        )
        families.add(family_id)
    require(set(by_id) == {f"CMIS-LEGACY-{row[0]:03d}" for row in legacy_rows}, "Extra or renamed claim entries")
    return {
        "result": "CLAIM_CONTRACT_AUDIT_PASS_ZERO_NEW_CERTIFICATION",
        "historical_declarations": len(claims),
        "historical_families": len(families),
        "historical_theorem_runs": len(legacy_ids),
        "historical_github_runs": len(run_entries),
        "unreconciled_github_runs": len(run_entries) - len(legacy_ids),
        "newly_certified_claims": 0,
    }


def require_release_certification(result: dict) -> None:
    """Always HOLD until an independent positive proof attestation gate exists."""
    raise AuditError(
        "RELEASE_HOLD: static metadata-only audit cannot certify 42 claims, "
        "reconcile the other historical runs or cover all 372 families. "
        "A separately reviewed pinned kernel/Comparator replay, artifact-byte "
        "verification, statement equivalence and independent human sign-off "
        "are mandatory. Do not infer theorem certification from this green audit."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", default="certification/claim-evidence-register.json")
    parser.add_argument("--runs", default="certification/github-run-inventory.json")
    parser.add_argument("--legacy", default="verification-register.json")
    parser.add_argument("--mode", choices=["audit", "release-gate"], default="audit")
    args = parser.parse_args()
    try:
        raw_legacy = Path(args.legacy).read_bytes()
        legacy = json.loads(raw_legacy)
        claims = json.loads(Path(args.claims).read_text(encoding="utf-8"))
        runs = json.loads(Path(args.runs).read_text(encoding="utf-8"))
        result = verify_contract(claims, legacy, runs, raw_legacy)
        print(json.dumps(result, indent=2))
        if args.mode == "release-gate":
            require_release_certification(result)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"CMIS AUDIT FAILURE: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
