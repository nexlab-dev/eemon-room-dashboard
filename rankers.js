(() => {
'use strict';
const KEY='eemon-ranker-reviewed-v1';
const $=id=>document.getElementById(id);
let data=[];
let states={};
try { const p=JSON.parse(localStorage.getItem(KEY)||'{}');if(p&&typeof p==='object'&&!Array.isArray(p)) states=p; } catch {}
function persist(){try{localStorage.setItem(KEY,JSON.stringify(states));return true;}catch{return false;}}
function element(tag,text,cls){
 const e=document.createElement(tag); if(typeof text==='string')e.textContent=text;if(cls)e.className=cls; return e;
}
function safeProfile(url,id){
 try{const u=new URL(url);return u.protocol==='https:'&&u.hostname==='room.rakuten.co.jp'&&
  u.username===''&&u.password===''&&u.search===''&&u.hash===''&&
  u.pathname===('/'+id+'/items')&&/^[a-z0-9_]{6,64}$/.test(id);}
 catch{return false;}
}
function valid(x){
 return x&&typeof x.id==='string'&&safeProfile(x.url,x.id)&&
 typeof x.name==='string'&&x.name.length>0&&x.name.length<130&&
 ['S','A','B'].includes(x.rank)&&typeof x.reason==='string'&&
 typeof x.verified_at==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(x.verified_at);
}
function status(id){return ['followed_reported','skipped'].includes(states[id])?states[id]:'';}
function render(){
 const list=$('ranker-candidates');list.replaceChildren();
 $('ranker-total').textContent=String(data.length);
 $('ranker-followed').textContent=String(data.filter(x=>status(x.id)==='followed_reported').length);
 $('ranker-unreviewed').textContent=String(data.filter(x=>!status(x.id)).length);
 if(!data.length)list.appendChild(element('p','確認済み候補はまだないで。','empty'));
 for(const x of data){
  const card=element('article',null,'card');
  const st=status(x.id);
  card.appendChild(element('span','ランク '+x.rank,'tag'+(x.rank==='S'?'':' blue')));
  card.appendChild(element('h3',x.name));
  card.appendChild(element('p',x.category||'','muted small'));
  card.appendChild(element('p',x.reason));
  card.appendChild(element('p','ランク確認日：'+x.verified_at,'muted small'));
  if(st==='followed_reported')card.appendChild(element('p','✅ フォローした（本人メモ・楽天側未照合）','small'));
  if(st==='skipped')card.appendChild(element('p','今回は見送り（端末内メモ）','small'));
  const buttons=element('div',null,'buttons');
  const a=element('a','① 楽天ROOMでプロフィールを開く','button green');
  a.href=x.url;a.target='_blank';a.rel='noopener noreferrer';
  buttons.appendChild(a);
  const b=element('button',st==='followed_reported'?'② フォローメモを取り消す':'② 公式で押したら「フォローした」を記録','secondary');
  b.type='button';
  b.addEventListener('click',()=>{if(st==='followed_reported')delete states[x.id];else states[x.id]='followed_reported';persist();render();});
  buttons.appendChild(b);
  const c=element('button',st==='skipped'?'見送りを解除':'今回は見送る','tertiary');
  c.type='button';c.addEventListener('click',()=>{if(st==='skipped')delete states[x.id];else states[x.id]='skipped';persist();render();});
  buttons.appendChild(c);
  card.appendChild(buttons);list.appendChild(card);
 }
}
async function load(){
 try{
  const r=await fetch('./rankers.json?fresh='+Date.now(),{cache:'no-store'});
  if(!r.ok)throw new Error('HTTP '+r.status);
  const x=await r.json();
  if(x.schema_version!==1||!Array.isArray(x.candidates)||x.candidates.length>30||
  !x.candidates.every(valid))throw new Error('候補データの形式が不正');
  const seen=new Set();data=x.candidates.filter(z=>{if(seen.has(z.id))return false;seen.add(z.id);return true;})
   .sort((a,b)=>(a.priority||99)-(b.priority||99));
  $('ranker-date').textContent='最終更新 '+x.updated_at;
  $('ranker-connection').textContent='最新データ取得';$('ranker-connection').className='live ok';
 }catch{
  $('ranker-connection').textContent='データ取得失敗';$('ranker-connection').className='live warn';
 }
 render();
}
load();
})();