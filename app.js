(()=>{
'use strict';
const $=id=>document.getElementById(id);
const KEY='eemon-mobile-v2';
const FALLBACK={schema_version:2,updated_at:'2026-11-07',room_url:'https://room.rakuten.co.jp/eemon_sagashi_papa/items',pending:[],published:[{id:'epson-ew-056a',name:'EPSON Colorio EW-056A',date:'2026-11-06',room_post:'https://room.rakuten.co.jp/eemon_sagashi_papa/1700400007475108',url:'https://item.rakuten.co.jp/epson/ew-056a/'},{id:'solow-pedal-twin-35l',name:'SOLOW ペダルオープンツイン35L',date:'2026-11-07',room_post:null,url:'https://item.rakuten.co.jp/air-rhizome/toh-solow-35l/'}],price_reviews:[]};
let feed=FALLBACK;
let device={added:[],approved:{},reported:{}};
try{const x=JSON.parse(localStorage.getItem(KEY)||'{}');if(Array.isArray(x.added))device.added=x.added;if(x.approved&&typeof x.approved==='object')device.approved=x.approved;if(x.reported&&typeof x.reported==='object')device.reported=x.reported;}catch{}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(device));return true;}catch{return false;}};
const node=(tag,label,cls)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(label!==undefined&&label!==null)x.textContent=String(label);return x;};
const btn=(label,fn,cls='secondary')=>{const b=node('button',label,cls);b.type='button';b.addEventListener('click',fn);return b;};
const link=(label,url,cls='button secondary')=>{if(!safeLink(url))return node('span','リンク要確認','muted small');const x=node('a',label,cls);x.href=url;x.target='_blank';x.rel='noopener noreferrer';return x;};
const validItemUrl=s=>{try{const u=new URL(s);return u.protocol==='https:'&&u.hostname==='item.rakuten.co.jp'&&u.pathname.split('/').filter(Boolean).length>=2;}catch{return false;}};
const validRoomUrl=s=>{try{const u=new URL(s);return u.protocol==='https:'&&u.hostname==='room.rakuten.co.jp';}catch{return false;}};
const safeLink=s=>{try{const u=new URL(s);return u.protocol==='https:'&&['item.rakuten.co.jp','room.rakuten.co.jp','search.rakuten.co.jp'].includes(u.hostname)&&!u.username&&!u.password;}catch{return false;}};
const ageDays=date=>{if(!/^\d{4}-\d{2}-\d{2}$/.test(date||''))return Infinity;const t=Date.parse(date+'T00:00:00+09:00');return Number.isFinite(t)?Math.floor((Date.now()-t)/86400000):Infinity;};
const idOK=s=>typeof s==='string'&&/^[a-z0-9][a-z0-9_-]{2,79}$/.test(s);
function validItem(i){return i&&idOK(i.id)&&typeof i.name==='string'&&i.name.length<=150&&validItemUrl(i.url)&&typeof i.caption==='string'&&i.caption.length>0&&i.caption.length<=500;}
function validateFeed(f){return f&&f.schema_version===2&&validRoomUrl(f.room_url)&&Array.isArray(f.pending)&&Array.isArray(f.published)&&Array.isArray(f.price_reviews)&&f.pending.every(validItem)&&f.published.every(x=>x&&idOK(x.id)&&validItemUrl(x.url));}
let toastTimer;
function toast(msg){const x=$('toast');x.textContent=msg;x.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>{x.hidden=true;},4200);}
async function copy(s){try{await navigator.clipboard.writeText(s);return true;}catch{}
  const e=node('textarea');e.value=s;e.style.cssText='position:fixed;opacity:0;left:-5000px';document.body.appendChild(e);e.focus();e.select();let ok=false;try{ok=document.execCommand('copy');}catch{}e.remove();return ok;}
