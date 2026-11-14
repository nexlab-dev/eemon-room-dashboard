from scripts.muse_intake import quarantine, validate_candidate

BASE = {
    "product_key": "EW-056A-W",
    "variant_key": "EW-056A-W",
    "item_url": "https://item.rakuten.co.jp/example/ew-056a/",
    "evidence_url": "https://item.rakuten.co.jp/example/ew-056a/",
    "observed_at": "2026-11-14T19:00:00+09:00",
    "source_permission": "unknown",
}

def test_unverified_never_promoted():
    result = quarantine({"candidates": [BASE]})
    assert result["eligible_price_count"] == 0
    assert result["candidates"][0]["status"] == "QUARANTINED_UNVERIFIED"
    assert "price_jpy" not in result["candidates"][0]["candidate"]

def test_untrusted_fields_and_secrets_not_copied():
    item = dict(BASE, price_jpy=100, verified_by="Muse", token="DO_NOT_LEAK")
    output = quarantine({"candidates": [item]})
    assert "DO_NOT_LEAK" not in str(output)
    assert "price_jpy" not in output["candidates"][0]["candidate"]

def test_invalid_url_and_permission_quarantined():
    item = dict(BASE, item_url="http://localhost/", source_permission="yes")
    assert "invalid_item_url" in validate_candidate(item)
    assert "invalid_source_permission" in validate_candidate(item)

def test_empty_and_bad_shape():
    assert quarantine({"candidates": []})["candidates"] == []
    import pytest
    with pytest.raises(ValueError):
        quarantine({"observations": []})
