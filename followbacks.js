(()=>{
'use strict';
const $=id=>document.getElementById(id);
const KEY='eemon-followback-manual-v1';
let rows=[],metadata={};
let states={};
try{const x=JSON.parse(localStorage.getItem(KEY)||'{}');if(x&&typeof x==='object'&&!Array.isArray(x))states=x;}catch{}
function save(){try{localStorage.setItem(KEY,JSON.stringify(states));return true;}catch{return false;}}
function safe(x){
 if(!x||typeof x.id!=='string'||typeof x.url!=='string')return false;
 if(!/^[a-z0-9_]{3,64}$/.test(x.id))return false;
 try{const u=new URL(x.url);return u.protocol==='https:'&&u.hostname==='room.rakuten.co.jp'&&!u.username&&!u.password&&!u.search&&!u.hash&&u.pathname==='/'+x.id+'/items';}
 catch{return false;}
}
function stamp(id){const x=states[id];return x&&typeof x==='object'&&['done','skip'].includes(x.status)?x.status:'';}
function remaining(){return rows.filter(x=>!stamp(x.id));}
function el(tag,text){const e=document.createElement(tag);e.textContent=text;return e;}
function render(){
 const pending=remaining();
 $('total').textContent=String(rows.length);
 $('remaining').textContent=String(pending.length);
 $('done').textContent=String(rows.filter(x=>stamp(x.id)==='done').length);
 $('source-info').textContent='公開リスト確認日：'+(metadata.checked_at||'未取得')+'｜フォロワー '+(metadata.follower_count??'不明')+' ／ フォロー中 '+(metadata.following_count??'不明')+'。'+(metadata.complete?'両一覧を照合済み。':'一覧は一部のみ確認。未表示分がある可能性あり。');
 const next=pending[0];
 $('index').textContent=next?'あと '+pending.length+' 人':'';
 $('next-name').textContent=next?(next.name||next.id):'未処理候補はないで！';
 $('next-note').textContent=next?'公開ROOMのプロフィールで相手を確認して、フォローした場合だけ次のボタンを押してな。':'次回の公開フォロワー確認で新しい候補が増えたら表示するで。';
 const a=$('open-profile');a.href=next?next.url:'https://room.rakuten.co.jp/eemon_sagashi_papa/items';
 a.textContent=next?'① '+(next.name||next.id)+' さんのROOMへ':'自分のROOMを開く';
 $('mark-done').disabled=!next;$('mark-skip').disabled=!next;
 const list=$('list');list.replaceChildren();
 for(const row of rows){
  const item=el('div','');item.className='history';
  const left=el('div',(row.name||row.id)+' ／ '+({done:'本人メモ：フォロー済み',skip:'見送り'}[stamp(row.id)]||'未処理'));
  const link=el('a','ROOM');link.href=row.url;link.target='_blank';link.rel='noopener noreferrer';
  item.append(left,link);
  if(stamp(row.id)){const b=el('button','戻す');b.type='button';b.className='tertiary';b.style.minHeight='38px';b.addEventListener('click',()=>{delete states[row.id];save();render();});item.appendChild(b);}
  list.appendChild(item);
 }
}
function mark(status){
 const next=remaining()[0];if(!next)return;
 states[next.id]={status,at:new Date().toISOString()};
 if(!save())alert('iPhone内の保存に失敗したで。ストレージ設定を確認してな。');
 render();window.scrollTo({top:0,behavior:'smooth'});
}
$('mark-done').addEventListener('click',()=>mark('done'));
$('mark-skip').addEventListener('click',()=>mark('skip'));
async function load(){
 try{
  const r=await fetch('./followbacks.json?fresh='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);
  const d=await r.json();if(d.schema_version!==1||!Array.isArray(d.candidates)||d.candidates.length>150||!d.candidates.every(safe))throw Error('invalid-data');
  const unique=new Set();rows=d.candidates.filter(x=>{if(unique.has(x.id))return false;unique.add(x.id);return true;});
  metadata=d;
  $('connection').textContent='最新データ取得';$('connection').className='live ok';
 }catch(e){$('connection').textContent='候補取得できず';$('connection').className='live warn';}
 render();
}
load();
})();