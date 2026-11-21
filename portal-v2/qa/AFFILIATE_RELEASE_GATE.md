# EEMON affiliate release gate (2026-11-16)

This is an **offline review guard**, not proof of ASP approval and not a publisher.
Source: `portal-v2/scripts/affiliate_release_gate.py`; tests: `portal-v2/tests/test_affiliate_release_gate.py`.
Works from normal Chat, Work, or a local Python 3 environment. No third-party dependencies.

## Run
```sh
python3 -m unittest discover -s portal-v2/tests -p 'test_affiliate_release_gate.py' -v
python3 portal-v2/scripts/affiliate_release_gate.py /path/to/private-owner-approval-manifest.json
```
Exit 1 / HOLD means no publishing. Exit 0 / REVIEW_READY means **only that the
manifest claims all required gates**; it is not evidence of approval and must
never trigger automatic publication. A reviewer must independently check
current ASP terms, medium approval, campaign approval, link ownership, PR label,
product facts, source permissions and explicit CEO publication approval.
Do not store the real manifest in GitHub; do not put bank details, credentials,
tokenized affiliate links or private approval URLs into GitHub.

## Private manifest shape
```json
{
  "owner_publish_approval": false,
  "asp_account_approved": false,
  "media_approved": false,
  "campaign_approved": false,
  "link_owner_verified": false,
  "advertising_disclosure_reviewed": false,
  "product_facts_verified": false,
  "affiliate_url": "",
  "evidence_refs": []
}
```

## Rollback
Revert the two additive code/test commits and this document on the Draft PR
branch only. No deployed site, ROOM queue, scheduled worker or public main is
modified by this feature.

## Acceptance
Five unittest cases cover HOLD defaults, all-true review-only, missing campaign
approval, unsafe URLs, and missing evidence. **Tests must actually be run**
before reporting PASS. Real ASP approvals, real product-price observations,
Safari E2E, public launch and first revenue remain separate uncompleted gates.
