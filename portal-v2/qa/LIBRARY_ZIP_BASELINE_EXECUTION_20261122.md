# EEMON v2 Library ZIP strict-media baseline QA — 2026-11-22 JST

## Evidence and scope
- Source: owner-held ChatGPT Library `/NEXLAB/EEMON/EEMON_PORTAL_v2.zip`, size **6,624,210 bytes**.
- Retrieved through Library metadata and raw-file materialization, not a newly generated or substituted archive.
- Extracted to an isolated temporary working directory; **no GitHub checkout, Mac service, ROOM, production or external website changed**.
- Python standard-library `zipfile.testzip()`: **None (CRC success)**.
- Original ZIP-bundled `EEMON_PORTAL_v2/tests/test_integrity.py` executed against the ZIP's actual `site/media/reels/*.mp4` files:
  `python -m unittest discover -s tests -p 'test_*.py' -v`
- **20 tests / OK / 0 skipped**, including `test_video_assets` requiring all 10 MP4 files to exist and exceed 100,000 bytes.
- This is **baseline ZIP-source QA**, **not** the newest GitHub PR #2 integrated `verify_release_zip.py` test. That newer integration is **not yet executed**; do not label it PASS.
- Existing Draft PR #2 Mac source-only QA previously had 38 OK with one explicit skip; the strict QA in the GitHub-only checkout failed because MP4s are intentionally not tracked there. This ZIP baseline demonstrates the distributed MP4s exist, not that latest-source integration is complete.

## Reproduction
1. Retrieve the original Library archive and do not commit MP4 binaries or credentials.
2. `python3 -c "import zipfile; z=zipfile.ZipFile('EEMON_PORTAL_v2.zip'); assert z.testzip() is None"`
3. Extract into a fresh disposable directory; `cd EEMON_PORTAL_v2`.
4. `python3 -m unittest discover -s tests -p 'test_*.py' -v` (20 tests on the original 2026-11-14 source).
5. **Next** run latest PR #2 `python3 portal-v2/scripts/verify_release_zip.py /path/to/EEMON_PORTAL_v2.zip` from a clean GitHub checkout, and separately test actual Safari/mobile. A PASS must include the current commit SHA, exit code, test count, and full log.

## Release status
**HOLD**. ZIP QA is not proof of real SKU evidence, price, tax/shipping, live availability, source permission, media/program approval, authorized affiliate URL, iPhone Safari E2E, legal disclosure, or CEO publication consent.

## Official ASP source spot-check (2026-11-22 JST)
- Moshimo: https://af.moshimo.com/af/www/help — Japanese domestic deposit-taking institutions are generally eligible with exclusions; normal payout threshold JPY 1,000, Sumishin SBI Net Bank JPY 1, transfer fees borne by Moshimo; each promotion requires affiliation and a registered media, subdomains require separate media registration. **Individual bank and account approval unverified.**
- ValueCommerce: https://help.valuecommerce.ne.jp/aff/transactions/comission/02/ — approved commission >= JPY 1,000, payout on 15th of second month after approval; account must be configured. **Individual bank compatibility and media/program approval unverified.**
- A8.net: https://support.a8.net/as/payment/ — JPY 1,000 / JPY 5,000 / carryover options, payout typically 15th, bank fees depend on account and are not confirmed for this user. **Individual bank/media/program approval unverified.**

## Change / rollback
Documentation only, no runtime dependencies or production changes. Revert this documentation commit if erroneous; preserve the original ZIP and PR branches.
