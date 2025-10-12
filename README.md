\# 🎙️ AI News Podcast Generator



毎日自動的に最新のAIニュースを収集し、ポッドキャストを生成してSpotifyに投稿するシステム



\## 📋 機能



1\. \*\*自動ニュース収集\*\*: Google News/TechCrunchから最新AIニュースを取得

2\. \*\*台本生成\*\*: Gemini 2.0 Flashで自然な会話形式の台本を作成

3\. \*\*音声生成\*\*: Gemini 2.5 Pro TTS で2人の話者による音声を生成

4\. \*\*自動投稿\*\*: Spotify Podcastersに自動アップロード

5\. \*\*スケジュール実行\*\*: GitHub Actionsで毎日自動実行



\## 🚀 セットアップ手順



\### 1. リポジトリの準備



```bash

\# リポジトリをクローン

git clone https://github.com/your-username/ai-podcast-generator.git

cd ai-podcast-generator



\# 必要なファイルを配置

\# - podcast\_generator.py

\# - upload\_to\_spotify.py

\# - .github/workflows/podcast.yml

```



\### 2. 必要なAPIキーの取得



\#### Gemini API キー

1\. \[Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス

2\. 「APIキーを取得」をクリック

3\. 生成されたキーをコピー



\#### GitHub Personal Access Token

1\. GitHub Settings → Developer settings → Personal access tokens

2\. "Generate new token (classic)" をクリック

3\. スコープ: `repo`, `write:packages` を選択

4\. トークンを生成してコピー



\### 3. GitHub Secretsの設定



リポジトリの Settings → Secrets and variables → Actions で以下を追加:



```

GEMINI\_API\_KEY=your\_gemini\_api\_key\_here

GITHUB\_TOKEN=your\_github\_token\_here (自動的に提供される場合もあります)

SPOTIFY\_SHOW\_ID=your\_spotify\_show\_id (オプション)

```



\### 4. requirements.txt の作成



```bash

cat > requirements.txt << EOF

google-genai>=0.3.0

requests>=2.31.0

beautifulsoup4>=4.12.0

lxml>=4.9.0

EOF

```



\### 5. 実行時間の設定



`.github/workflows/podcast.yml` のcron設定を編集:



```yaml

schedule:

&nbsp; # 毎日日本時間 21:00 (UTC 12:00) に実行

&nbsp; - cron: '0 12 \* \* \*'

```



\*\*Cron構文の例:\*\*

\- `0 0 \* \* \*` - 毎日 UTC 0:00 (日本時間 9:00)

\- `0 12 \* \* \*` - 毎日 UTC 12:00 (日本時間 21:00)

\- `0 \*/6 \* \* \*` - 6時間ごと

\- `0 9 \* \* 1-5` - 平日のみ UTC 9:00



\### 6. Spotifyポッドキャストの設定



\#### 方法A: RSS フィード (推奨)



1\. \*\*Spotify for Podcasters アカウント作成\*\*

&nbsp;  - \[Spotify for Podcasters](https://podcasters.spotify.com/) にアクセス

&nbsp;  - アカウントを作成



2\. \*\*RSSフィードのURL取得\*\*

&nbsp;  - GitHub Pagesを有効化

&nbsp;  - `https://your-username.github.io/ai-podcast-generator/podcast\_feed.xml` が公開URL



3\. \*\*SpotifyにRSSを登録\*\*

&nbsp;  - Spotify for Podcastersで「Add your podcast」

&nbsp;  - RSSフィードURLを入力



\#### 方法B: 手動アップロード



GitHub Actionsの「Artifacts」から音声ファイルをダウンロードして手動でアップロード



\## 🎯 使い方



\### 自動実行

設定したスケジュールで自動的に実行されます



\### 手動実行

1\. GitHubリポジトリの「Actions」タブ

2\. 「AI Podcast Generator」ワークフローを選択

3\. 「Run workflow」をクリック



\### ローカルテスト



```bash

\# 依存関係をインストール

pip install -r requirements.txt



\# 環境変数を設定

export GEMINI\_API\_KEY=your\_key\_here



\# 実行

python podcast\_generator.py

```



\## 📁 ファイル構成



```

ai-podcast-generator/

├── .github/

│   └── workflows/

│       └── podcast.yml          # GitHub Actions ワークフロー

├── podcast\_generator.py         # メインスクリプト

├── upload\_to\_spotify.py         # Spotifyアップロード

├── requirements.txt             # Python依存関係

├── podcast\_feed.xml            # RSS フィード (自動生成)

└── README.md                    # このファイル

```



\## 🔧 カスタマイズ



\### ニュースソースの追加



`podcast\_generator.py` の `search\_ai\_news()` メソッドを編集:



```python

news\_sources = \[

&nbsp;   "あなたの好きなRSS URL",

&nbsp;   "https://...",

]

```



\### 音声スタイルの変更



`generate\_audio()` メソッドで話者の声を変更:



```python

voice\_name="Aoede"  # 利用可能な音声: Puck, Charon, Kore, Fenrir, Aoede

```



\### ポッドキャストの長さ調整



`generate\_podcast\_script()` のプロンプトを編集:



```python

prompt = f"""...10分程度のポッドキャスト台本を作成..."""

```



\## 📊 モニタリング



\### GitHub Actions

\- Actions タブで実行履歴を確認

\- 失敗時はメール通知



\### 生成されたファイル

\- Artifacts から音声ファイルと台本をダウンロード可能

\- 30日間保持



\## ⚠️ 注意事項



1\. \*\*API利用制限\*\*

&nbsp;  - Gemini APIの無料枠: 1分あたり15リクエスト

&nbsp;  - GitHub Actionsの無料枠: 月2000分



2\. \*\*音声ファイルサイズ\*\*

&nbsp;  - 長時間のポッドキャストは大きなファイルになります

&nbsp;  - GitHub Releasesは2GBまで



3\. \*\*Spotifyの更新頻度\*\*

&nbsp;  - RSS経由の場合、反映まで数時間かかる場合があります



\## 🆘 トラブルシューティング



\### エラー: "GEMINI\_API\_KEY not found"

→ GitHub Secretsが正しく設定されているか確認



\### エラー: "News not found"

→ ニュースソースが応答しているか確認

→ プロキシやファイアウォールの設定を確認



\### Spotifyに表示されない

→ RSSフィードが公開されているか確認

→ Spotify for PodcastersでRSS URLを再検証



\## 📝 今後の改善案



\- \[ ] Discord/Slackへの通知機能

\- \[ ] 複数言語対応

\- \[ ] カスタム音楽・効果音の追加

\- \[ ] YouTube Podcastsへの同時投稿

\- \[ ] ニュース要約の品質向上

\- \[ ] リスナーフィードバックの収集



\## 📄 ライセンス



MIT License



\## 🤝 貢献



プルリクエスト大歓迎！



---



\*\*作成者\*\*: \[Your Name]  

\*\*最終更新\*\*: 2025年10月

