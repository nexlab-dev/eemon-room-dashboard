(()=>{
'use strict';
const label=document.getElementById('stock-health-summary');
const detail=document.getElementById('stock-health-detail');
if(!label||!detail)return;
const toJst=time=>new Date(time).toLocaleString('ja-JP',{timeZone:'Asia/Tokyo',month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit'});
async function load(){
 try{
  const r=await fetch('./stock_status.json?fresh='+Date.now(),{cache:'no-store',credentials:'omit'});
  if(!r.ok)throw Error('HTTP '+r.status);
  const x=await r.json();
  if(x.schema_version!==1||typeof x.checked_at!=='string'||!Number.isFinite(Date.parse(x.checked_at))||
    !Number.isInteger(x.pending_count)||!Number.isInteger(x.staged_remaining)||
    x.pending_count<0||x.staged_remaining<0||x.pending_count>100||x.staged_remaining>500)
    throw Error('invalid-status');
  const age=(Date.now()-new Date(x.checked_at).getTime())/60000;
  const overdue=age>95||age< -10;
  const released=x.last_run_status==='HOURLY_SYNCED';
  const healthy=['HOURLY_SYNCED','HEALTH_CHECK_OK'].includes(x.last_run_status);
  label.textContent=overdue?'⚠️ 毎時補充の最新実行が確認できへん':
    healthy?'✅ 自動補充の実行を確認済み':
    '⚠️ 今回は新商品を補充できてへん';
  detail.textContent='最終確認 '+toJst(x.checked_at)+'｜承認待ち '+x.pending_count+
    '件｜次の事前調査済みストック '+x.staged_remaining+'件。'+
    (x.staged_remaining<=3?'次の商品の調査・補充が必要やで。':
      (released?'今回の商品は公開管理室へ同期済み。':'次の補充は毎時20分を予定。'));
 }catch{
  label.textContent='稼働状況を取得できへんかった';
  detail.textContent='商品一覧は下に表示されるで。更新時刻はMacの実行ログで確認が必要。';
 }
}
load();
setInterval(load,300000);
})();