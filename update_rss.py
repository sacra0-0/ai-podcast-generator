import os
import glob
import shutil
from datetime import datetime
from xml.etree import ElementTree as ET

# iTunes名前空間を登録
ET.register_namespace('itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
ET.register_namespace('content', 'http://purl.org/rss/1.0/modules/content/')


class RSSUpdater:
    def __init__(self, github_repo):
        """
        github_repo: "username/repo-name" の形式
        """
        self.github_repo = github_repo
        self.rss_file = "docs/podcast_feed.xml"
        self.audio_dir = "docs/audio"

        # docsディレクトリが存在しない場合は作成
        os.makedirs("docs", exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
    
    def get_latest_audio_file(self):
        """最新の音声ファイルを取得"""
        audio_files = glob.glob("podcast_*.wav")
        if not audio_files:
            print("⚠️ 音声ファイルが見つかりません")
            return None
        
        latest_audio = max(audio_files, key=os.path.getctime)
        print(f"📁 最新音声: {latest_audio}")
        return latest_audio
    
    def get_latest_script_file(self):
        """最新の台本ファイルを取得"""
        script_files = glob.glob("script_*.txt")
        if not script_files:
            return None
        
        latest_script = max(script_files, key=os.path.getctime)
        return latest_script
    
    def read_script_summary(self, script_file):
        """台本から概要を抽出（最初の200文字）"""
        if not script_file or not os.path.exists(script_file):
            return "今日の最新AIニュースをお届けします"

        try:
            with open(script_file, "r", encoding="utf-8") as f:
                content = f.read()
                # 最初の200文字を取得
                summary = content[:200].replace("\n", " ").strip()
                if len(content) > 200:
                    summary += "..."
                return summary
        except Exception as e:
            print(f"⚠️ 台本読み込みエラー: {e}")
            return "今日の最新AIニュースをお届けします"

    def copy_audio_to_docs(self, audio_file):
        """音声ファイルをdocs/audioフォルダにコピー"""
        if not os.path.exists(audio_file):
            print(f"❌ 音声ファイルが見つかりません: {audio_file}")
            return None

        try:
            audio_filename = os.path.basename(audio_file)
            destination = os.path.join(self.audio_dir, audio_filename)

            # ファイルをコピー
            shutil.copy2(audio_file, destination)
            print(f"✅ 音声ファイルをコピー: {destination}")

            return audio_filename
        except Exception as e:
            print(f"❌ ファイルコピーエラー: {e}")
            return None
    
    def update_rss(self):
        """RSSフィードを更新"""
        print("=" * 50)
        print("📡 RSSフィード更新")
        print("=" * 50)

        # 最新の音声ファイルを取得
        latest_audio = self.get_latest_audio_file()
        if not latest_audio:
            print("❌ 更新する音声ファイルがありません")
            return False

        # 音声ファイルをdocs/audioにコピー
        audio_filename = self.copy_audio_to_docs(latest_audio)
        if not audio_filename:
            print("❌ 音声ファイルのコピーに失敗しました")
            return False

        # 最新の台本を取得
        latest_script = self.get_latest_script_file()
        description = self.read_script_summary(latest_script)
        
        # RSSフィードを読み込むか新規作成
        if os.path.exists(self.rss_file):
            try:
                tree = ET.parse(self.rss_file)
                root = tree.getroot()
                print("✅ 既存のRSSを読み込み")
                # 既存のRSSに不足している情報を追加
                self.ensure_required_fields(root)
            except ET.ParseError as e:
                print(f"⚠️ 既存RSSの解析エラー: {e}")
                print("🔄 新しいRSSフィードを作成します")
                root = self.create_base_rss()
                tree = ET.ElementTree(root)
        else:
            root = self.create_base_rss()
            tree = ET.ElementTree(root)
            print("✅ 新規RSSを作成")

        channel = root.find("channel")
        
        # 新しいエピソードを追加
        item = ET.SubElement(channel, "item")
        
        # タイトル
        title = ET.SubElement(item, "title")
        title.text = f"AIニュースポッドキャスト - {datetime.now().strftime('%Y年%m月%d日')}"
        
        # 説明
        desc = ET.SubElement(item, "description")
        desc.text = description
        
        # 公開日時
        pub_date = ET.SubElement(item, "pubDate")
        pub_date.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        # 音声ファイルのURL（GitHub Pagesを使用）
        username = self.github_repo.split('/')[0]
        repo_name = self.github_repo.split('/')[1]
        audio_url = f"https://{username}.github.io/{repo_name}/audio/{audio_filename}"
        
        enclosure = ET.SubElement(item, "enclosure")
        enclosure.set("url", audio_url)
        enclosure.set("type", "audio/wav")
        
        # ファイルサイズ
        file_size = os.path.getsize(latest_audio)
        enclosure.set("length", str(file_size))
        
        # GUID（一意のID）
        guid = ET.SubElement(item, "guid")
        guid.set("isPermaLink", "false")
        guid.text = f"{self.github_repo}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 再生時間（オプション）
        duration = ET.SubElement(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}duration")
        # 仮の再生時間（実際の長さを計算する場合は別途処理が必要）
        duration.text = "05:00"
        
        # XMLを整形して保存
        self.indent(root)
        tree.write(self.rss_file, encoding="utf-8", xml_declaration=True)
        
        print(f"✅ RSSフィード更新完了: {self.rss_file}")
        print(f"📊 ファイルサイズ: {file_size / 1024 / 1024:.2f} MB")
        print("=" * 50)
        
        return True
    
    def create_base_rss(self):
        """基本的なRSSフィード構造を作成"""
        itunes_ns = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"

        rss = ET.Element("rss")
        rss.set("version", "2.0")
        rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
        rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")

        channel = ET.SubElement(rss, "channel")

        # ポッドキャストのメタ情報
        title = ET.SubElement(channel, "title")
        title.text = "AIニュースポッドキャスト"

        description = ET.SubElement(channel, "description")
        description.text = "毎日最新のAIニュースを自動生成でお届けするポッドキャスト"

        link = ET.SubElement(channel, "link")
        link.text = f"https://github.com/{self.github_repo}"

        language = ET.SubElement(channel, "language")
        language.text = "ja"

        # メールアドレス（必須）
        managing_editor = ET.SubElement(channel, "managingEditor")
        managing_editor.text = "sakuraryota1118@gmail.com (AI Podcast Generator)"

        # カバーアート（必須）
        image = ET.SubElement(channel, "image")
        image_url = ET.SubElement(image, "url")
        image_url.text = f"https://{self.github_repo.split('/')[0]}.github.io/{self.github_repo.split('/')[1]}/podcast-cover.png"
        image_title = ET.SubElement(image, "title")
        image_title.text = "AIニュースポッドキャスト"
        image_link = ET.SubElement(image, "link")
        image_link.text = f"https://github.com/{self.github_repo}"

        # iTunes用のカバーアート
        itunes_image = ET.SubElement(channel, f"{itunes_ns}image")
        itunes_image.set("href", f"https://{self.github_repo.split('/')[0]}.github.io/{self.github_repo.split('/')[1]}/podcast-cover.png")

        # iTunes固有のタグ
        itunes_author = ET.SubElement(channel, f"{itunes_ns}author")
        itunes_author.text = "sacra0-0"

        itunes_category = ET.SubElement(channel, f"{itunes_ns}category")
        itunes_category.set("text", "Technology")

        itunes_explicit = ET.SubElement(channel, f"{itunes_ns}explicit")
        itunes_explicit.text = "false"

        # オーナー情報（Spotify for Podcastersで必要）
        itunes_owner = ET.SubElement(channel, f"{itunes_ns}owner")
        itunes_owner_name = ET.SubElement(itunes_owner, f"{itunes_ns}name")
        itunes_owner_name.text = "sacra0-0"
        itunes_owner_email = ET.SubElement(itunes_owner, f"{itunes_ns}email")
        itunes_owner_email.text = "sakuraryota1118@gmail.com"
        
        # 著作権情報
        copyright_elem = ET.SubElement(channel, "copyright")
        copyright_elem.text = "Copyright 2025 sacra0-0. All rights reserved."
        
        # ウェブマスター
        webmaster = ET.SubElement(channel, "webMaster")
        webmaster.text = "sakuraryota1118@gmail.com (sacra0-0)"
        
        return rss
    
    def ensure_required_fields(self, root):
        """既存のRSSフィードに必要なフィールドが不足していないか確認し、追加"""
        channel = root.find("channel")
        itunes_ns = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"

        # iTunes owner情報を確認・追加
        if channel.find(f"{itunes_ns}owner") is None:
            itunes_owner = ET.SubElement(channel, f"{itunes_ns}owner")
            itunes_owner_name = ET.SubElement(itunes_owner, f"{itunes_ns}name")
            itunes_owner_name.text = "sacra0-0"
            itunes_owner_email = ET.SubElement(itunes_owner, f"{itunes_ns}email")
            itunes_owner_email.text = "sakuraryota1118@gmail.com"
            print("✅ iTunes owner情報を追加")

        # 著作権情報を確認・追加
        if channel.find("copyright") is None:
            copyright_elem = ET.SubElement(channel, "copyright")
            copyright_elem.text = "Copyright 2025 sacra0-0. All rights reserved."
            print("✅ 著作権情報を追加")

        # ウェブマスター情報を確認・追加
        if channel.find("webMaster") is None:
            webmaster = ET.SubElement(channel, "webMaster")
            webmaster.text = "sakuraryota1118@gmail.com (sacra0-0)"
            print("✅ ウェブマスター情報を追加")

        # iTunes author情報を更新
        itunes_author = channel.find(f"{itunes_ns}author")
        if itunes_author is not None:
            itunes_author.text = "sacra0-0"
        else:
            itunes_author = ET.SubElement(channel, f"{itunes_ns}author")
            itunes_author.text = "sacra0-0"
            print("✅ iTunes author情報を追加")
    
    def indent(self, elem, level=0):
        """XMLを見やすく整形"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self.indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


def main():
    # 環境変数からリポジトリ名を取得
    github_repo = os.environ.get("GITHUB_REPOSITORY")
    
    if not github_repo:
        print("⚠️ GITHUB_REPOSITORY が設定されていません")
        print("ローカルテスト用にデフォルト値を使用")
        github_repo = "your-username/ai-podcast-generator"
    
    updater = RSSUpdater(github_repo)
    success = updater.update_rss()
    
    if success:
        print("\n🎉 RSS更新完了！")
        print(f"📡 フィードURL: https://{github_repo.split('/')[0]}.github.io/{github_repo.split('/')[1]}/podcast_feed.xml")
    else:
        print("\n❌ RSS更新失敗")


if __name__ == "__main__":
    main()