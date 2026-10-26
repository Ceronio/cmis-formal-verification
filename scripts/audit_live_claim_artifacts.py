#!/usr/bin/env python3
"""Verify live GitHub run/artifact metadata for legacy theorem declarations.

This checks GitHub-hosted *metadata*, NOT proof contents or mathematical scope.
It fails closed on missing, expired or changed artifacts and outputs ZERO theorem
certification credit. Requires read-only GitHub Actions access via GITHUB_TOKEN.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = "Ceronio/cmis-formal-verification"
API = "https://api.github.com/repos/" + REPO
TOKEN = os.environ.get("GITHUB_TOKEN", "")


class LiveAuditError(ValueError):
    pass


def fetch_json(path: str) -> dict:
    if not TOKEN:
        raise LiveAuditError("GITHUB_TOKEN missing (read-only Actions permission required)")
    url = API + path
    if not path.startswith("/actions/runs/"):
        raise LiveAuditError("Unexpected endpoint")
    last_error: Exception | None = None
    for attempt in range(3):
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": "Bearer " + TOKEN,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "cmis-claim-provenance-audit",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                if response.status != 200:
                    raise LiveAuditError("Unexpected GitHub HTTP status")
                return json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                break
            time.sleep(1 + attempt)
    raise LiveAuditError(f"GitHub metadata fetch failed: {path}: {last_error}")


def validate_run(run_id: int, claims: list[dict]) -> dict:
    run = fetch_json(f"/actions/runs/{run_id}")
    if run.get("id") != run_id or run.get("status") != "completed" or run.get("conclusion") != "success":
        raise LiveAuditError(f"Run {run_id} not successfully completed")
    if run.get("head_branch") != "main":
        raise LiveAuditError(f"Run {run_id} not on the recorded historical main branch")
    for claim in claims:
        if claim["primary_github_run"]["head_sha"] != run.get("head_sha"):
            raise LiveAuditError(f"Run {run_id} source commit mismatch for {claim['claim_id']}")
    listing = fetch_json(f"/actions/runs/{run_id}/artifacts?per_page=100")
    artifacts = listing.get("artifacts", [])
    if not isinstance(artifacts, list) or len(artifacts) != listing.get("total_count"):
        raise LiveAuditError(f"Run {run_id} artifact result is incomplete")
    artifact_index = {a.get("id"): a for a in artifacts}
    for claim in claims:
        expected = claim["github_artifact_metadata"]
        artifact = artifact_index.get(expected["artifact_id"])
        if artifact is None:
            raise LiveAuditError(f"Artifact {expected['artifact_id']} missing for {claim['claim_id']}")
        if artifact.get("expired") is not False:
            raise LiveAuditError(f"Artifact expired or expiry unknown for {claim['claim_id']}")
        if artifact.get("digest") != expected["github_artifact_zip_sha256"]:
            raise LiveAuditError(f"Artifact SHA-256 metadata differs for {claim['claim_id']}")
        if artifact.get("workflow_run", {}).get("id") not in (None, run_id):
            raise LiveAuditError(f"Artifact owner run differs for {claim['claim_id']}")
    return {"run_id": run_id, "claims_checked": len(claims)}


def main() -> int:
    try:
        document = json.loads(Path("certification/claim-evidence-register.json").read_text())
        claims = document["claims"]
        grouped: dict[int, list[dict]] = {}
        for claim in claims:
            if claim["certification"]["status"] != "UNCERTIFIED":
                raise LiveAuditError("Unexpected mathematical certification promotion")
            run_id = claim["primary_github_run"]["run_id"]
            grouped.setdefault(run_id, []).append(claim)
        if len(claims) != 42 or len(grouped) != 26:
            raise LiveAuditError("Historical claim inventory count is incomplete")
        checks = []
        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {pool.submit(validate_run, run_id, group): run_id for run_id, group in grouped.items()}
            for future in as_completed(futures):
                checks.append(future.result())
        if sum(x["claims_checked"] for x in checks) != 42:
            raise LiveAuditError("Incomplete artifact-to-claim mapping")
        result = {
            "result": "LIVE_GITHUB_ARTIFACT_METADATA_PASS_NO_PROOF_CERTIFICATION",
            "historical_claim_metadata_checked": 42,
            "historical_successful_runs_checked": 26,
            "expired_or_missing_artifacts": 0,
            "mathematically_certified_claims": 0,
            "limitations": [
                "Did not independently download and validate full receipt ZIP contents",
                "Did not independently replay Lean or Comparator proof",
                "Did not independently review equivalence with published manuscript claims",
                "Artifact metadata hashes do not replace proof verification",
            ],
        }
        print(json.dumps(result, indent=2))
        return 0
    except (LiveAuditError, OSError, KeyError, ValueError, urllib.error.URLError) as exc:
        print("LIVE ARTIFACT AUDIT HOLD: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
