"""Offline, deterministic acceptance tests for the EEMON v2 portal."""
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
from unittest import mock
import unittest

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
spec=importlib.util.spec_from_file_location('eemon_price_engine', ROOT/'scripts/price_engine.py')
pe=importlib.util.module_from_spec(spec);spec.loader.exec_module(pe)
spec2=importlib.util.spec_from_file_location('eemon_server', ROOT/'server.py')
srv=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(srv)
UTC=timezone.utc

class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content=json.loads((SITE/'guides.json').read_text('utf-8'))
    def test_has_twelve_unique_guides(self):
        guides=self.content['guides'];self.assertEqual(len(guides),12)
        self.assertEqual(len({g['id'] for g in guides}),12)
    def test_every_guide_has_corresponding_original_art(self):
        for g in self.content['guides']:
            art=SITE/'assets'/(g['art']+'.svg')
            self.assertTrue(art.is_file(),art)
            self.assertIn('svg',art.read_text('utf-8'))
            self.assertEqual(len(g['points']),3)
            self.assertTrue(g['question'])
    def test_video_assets(self):
        for n in range(1,11):
            video=SITE/'media'/'reels'/f'reel{n:02}.mp4'
            self.assertTrue(video.is_file(),video)
            self.assertGreater(video.stat().st_size,100_000)
    def test_video_content(self):
        data=json.loads((SITE/'reels.json').read_text('utf-8'))
        self.assertEqual(len(data['reels']),10)
    def test_no_fake_default_prices(self):
        j=json.loads((SITE/'price_output.json').read_text('utf-8'))
        self.assertEqual(j['verification'],'NO_DATA')
        self.assertEqual(j['summary'],[])
    def test_index_has_disclosures(self):
        txt=(SITE/'index.html').read_text('utf-8')
        for expected in ['実価格未取得','AIに相談','広告','未接続','カテゴリ','price-watch']:
            self.assertIn(expected,txt)
    def test_server_is_unconfigured_by_default(self):
        with mock.patch.dict(os.environ,{'EEMON_LLM_ENABLED':'0','EEMON_GEMINI_API_KEY':''}):
            self.assertFalse(srv.remote_enabled())
            with self.assertRaises(RuntimeError):srv.generate_remote('家電を探しています')
    def test_remote_requires_both_opt_in_and_key(self):
        with mock.patch.dict(os.environ,{'EEMON_LLM_ENABLED':'1','EEMON_GEMINI_API_KEY':''}):self.assertFalse(srv.remote_enabled())
        with mock.patch.dict(os.environ,{'EEMON_LLM_ENABLED':'0','EEMON_GEMINI_API_KEY':'secret'}):self.assertFalse(srv.remote_enabled())
    def test_no_production_api_credentials_in_site(self):
        for p in [SITE/'index.html',SITE/'app.js',SITE/'guides.json']:
            self.assertNotIn('AIza',p.read_text('utf-8'))
    def test_remote_mock_without_external_network(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*a):return False
            def read(self):return b''
        def opener(req,timeout):
            self.assertTrue(req.full_url.startswith('https://generativelanguage.googleapis.com/'))
            self.assertEqual(req.headers['X-goog-api-key'],'fake_local_test')
            body=json.loads(req.data)
            self.assertIn('最安値',body['systemInstruction']['parts'][0]['text'])
            return mock.Mock(__enter__=lambda _:mock.Mock(read=lambda:json.dumps({'candidates':[{'content':{'parts':[{'text':'予算と部屋の広さを確認しよう。'}]}}]}).encode('utf-8')),__exit__=lambda *_:False)
        with mock.patch.dict(os.environ,{'EEMON_LLM_ENABLED':'1','EEMON_GEMINI_API_KEY':'fake_local_test'}):
            self.assertEqual(srv.generate_remote('暖房選び',opener=opener),'予算と部屋の広さを確認しよう。')

class PriceGateTest(unittest.TestCase):
    def fixture(self,overrides=None):
        now=datetime(2026,11,14,13,tzinfo=UTC)
        v={'product_key':'X-101','variant_key':'X-101','product_name':'同じ商品',
           'listing_key':'shop/item-x101','shop_name':'公式例','item_url':'https://example.com/item',
           'evidence_url':'https://example.com/item','price_jpy':2000,'shipping_jpy':500,
           'currency':'JPY','tax_included':True,'stock':'available',
           'checked_at':(now-timedelta(hours=2)).isoformat(),
           'verification':'human_verified_official_page','verified_by':'reviewer'}
        v.update(overrides or {})
        return now,{'observations':[v]}
    def test_price_total_and_group(self):
        now,p=self.fixture()
        result=pe.compare(p,now=now)
        self.assertEqual(result['summary'][0]['offers'][0]['total_jpy'],2500)
        self.assertEqual(result['verification'],'SOURCE_ASSERTED_NOT_INDEPENDENTLY_AUDITED')
    def test_unknown_shipping_excluded(self):
        now,p=self.fixture({'shipping_jpy':None})
        self.assertEqual(pe.compare(p,now=now)['summary'],[])
    def test_stale_excluded(self):
        now,p=self.fixture({'checked_at':'2026-11-11T13:00:00+00:00'})
        self.assertEqual(pe.compare(p,now=now)['summary'],[])
    def test_variant_mismatch_excluded(self):
        now,p=self.fixture({'variant_key':'X-102'})
        self.assertEqual(pe.compare(p,now=now)['summary'],[])
    def test_unverified_excluded(self):
        now,p=self.fixture({'verification':'muse_suggested'})
        self.assertEqual(pe.compare(p,now=now)['summary'],[])
    def test_unavailable_stock_excluded(self):
        now,p=self.fixture({'stock':'out_of_stock'})
        self.assertEqual(pe.compare(p,now=now)['summary'],[])
    def test_negative_shipping_excluded(self):
        now,p=self.fixture({'shipping_jpy':-1})
        self.assertEqual(pe.compare(p,now=now)['summary'],[])
    def test_http_url_excluded(self):
        now,p=self.fixture({'item_url':'http://example.com/item'})
        self.assertEqual(pe.compare(p,now=now)['summary'],[])
    def test_demo_price_rejected(self):
        now,p=self.fixture();p['demo_data']=True
        with self.assertRaises(pe.ValidationError):pe.compare(p,now=now)
    def test_duplicate_listing_excluded(self):
        now,p=self.fixture();p['observations'].append(dict(p['observations'][0]))
        result=pe.compare(p,now=now)
        self.assertEqual(len(result['summary'][0]['offers']),1)
        self.assertEqual(len(result['excluded']),1)

if __name__=='__main__':unittest.main()