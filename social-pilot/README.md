# EEMON SOCIAL PILOT v1.0

**Status (2026-11-14): `LOCAL_QA_BUILD` — SNS未投稿、ASP未承認、広告未掲載、未公開。**

「ええもん探しパパ」— EEMONを **Instagram / TikTok → 独立した比較入口 → 正規ASP広告**へ育てるための、再現可能な試験運用パッケージ。既存の楽天ROOM管理サイトを壊さず、通常チャットでもWorkでもこのフォルダ・GitHubから修正できます。

## 成果物

| 場所 | 内容 | 判定 |
|---|---|---|
| `site/index.html`, `style.css`, `app.js` | iPhone優先の検索不要ランディング。10動画ギャラリー、動画再生、カテゴリ絞込、キャプションコピー、価格監視JSONの検証表示、PR/個人情報説明 | ローカルで実動作 |
| `site/media/reels/reel01.mp4`〜`reel10.mp4` | 1080×1920、12秒、H.264/AAC、オリジナルBGM付き・本人顔写真不要・未検証価格ゼロの縦型ショート10本 | mp4生成・動画/音声QC |
| `content/reel*_caption.txt` | 10本の投稿文。実体験や架空値下げの断定なし | 投稿前レビュー必要 |
| `content/pilot_metrics.csv` | IG/TikTok×10本の別管理KPI表。「空欄=未測定」、状態は`DRAFT_NOT_POSTED` | 実運用前 |
| `scripts/price_engine.py` | Muse候補の構造/鮮度/SKU/税込/送料/証拠検査、採用店舗内の総額昇順ランキング。広告URLは自動生成しない | テスト実施 |
| `data/price-input.schema.json` | Muse→レビュー担当の引き継ぎ入力仕様 | 定義済み |
| `site/price_output.json` | 公開前の確認済み価格 **0件**。空表示が正しい | 準備中 |
| `tests/` | 価格算定・除外・サイト表示・モバイルQA | 自動検証 |

## すぐ試す

このパッケージがあるパソコンで：

```bash
cd EEMON_SOCIAL_PILOT_v1
python3 -m http.server 8765 --directory site
```

iPhoneと同じ画面をブラウザで試すには `http://localhost:8765/`。同じWi-FiからiPhoneで見る場合、起動機のIPとファイアウォール設定が別途必要。

動画は `site/media/reels/reel01.mp4`〜`reel10.mp4` を直接再生可能（BGM/テロップは焼き込み済み）。本フォルダのzipにも含める。

### 動画の再制作

```bash
python3 scripts/render_reels.py             # 10本を全再生成
python3 scripts/render_reels.py --only 1    # 1本だけ再生成
```

依存: Python 3.10以降、Pillow、NumPy、FFmpeg、Noto Sans CJK JP。元画像・動画・フォントファイルを商品として第三者に譲渡しない。動画の背景・ピクトグラム・BGMは本スクリプトから生成したオリジナル。市販商品の画像や人の顔は未使用。

### Muse価格監視データの受け渡し

**この版では定期的な外部巡回・スクレイピングを実行しません。** Museや人が規約に合う方法で取得し、**実際に原典を目視確認した結果だけ**を `data/muse_observations.template.json` の `observations` に書き込む。必須項目は `data/price-input.schema.json` を参照。

```bash
python3 scripts/price_engine.py data/muse_observations.template.json site/price_output.json
```

判定ルール:
1. **同じSKU・色・仕様** (`product_key == variant_key`) ごとだけ比較。
2. 税込JPY + 送料の総額。送料不明 / 在庫なし / URL不適切 / 目視未確認は除外。
3. 確認時刻が未来、または24時間超なら除外。
4. 同じ商品/店舗の重複は除外。
5. 出力した順位は **「入力データのうち条件を満たす店舗内」** に限る。全国最安値・全店舗調査済みとは表示しない。
6. このプログラムが検証できるのはデータ構造と整合性まで。**ショップ画面の真偽・取得許可・ASP提携状態は独立に確認が必要。**
7. SNSに誤った価格を出さないため、動画10本は価格を言わない汎用の教育コンテンツとして制作。

価格データの公開は、出典の利用規約・アクセス許諾・広告契約・個人情報のリスクを担当者が確認した後に行う。原典確認のない情報はGitHubメイン・公開サイトに流さない。

## 公開・収益化ゲート

`GH_PR_DRAFT → CEO_CONTENT_REVIEW → SNS_ACCOUNT_REVIEW → ASP_ACCOUNT_APPROVED → MEDIA_REGISTERED → ADS_APPROVED → WEBSITE_PUBLISH → SOCIAL_PUBLISH → MEASURE`。

- **未実施**: もしも/VC/A8の本登録完了と提携承認の確認、使用するEEMONのInstagram/TikTokアカウントの確認、URL/ドメイン決定、実サイト公開、動画投稿、広告リンク設置、成果発生・着金。
- 登録メール、パスワード、口座・本人情報、秘密トークンは本パッケージやGitHubに入れない。
- IG/TikTokの音源利用規則や各媒体の広告表示、プロフィールリンクの表示条件、一般的な表示法を投稿時に確認。音源はオリジナル電子音なので第三者市販曲は使用していないが、平台のその他審査は別。
- 売上が発生していない段階で自動投稿や大量フォローは開始しない。既存ROOMのLaunchAgent、`eemon-room-dashboard` の公開ルートは変更しない。

## 14日パイロットの計測

制作物10本を、本人の公開承認・利用規約確認後、**InstagramとTikTokで媒体別に比較**する。14日間で10本を投稿する案であり、自動投稿済みの意味ではない。主要指標は `リンククリック数`、`成果発生数`、`確定報酬額`。再生・保存・プロフィール訪問は先行指標。

- 分析タグ案：`utm_source=instagram|tiktok`、`utm_medium=social`、`utm_campaign=eemon_14d`、`utm_content=reel01〜reel10`。**広告リンクにUTMを無断付与しない**。まず自己サイト入口に付けて計測する。
- テスト合格は動画完成数ではなく、審査済み購入導線の安全な公開と実クリック観測。売上は保証しない。
- 既知のROOM実績「直近30日クリック8・売上0」とSNSのクリックは母集団が異なるので混合しない。

## 開発正本

- NEXLAB private `Project-ORCHESTRA` Issue **#66**：ASP軸足転換。`automation/eemon/ASP_PIVOT_SKILL.md` を尊重。
- 既存 `nexlab-dev/eemon-room-dashboard` のメイン配信・ROOM管理は保護。新たな `social-pilot/` ディレクトリとして **Draft PR** でレビューし、独立導線として切り分ける。GitHubには再現可能なソースコードを置く。MP4の実ファイルは容量管理のため配布ZIP側へ同梱し、GitHubのブランチだけを取得したときは `python scripts/render_reels.py` で再生成してからサイトを起動する。
- `reels.json` と `build_content.py` が10本の原稿正本。レンダラは「原稿が変わったら再実行」する再現可能な実装。
- README + バグ/QAを残し、通常チャットとWorkの両方から改修可能にする。コードは本番公開や実投稿を勝手に行わない。