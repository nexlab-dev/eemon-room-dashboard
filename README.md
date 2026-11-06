# EEMON｜ええもん管理室（iPhone用）

楽天ROOMの紹介文の**事前承認とコピーを支援**する無償・静的なWebサイトです。

- 候補の紹介文をコピーし、楽天市場の公式商品ページへ移動できます。
- **実際のROOM投稿は自動では行いません。** 商品ページからROOMの正規投稿画面を開き、本人が最後の「投稿／完了」を押します。
- 承認と自己報告の記録はブラウザ内にのみ保存。運営者や他ユーザーのブラウザへ同期しません。
- 公開するJSONは一般公開可能な商品情報・掲載価格例のみ。ログイン情報や売上データは保存しません。
- 価格・送料・付属品・保証・納期などは購入前に要再確認。

## 技術

追加課金・外部APIキー・ブラウザ自動操作・GitHub Actionsなし。GitHub Pagesの公開ブランチから配信します。候補更新は `feed.json` の編集で実施。公開サイトとフィードは第三者も閲覧できます。

[楽天ROOMの公式利用規約](https://room.rakuten.co.jp/info/agreement.html)


## v2.1（2026-11-07）

- iPhoneでの「①承認・原稿コピー→②楽天公式の商品ページ→③本人がROOMで完了→④報告文コピー」が、公開ブラウザの独立セッションで動作確認済み。承認はiPhoneブラウザのローカル保存、公開・報告が自動実行されたわけではない。
- 公開済みと同一のIDだけでなく、同一商品URLの重複も遮断。コピー失敗は承認成功と記録しない。
- 7日超の候補は表示候補から外す。価格調査が古い場合は金額の代わりに再調査案内を表示。商品寸法・価格帯・送料条件は確認日時付きで伝える。
- Public GitHubには **商品名・正規商品リンク・公開紹介文・調査日付き価格のみ**。研究ログ・経費・報酬・個人情報・楽天ID・Cookie・セッションキーを置かない。
- Private 正本：`nexlab-dev/Project-ORCHESTRA/automation/eemon/queue.json`・`published.json`・`price_watch.json`。安全な出力プログラム `export_feed.py` はGitHub書き換えやROOM投稿を行わない。公開`feed.json`の更新はChatGPT/WorkからGitHub connectorで行う。
- GitHub Pages URL: https://nexlab-dev.github.io/eemon-room-dashboard/
- 静的サイト自身はプッシュ通知、楽天ログイン、公開投稿、端末状態のGitHub自動同期を行わない。投稿依頼は既存のChatGPT PMO定期タスクが担当するが、実通知は設定・実行結果に依存。
