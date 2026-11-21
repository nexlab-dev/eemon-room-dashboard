"""Regression test: the same seller URL must not be ranked twice under another SKU.
Run: python3 -m unittest discover -s tests -p 'test_price_duplicate_url.py' -v
"""
import datetime as dt
import importlib.util
from pathlib import Path
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "scripts" / "price_engine.py"
spec = importlib.util.spec_from_file_location("eemon_price_engine", ENGINE)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


class DuplicateURLTests(unittest.TestCase):
    def test_same_url_different_sku_excluded(self):
        now = dt.datetime(2026, 11, 15, tzinfo=dt.timezone.utc)
        def observation(key, listing):
            return {
                "product_key": key, "variant_key": key, "listing_key": listing,
                "product_name": "QA-only fixture", "shop_name": "QA shop",
                "stock": "available", "verification": "human_verified_official_page",
                "verified_by": "fixture-not-real-verification",
                "item_url": "https://example.com/item/123",
                "evidence_url": "https://example.com/item/123",
                "price_jpy": 1000, "shipping_jpy": 0,
                "checked_at": now.isoformat(), "currency": "JPY", "tax_included": True,
            }
        result = engine.compare({"observations": [
            observation("sku-A", "listing-A"),
            observation("sku-B", "listing-B"),
        ]}, now=now)
        self.assertEqual(sum(row["offer_count"] for row in result["summary"]), 1)
        self.assertEqual(len(result["excluded"]), 1)
        self.assertIn("重複", result["excluded"][0]["reason"])

    def test_equivalent_https_url_not_double_counted(self):
        now = dt.datetime(2026, 11, 15, tzinfo=dt.timezone.utc)
        def record(key, url):
            return {
                "product_key": key, "variant_key": key, "listing_key": "listing-" + key,
                "product_name": "Fixture", "shop_name": "Fixture seller",
                "stock": "available", "verification": "human_verified_official_page",
                "verified_by": "fixture-only", "item_url": url,
                "evidence_url": "https://example.com/evidence",
                "price_jpy": 1200, "shipping_jpy": 0, "checked_at": now.isoformat(),
                "currency": "JPY", "tax_included": True,
            }
        result = engine.compare({"observations": [
            record("sku-A", "https://EXAMPLE.com:443/item?a=1"),
            record("sku-B", "https://example.com/item?a=1"),
            record("sku-C", "https://example.com/item?a=2"),
        ]}, now=now)
        self.assertEqual(sum(x["offer_count"] for x in result["summary"]), 2)
        self.assertEqual(len(result["excluded"]), 1)
        self.assertIn("重複", result["excluded"][0]["reason"])

    def test_nonstandard_port_excluded(self):
        now = dt.datetime(2026, 11, 15, tzinfo=dt.timezone.utc)
        row = {
            "product_key": "sku-A", "variant_key": "sku-A", "listing_key": "listing-A",
            "product_name": "Fixture", "shop_name": "Fixture seller",
            "stock": "available", "verification": "human_verified_official_page",
            "verified_by": "fixture-only", "item_url": "https://example.com:8443/item",
            "evidence_url": "https://example.com/evidence", "price_jpy": 1000,
            "shipping_jpy": 0, "checked_at": now.isoformat(), "currency": "JPY",
            "tax_included": True,
        }
        result = engine.compare({"observations": [row]}, now=now)
        self.assertEqual(result["summary"], [])
        self.assertIn("ポート", result["excluded"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
