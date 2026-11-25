"""Run: python3 -m unittest discover -s portal-v2/tests -p test_revenue_scorecard.py -v"""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("revenue_scorecard", ROOT / "scripts" / "revenue_scorecard.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class RevenueScorecardTests(unittest.TestCase):
    def sample(self):
        return {m: {k: None for k in mod.FIELDS} for m in mod.MEDIA}

    def test_unmeasured_is_not_zero(self):
        data = self.sample()
        data["room"]["referral_clicks"] = 8
        data["room"]["orders"] = 0
        report = mod.summarize(data)
        self.assertIsNone(report["total"]["referral_clicks"])
        self.assertEqual(report["media"]["room"]["referral_clicks"], 8)
        self.assertEqual(report["status"], "UNMEASURED_INCLUDED")

    def test_all_measured_can_total(self):
        data = {m: {k: 0 for k in mod.FIELDS} for m in mod.MEDIA}
        data["asp_site"]["referral_clicks"] = 7
        data["room"]["referral_clicks"] = 8
        self.assertEqual(mod.summarize(data)["total"]["referral_clicks"], 15)

    def test_rejects_invalid_or_private_like_fields(self):
        data = self.sample()
        data["asp_site"]["bank_account"] = "never-store"
        with self.assertRaises(ValueError):
            mod.summarize(data)

    def test_rejects_negative_bool_float(self):
        for bad in (-1, True, 1.2):
            with self.subTest(value=bad):
                data = self.sample()
                data["asp_x"]["orders"] = bad
                with self.assertRaises(ValueError):
                    mod.summarize(data)


if __name__ == "__main__":
    unittest.main()
