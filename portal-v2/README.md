# EEMON 買い物ポータル v2.0

**制作日：2026-11-14 / ステータス：LOCAL_QA_PASS / EXTERNAL_PUBLISH_HOLD**

ユーザー提供のYahoo!ショッピングの実機スクリーンショットを、検索・カテゴリ・パーソナル導線・おすすめ・AI相談の**情報設計の参考**として再構成した「ええもん探しパパ」オリジナルの買い物サポートサイト。Yahoo!の名称・ロゴ・UI画像・商品画像・広告文面・パーソナルデータの複製はしていない。

## まず触る

**iPhone / PCで単体のHTMLを開いて試す**：同梱 `EEMON_買い物ポータル_体験版.html` をブラウザで開く。CSS、商品ガイドJSON、完全オリジナルのイラスト12種、動画MP4 10本を**1ファイル内**へ埋め込んでいるため、ローカルファイルでも全機能を試せる。サイズ約9.1MB。

開発時のソース版（ファイル分割）：

```bash
cd EEMON_PORTAL_v2
python3 server.py                  # http://127.0.0.1:8765
# or without an AI endpoint:
python3 -m http.server 8765 --directory site
```

初期状態で**APIキー不要・追加課金なし・外部通信なし**。ブラウザから独立に動く静的デモ。会員登録・ログイン・注文・決済は一切持たない。ZIPの動画10本は `site/media/reels/` に同梱。Macで既存EEMON/ROOM・CURATION・NEXLABブラウザを変更する必要なし。

## 実装済み機能と挙動

| 機能 | 実装内容 | 本番の注意 |
|---|---|---|
| Yahoo型のモバイル情報設計 | sticky検索、横スクロール6カテゴリ、タッチ対応ヒーロー3枚、おすすめガイド、下部固定5タブ | デザインはEEMON独自。商品広告バナーは現在なし |
| 買い物ガイド | 12テーマ、名称・カテゴリ検索、並べ替え、選び方、型番・安全などのチェックリスト | 実商品、実使用レビュー、実価格とは区別 |
| お気に入り / 閲覧履歴 | localStorageにブラウザ内のみ保存。3件までの比較リスト | 端末・ブラウザ間同期なし |
| AI相談室 | キーワード・予算・用途を判定する**ルールベースのローカル応答**。会話、質問候補、関連ガイド表示 | **生成AIではない**。価格・在庫・最安値の捏造なし |
| 生成AI接続準備 | 任意のローカルサーバー `server.py` にGemini公式REST接続口。サーバー環境変数が明示的に設定されたときのみONのチェックボックスが現れる | **本番未接続・動作先API未実呼出し**。本人の利用規約・データ処理・利用額・サーバー保護承認が必要。キーはブラウザへ送らない |
| Muse価格入力 | `scripts/price_engine.py` でSKU・税込JPY+送料・在庫・24時間鮮度・根拠URL・目視確認を検査。同一SKUの**入力店舗内最小総額**に並べ替え、JSON読み込み表示 | **Muse自動巡回は未接続**。真偽はプログラムで保証できない。現在検証済み価格0件 |
| 動画 | オリジナル1080×1920、12秒のMP4を10本一覧・再生・投稿文コピー | 実商品映像ではなくモーショングラフィック。SNS未投稿 |
| 安全と公開 | PR/非PR、価格未確認、一般ガイド、生成AIモデル未接続を明示。CSS / SVGオリジナル。クロスサイトURLの検査、入力JSONの表示エスケープ | ASP登録・広告提携審査・SNS本人アカウント・公開URLはまだ |

## 実際のAI接続（標準で無効）

Google Gemini公式文書（2026-11-14確認）: https://ai.google.dev/api/generate-content 。2026年6月以降はInteractions APIが新規向け推奨だが、従来の `generateContent` もサポート継続。現コードは単発入力を使う互換アダプタで、将来Interactions APIへ切替可能。

