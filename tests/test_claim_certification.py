"""Negative-control tests: historical GitHub success must never imply proof certification."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_claim_certification import (  # noqa: E402
    AuditError,
    require_release_certification,
    verify_contract,
)

LEGACY_PATH = ROOT / "verification-register.json"


class ClaimCertificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_legacy = LEGACY_PATH.read_bytes()
        cls.legacy = json.loads(cls.raw_legacy)
        cls.claims = json.loads((ROOT / "certification/claim-evidence-register.json").read_text())
        cls.runs = json.loads((ROOT / "certification/github-run-inventory.json").read_text())

    def copies(self):
        return copy.deepcopy(self.claims), copy.deepcopy(self.legacy), copy.deepcopy(self.runs)

    def verify(self, claims=None, legacy=None, runs=None):
        return verify_contract(
            claims if claims is not None else self.claims,
            legacy if legacy is not None else self.legacy,
            runs if runs is not None else self.runs,
            self.raw_legacy,
        )

    def test_exact_historical_claims_audit_but_certify_none(self):
        r = self.verify()
        self.assertEqual(r["historical_declarations"], 42)
        self.assertEqual(r["historical_theorem_runs"], 26)
        self.assertEqual(r["historical_github_runs"], 70)
        self.assertEqual(r["newly_certified_claims"], 0)

    def test_release_gate_is_always_closed_without_trusted_proof_replay(self):
        with self.assertRaisesRegex(AuditError, "RELEASE_HOLD"):
            require_release_certification(self.verify())

    def test_removal_of_one_claim_is_rejected(self):
        a, b, c = self.copies()
        a["claims"].pop()
        with self.assertRaises(AuditError):
            self.verify(a, b, c)

    def test_duplicate_claim_identifier_is_rejected(self):
        a, b, c = self.copies()
        a["claims"][1]["claim_id"] = a["claims"][0]["claim_id"]
        with self.assertRaises(AuditError):
            self.verify(a, b, c)

    def test_substitution_of_theorem_is_rejected(self):
        a, b, c = self.copies()
        a["claims"][0]["source_declaration"] = "OAI.NotTheRecordedTheorem"
        with self.assertRaises(AuditError):
            self.verify(a, b, c)

    def test_narrow_theorem_cannot_be_promoted_to_full_family(self):
        a, b, c = self.copies()
        narrowed = next(x for x in a["claims"] if x["family_id"] == "149")
        narrowed["historical_scope_label"] = "family-validating"
        with self.assertRaises(AuditError):
            self.verify(a, b, c)

    def test_forged_proof_certificate_is_rejected(self):
        a, b, c = self.copies()
        a["claims"][0]["certification"]["status"] = "CERTIFIED"
        a["claims"][0]["certification"]["certificate_id"] = "untrusted-self-assertion"
        with self.assertRaisesRegex(AuditError, "UNAUTHORIZED CERTIFICATION"):
            self.verify(a, b, c)

    def test_fake_independent_reproduction_is_rejected(self):
        a, b, c = self.copies()
        a["claims"][0]["independent_reproduction"]["status"] = "PASS"
        with self.assertRaises(AuditError):
            self.verify(a, b, c)

    def test_fake_human_scope_review_is_rejected(self):
        a, b, c = self.copies()
        a["claims"][0]["peer_scope_review"]["status"] = "APPROVED"
        with self.assertRaises(AuditError):
            self.verify(a, b, c)

    def test_false_nested_manifest_audit_is_rejected(self):
        a, b, c = self.copies()
        a["claims"][0]["evidence_integrity"]["nested_manifest_independently_checked"] = True
        with self.assertRaises(AuditError):
            self.verify(a, b, c)

    def test_rewritten_registry_blob_is_rejected(self):
        a, b, c = self.copies()
        a["source_registry"]["blob_sha"] = "0" * 40
        with self.assertRaises(AuditError):
            self.verify(a, b, c)

    def test_altered_artifact_digest_is_rejected(self):
        a, b, c = self.copies()
        a["claims"][0]["github_artifact_metadata"]["github_artifact_zip_sha256"] = "not-a-digest"
        with self.assertRaises(AuditError):
            self.verify(a, b, c)

    def test_run_conclusion_corruption_is_rejected(self):
        a, b, c = self.copies()
        run_id = a["claims"][0]["historical_main_registry_run_id"]
        run = next(x for x in c["entries"] if x["run_id"] == run_id)
        run["conclusion"] = "failure"
        with self.assertRaises(AuditError):
            self.verify(a, b, c)

    def test_historical_run_reclassification_is_rejected(self):
        a, b, c = self.copies()
        run_id = a["claims"][0]["historical_main_registry_run_id"]
        run = next(x for x in c["entries"] if x["run_id"] == run_id)
        run["historical_formal_claim_registered"] = False
        with self.assertRaises(AuditError):
            self.verify(a, b, c)

    def test_feature_branch_or_engineering_run_cannot_claim_certification(self):
        a, b, c = self.copies()
        unregistered = next(x for x in c["entries"] if not x["historical_formal_claim_registered"])
        unregistered["certification_status"] = "CERTIFIED"
        with self.assertRaises(AuditError):
            self.verify(a, b, c)

    def test_wrong_openai_source_pin_is_rejected(self):
        a, b, c = self.copies()
        a["source_openai_commit"] = "0" * 40
        with self.assertRaises(AuditError):
            self.verify(a, b, c)


if __name__ == "__main__":
    unittest.main()
