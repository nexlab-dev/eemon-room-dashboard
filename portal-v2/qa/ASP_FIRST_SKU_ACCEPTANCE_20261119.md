# EEMON first SKU commercial acceptance / 2026-11-19

Status: HOLD — preparation only. This checklist is not evidence of ASP approval, price verification, publication, or sales.

## Single-SKU evidence packet (private review)

Record: SKU/model/variant/color; merchant product URL; evidence URL; observed timestamp (JST); tax-inclusive item price; shipping fee or explicit shipping condition; inventory state; source's automated-access permission; source reviewer; verified-by-human timestamp; affiliate network; media and campaign approval references; advertising disclosure placement; owner publication approval. Do not store credentials, personal bank data, or private account screenshots in a public repository.

## Fail-closed acceptance

1. Verify exact model, variant and color against merchant's own product page; reject ambiguous SKU or cross-variant comparison.
2. Reject stale observations older than 24 hours, missing timestamp, unknown shipping, missing stock status, duplicated canonical merchant URLs, or missing original evidence URL. Missing price is UNKNOWN, never zero.
3. Treat all machine-collected data as `verification=unverified` until a human has checked the original merchant page. Unverified entries cannot enter total-cost comparisons, best-price claims, discount claims, or SNS copy.
4. Verify permission for the collection method and image/text reuse; do not scrape or republish without rights.
5. Before any commercial link, require owner-approved ASP registration, approved media, approved campaign, legitimate network-generated tracked link, PR disclosure, and owner release approval. The local affiliate release gate returns REVIEW_READY only, never auto-publishes.
6. Measure EEMON ASP outbound clicks separately from ROOM's historical 8 clicks/30 days; separately record orders, accepted conversions, confirmed commission and bank receipt. Unknown is not zero.

## Review/test sequence

- Validate source record against `social-pilot/data/price-input.schema.json` and the `portal-v2` price engine tests. Run `python3 -m unittest discover -s portal-v2/tests -p 'test_affiliate_release_gate.py'` from repository root, and retain stdout, exit status, Git SHA and timestamp. Do not mark PASS until executed on exact branch sources.
- Check the anonymous mobile page on real iPhone Safari, including disclosure, link destination, price/stock freshness, and no false AI/person reviews.
- Restore by reverting only this documentation commit if necessary. Never change main, ROOM production workers, or publish from this checklist.

## Outstanding gates

Muse price evidence with GitHub proof: not verified. Human source check: not verified. ASP/media/campaign approvals: not verified. Authorized tracked link: not verified. Real Safari QA: not verified. Public release and revenue: not verified.