**明示的な本人承認と料金/契約条件確認後に限る**。ローカル検証する場合は、実行環境の秘密情報ストアなどで以下を設定（値をChatGPTやGitHubへ送らない）。

```bash
export EEMON_LLM_ENABLED=1
export EEMON_GEMINI_API_KEY='(private secret store only)'
export EEMON_GEMINI_MODEL='gemini-3.5-flash'
python3 server.py
```

UIの「生成AIモードを使う」に**ユーザー自身がチェックを入れた場合のみ**質問文をGeminiへ送る。1時間10回/IPの簡易ローカル制限、最大240文字、接続タイムアウトとfallbackを設置。現時点では接続先のライブ応答はテストしていない。テキスト送信前のプライバシー/利用条件/料金確認が必要。**`server.py` はローカル限定サーバー。直接インターネット公開しない**。公開時は適切な認証、CSRF、クォータ、 abuse対策、secret管理、ユーザーへの同意説明が必要。

## 価格データの作り方

```bash
python3 scripts/price_engine.py price-observations.template.json site/price_output.json
```

`price-observations.template.json` は空で配布、入手したデータは秘密情報や本人名義を入れず、適法な取得方法と原典確認を守る。`price-input.schema.json` に必須フィールド。`price_engine.py` の構造QAで通過した候補も **SOURCE_ASSERTED_NOT_INDEPENDENTLY_AUDITED** であり、全国最安・広告提携承認・価格情報の真実性を保証しない。値下がりランキングは真正な時系列エビデンスがないため未実装で表示しない。

## 再生成コマンドと検証

```bash
python3 scripts/build_art.py
python3 scripts/build_preview.py
python3 -m unittest discover -s tests -p 'test_integrity.py' -v
# ブラウザ検査は Playwright と Chromium がある環境のみ
python3 tests/browser_qa.py
```

2026-11-14の検収：**ユニットテスト20件 PASS、Chromium DOM統合/画面テスト14件 PASS、単体HTMLの実ブラウザ読み込み・ガイド会話・動画10本埋込を確認**。ブラウザ実行環境が `http://127.0.0.1:8765` のナビゲーションを `ERR_BLOCKED_BY_ADMINISTRATOR` で拒否したため、ブラウザテストは**実HTTPナビゲーションではなくHTML/CSS/JS/JSONの同一DOM注入**で実施。これはライブWeb配信のE2Eテストに代替しない。スクリーンショットは `qa/iphone.png` 等を参照。

## 公開ゲート / GitHub正本

- [x] 静的サイトとガイド機能、カテゴリ絞込、保存、比較、短尺再生、オフラインプレビュー
- [x] Muse受入用価格検証ソースと空値の誠実な表示
- [x] 任意APIのローカル接続口（実連携ONではない）
- [x] セキュリティ・UI自動テスト / バージョン別ソース管理
- [ ] CEOデザイン・内容確認（外部公開前）
- [ ] 実iPhone Safariで公開URL上の動作検査、Core Web Vitals、アクセシビリティQA
- [ ] ASP登録/メディア審査/案件提携の承認済み証拠
- [ ] Museの合法な実価格ソースとの定時接続・真偽検証
- [ ] 生成AIを**本番で**接続する場合、費用・規約・個人情報・上限管理の承認
- [ ] 追加課金や公開投稿を伴わない独立EEMON URLの決定・本番デプロイ承認
- [ ] 実価格の確認、匿名購入導線QA、自然クリック/初成果計測

**現時点：開発・ローカル検収は完了、事業としての本番完成・外部公開は未完了**。旧ROOM管理トップ、CURATION、Mac実働、各ASPの認証情報には変更なし。

正本：`nexlab-dev/eemon-room-dashboard` の独立 `portal-v2/` ディレクトリ / Draft PR、`nexlab-dev/Project-ORCHESTRA` Issue #66。配布バイナリはZIP/単体HTML、GitHubにはソースと再生成スクリプトを置く。通常チャット・Workの双方で改修可能。