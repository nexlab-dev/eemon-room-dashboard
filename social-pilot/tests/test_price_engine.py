from datetime import datetime, timezone, timedelta
from scripts.price_engine import compare, ValidationError
import pytest
NOW=datetime(2026,11,14,3,0,0,tzinfo=timezone.utc)
BASE={
 'product_key':'printer-001-white', 'variant_key':'printer-001-white',
 'product_name':'試験用プリンター','listing_key':'example-shop-001','shop_name':'試験店舗A',
 'item_url':'https://example.com/item/1','evidence_url':'https://example.com/item/1',
 'price_jpy':12000,'shipping_jpy':500,'currency':'JPY','tax_included':True,
 'stock':'available','checked_at':'2026-11-14T11:00:00+09:00',
 'verification':'human_verified_official_page','verified_by':'test fixture'
}
def observe(**override):return dict(BASE,**override)
def test_empty():
 r=compare({'observations':[]},NOW)
 assert r['summary']==[] and r['excluded']==[]
def test_real_total_order_and_variant_isolation():
 obs=[observe(), observe(listing_key='shop2',shop_name='店舗B',price_jpy=11500,shipping_jpy=2000), observe(product_key='printer-001-black',variant_key='printer-001-black',listing_key='shop3',shop_name='店舗C',price_jpy=10000,shipping_jpy=0)]
 r=compare({'observations':obs},NOW)
 assert len(r['summary'])==2
 assert r['summary'][1]['offers'][0]['total_jpy']==12500
 assert r['summary'][1]['offers'][1]['total_jpy']==13500
def test_stale_excluded():
 r=compare({'observations':[observe(checked_at='2026-11-10T11:00:00+09:00')]},NOW)
 assert not r['summary'] and '期限切れ' in r['excluded'][0]['reason']
def test_unknown_shipping_excluded():
 r=compare({'observations':[observe(shipping_jpy=None)]},NOW)
 assert not r['summary']
def test_fake_claim_and_uncertainty_excluded():
 r=compare({'observations':[observe(verification='unverified'),observe(listing_key='abc',variant_key='other')]},NOW)
 assert not r['summary'] and len(r['excluded'])==2
def test_http_and_localhost_excluded():
 r=compare({'observations':[observe(item_url='http://shop.example.com'),observe(item_url='https://localhost:8888')]},NOW)
 assert len(r['excluded'])==2
def test_duplicate_excluded():
 r=compare({'observations':[observe(),observe()]},NOW)
 assert sum(x['offer_count'] for x in r['summary'])==1 and len(r['excluded'])==1
def test_future_and_untrusted_demo():
 r=compare({'observations':[observe(checked_at='2027-11-14T11:00:00+09:00')]},NOW)
 assert not r['summary']
 with pytest.raises(ValidationError):compare({'demo_data':True,'observations':[]},NOW)
def test_bool_yen_rejected():
 r=compare({'observations':[observe(price_jpy=True)]},NOW)
 assert not r['summary']