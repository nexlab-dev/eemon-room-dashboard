# Affiliate release gate isolated regression QA — 2026-11-18 19:17 JST

## Scope and provenance
GitHub branch: `feature/eemon-buying-portal-v2-20261114`.
Source blob SHAs fetched before testing:
- `portal-v2/scripts/affiliate_release_gate.py`: `6c5aa94513883db60856395eb0f2c5b72c266352`
- `portal-v2/tests/test_affiliate_release_gate.py`: `db90b331fbeeca96a594c1d63d04860a99a21462`

## Execution
In an isolated Linux /tmp directory, manually reconstructed the fetched gate logic and eight test cases (no repository checkout, no Mac execution, no network, no publishing). Command:
`python3 -m unittest discover -s /tmp/eemonqa/tests -p 'test_affiliate_release_gate.py' -v`

Result: **8 tests executed; 8 passed; 0 failures** (0.001s). Cases: empty manifest; all approval flags; unapproved campaign; HTTP/credentials/localhost; private/nonstandard hosts; standard port 443; whitespace/control characters; missing evidence.

## Important limitation
This is an **isolated reproduction**, not an exact-source repository CI run. The source files were reconstructed from connector-fetched content; this result does not certify exact byte identity, other test suites, DNS, redirects, approval authenticity, or deployment readiness. GitHub Actions/CI or exact-source checkout run remains PENDING.

## Release decision
HOLD: ASP registration, campaign approval, verified 1 SKU price/shipping/stock/evidence, actual affiliate link, human source verification, and owner publication authorization are not established. No changes to main, ROOM, live tasks, or accounts.

## Next acceptance step
Run exact GitHub branch checkout tests with `python3 -m unittest discover -s portal-v2/tests -p 'test_affiliate_release_gate.py' -v` and `test_price_url_safety.py`; retain logs and commit SHA. Verify Muse's permitted original price source and exact SKU separately. Revert this QA note alone if necessary; no runtime dependencies.
