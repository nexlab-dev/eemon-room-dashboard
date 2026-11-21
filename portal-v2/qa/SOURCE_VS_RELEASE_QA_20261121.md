# EEMON v2 source QA vs release QA (2026-11-21)

Source: Draft PR #2 `portal-v2/`. Generated MP4 files are **not tracked in Git**. A source-only clone therefore cannot honestly pass a video-distribution check.

## Reproducible tests (Mac / ordinary Chat / Work)

From the repository root, no API key or live service required:

```sh
python3 -m unittest discover -s portal-v2/tests -p 'test_*.py' -v
EEMON_RELEASE_MEDIA_REQUIRED=1 python3 -m unittest discover -s portal-v2/tests -p 'test_*.py' -v
```

The first command checks source behavior; its video test reports **SKIP**, not PASS. The second command is the strict release gate: missing/undersized `site/media/reels/reel01.mp4` through `reel10.mp4` fail. Do not merge, distribute, or publish the video-enabled build until this gate passes. Never replace missing MP4 with placeholders or silently remove videos from a claimed complete release.

## Verified Mac result

At commit `cd4717a47be4cf6444e867dec83e43382f36d830`, 2026-11-21 JST: source suite **38 tests, OK (skipped=1)**; strict `test_integrity.py` **20 tests, FAILED (failures=1)** because `reel01.mp4` is missing. This is a packaging/reproducibility blocker, not evidence of an ASP or product approval.

## Recovery

1. Obtain the already-generated original videos from the approved EEMON Portal v2 Library ZIP, or regenerate from `scripts/render_reels.py` in a separate, capacity-checked workspace with Pillow, NumPy, and FFmpeg. Do not commit third-party assets or fonts.
2. Verify 10 expected filenames, nonzero duration/audio, actual content and rights, then run strict QA with `EEMON_RELEASE_MEDIA_REQUIRED=1`.
3. Keep release blocked until strict QA passes **and** the separate gates for official same-SKU price evidence, media/program approval, tracked affiliate URL, disclosure, CEO publication consent, and real-device Safari E2E are met.
4. Rollback of this source-only QA behavior: revert the `test_integrity.py` commit; never delete existing user videos.

## ASP official checks (2026-11-21 JST)

- もしも: https://af.moshimo.com/af/www/help — free registration; a site/blog is required for advertising per FAQ; subdomains need separate registration; program affiliation must be requested. Bank and individual approval status still unverified.
- バリューコマース: https://help.valuecommerce.ne.jp/aff/transactions/comission/02/ — minimum transfer JPY 1,000; approved-month +2 months on the 15th; bank registration required. Account-specific suitability unknown.
- A8.net: https://support.a8.net/as/payment/ — JPY 1,000 / JPY 5,000 / carry-over methods; exact bank fee and eligibility must be checked for the user's bank.

Do not mix ROOM's 2026-11-14 confirmed 8 clicks/30d and JPY 0 revenue with unmeasured new ASP traffic. No publishing, external registration, paid API, or production changes were made.
