import json, pathlib, datetime as dt, io, subprocess
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parent.parent
def inject_site(page):
    html=(ROOT/'site/index.html').read_text(encoding='utf8').replace('<script defer src="app.js"></script>','')
    page.set_content(html, wait_until='domcontentloaded')
    page.add_style_tag(content=(ROOT/'site/style.css').read_text(encoding='utf8'))
    content=json.loads((ROOT/'site/content.json').read_text(encoding='utf8'))
    prices=json.loads((ROOT/'site/price_output.json').read_text(encoding='utf8'))
    page.evaluate('''([content,prices]) => {window.fetch=async(url)=>({ok:true,json:async()=>String(url).includes('content')?content:prices})}''',[content,prices])
    page.add_script_tag(content=(ROOT/'site/app.js').read_text(encoding='utf8'))
    page.wait_for_selector('.reel-card')

def test_site_interactive_and_mobile():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        desktop=browser.new_page(viewport={'width':1440,'height':900});inject_site(desktop)
        assert 'EEMON' in desktop.title()
        assert desktop.locator('.reel-card').count()==10
        assert 'データ待ち' in desktop.locator('#priceStatus').inner_text()
        desktop.locator('#reelFilter').select_option('家電')
        assert desktop.locator('.reel-card').count()==3
        desktop.locator('#reelFilter').select_option('all')
        desktop.locator('.reel-card').first.click()
        assert desktop.locator('#modal').get_attribute('aria-hidden')=='false'
        assert '送料込みで比べる' in desktop.locator('#modalTitle').inner_text()
        assert desktop.locator('#modalSource').get_attribute('src').endswith('reel01.mp4')
        desktop.locator('#modalClose').click()
        assert desktop.locator('#modal').get_attribute('aria-hidden')=='true'

        fresh=dt.datetime.now(dt.timezone.utc).isoformat()
        obs={"generated_at":fresh,"verification":"SOURCE_ASSERTED_NOT_INDEPENDENTLY_AUDITED","summary":[{"product_name":"試験用製品","product_key":"testsku001","offers":[
          {"total_jpy":12000,"price_jpy":11500,"shipping_jpy":500,"shop_name":"ショップB","item_url":"https://example.com/b","evidence_url":"https://example.com/b","checked_at":fresh},
          {"total_jpy":11000,"price_jpy":10000,"shipping_jpy":1000,"shop_name":"ショップA","item_url":"https://example.com/a","evidence_url":"https://example.com/a","checked_at":fresh}]}]}
        desktop.locator('#priceImport').set_input_files({'name':'verified.json','mimeType':'application/json','buffer':json.dumps(obs,ensure_ascii=False).encode('utf8')})
        assert '2件' in desktop.locator('#priceStatus').inner_text()
        assert desktop.locator('.offer').count()==2
        assert 'ショップA' in desktop.locator('.offer').first.inner_text()
        desktop.locator('#clearPrice').click()
        assert desktop.locator('.offer').count()==0

        desktop.screenshot(path=str(ROOT/'qa/desktop.png'),full_page=True)
        mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
        inject_site(mobile)
        assert mobile.locator('.reel-card').count()==10
        assert mobile.evaluate('document.documentElement.scrollWidth')<=394
        mobile.screenshot(path=str(ROOT/'qa/mobile.png'),full_page=True)
        browser.close()

def test_no_unauthorized_live_links_or_affiliate_snippets():
    html=(ROOT/'site/index.html').read_text()
    assert 'A8.netアフィリエイトID' not in html
    assert 'amazon-adsystem.com' not in html
    j=json.loads((ROOT/'site/price_output.json').read_text())
    assert j['summary']==[]
    assert len(json.loads((ROOT/'site/content.json').read_text())['reels'])==10

def test_all_video_assets_have_mobile_profile():
    assets=sorted((ROOT/'site/media/reels').glob('reel*.mp4'))
    if not assets:
        import pytest
        pytest.skip('Render videos with: python scripts/render_reels.py')
    assert len(assets)==10
    for p in assets:
        result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height','-of','json',str(p)],capture_output=True,text=True,check=True)
        j=json.loads(result.stdout)
        assert abs(float(j['format']['duration'])-12)<.15
        assert any(s.get('codec_name')=='h264' and s.get('width')==1080 and s.get('height')==1920 for s in j['streams'])
        assert any(s.get('codec_name')=='aac' for s in j['streams'])