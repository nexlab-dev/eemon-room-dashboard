#!/usr/bin/env python3
"""Offline fail-closed gate for EEMON affiliate publication. No network or publishing.

Input JSON is an owner-maintained approval manifest; this tool does not authenticate
the claimed approvals. Never store personal data, passwords or bank details here.
"""
import argparse
import json
import ipaddress
from pathlib import Path
from urllib.parse import urlsplit

REQUIRED = ("owner_publish_approval", "asp_account_approved",
            "media_approved", "campaign_approved", "link_owner_verified",
            "advertising_disclosure_reviewed", "product_facts_verified")

def _is_ip(host):
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False

def check(manifest):
    if not isinstance(manifest, dict):
        return ["manifest must be an object"]
    errors = [f"{key} is not explicitly true" for key in REQUIRED
              if manifest.get(key) is not True]
    url = manifest.get("affiliate_url")
    if not isinstance(url, str) or len(url) > 2048:
        errors.append("approved affiliate_url missing")
    else:
        try:
            parsed = urlsplit(url)
            if (parsed.scheme != "https" or not parsed.hostname or
                parsed.username or parsed.password or parsed.fragment or
                parsed.hostname.lower() in ("localhost", "127.0.0.1") or
                parsed.hostname.lower().endswith((".localhost", ".local")) or
                "." not in parsed.hostname or
                parsed.port not in (None, 443) or
                _is_ip(parsed.hostname)):
                errors.append("affiliate_url must be public HTTPS without credentials")
        except ValueError:
            errors.append("affiliate_url invalid")
    if not isinstance(manifest.get("evidence_refs"), list) or not manifest["evidence_refs"]:
        errors.append("approval evidence_refs missing")
    return errors

def main():
    parser = argparse.ArgumentParser(description="Check readiness only; never publish")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    errors = check(json.loads(args.manifest.read_text(encoding="utf-8")))
    print(json.dumps({"status": "HOLD" if errors else "REVIEW_READY",
                      "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
