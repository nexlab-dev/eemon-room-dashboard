"""Run: python3 -m unittest discover -s portal-v2/tests -p test_affiliate_release_gate.py"""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("affiliate_release_gate", ROOT / "scripts" / "affiliate_release_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class AffiliateReleaseGateTests(unittest.TestCase):
    def valid(self):
        data = {key: True for key in gate.REQUIRED}
        data.update(affiliate_url="https://example.org/approved-link", evidence_refs=["private-owner-review"])
        return data

    def test_empty_manifest_blocks(self):
        self.assertTrue(gate.check({}))

    def test_all_gates_allow_review_only(self):
        self.assertEqual(gate.check(self.valid()), [])

    def test_unapproved_campaign_blocks(self):
        data = self.valid()
        data["campaign_approved"] = False
        self.assertTrue(gate.check(data))

    def test_non_https_or_credentials_block(self):
        for url in ("http://example.org/a", "https://u:p@example.org/a", "https://localhost/a"):
            with self.subTest(url=url):
                data = self.valid()
                data["affiliate_url"] = url
                self.assertTrue(gate.check(data))

    def test_private_or_nonstandard_affiliate_hosts_block(self):
        for url in (
            "https://127.0.0.2/link",
            "https://192.168.1.1/link",
            "https://[::1]/link",
            "https://intranet.local/link",
            "https://shop.localhost/link",
            "https://example.org:8443/link",
            "https://example.org:bad/link",
        ):
            with self.subTest(url=url):
                data = self.valid()
                data["affiliate_url"] = url
                self.assertTrue(gate.check(data))

    def test_standard_https_port_allowed_for_review_only(self):
        data = self.valid()
        data["affiliate_url"] = "https://example.org:443/approved-link"
        self.assertEqual(gate.check(data), [])

    def test_whitespace_and_control_character_urls_block(self):
        for url in ("https://example.org/has space", "https://example.org/has\\nnewline",
                    "https://example.org/has\\ttab", "https://example.org/has\\x7fdel"):
            with self.subTest(url=repr(url)):
                data = self.valid()
                data["affiliate_url"] = url
                self.assertTrue(gate.check(data))

    def test_missing_evidence_blocks(self):
        data = self.valid()
        data["evidence_refs"] = []
        self.assertTrue(gate.check(data))

if __name__ == "__main__":
    unittest.main()
