# Affiliate URL gate hardening — 2026-11-16 JST

Scope: `portal-v2/scripts/affiliate_release_gate.py`, `portal-v2/tests/test_affiliate_release_gate.py`.

The offline publication readiness checker now rejects direct IPv4/IPv6 destinations, `.local` and `.localhost` names, hostnames without a dot, and HTTPS ports other than the default 443. Credentials, fragments, HTTP, and missing explicit approvals remain rejected. This prevents local/intranet targets being treated as review-ready affiliate links. **It is not a network request, DNS validation, ASP approval verification, or permission to publish.** A public hostname could still resolve to private IP; review the actual approved link and its redirects manually.

Reproduce (Python 3.10+, stdlib only):
```sh
python3 -m unittest discover -s portal-v2/tests -p 'test_affiliate_release_gate.py' -v
```
Acceptance: all tests pass; localhost, IP literals, private hostname and nonstandard ports return HOLD; public HTTPS URL with all owner-maintained evidence flags returns REVIEW_READY, never auto-published.

Rollback: revert commits `c31c60e` and `edac7d8` on the Draft PR branch. Do not touch main or ROOM automations.

Evidence limitation: the code and tests were committed via GitHub, but test execution is **PENDING**; no claims of verified ASP approvals, live price, site deployment, clicks or revenue. Human source verification and CEO publication gate still apply.
