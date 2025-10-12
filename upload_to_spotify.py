import os
import glob
from datetime import datetime
import requests


class SpotifyPodcastUploader:
    """
    Spotify for Podcasters (旧Anchor) APIを使用したアップロード
    
    注意: Spotifyは公式のPodcast APIを提供していないため、
    以下のいずれかの方法を使用する必要があります:
    
    1. RSS フィードを使用 (推奨)
       - 自分のサーバーにRSSフィードをホスト
       - SpotifyがRSSをクロール
    
    2. Anchor API (非公式)
       - Anchorアカウントが必要
       
    3. サードパーティサービス
       - Buzzsprout, Transistor, Libsyn等を使用
    """
    
    def __init__(self):
        self.access_token = os.environ.get("SPOTIFY_ACCESS_TOKEN")
        self.show_id = os.environ.get("SPOTIFY_SHOW_ID")
        
    def upload_via_rss(self, audio_file):
        """
        RSS フィード方式でのアップロード
        
        この方式では:
        1. 音声ファイルを公開可能な場所にアップロード (S3, GitHub Releases等)
        2. RSS XMLを更新
        3. Spotifyが自動的にクロール
        """
        print("📡 RSS フィード方式でアップロード準備中...")
        
        # GitHub Releasesにアップロード
        audio_url = self.upload_to_github_releases(audio_file)
        
        # RSS XMLを更新
        self.update_rss_feed(audio_file, audio_url)
        
        print("✅ RSSフィード更新完了")
        print("ℹ️  Spotifyが数時間以内に自動的にエピソードを取得します")
        
    def upload_to_github_releases(self, audio_file):
        """GitHub Releasesに音声ファイルをアップロード"""
        github_token = os.environ.get("GITHUB_TOKEN")
        repo = os.environ.get("GITHUB_REPOSITORY")
        
        if not github_token or not repo:
            print("⚠️  GitHub認証情報が設定されていません")
            return None
        
        # タグ名を生成
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        tag_name = f"podcast-{timestamp}"
        
        # GitHub API エンドポイント
        api_url = f"https://api.github.com/repos/{repo}/releases"
        
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # リリースを作成
        release_data = {
            "tag_name": tag_name,
            "name": f"AI Podcast {timestamp}",
            "body": f"Automated podcast episode generated on {datetime.now().isoformat()}",
            "draft": False,
            "prerelease": False
        }
        
        try:
            response = requests.post(api_url, json=release_data, headers=headers)
            response.raise_for_status()
            release = response.json()
            
            # アセットをアップロード
            upload_url = release["upload_url"].replace("{?name,label}", "")
            
            with open(audio_file, "rb") as f:
                asset_response = requests.post(
                    f"{upload_url}?name={os.path.basename(audio_file)}",
                    headers={
                        "Authorization": f"Bearer {github_token}",
                        "Content-Type": "audio/wav"
                    },
                    data=f
                )
                asset_response.raise_for_status()
                
            audio_url = asset_response.json()["browser_download_url"]
            print(f"✅ GitHub Releasesにアップロード: {audio_url}")
            return audio_url
            
        except Exception as e:
            print(f"❌ GitHub Releasesアップロードエラー: {e}")
            return None
    
    def update_rss_feed(self, audio_file, audio_url):
        """RSSフィードを更新"""
        from xml.etree import ElementTree as ET
        from datetime import datetime
        
        rss_file = "podcast_feed.xml"
        
        # 既存のRSSを読み込むか、新規作成
        if os.path.exists(rss_file):
            tree = ET.parse(rss_file)
            root = tree.getroot()
            channel = root.find("channel")
        else:
            root = self.create_base_rss()
            channel = root.find("channel")
            tree = ET.ElementTree(root)
        
        # 新しいエピソードを追加
        item = ET.SubElement(channel, "item")
        
        title = ET.SubElement(item, "title")
        title.text = f"AI News Podcast - {datetime.now().strftime('%Y年%m月%d日')}"
        
        description = ET.SubElement(item, "description")
        description.text = "今日の最新AIニュースをお届けします"
        
        pub_date = ET.SubElement(item, "pubDate")
        pub_date.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        enclosure = ET.SubElement(item, "enclosure")
        enclosure.set("url", audio_url or "")
        enclosure.set("type", "audio/mpeg")
        
        # ファイルサイズを取得
        if os.path.exists(audio_file):
            file_size = os.path.getsize(audio_file)
            enclosure.set("length", str(file_size))
        
        guid = ET.SubElement(item, "guid")
        guid.text = audio_url or f"episode-{datetime.now().timestamp()}"
        
        # XMLを保存
        tree.write(rss_file, encoding="utf-8", xml_declaration=True)
        print(f"✅ RSSフィード更新: {rss_file}")
    
    def create_base_rss(self):
        """基本的なRSSフィード構造を作成"""
        from xml.etree import ElementTree as ET
        
        rss = ET.Element("rss")
        rss.set("version", "2.0")
        rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
        
        channel = ET.SubElement(rss, "channel")
        
        title = ET.SubElement(channel, "title")
        title.text = "AI Daily News Podcast"
        
        description = ET.SubElement(channel, "description")
        description.text = "毎日最新のAIニュースをお届けするポッドキャスト"
        
        language = ET.SubElement(channel, "language")
        language.text = "ja"
        
        return rss
    
    def run(self):
        """メイン実行"""
        print("=" * 50)
        print("📤 Spotifyアップロード処理")
        print("=" * 50)
        
        # 最新の音声ファイルを検索
        audio_files = glob.glob("podcast_*.wav")
        if not audio_files:
            print("❌ 音声ファイルが見つかりません")
            return
        
        latest_audio = max(audio_files, key=os.path.getctime)
        print(f"📁 アップロード対象: {latest_audio}")
        
        # RSSフィード方式でアップロード
        self.upload_via_rss(latest_audio)
        
        print("=" * 50)
        print("✅ アップロード処理完了")
        print("=" * 50)


if __name__ == "__main__":
    uploader = SpotifyPodcastUploader()
    uploader.run()