"""Reproducibly bundle the local-first EEMON portal as one offline HTML file."""
from pathlib import Path
import base64
import json

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
SRC=(SITE/'index.html').read_text('utf-8')
CSS=(SITE/'style.css').read_text('utf-8')
JS=(SITE/'app.js').read_text('utf-8')
PAYLOAD={x:json.loads((SITE/x).read_text('utf-8')) for x in ('guides.json','reels.json','price_output.json')}
ASSETS={p.stem:'data:image/svg+xml;base64,'+base64.b64encode(p.read_bytes()).decode('ascii') for p in (SITE/'assets').glob('*.svg')}
VIDEOS={p.stem:'data:video/mp4;base64,'+base64.b64encode(p.read_bytes()).decode('ascii') for p in (SITE/'media/reels').glob('reel*.mp4')}

def script_data(obj):
    return json.dumps(obj,ensure_ascii=True,separators=(',',':')).replace('</','<\\/')

# One large JS payload, no external JS/CSS/video and no external API access.
PRELOAD='<script>window.__EEMON_DATA='+script_data(PAYLOAD)+';window.__EEMON_ASSETS='+script_data(ASSETS)+';window.__EEMON_VIDEOS='+script_data(VIDEOS)+''';
window.fetch=async function(path){if(path==='/api/health')return {ok:true,json:async()=>({remote_ai_available:false})};
if(!(path in window.__EEMON_DATA))return {ok:false};return {ok:true,json:async()=>window.__EEMON_DATA[path]}};</script>'''
SRC=SRC.replace('<link rel="icon" href="assets/logo.svg" type="image/svg+xml">',
     '<link rel="icon" href="'+ASSETS['logo']+'" type="image/svg+xml">')
SRC=SRC.replace('<link rel="stylesheet" href="style.css">','<style>'+CSS+'</style>')
SRC=SRC.replace('<script src="app.js" defer></script>',PRELOAD+'<script>'+JS+'</script>')
assert 'src="app.js"' not in SRC and 'href="style.css"' not in SRC
assert SRC.count('data:video/mp4;base64,') == 10
OUT=ROOT/'EEMON_買い物ポータル_体験版.html'
OUT.write_text(SRC,encoding='utf-8')
print('Offline HTML',OUT,OUT.stat().st_size,'bytes, videos',len(VIDEOS))