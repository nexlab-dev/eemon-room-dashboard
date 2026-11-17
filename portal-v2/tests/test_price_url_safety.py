"""Regression tests for malformed seller/evidence URLs. No network required."""
import datetime as dt
import importlib.util
from pathlib import Path
import unittest

p = Path(__file__).resolve().parents[1] / "scripts" / "price_engine.py"
spec = importlib.util.spec_from_file_location("price_engine_safety", p)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

class URLSafetyTests(unittest.TestCase):
    def test_rejects_control_and_whitespace(self):
        for url in ("https://example.com/a b", "https://example.com/a\n", "https://example.com/a\t", "https://example.com/a\x7f"):
            with self.subTest(url=repr(url)), self.assertRaises(engine.ValidationError):
                engine.safe_url(url)

    def test_rejects_bad_port_and_ipv6(self):
        for url in ("https://example.com:abc/a", "https://example.com:8443/a", "https://[bad-ipv6/a"):
            with self.subTest(url=url), self.assertRaises(engine.ValidationError):
                engine.safe_url(url)

    def test_compare_excludes_bad_evidence_without_crashing(self):
        now = dt.datetime(2026, 11, 17, tzinfo=dt.timezone.utc)
        row = dict(product_key="sku-123", variant_key="sku-123", listing_key="listing-123",
            product_name="Fixture only", shop_name="Fixture shop", stock="available",
            verification="human_verified_official_page", verified_by="fixture",
            item_url="https://example.com/item", evidence_url="https://example.com:bad/evidence",
            price_jpy=1000, shipping_jpy=0, checked_at=now.isoformat(),
            currency="JPY", tax_included=True)
        result = engine.compare({"observations":[row]}, now=now)
        self.assertEqual(result["summary"], [])
        self.assertEqual(len(result["excluded"]), 1)

if __name__ == "__main__":
    unittest.main()
