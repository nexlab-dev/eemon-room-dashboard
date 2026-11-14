'use strict';
(() => {
  const $ = sel => document.querySelector(sel);
  const $$ = sel => [...document.querySelectorAll(sel)];
  const esc = value => String(value ?? '').replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[s]));
  const nf = n => new Intl.NumberFormat('ja-JP').format(n);
  const CATEGORY = [
    {name:'家電', emoji:'🖨️', color:'#fff0e8'},
    {name:'カー用品', emoji:'🚗', color:'#ecf1fc'},
    {name:'日用品', emoji:'🧺', color:'#f6ecff'},
    {name:'防災', emoji:'🔋', color:'#e8f5ef'},
    {name:'食品', emoji:'🍚', color:'#fff5d8'},
    {name:'デジタル', emoji:'📱', color:'#ecf3fe'},
  ];
  const HINTS = ['予算2万円で暖房器具を探したい','プリンターのインク代が気になる','防災用品、何から揃えたらいい？','車のLEDライトを交換したい'];
  const state = { guides:[], reels:[], category:'すべて', query:'', sort:'featured', showAll:false, saved:new Set(), recent:[], compare:[], slides:0, activeVideo:null, priceGroups:[], privacyMode:true, apiEnabled:false, aiMode:'ガイド応答' };
  const PUBLIC_ASSET_IDS = new Set(['printer','heater','humidifier','vacuum','car','tire','power','bag','storage','rice','ink','phone']);
  let toastTimer = 0;
  let remoteAvailable = false;
  let lastFocus = null;

  function readStore(key, fallback) {
    try { const x=JSON.parse(localStorage.getItem('eemon_v2_'+key) || 'null'); return x ?? fallback; } catch { return fallback; }
  }
  function saveStore(key, value) { try { localStorage.setItem('eemon_v2_'+key,JSON.stringify(value)); } catch {} }
  function setupStored() {
    state.saved = new Set(readStore('favorites',[]).filter(x=>typeof x==='string').slice(0,100));
    state.recent = readStore('recent',[]).filter(x=>typeof x==='string').slice(0,12);
    state.compare = readStore('compare',[]).filter(x=>typeof x==='string').slice(0,3);
  }
  function notice(message) {
    const el=$('#toast'); el.textContent=message; el.classList.add('show');
    clearTimeout(toastTimer); toastTimer=setTimeout(()=>el.classList.remove('show'),2500);
  }
  function byId(id){return state.guides.find(g=>g.id===id)}
  function guideImg(g){const art=PUBLIC_ASSET_IDS.has(g.art)?g.art:'storage';return (window.__EEMON_ASSETS&&window.__EEMON_ASSETS[art])||`assets/${art}.svg`}
  function safeId(s){return typeof s==='string' && /^[a-z][a-z\d-]{1,30}$/.test(s)}
  function toBrowse(){ $('#browse').scrollIntoView({behavior:'smooth',block:'start'}); }
  function scrollToId(id){const node=document.getElementById(id);if(node)node.scrollIntoView({behavior:'smooth',block:'start'});}
  function renderQuick(){ $('#quickCategories').innerHTML=CATEGORY.map(c=>`<button type="button" class="quick-item" data-category="${esc(c.name)}"><span class="quick-icon" style="background:${c.color}" aria-hidden="true">${c.emoji}</span><b>${esc(c.name)}</b></button>`).join(''); }
  function setCategory(cat){
    state.category=CATEGORY.some(c=>c.name===cat)?cat:'すべて'; state.showAll=false;
    $$('.category-pill').forEach(b=>{const selected=b.dataset.category===state.category;b.classList.toggle('active',selected);b.setAttribute('aria-pressed',String(selected))});
    renderProducts(); toBrowse();
  }
  function score(g, term){
    const q=term.trim().toLocaleLowerCase('ja-JP');if(!q)return 1;
    const fields=[g.title,g.category,g.tagline,g.for,...g.tags].map(v=>String(v).toLocaleLowerCase('ja-JP'));
    if(fields.some(x=>x.includes(q)))return 10;
    return q.split(/[\s　]+/).reduce((s,token)=>s+fields.some(x=>x.includes(token))*(token.length>=2?2:0),0);
  }
  function filtered(){
    let list=state.guides.filter(g=>(state.category==='すべて'||g.category===state.category)&&score(g,state.query)>0);
    if(state.sort==='name')list.sort((a,b)=>a.title.localeCompare(b.title,'ja'));
    if(state.sort==='category')list.sort((a,b)=>a.category.localeCompare(b.category,'ja')||a.title.localeCompare(b.title,'ja'));
    return list;
  }
  function card(g){
    return `<article class="product-card" data-guide-card="${esc(g.id)}">
      <button type="button" class="product-open" data-open-guide="${esc(g.id)}" aria-label="${esc(g.title)}の選び方を開く"><div class="product-visual"><img src="${guideImg(g)}" alt="${esc(g.title)}のオリジナルイラスト" loading="lazy"><span class="tag">${esc(g.category)}の選び方</span></div><div class="product-copy"><h3>${esc(g.title)}</h3><p>${esc(g.tagline)}</p></div><div class="product-meta"><span>購入前チェック ✓</span><small>実価格は未確認</small></div></button>
      <div class="card-actions"><button type="button" data-save="${esc(g.id)}" aria-pressed="${state.saved.has(g.id)}" class="${state.saved.has(g.id)?'is-saved':''}">${state.saved.has(g.id)?'♥ 保存済み':'♡ 保存する'}</button><button type="button" data-compare="${esc(g.id)}" aria-pressed="${state.compare.includes(g.id)}">${state.compare.includes(g.id)?'✓ 比較中':'＋ 比較する'}</button></div></article>`;
  }
  function renderProducts(){
    const result=filtered();const subset=state.showAll?result:result.slice(0,8);
    $('#productGrid').innerHTML=subset.map(card).join('');
    $('#loadMoreWrap').hidden=result.length<=subset.length;$('#emptyResults').hidden=result.length>0;
    const filtering=state.category!=='すべて'||Boolean(state.query);
    $('#activeFilters').hidden=!filtering;
    $('#filterSummaryText').textContent=(state.category!=='すべて'?state.category+' / ':'')+(state.query?'「'+state.query+'」 / ':'')+result.length+'件のガイド';
    $('#resultsCaption').textContent=state.query?`「${state.query}」の検索結果 ${result.length}件`:`${result.length}件の買い物ガイドから探せます。`;
    $('#favCount').textContent=state.saved.size;$('#favCount').hidden=!state.saved.size;
    $('#compareCount').textContent=state.compare.length;$('#compareCount').hidden=!state.compare.length;
  }
  function toggleSave(id){if(!byId(id))return;if(state.saved.has(id))state.saved.delete(id);else state.saved.add(id);saveStore('favorites',[...state.saved]);renderProducts();notice(state.saved.has(id)?'お気に入りに保存したで ♡':'お気に入りを解除したで')}
  function toggleCompare(id){if(!byId(id))return;const i=state.compare.indexOf(id);if(i>=0){state.compare.splice(i,1)}else if(state.compare.length>=3){notice('比較は3テーマまでやで');return;}else{state.compare.push(id)}saveStore('compare',state.compare);renderProducts();notice(state.compare.includes(id)?'比較リストに追加したで':'比較リストから外したで')}
  function openOverlay(id){
    const target=document.getElementById(id);if(!target)return;
    lastFocus=document.activeElement;target.hidden=false;document.body.style.overflow='hidden';
    const close=target.querySelector('[data-close]');if(close)close.focus();
  }
  function closeOverlay(id){const node=document.getElementById(id);if(!node)return;node.hidden=true;
    if(id==='videoOverlay')$('#videoPlayer').pause();
    if($$('.overlay:not([hidden])').length===0)document.body.style.overflow='';
    if(lastFocus && typeof lastFocus.focus==='function')lastFocus.focus();lastFocus=null;
  }
  function renderRecent(){
    const guides=state.recent.map(byId).filter(Boolean).slice(0,4);
    $('#recentSection').hidden=!guides.length;
    $('#recentRail').innerHTML=guides.map(g=>`<button class="recent-card" type="button" data-open-guide="${esc(g.id)}"><img src="${guideImg(g)}" alt=""><span><b>${esc(g.title)}</b><small>もう一度確認する ↗</small></span></button>`).join('');
  }
  function openGuide(id){
    const g=byId(id);if(!g)return;
    state.recent=[g.id,...state.recent.filter(x=>x!==g.id)].slice(0,12);saveStore('recent',state.recent);renderRecent();
    $('#detailBody').innerHTML=`<div class="detail-cover"><img src="${guideImg(g)}" alt="${esc(g.title)}のイラスト"></div><div class="detail-tag">EEMON / BUYING GUIDE　${esc(g.category)}</div><h2 id="detailTitle">${esc(g.title)}</h2><p class="detail-intro">${esc(g.tagline)}<br>${esc(g.for)}</p><h3>買う前のチェックリスト</h3><ul class="detail-list">${g.points.map(p=>`<li>${esc(p)}</li>`).join('')}</ul><div class="detail-actions"><button type="button" class="button-solid" data-compare="${esc(g.id)}">${state.compare.includes(g.id)?'比較リストから外す':'比較リストに追加 ＋'}</button><button type="button" class="button-subtle" data-save="${esc(g.id)}">${state.saved.has(g.id)?'♥ 保存を解除':'♡ 保存する'}</button><button type="button" class="button-subtle" data-chat-about="${esc(g.id)}">AIに相談 ✦</button></div><p class="detail-warning">掲載内容はカテゴリー選びの一般的なガイドです。商品仕様・価格・在庫・口コミ・販売条件を確認した特定商品の販売ページではありません。</p>`;
    openOverlay('productOverlay');
  }
  function openCompare(){
    const guides=state.compare.map(byId).filter(Boolean);
    $('#compareBody').innerHTML=guides.length?`<div class="compare-table">${guides.map(g=>`<div class="compare-column"><img src="${guideImg(g)}" alt=""><h3>${esc(g.title)}</h3><small>${esc(g.category)}</small><ul>${g.points.map(p=>`<li>${esc(p)}</li>`).join('')}</ul><button type="button" data-remove-compare="${esc(g.id)}">比較から外す</button></div>`).join('')}</div><p class="compare-notice">同じ商品同士の価格比較ではなく、買う前の比較観点を横に並べる機能です。最大3テーマ。</p>`:`<div class="compare-empty"><span style="font-size:40px">☷</span><h3>比較リストは空です</h3><p>気になるテーマの「＋ 比較する」で追加できます。</p></div>`;
    openOverlay('compareOverlay');
  }
  function savedView(){
    state.category='すべて';state.query='';$('#searchInput').value='';
    $$('.category-pill').forEach(b=>{const s=b.dataset.category==='すべて';b.classList.toggle('active',s);b.setAttribute('aria-pressed',String(s))});
    const list=state.guides.filter(g=>state.saved.has(g.id));
    $('#productGrid').innerHTML=list.map(card).join('');$('#resultsCaption').textContent=`お気に入り ${list.length}件`;$('#activeFilters').hidden=false;$('#filterSummaryText').textContent='保存したガイド';$('#loadMoreWrap').hidden=true;
    $('#emptyResults').hidden=!!list.length;
    $('#emptyResults').querySelector('h3').textContent='保存したガイドはまだありません';
    toBrowse();notice('お気に入りを表示中 ♡');
  }
  function showSlide(index){state.slides=(index+3)%3;$$('.hero-slide').forEach(s=>s.classList.toggle('active',Number(s.dataset.slide)===state.slides));$$('.dot').forEach(d=>{const a=Number(d.dataset.carousel)===state.slides;d.classList.toggle('active',a);if(a)d.setAttribute('aria-current','true');else d.removeAttribute('aria-current')});}
  function renderReels(){
    $('#videoRail').innerHTML=state.reels.map(r=>`<button class="video-card" type="button" data-open-reel="${esc(r.id)}" aria-label="${esc(r.topic)} 動画を開く"><div class="video-thumb"><span class="video-number">EEMON / ${String(r.number).padStart(2,'0')}</span><span class="video-emoji">${{printer:'🖨️',bed:'🛏️',plug:'🔌',vacuum:'🧹',storage:'📦',car:'🚙',humidifier:'💧',sale:'🏷️',check:'✅',shopping:'🛒'}[r.icon]||'💡'}</span><span class="video-play">▶</span></div><div class="video-copy"><b>${esc(r.topic)}</b><small>${esc(r.category)} ・12秒</small></div></button>`).join('');
  }
  function openReel(id){const reel=state.reels.find(r=>r.id===id);if(!reel||!/^reel\d{2}$/.test(id))return;state.activeVideo=reel;$('#videoTitle').textContent=reel.topic;$('#videoCaption').textContent=reel.caption;const v=$('#videoPlayer');v.src=(window.__EEMON_VIDEOS&&window.__EEMON_VIDEOS[reel.id])||'media/reels/'+reel.id+'.mp4';v.load();openOverlay('videoOverlay')}
  function validHttps(value){try{const u=new URL(value);return u.protocol==='https:'&&u.hostname.includes('.')&&!u.username&&!u.password&&!/^\d{1,3}(?:\.\d{1,3}){3}$/.test(u.hostname)}catch{return false}}
  function validOffer(o){
    if(!o||typeof o!=='object'||o.verification!=='SOURCE_ASSERTED_NOT_INDEPENDENTLY_AUDITED')return false;
    if(!Number.isSafeInteger(o.price_jpy)||o.price_jpy<1||!Number.isSafeInteger(o.shipping_jpy)||o.shipping_jpy<0||!Number.isSafeInteger(o.total_jpy)||o.total_jpy!==o.price_jpy+o.shipping_jpy||o.total_jpy>1e8)return false;
    if(!validHttps(o.item_url)||!validHttps(o.evidence_url))return false;
    if(typeof o.shop_name!=='string'||!o.shop_name.trim()||typeof o.verified_by!=='string'||!o.verified_by.trim())return false;
    const age=Date.now()-Date.parse(o.checked_at);return Number.isFinite(age)&&age>=-300000&&age<=24*3600*1000;
  }
  function renderPrices(payload){
    state.priceGroups=[];
    if(payload&&payload.verification==='SOURCE_ASSERTED_NOT_INDEPENDENTLY_AUDITED'&&Array.isArray(payload.summary)){
      state.priceGroups=payload.summary.filter(g=>g&&typeof g.product_key==='string'&&Array.isArray(g.offers)).map(g=>({name:String(g.product_name||''),key:String(g.product_key),offers:g.offers.filter(validOffer).sort((a,b)=>a.total_jpy-b.total_jpy)})).filter(g=>g.offers.length>0);
    }
    const total=state.priceGroups.reduce((s,g)=>s+g.offers.length,0);$('#verifiedCount').textContent=total+'件';$('#priceState').textContent=total?'入力データ確認中':'データ待ち';
    $('#priceResults').innerHTML=state.priceGroups.map(g=>`<div class="price-group"><h4>${esc(g.name)} <small>${esc(g.key)}</small></h4><p class="price-note">入力記録を機械検査した結果。第三者による価格の独立監査は未実施。</p>${g.offers.map((o,i)=>`<div class="price-offer"><div><b>${i===0?'入力店舗内の最小総額：':''}${esc(o.shop_name)}</b><br><small>本体 ¥${nf(o.price_jpy)} ＋ 送料 ¥${nf(o.shipping_jpy)} / 確認 ${esc(new Date(o.checked_at).toLocaleString('ja-JP',{timeZone:'Asia/Tokyo'}))}</small><br><a target="_blank" rel="noopener noreferrer nofollow" href="${esc(o.evidence_url)}">原典を確認 ↗</a></div><strong>¥${nf(o.total_jpy)}</strong></div>`).join('')}</div>`).join('');
    if(total)notice('調査JSONを取り込み、条件を検査したで。原典を確認してな');
  }
  const tokenMap=[
    {pattern:/プリンタ|インク|印刷|年賀状/,ids:['printer','ink']},
    {pattern:/暖房|ヒーター|冬|電気代|寒い/,ids:['heater','humidifier']},
    {pattern:/掃除|軽い|コードレス|家事/,ids:['vacuum','storage']},
    {pattern:/車|タイヤ|LED|ライト|フォグ|バイク/,ids:['car-lamp','tire']},
    {pattern:/災害|防災|停電|非常|地震|備え/,ids:['power','emergency']},
    {pattern:/米|お米|食品|食事|保存/,ids:['rice']},
    {pattern:/スマホ|iPhone|充電|ケーブル/,ids:['smartphone','power']},
    {pattern:/収納|整理|片付け|棚/,ids:['storage']},
    {pattern:/加湿|乾燥|湿度/,ids:['humidifier']},
  ];
  function extractBudget(text){
    const pattern=/([\d,]+(?:\.\d+)?)\s*(万円|万|千円|円)/;
    const match=text.match(pattern);if(!match)return null;
    const raw=Number(match[1].replaceAll(',',''));const x=match[2]==='万円'||match[2]==='万'?raw*10000:match[2]==='千円'?raw*1000:raw;
    return Number.isFinite(x)&&x>=100&&x<=1e7?Math.round(x):null;
  }
  function respond(text){
    const budget=extractBudget(text);const matched=tokenMap.filter(x=>x.pattern.test(text)).flatMap(x=>x.ids);
    const ids=[...new Set(matched)].filter(byId).slice(0,3);
    let answer='';
    if(/最安|お得|値下|セール|価格|安い|キャンペーン/.test(text)&&!/プリンタ|インク|暖房|車|防災|加湿|掃除/.test(text)){
      answer=state.priceGroups.length?'入力済みの価格は価格ウォッチで確認できるで。ただし機械検査のみで、販売店で最新価格を確認してな。':'いまは価格の原典確認が揃ってへんから、実際の「最安値」やセール情報は案内できへんのよ。型番・送料・税込価格・在庫を揃えてから比べるのが安全やで。';
    } else if(ids.length){
      const g=byId(ids[0]);
      answer=(budget?`予算は約${nf(budget)}円やね。`:'')+`「${g.title}」なら、まず次の3つを確認しよう。\n① ${g.points[0]}\n② ${g.points[1]}\n③ ${g.points[2]}\n\n${g.question}`;
      if(budget)answer+='\n※この予算内の商品在庫や販売価格を確認したという意味ではないで。';
    } else if(/違い|比較|どっち|おすすめ/.test(text)){
      answer='比較するときは、①用途と必要条件 ②型番・仕様 ③税込＋送料の総額 ④保証と返品条件、の順がおすすめやで。\n探している商品ジャンルと予算を教えてくれたら、見るべきポイントを絞れるよ。';
    } else {
      answer='いらっしゃい！ どんな「ええもん」を探してる？\nたとえば「予算2万円で暖房」「プリンターのインク代が気になる」みたいに、用途と予算を教えてな。\n今は商品選びのガイド応答で、実店舗の在庫・最安値は取得していないで。';
    }
    return {answer,ids};
  }
  function addMessage(role,text,ids=[]){
    const box=document.createElement('div');box.className='chat-msg '+role;
    if(role==='assistant'){
      box.innerHTML=`<span class="chat-msg-icon">✦ EEMON ガイド</span><span>${esc(text)}</span>${ids.length?`<div class="chat-linked">${ids.map(id=>{const g=byId(id);return `<button type="button" data-open-guide="${esc(id)}">${esc(g.title)} ↗</button>`}).join('')}</div>`:''}`;
    } else box.textContent=text;
    $('#chatLog').appendChild(box);$('#chatLog').scrollTop=$('#chatLog').scrollHeight;
  }
  async function sendChat(text){
    const query=String(text).trim().slice(0,240);if(!query)return;
    addMessage('user',query);$('#chatInput').value='';
    if(remoteAvailable&&$('#useRemoteAI').checked){
      const ctl=new AbortController();const timeout=setTimeout(()=>ctl.abort(),12000);
      try{
        const res=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json','X-EEMON-Consent':'yes'},body:JSON.stringify({question:query}),signal:ctl.signal});
        if(!res.ok)throw Error('AI_NOT_AVAILABLE');
        const data=await res.json();if(typeof data.answer!=='string'||!data.answer.trim())throw Error('NO_RESPONSE');
        addMessage('assistant','【生成AIによる回答・未検証】\n'+data.answer);return;
      }catch{notice('生成AIが利用できないため、ガイド応答に切り替えるで');}
      finally{clearTimeout(timeout)}
    }
    const r=respond(query);addMessage('assistant',r.answer,r.ids);
  }
  function openChat(seed){
    if($('#chatLog').children.length===0)addMessage('assistant','こんにちは！ ええもん探しパパの買い物ガイドやで。\n気になる商品や予算を教えてな。一緒に選ぶ条件を整理しよ。');
    openOverlay('aiOverlay');if(seed){$('#chatInput').value=seed;sendChat(seed)}setTimeout(()=>$('#chatInput').focus(),100);
  }
  function showTab(tab){
    $$('.nav-item').forEach(btn=>btn.classList.toggle('active',btn.dataset.tab===tab));
    if(tab==='home')scrollToId('top');
    if(tab==='explore'){state.category='すべて';state.query='';$('#searchInput').value='';$$('.category-pill').forEach(b=>b.classList.toggle('active',b.dataset.category==='すべて'));renderProducts();toBrowse()}
    if(tab==='saved')savedView();
    if(tab==='compare')openCompare();
    if(tab==='ai')openChat();
  }
  function setQuery(s){state.query=s.trim();state.showAll=false;renderProducts();$('#searchClear').hidden=!state.query;}
  function wire(){
    $('#searchForm').addEventListener('submit',e=>{e.preventDefault();setQuery($('#searchInput').value);toBrowse()});
    $('#searchInput').addEventListener('input',e=>setQuery(e.target.value));
    $('#searchClear').addEventListener('click',()=>{$('#searchInput').value='';setQuery('');$('#searchInput').focus()});
    $('#sortSelect').addEventListener('change',e=>{state.sort=e.target.value;renderProducts()});
    $('#clearFilters').addEventListener('click',()=>{state.category='すべて';state.query='';$('#searchInput').value='';setCategory('すべて')});
    $('#loadMore').addEventListener('click',()=>{state.showAll=true;renderProducts()});
    $('#headerSaved').addEventListener('click',()=>showTab('saved'));
    $('#headerAi').addEventListener('click',()=>openChat());
    $('#slidePrev').addEventListener('click',()=>showSlide(state.slides-1));$('#slideNext').addEventListener('click',()=>showSlide(state.slides+1));
    let touchStart=null;
    $('.hero-carousel').addEventListener('touchstart',e=>{if(e.touches.length===1)touchStart=e.touches[0].clientX},{passive:true});
    $('.hero-carousel').addEventListener('touchend',e=>{if(touchStart===null)return;const diff=e.changedTouches[0].clientX-touchStart;touchStart=null;if(Math.abs(diff)>55)showSlide(state.slides+(diff<0?1:-1))},{passive:true});
    $('#chatForm').addEventListener('submit',e=>{e.preventDefault();sendChat($('#chatInput').value)});
    $('#priceFile').addEventListener('change',async e=>{const file=e.target.files?.[0];if(!file)return;if(file.size>500000){notice('JSONは500KB以内にしてな');return}try{renderPrices(JSON.parse(await file.text()))}catch{notice('価格JSONを読み込めませんでした')}});
    $('#priceReset').addEventListener('click',()=>{$('#priceFile').value='';renderPrices(null)});
    $('#copyVideoCaption').addEventListener('click',async()=>{if(!state.activeVideo)return;try{await navigator.clipboard.writeText(state.activeVideo.caption);notice('投稿原稿をコピーしたで')}catch{notice('コピーできへんかった。本文を選択してな')}});
    document.addEventListener('click',event=>{
      const target=event.target.closest('button,[data-open-guide],[data-open-ai],[data-scroll]');if(!target)return;
      if(target.dataset.category){setCategory(target.dataset.category);return}
      if(target.dataset.save){toggleSave(target.dataset.save);if(!$('#productOverlay').hidden)openGuide(target.dataset.save);return}
      if(target.dataset.compare){toggleCompare(target.dataset.compare);if(!$('#productOverlay').hidden)openGuide(target.dataset.compare);return}
      if(target.dataset.openGuide){openGuide(target.dataset.openGuide);return}
      if(target.dataset.chatAbout){const g=byId(target.dataset.chatAbout);closeOverlay('productOverlay');openChat(g?g.title+'について教えて':'');return}
      if(target.dataset.openAi!==undefined){openChat();return}
      if(target.dataset.openReel){openReel(target.dataset.openReel);return}
      if(target.dataset.scroll){scrollToId(target.dataset.scroll);return}
      if(target.dataset.carousel){showSlide(Number(target.dataset.carousel));return}
      if(target.dataset.tab){showTab(target.dataset.tab);return}
      if(target.dataset.close){closeOverlay(target.dataset.close);return}
      if(target.dataset.removeCompare){toggleCompare(target.dataset.removeCompare);closeOverlay('compareOverlay');openCompare();return}
    });
    document.addEventListener('keydown',e=>{if(e.key==='Escape')$$('.overlay:not([hidden])').forEach(x=>closeOverlay(x.id))});
    const suggestions=$('#chatSuggestions');suggestions.innerHTML=HINTS.map(x=>`<button type="button" data-question="${esc(x)}">${esc(x)}</button>`).join('');suggestions.addEventListener('click',e=>{const b=e.target.closest('[data-question]');if(b)sendChat(b.dataset.question)});
  }
  async function init(){
    setupStored();wire();renderQuick();
    // The default is private/local: a remote request is never sent without user opt-in.
    fetch('/api/health',{signal:AbortSignal.timeout?.(2000)}).then(r=>r.ok?r.json():null).then(x=>{
      if(x&&x.remote_ai_available===true){remoteAvailable=true;$('#remoteOption').hidden=false}
    }).catch(()=>{});
    const load=async p=>{const r=await fetch(p,{cache:'no-store'});if(!r.ok)throw Error(p);return r.json()};
    try{
      const [g,r,p]=await Promise.all([load('guides.json'),load('reels.json'),load('price_output.json')]);
      if(!Array.isArray(g.guides)||!Array.isArray(r.reels))throw Error('malformed data');
      state.guides=g.guides.filter(x=>x&&safeId(x.id)&&PUBLIC_ASSET_IDS.has(x.art)&&Array.isArray(x.points)&&Array.isArray(x.tags));
      state.reels=r.reels.filter(x=>x&&/^reel\d{2}$/.test(x.id));
      renderProducts();renderReels();renderPrices(p);renderRecent();
    }catch(err){$('#productGrid').innerHTML='<p class="loading-text">データを読み込めません。ダウンロードZIPを展開し、付属サーバーで起動してください。</p>';$('#resultsCaption').textContent='データを読み込めません';console.error('EEMON portal load failed',err)}
  }
  window.EEMON_QA={respond,validOffer,score,extractBudget,validHttps};
  document.addEventListener('DOMContentLoaded',init);
})();