function allCandidates(){const publishedIds=new Set(feed.published.map(x=>x.id)),publishedUrls=new Set(feed.published.map(x=>x.url));const seenIds=new Set(),seenUrls=new Set();return [...feed.pending,...device.added].filter(x=>{if(!validItem(x)||publishedIds.has(x.id)||publishedUrls.has(x.url)||seenIds.has(x.id)||seenUrls.has(x.url))return false;if(x.observed_at&&ageDays(x.observed_at)>7)return false;seenIds.add(x.id);seenUrls.add(x.url);return true;});}
function setReported(item){device.reported[item.id]=new Date().toISOString();save();render();const text='Project EEMON｜楽天ROOMで投稿完了を押したので公開確認して。商品：'+item.name+' / 楽天商品ページ：'+item.url+' / 自分のROOM：'+feed.room_url;
  copy(text).then(ok=>toast(ok?'報告文をコピーしたで。ChatGPTに貼り付けてな。':'ChatGPTで投稿確認を依頼してな。'));}
function renderPending(){const items=allCandidates();$('pending-count').textContent=items.filter(x=>!device.approved[x.id]).length;$('reported-count').textContent=items.filter(x=>device.reported[x.id]).length;
  const holder=$('pending');holder.replaceChildren();if(!items.length)holder.appendChild(node('div','いま承認待ちの商品はないで。次のAI選定を待てばOK。','empty'));
  for(const item of items){const card=node('article',null,'card'),approved=Boolean(device.approved[item.id]),reported=Boolean(device.reported[item.id]);
    card.appendChild(node('span',reported?'公開確認待ち（自己報告）':approved?'承認済み・ROOM未確認':'承認待ち','tag'+(reported?' warn':approved?' blue':'')));
    card.appendChild(node('h3',item.name));if(item.observed_at)card.appendChild(node('p','商品確認日：'+item.observed_at+'（購入条件は投稿前に再確認）','muted small'));if(item.shop)card.appendChild(node('p','紹介する店舗：'+item.shop,'muted small'));
    if(item.price_yen!==undefined)card.appendChild(node('p','参考価格：'+Number(item.price_yen).toLocaleString('ja-JP')+'円（投稿前に要確認）','muted small'));if(item.price_note)card.appendChild(node('p','価格条件：'+item.price_note,'muted small'));
    if(item.differentiator)card.appendChild(node('p','🙆 違い：'+item.differentiator,'small'));
    const cap=node('div',item.caption,'description');card.appendChild(cap);
    const b=node('div',null,'buttons');b.appendChild(btn(approved?'① 原稿をもう一度コピー':'① 承認して原稿をコピー',async()=>{const ok=await copy(item.caption);if(!ok){toast('コピーできへんかった。紹介文を長押ししてコピーしてな。');return;}device.approved[item.id]=new Date().toISOString();save();render();toast('コピー済み！②楽天市場に進んでな。');},'primary'));
    if(approved){b.appendChild(link('② 楽天市場で「ROOMに投稿」を選ぶ',item.url,'button green'));b.appendChild(btn('③ 楽天公式で完了した → 報告文コピー',()=>setReported(item),'secondary'));}
    if(reported)b.appendChild(link('自分のROOMで公開を確かめる',feed.room_url,'button secondary'));
    card.appendChild(b);holder.appendChild(card);}
}
function renderReviews(){const holder=$('reviews');holder.replaceChildren();if(!feed.price_reviews.length)holder.appendChild(node('div','価格見直し対象はまだないで。','empty'));
  for(const item of feed.price_reviews){const card=node('article',null,'card');card.appendChild(node('span','価格比較・要再確認','tag warn'));card.appendChild(node('h3',item.name));card.appendChild(node('p','調査日：'+item.observed_at,'muted small'));if(ageDays(item.observed_at)>7){card.appendChild(node('p','調査から7日以上。古い金額は表示せず、楽天の最新情報を確認してな。','muted small'));if(item.source_url)card.appendChild(link('最新の価格を確認',item.source_url,'button secondary'));holder.appendChild(card);continue;}
    const offers=[...(item.offers||[])].filter(x=>Number.isFinite(x.price_yen)&&Number.isFinite(x.shipping_yen)).sort((a,b)=>(a.price_yen+a.shipping_yen)-(b.price_yen+b.shipping_yen));
    if(offers.length>1){const delta=(offers[offers.length-1].price_yen+offers[offers.length-1].shipping_yen)-(offers[0].price_yen+offers[0].shipping_yen);card.appendChild(node('p','最安掲載例と最高掲載例の差：'+delta.toLocaleString('ja-JP')+'円','saving'));}
    const list=node('div',null,'price-list');for(const o of offers){const row=node('div',null,'price-row');const a=node('div');a.appendChild(node('b',o.shop+'：'+(o.price_yen+o.shipping_yen).toLocaleString('ja-JP')+'円'));a.appendChild(node('span',o.condition||'購入前に要確認'));row.appendChild(a);if(o.link)row.appendChild(link('商品を見る',o.link,'inline-link'));list.appendChild(row);}card.appendChild(list);
    card.appendChild(node('p',item.note||'掲載価格と在庫は投稿前に確認してな。','muted small'));if(item.source_url)card.appendChild(link('楽天で最新の価格を比較',item.source_url,'button secondary'));holder.appendChild(card);}
}
function renderHistory(){$('published-count').textContent=feed.published.length;const holder=$('published');holder.replaceChildren();for(const item of feed.published){const row=node('div',null,'history'),a=node('div');a.appendChild(node('b',item.name));a.appendChild(node('p',item.date,'muted small'));row.appendChild(a);row.appendChild(link('ROOMを見る',item.room_post||feed.room_url,'inline-link'));holder.appendChild(row);}}
function render(){$('feed-date').textContent='更新 '+(feed.updated_at||'未確認');renderPending();renderReviews();renderHistory();}
$('manual-form').addEventListener('submit',event=>{event.preventDefault();const f=new FormData(event.currentTarget);const item={id:'manual-'+Date.now(),name:String(f.get('name')||'').trim(),url:String(f.get('url')||'').trim(),caption:String(f.get('caption')||'').trim()};if(!validItem(item)){toast('正しい楽天市場の商品URLと500文字以内の紹介文が必要やで。');return;}
  const duplicate=[...feed.pending,...feed.published,...device.added].some(x=>x.url===item.url);if(duplicate){toast('同じ店舗の商品URLは登録済みやで。');return;}device.added.push(item);save();event.currentTarget.reset();render();toast('候補を保存したで。');});
