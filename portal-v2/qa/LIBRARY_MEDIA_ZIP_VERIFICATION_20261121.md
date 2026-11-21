# EEMON portal v2 owner ZIP media verification — 2026-11-21

Source: ChatGPT Library `/NEXLAB/EEMON/EEMON_PORTAL_v2.zip` (6,624,210 bytes). **Not** GitHub tracked media. No production deploy.

## Actual inspection
The Library ZIP was materialized in an isolated container and checked using Python `zipfile`. `testzip() == None` (CRC passes), exactly 10 MP4 entries at `EEMON_PORTAL_v2/site/media/reels/reel01.mp4` through `reel10.mp4`, each >100,000 bytes. This verifies archive presence/CRC only, **not** playable audio/video, identity with current source, iPhone Safari or rights.

| file | bytes | SHA256 first 16 hex |
|---|---:|---|
| reel01.mp4 | 653463 | 3ccb55e0aca7d3af |
| reel02.mp4 | 723438 | eb8bd02546c39690 |
| reel03.mp4 | 686830 | 6d5afaa1a18290ab |
| reel04.mp4 | 675134 | d96b082b5f4f5152 |
| reel05.mp4 | 616672 | ec5f6072c799400a |
| reel06.mp4 | 732499 | 15d0716a163d470a |
| reel07.mp4 | 644954 | aa0e5c5178b3626d |
| reel08.mp4 | 636162 | 9dbe0e05e2ff69ca |
| reel09.mp4 | 747017 | 69d1b1aebd8a4628 |
| reel10.mp4 | 597167 | 2d16f35a4de95c7c |

## Repeatable strict QA from normal Chat / Work
1. Obtain owner-held ZIP with authorization; do not commit MP4 binaries or secrets.
2. From repo root run `python3 portal-v2/scripts/verify_release_zip.py /path/to/EEMON_PORTAL_v2.zip`.
3. Script checks ZIP CRC, 10 named files, size and runs **all** current `test_*.py` with `EEMON_RELEASE_MEDIA_REQUIRED=1` inside a temporary source copy, leaving checkout untouched.
4. A nonzero exit is HOLD. Even a PASS does not authorize publishing; separate ASP program/media approval, verified 1SKU, owner approval, Safari E2E and bank eligibility remain.

## Current state
The new script was committed to Draft PR #2 but has **not yet been executed end-to-end** against the Library ZIP and current GitHub checkout together. The ZIP-only CRC and count checks above were actually run. Earlier strict checkout-only QA failed because MP4s are not tracked. No changes to main/ROOM/production.
