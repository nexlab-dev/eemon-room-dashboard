# EEMON ASP revenue scorecard — 2026-11-22

## Purpose
The independent ASP business needs an evidence-led funnel without merging Rakuten ROOM clicks with unknown ASP metrics. This is a **local, offline aggregate scorecard**, not a live analytics integration. It records source-separated counts and amounts. It does not collect user IDs, bank details, referral tokens or customer records.

## Usage
Run from repository root:

```bash
python3 portal-v2/scripts/revenue_scorecard.py /private/path/eemon-aggregates.json
python3 -m unittest discover -s portal-v2/tests -p test_revenue_scorecard.py -v
python3 -m unittest discover -s portal-v2/tests -p 'test_*.py' -q
```

Input format (example values are **illustrative**, not verified new ASP results):

```json
{
  "asp_site": {"referral_clicks": null, "orders": null, "approved_actions": null, "confirmed_commission_jpy": null, "bank_received_jpy": null},
  "asp_x": {"referral_clicks": null, "orders": null, "approved_actions": null, "confirmed_commission_jpy": null, "bank_received_jpy": null},
  "room": {"referral_clicks": 8, "orders": 0, "approved_actions": null, "confirmed_commission_jpy": null, "bank_received_jpy": null}
}
```

The ROOM example is historical 2026-11-14 CEO-provided 30-day clicks and sales; it is **not** a current-period total. Use identical, explicit date ranges in real reporting. Unknown remains `null`; a combined metric is `null` until every included medium has a measured value. Do not infer sales, approved actions, payouts or bank receipt from click events. No third-party attribution without evidence. Use only confirmed counts, never invent zeros.

## Dependency and safety
Python 3 standard library only. No network, paid API, persistent write, personal data or tracking cookies. Keep the input outside the repo/public site and never commit account or bank details. No output means actual conversion occurred.

## Verification / rollback
2026-11-22 Mac GitHub checkout HEAD `6a2aae83190690349801ec06403313f12ba22e21`: scorecard tests **4/4 PASS**; source-only full suite **42 tests OK, 1 skipped** (video assets absent from GitHub checkout). Strict release-media QA, actual iPhone Safari, verified SKU, approved affiliate program/link and CEO publish approval remain pending. To roll back, remove the new `scripts/revenue_scorecard.py`, `tests/test_revenue_scorecard.py` and this document from the Draft PR branch; no production state is touched.

## Official ASP sources checked 2026-11-22
- Moshimo FAQ: https://af.moshimo.com/af/www/help (free media registration, media/campaign approval and bank/transfer FAQs; account-specific eligibility unverified)
- ValueCommerce: https://help.valuecommerce.ne.jp/aff/transactions/comission/02/ (approved commission paid on the 15th of the second subsequent month, threshold JPY 1,000)
- A8.net: https://support.a8.net/as/payment/ (JPY 1,000 / 5,000 / carryover; actual bank transfer fee borne by affiliate)

No claim of verified owner bank, ASP program approval, usable link or actual ASP conversion.
