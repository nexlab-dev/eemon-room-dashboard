#!/usr/bin/env python3
"""Fail-closed Muse price intake: candidates only, never a verified price feed.

Usage: python3 scripts/muse_intake.py data/muse_candidates.json data/muse_review_queue.json
No scraping, publishing, network calls, credentials, or automatic promotion.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlsplit

REQUIRED = ("product_key", "variant_key", "item_url", "evidence_url",
            "observed_at", "source_permission")
ALLOWED_PERMISSION = ("documented_permitted", "unknown", "restricted")

def validate_candidate(raw):
    if not isinstance(raw, dict):
        return ["not_an_object"]
    errors = [f"missing_{k}" for k in REQUIRED if not raw.get(k)]
    for key in ("item_url", "evidence_url"):
        value = raw.get(key)
        try:
            u = urlsplit(value)
            if u.scheme != "https" or not u.hostname or u.username or u.password or u.fragment:
                errors.append(f"invalid_{key}")
            if u.hostname in ("localhost", "127.0.0.1") or u.hostname.endswith(".local"):
                errors.append(f"invalid_{key}")
        except (TypeError, ValueError):
            errors.append(f"invalid_{key}")
    if raw.get("source_permission") not in ALLOWED_PERMISSION:
        errors.append("invalid_source_permission")
    try:
        t = dt.datetime.fromisoformat(raw.get("observed_at", "").replace("Z", "+00:00"))
        if t.tzinfo is None:
            errors.append("timestamp_without_timezone")
    except (TypeError, ValueError, AttributeError):
        errors.append("invalid_timestamp")
    return sorted(set(errors))

def quarantine(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("candidates"), list):
        raise ValueError("expected object with candidates array")
    result = []
    for index, raw in enumerate(payload["candidates"]):
        errors = validate_candidate(raw)
        # Never carry personal data, credentials, arbitrary fields or asserted price
        # into a publishable dataset. Only allowlisted evidence metadata survives.
        allowed = ("product_key", "variant_key", "item_url", "evidence_url",
                   "observed_at", "source_permission")
        clean = {key: raw[key] for key in allowed if isinstance(raw, dict) and key in raw}
        result.append({"index": index, "status": "QUARANTINED_UNVERIFIED",
                       "validation_errors": errors, "candidate": clean,
                       "review_required": ["source_permission", "exact_variant",
                                           "tax_included_price", "shipping",
                                           "availability", "original_page_human_check",
                                           "asp_program_and_media_approval"]})
    return {"schema_version": 1, "verification": "UNVERIFIED_NO_PUBLICATION",
            "eligible_price_count": 0, "candidates": result}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    output = quarantine(source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"QUARANTINED:{len(output['candidates'])} VERIFIED:0")

if __name__ == "__main__":
    main()
