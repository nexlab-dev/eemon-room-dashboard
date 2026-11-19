import json, pathlib, csv
root=pathlib.Path(__file__).resolve().parent.parent
entries=[
 ('01','送料込みで比べる','「安い！」\nそれ、送料込み？','値札だけやと\n逆転することも','本体価格・送料・税込\n同じ条件でチェック','比較は総額で。','shopping','価格比較は「支払総額」で。送料や付属品が違う店舗を、金額だけで順位付けしないのがコツ。','送料が未確認の店舗は比較保留。最安値と断定しない。'),
 ('02','プリンターはインク代まで','プリンター\n本体価格だけで選ぶ？','印刷する頻度で\n選び方は変わる','インク方式・用紙・\nスマホ接続を確認','後から困らん選び方。','printer','プリンター選びは本体価格だけじゃない。インク代、対応用紙、スマホ接続をセットで確認。','利用頻度・対応用紙を確認。実際の維持費はモデルで異なる。'),
 ('03','布団乾燥機の見落とし','布団乾燥機\n数字だけ見てない？','使う布団と\nノズルの相性が大事','収納場所・重さ・\n運転音も確認','寝る前の手間まで。','bed','布団乾燥機は乾燥時間だけで決めず、ノズル形状・布団との相性・収納場所まで。','適合する寝具・取り扱いはメーカー説明を確認。'),
 ('04','電源タップは安全優先','電源タップ\n見た目だけで選ばんといて','同時につなぐ\n機器を思い出して','定格容量・差込口・\n設置場所を確認','安全が最優先。','plug','電源タップは「口数」だけじゃなく定格容量や発熱リスクも重要。','定格の超過、ホコリ、たこ足配線に注意。'),
 ('05','掃除機は重さの数字だけ？','軽い掃除機\nそれだけで正解？','持ち方と掃除する\n場所で変わる','ヘッド・ゴミ捨て・\n手入れ方法も確認','続けられる家事に。','vacuum','掃除機は重量の数字だけでなく持ちやすさやゴミ捨て、手入れの負担も確認。','使用環境で合う機種は変わる。'),
 ('06','収納グッズは1cmが大事','収納グッズ\n先に買ってない？','まず測るのは\n外寸と内寸','扉の開閉・動線・\n床の段差も確認','測ってから買おう。','storage','収納グッズは見た目より寸法。外寸・内寸、扉の開閉まで想像してから選ぶ。','施工や耐荷重の条件は個別確認。'),
 ('07','ドラレコは夜の条件も','ドラレコ\n画素数だけ見てない？','必要な場面を\n先に決めよう','夜間・前後撮影・\n駐車監視の条件','使い方から選ぼう。','car','ドライブレコーダーは解像度だけでは選べない。撮影範囲や夜間性能、駐車監視の電源条件を確認。','対応車種と取り付けは機種・車種による。'),
 ('08','加湿器は洗いやすさ','加湿器\n給水だけで選ぶ？','毎日のお手入れが\n意外と大事','洗える構造・方式・\n部屋の広さを確認','清潔に使える一台。','humidifier','加湿器の比較は適用床面積・方式・洗浄方法のセットで。','説明書どおりの清掃と水交換が必要。'),
 ('09','セール価格は条件確認','本日だけ安い？\nその条件ほんま？','クーポン・ポイントは\n誰でも同じじゃない','有効期限・対象者・\n送料条件を確認','焦らず賢く買おう。','sale','セールは表示価格と実際に払う金額が違うことも。条件と期限を先に確認。','値下げ実績や最安値は検証なしに断定しない。'),
 ('10','買う前の最終チェック','買う前に\n最後の3チェック','同じ型番？\n送料込み？','保証・返品条件も\nスクショで保存','迷ったら保存してな。','check','最後に型番、支払総額、保証・返品条件の3つを確認。比較の失敗を減らそう。','販売条件は各店舗の最新表示を優先。')
]
items=[]
for no,topic,hook,reason,check,close,icon,caption,note in entries:
 items.append({'id':'reel'+no,'number':int(no),'topic':topic,'category':{'shopping':'価格','printer':'家電','bed':'家電','plug':'安全','vacuum':'家事','storage':'収納','car':'カー用品','humidifier':'家電','sale':'価格','check':'買い物術'}[icon], 'icon':icon,'slides':[{'kicker':'BUY SMART / '+no,'headline':hook,'subline':'買う前に、ここだけチェック。'}, {'kicker':'WHY IT MATTERS','headline':reason,'subline':'後悔しないための比較ポイント'}, {'kicker':'CHECK POINT','headline':check,'subline':note}, {'kicker':'EEMON EDITORIAL','headline':close,'subline':'ええもん探しパパ｜保存して見返してな'}], 'caption':caption+'\n\n買う前の確認に使ってな。商品や販売価格は公式ページで最終確認を。\n\n#ええもん探しパパ #買い物のコツ #暮らしの便利 #商品比較', 'note':note,'status':'DRAFT_NOT_POSTED','asp_link_status':'NOT_APPROVED'})
(root/'content/reels.json').write_text(json.dumps({'brand':'ええもん探しパパ','version':'1.0','updated_at':'2026-11-14','reels':items},ensure_ascii=False,indent=2)+'\n')
(root/'site/content.json').write_text(json.dumps({'brand':'ええもん探しパパ','reels':[{k:v for k,v in e.items() if k in ['id','number','topic','category','icon','slides','caption','note','status']} for e in items]},ensure_ascii=False,indent=2)+'\n')
for e in items:(root/'content'/(e['id']+'_caption.txt')).write_text(e['caption']+'\n\n【運営メモ・投稿時削除】本動画にアフィリエイトリンク未設置。将来の広告紹介にはPR表示と媒体審査が必要。\n',encoding='utf-8')
with (root/'content/pilot_metrics.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['reel_id','theme','platform','planned_date','posted_at','public_url','views','profile_visits','link_clicks','approved_sales','confirmed_reward_jpy','state','evidence_url']);
 for e in items:
  for p in ['instagram','tiktok']:w.writerow([e['id'],e['topic'],p,'','','','','','','','','DRAFT_NOT_POSTED',''])
(root/'site/price_output.json').write_text(json.dumps({'generated_at':None,'verification':'NO_DATA','summary':[],'excluded':[],'message':'確認済みの価格データはまだありません。比較順位は表示しません。'},ensure_ascii=False,indent=2)+'\n')
print('generated',len(items),'reels scripts')