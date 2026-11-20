"""Offline CLI regression tests. Run: python3 -m unittest discover -s portal-v2/tests -p 'test_affiliate_gate_cli.py' -v.

No network, accounts, external links, or publishing. REVIEW_READY is not approval.
"""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "affiliate_release_gate.py"
REQUIRED = (
    "owner_publish_approval", "asp_account_approved", "media_approved",
    "campaign_approved", "link_owner_verified",
    "advertising_disclosure_reviewed", "product_facts_verified"
)


class AffiliateGateCliTests(unittest.TestCase):
    def run_gate(self, payload):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / "approval.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(GATE), str(path)],
                capture_output=True, text=True, timeout=10, check=False
            )
            self.assertFalse(result.stderr, result.stderr)
            return result.returncode, json.loads(result.stdout)

    def test_empty_manifest_holds_with_nonzero_exit(self):
        code, result = self.run_gate({})
        self.assertNotEqual(code, 0)
        self.assertEqual(result["status"], "HOLD")
        self.assertTrue(result["errors"])

    def test_unverified_price_and_campaign_cannot_publish(self):
        payload = {key: True for key in REQUIRED}
        payload["campaign_approved"] = False
        payload["product_facts_verified"] = False
        payload["affiliate_url"] = "https://example.org/link"
        payload["evidence_refs"] = ["candidate-only"]
        code, result = self.run_gate(payload)
        self.assertNotEqual(code, 0)
        self.assertEqual(result["status"], "HOLD")
        self.assertTrue(any("campaign_approved" in e for e in result["errors"]))
        self.assertTrue(any("product_facts_verified" in e for e in result["errors"]))

    def test_review_ready_never_claims_publish_or_approval(self):
        payload = {key: True for key in REQUIRED}
        payload["affiliate_url"] = "https://example.org/link"
        payload["evidence_refs"] = ["owner-review-placeholder"]
        code, result = self.run_gate(payload)
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "REVIEW_READY")
        self.assertEqual(result["errors"], [])
        self.assertNotIn("PUBLISHED", result["status"])


if __name__ == "__main__":
    unittest.main()
