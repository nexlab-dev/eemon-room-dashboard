# EEMON / First SKU commercial handoff — 2026-11-23 JST

**Status: HOLD (not published; no approved SKU/link).** This is the exact owner/Muse evidence handoff to unblock the first commercial product. It does not authorize an ASP signup, media application, publication, or bank change.

## First actionable owner-side gate
Use **the existing Moshimo account only if its actual account status is approved**. In the authenticated dashboard, confirm (1) exact EEMON site URL registered as media, (2) that exact domain/subdomain is approved, (3) a relevant merchant program approved for that medium, (4) its permitted ad/link format, (5) owner-named eligible domestic receiving bank confirmed in the dashboard. **Do not record credentials, account numbers, full private screenshots, or bank identifiers in GitHub.** An owner-confirmed yes/no and redacted evidence reference are sufficient for tracking. If no account exists or it is not approved, remain HOLD; new registration/submission requires separate CEO authorization.

**Critical verified policy nuance:** Moshimo requires separate media registration for a **subdomain**, while a subdirectory under the registered domain does not require another media registration. Therefore do not assume the existing ROOM page, X profile, or another NEXLAB domain approves a new EEMON portal host.

## Muse → EEMON one-SKU handoff (private GitHub, no secret data)
- Candidate SKU / manufacturer / model / color / variant: **UNKNOWN**
- Merchant canonical product URL and original evidence URL: **UNKNOWN**
- Tax-inclusive item price / shipping / total / stock: **UNKNOWN** (never zero)
- Original merchant observation timestamp JST: **UNKNOWN**
- Permitted collection method / source terms: **UNKNOWN**
- Human verification of exact merchant source, by whom and when: **NOT VERIFIED**
- Media URL / program approval / legitimate network-generated affiliate URL: **NOT VERIFIED**
- PR disclosure / CEO publication approval: **NOT VERIFIED**

Muse must submit an evidence-backed observation consistent with `social-pilot/data/price-input.schema.json` and `portal-v2/price-input.schema.json`; GitHub comment/commit URL is the handoff proof, not a verbal claim. Reject >24-hour observations, variant mismatches, duplicate canonical URLs, unknown shipping, missing stock, and machine-only `verification=unverified`. Never use unverified price for total-cost, discount or cheapest-price copy. Do not copy third-party photos or reviews.

## Gate sequence and acceptance evidence
1. **SOURCE**: human opens the merchant's original product page and checks exact SKU, tax, shipping, stock, timestamp, rights and terms. Evidence reference with date. Missing => HOLD.
2. **ASP**: approved EEMON media + approved exact merchant program + network-generated tracking URL + bank suitability owner confirmation. No inferred approvals. Missing => HOLD.
3. **REVIEW**: offline `portal-v2/scripts/affiliate_release_gate.py` returns `REVIEW_READY`, not `PUBLISHED`. Check actual permissions and PR label manually.
4. **QA**: `python3 -m unittest discover -s portal-v2/tests -p 'test_*.py' -v`; strict media test `python3 portal-v2/scripts/verify_release_zip.py /path/to/EEMON_PORTAL_v2.zip`; real iPhone Safari anonymous link/disclosure check. A skipped video test is not release PASS.
5. **CEO_GATE**: explicit approval of exact site, SKU, campaign and release. Only then publish and check anonymous outbound destination. Keep clicks, orders, accepted actions, confirmed commissions, bank deposits separate; unknown != 0.

## Official primary sources checked 2026-11-23
- Moshimo https://af.moshimo.com/af/www/help — domestic-bank eligibility has exceptions; normal approved commission payout threshold JPY 1,000 (Sumishin SBI Net Bank JPY 1); Moshimo bears transfer fee; subdomain requires its own media registration; merchant program linkage required. Exact account and program states **not checked**.
- ValueCommerce https://help.valuecommerce.ne.jp/aff/transactions/comission/02/ and https://help.valuecommerce.ne.jp/aff/transactions/finance/01/ — JPY 1,000 minimum; payment on 15th of second month after approval; provider bears transfer fee. Exact account eligibility **not checked**.
- A8.net https://support.a8.net/as/payment/ — JPY 1,000 / JPY 5,000 / carry-over methods; bank transfer fees borne by recipient, amount depends on bank. Exact bank/account eligibility **not checked**.

## Safety / ownership / rollback
This file is documentation-only; no code, media, published main, ROOM schedules, external accounts, VPS or bank settings changed. No revenue claims. Revert only this documentation commit to roll back. Sources: PR #2 for portal, PR #1 for original pilot, ORCHESTRA #66 for revenue SSOT. Ordinary Chat/Work can edit this Markdown and accompanying GitHub code without hidden Work-only state.
