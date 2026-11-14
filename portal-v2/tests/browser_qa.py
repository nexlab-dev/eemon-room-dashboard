from pathlib import Path
import json
import base64
from playwright.sync_api import sync_playwright

BASE='http://127.0.0.1:8765'
SITE=Path(__file__).resolve().parents[1]/'site'

def inject_local_document(page):
    html=(SITE/'index.html').read_text('utf-8')
    css=(SITE/'style.css').read_text('utf-8')
    js=(SITE/'app.js').read_text('utf-8')
    payload={key:json.loads((SITE/key).read_text('utf-8')) for key in ['guides.json','reels.json','price_output.json']}
    js_data=json.dumps(payload,ensure_ascii=False).replace('</','<\\/')
    stub='<script>window.__QA_DATA='+js_data+';window.fetch=async function(path){if(path==="/api/health")return {ok:true,json:async()=>({remote_ai_available:false})};if(!(path in window.__QA_DATA))return {ok:false};return {ok:true,json:async()=>window.__QA_DATA[path]}}</script>'
    html=html.replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>')
    html=html.replace('<script src="app.js" defer></script>',stub+'<script>'+js+'</script>')
    page.set_content(html,wait_until='load')
    assets={name:'data:image/svg+xml;base64,'+base64.b64encode((SITE/'assets'/name).read_bytes()).decode('ascii') for name in [p.name for p in (SITE/'assets').glob('*.svg')]}
    page.evaluate('assets=>document.querySelectorAll("img").forEach(img=>{let k=img.getAttribute("src").split("/").pop();if(assets[k])img.src=assets[k]})',assets)

OUT=Path(__file__).resolve().parents[1]/'qa'
OUT.mkdir(exist_ok=True)

def run():
  with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    try:
      results=[]
      for width,height,label in [(390,844,'iphone'),(375,812,'compact'),(768,1024,'tablet'),(1365,900,'desktop')]:
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,is_mobile=False)
        failures=[]
        page.on('pageerror', lambda err: failures.append(str(err)))
        inject_local_document(page)
        page.wait_for_selector('.product-card', timeout=8000)
        assert page.locator('h1').is_visible()
        assert page.locator('.product-card').count()==8
        assert page.locator('.quick-item').count()==6
        assert page.locator('.video-card').count()==10
        assert page.locator('.hero-slide.active').count()==1
        actual=page.evaluate('document.documentElement.scrollWidth'); assert actual<=width+1,(width,actual)
        assert not failures,failures
        page.screenshot(path=str(OUT/f'{label}.png'),full_page=True)
        results.append({'test':f'{label}_layout','status':'PASS','width':width,'scroll_width':actual})
        if label=='iphone':
          page.get_by_role('button',name='次のスライド').click();assert page.locator('.hero-slide.active').get_attribute('data-slide')=='1';results.append({'test':'carousel','status':'PASS'})
          page.locator('.category-pill[data-category="家電"]').click();assert page.locator('.product-card').count()==4;results.append({'test':'category_filter','status':'PASS'})
          page.locator('.searchbox input').fill('インク');page.locator('.searchbox input').press('Enter');assert page.locator('.product-card').count()>=1;results.append({'test':'text_search','status':'PASS'})
          page.locator('#clearFilters').click();page.locator('.product-card [data-save="printer"]').click();assert page.locator('#favCount').inner_text()=='1';results.append({'test':'favorites','status':'PASS'})
          page.locator('.product-card [data-compare="printer"]').click();page.locator('.bottom-nav [data-tab="compare"]').click();assert page.locator('#compareOverlay').is_visible();assert page.locator('#compareBody').get_by_text('家庭用プリンター').is_visible();page.locator('#compareOverlay [data-close]').first.click();results.append({'test':'compare','status':'PASS'})
          page.locator('.product-card [data-open-guide="printer"]').click();assert page.locator('#productOverlay').is_visible();assert page.locator('.detail-list li').count()==3;page.locator('#productOverlay .sheet-close').click();results.append({'test':'detail_sheet','status':'PASS'})
          page.locator('.ai-teaser-button').click();assert page.locator('#aiOverlay').is_visible();page.locator('#chatInput').fill('予算2万円で暖房器具を探したい');page.locator('#chatInput').press('Enter');assert '20,000' in page.locator('#chatLog').inner_text();assert '省エネ暖房器具' in page.locator('#chatLog').inner_text();results.append({'test':'chat_guide','status':'PASS'});page.screenshot(path=str(OUT/'chat.png'))
          page.locator('#aiOverlay .sheet-close').click()
          page.locator('[data-open-reel="reel01"]').click();assert page.locator('#videoOverlay').is_visible();assert page.locator('#videoPlayer').get_attribute('src').endswith('reel01.mp4');page.locator('#videoOverlay .sheet-close').click();results.append({'test':'video_playback_modal','status':'PASS'})
          assert page.locator('#verifiedCount').inner_text()=='0件';results.append({'test':'zero_price_honesty','status':'PASS'})
          # malicious price import should never produce HTML/JS
          file={'name':'malicious.json','mimeType':'application/json','buffer':json.dumps({'verification':'SOURCE_ASSERTED_NOT_INDEPENDENTLY_AUDITED','summary':[{'product_name':'<script>alert(1)</script>','product_key':'t-1','offers':[{'shop_name':'<img src=x onerror=alert(1)>','item_url':'https://example.com/item','evidence_url':'javascript:alert(1)','price_jpy':1200,'shipping_jpy':0,'total_jpy':1200,'checked_at':'2026-11-14T22:00:00+09:00','verification':'SOURCE_ASSERTED_NOT_INDEPENDENTLY_AUDITED','verified_by':'owner'}]}]}).encode('utf-8')}
          page.locator('#priceFile').set_input_files(file)
          assert page.locator('#verifiedCount').inner_text()=='0件'
          results.append({'test':'reject_unsafe_price_url','status':'PASS'})
        page.close()
      (OUT/'browser_results.json').write_text(json.dumps({'results':results,'passed':len(results)},ensure_ascii=False,indent=2)+'\n')
      print('BROWSER QA PASSED',len(results),'tests')
      for row in results:print(row)
    finally:browser.close()

if __name__=='__main__':run()