#!/usr/bin/env python3
"""EEMON offline revenue funnel scorecard. No tracking, network, or personal data.

Read owner-entered aggregate evidence, never infer missing counts as zero.
Usage: python3 portal-v2/scripts/revenue_scorecard.py path/to/private-aggregates.json
The input file MUST stay outside public GitHub and site/. No writes.
"""
import json
import sys
from pathlib import Path

FIELDS = ("referral_clicks", "orders", "approved_actions",
          "confirmed_commission_jpy", "bank_received_jpy")
MEDIA = ("asp_site", "asp_x", "room")


def summarize(data):
    if not isinstance(data, dict) or set(data) != set(MEDIA):
        raise ValueError("expected exact media keys: asp_site, asp_x, room")
    result = {}
    for medium in MEDIA:
        row = data[medium]
        if not isinstance(row, dict) or set(row) != set(FIELDS):
            raise ValueError(f"{medium}: missing or extra metrics")
        cleaned = {}
        for key in FIELDS:
            value = row[key]
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError(f"{medium}.{key}: must be nonnegative integer or null")
            cleaned[key] = value
        result[medium] = cleaned
    # Only sum a metric when every included source has actual evidence.
    totals = {key: sum(result[m][key] for m in MEDIA)
              if all(result[m][key] is not None for m in MEDIA) else None
              for key in FIELDS}
    return {"media": result, "total": totals, "status": "UNMEASURED_INCLUDED" if
            any(v is None for v in totals.values()) else "FULLY_MEASURED"}


def main():
    if len(sys.argv) != 2:
        print("usage: revenue_scorecard.py private-aggregates.json", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        print(json.dumps(summarize(data), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"HOLD: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
