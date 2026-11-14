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

if __name__ == "__main__":
    unittest.main()