$('export').addEventListener('click',()=>{const blob=new Blob([JSON.stringify({schema_version:2,exported_at:new Date().toISOString(),device},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=node('a');a.href=url;a.download='eemon-device-backup.json';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);});
$('clear').addEventListener('click',()=>{if(confirm('このiPhone内の承認と追加候補だけ削除する？楽天ROOMの公開内容は消えへんで。')){device={added:[],approved:{},reported:{}};save();render();toast('端末内記録を消去したで。');}});
async function importFromFragment(){const prefix='#add=';if(!location.hash.startsWith(prefix))return;const raw=location.hash.slice(prefix.length);if(raw.length>5000){toast('候補データが長すぎるで。');return;}try{const normalized=raw.replace(/-/g,'+').replace(/_/g,'/');const bytes=Uint8Array.from(atob(normalized),c=>c.charCodeAt(0));const item=JSON.parse(new TextDecoder().decode(bytes));if(!validItem(item))throw Error('invalid');if(![...feed.published,...feed.pending,...device.added].some(x=>x.id===item.id||x.url===item.url)){device.added.push(item);save();toast('AI候補を端末に取り込んだで。');}history.replaceState(null,'',location.pathname+location.search);}catch{toast('候補を読み込めなかったで。');}}
async function load(){render();try{const r=await fetch('./feed.json?ts='+Date.now(),{cache:'no-store',credentials:'omit'});if(!r.ok)throw Error('http-'+r.status);const result=await r.json();if(!validateFeed(result))throw Error('invalid-feed');feed=result;const stale=ageDays(feed.updated_at)>2;$('connection').className='live '+(stale?'warn':'ok');$('connection').textContent=stale?'データ更新待ち':'フィード取得済';}catch(e){$('connection').className='live warn';$('connection').textContent='保存版を表示';}await importFromFragment();render();}
load();
})();