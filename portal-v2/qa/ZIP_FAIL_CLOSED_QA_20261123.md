# EEMON ZIP fail-closed QA — 2026-11-23 JST

## Scope and proof
- Draft PR #2 branch `feature/eemon-buying-portal-v2-20261114`, Mac clone HEAD `d83a1b4c42a11427b5ad23df741ce20a2fadec63`.
- Added `tests/test_verify_release_zip.py` (six standard-library-only synthetic ZIP cases). First execution revealed a **test expectation error**: production verifier raises `ValueError("ZIP integrity failed")` on a CRC mismatch; test was corrected and rerun. This is not a change to the production verifier.
- Mac command: `python3 -m unittest discover -s portal-v2/tests -p 'test_verify_release_zip.py' -v` → **6/6 PASS**.
- Mac command: `python3 -m unittest discover -s portal-v2/tests -p 'test_*.py' -q` → **48 tests OK, skipped=1** (video presence skipped because GitHub checkout contains no MP4).
- Cases: ten unique videos >100KB, missing video, undersized video, duplicate ZIP member, CRC tampering, missing archive.
- Free disk reported by `df -h /`: approximately 11GiB available (filesystem root). No production modifications.

## Remaining release gate — HOLD
This test uses synthetic ZIP fixtures. **It does not prove that the current PR #2 checkout combined with the actual owner-held EEMON_PORTAL_v2.zip passes the strict integration QA**. Execute:
```bash
python3 portal-v2/scripts/verify_release_zip.py /path/to/EEMON_PORTAL_v2.zip
```
The source-only test skip is not release approval. Actual ZIP verified separately in Library in earlier run; combined current-head execution still pending.

No independently checked exact SKU, price including tax/shipping, stock and rights evidence; no account-specific ASP bank suitability, approved program, tracked link, iPhone Safari E2E, or CEO publication approval. Keep prices unpublished until human evidence and source permission are confirmed.

## Official ASP policy snapshot (accessed 2026-11-23 JST)
- Moshimo: https://af.moshimo.com/ — free publisher registration, X/Instagram/YouTube/blog support subject to channel rules, payout normally >=JPY1,000, transfer fee free. Actual bank and program status **unknown**.
- ValueCommerce: https://help.valuecommerce.ne.jp/aff/transactions/comission/02/ — minimum JPY1,000; approved-month plus two months, 15th; fee borne by provider: https://help.valuecommerce.ne.jp/aff/transactions/finance/01/ . Media/campaign approvals and bank eligibility **unknown**.
- A8: https://support.a8.net/as/payment/ — JPY1,000/5,000/carryover payout choices, recipient bears bank fee; account eligibility and approved programs **unknown**.

## Repeatability and rollback
Re-run the two unittest commands above on a fresh PR #2 clone. Test creates temporary synthetic archives only and needs no account credentials. Revert only the added test/report commits if necessary; do not modify main, existing ROOM automation, production site or the private performance ledger. Work and ordinary Chat use these GitHub paths as the shared source.
