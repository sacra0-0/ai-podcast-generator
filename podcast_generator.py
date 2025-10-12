import os
import struct
from datetime import datetime
from google import genai
from google.genai import types
import requests
from bs4 import BeautifulSoup


class PodcastGenerator:
    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.gemini_api_key)
        
    def search_ai_news(self):
        """最新のAIニュースを検索"""
        print("🔍 AIニュースを検索中...")
        
        # Google検索APIまたはニュースサイトのRSSを使用
        # ここでは例として複数のAIニュースソースを統合
        news_sources = [
            "https://news.google.com/rss/search?q=AI+artificial+intelligence+when:1d&hl=ja&gl=JP&ceid=JP:ja",
            "https://techcrunch.com/category/artificial-intelligence/feed/",
        ]
        
        news_items = []
        for source in news_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all('item')[:3]  # 各ソースから3件
                    for item in items:
                        title = item.find('title').text if item.find('title') else ""
                        description = item.find('description').text if item.find('description') else ""
                        link = item.find('link').text if item.find('link') else ""
                        
                        news_items.append({
                            'title': title,
                            'description': description,
                            'link': link
                        })
            except Exception as e:
                print(f"ニュース取得エラー ({source}): {e}")
                
        return news_items[:5]  # 最大5件のニュース
    
    def generate_podcast_script(self, news_items):
        """ニュースをポッドキャスト台本に変換"""
        print("📝 ポッドキャスト台本を生成中...")
        
        news_summary = "\n\n".join([
            f"ニュース{i+1}: {item['title']}\n{item['description']}"
            for i, item in enumerate(news_items)
        ])
        
        prompt = f"""以下の最新AIニュースを基に、2人の話者による5分程度のポッドキャスト台本を作成してください。

【ニュース内容】
{news_summary}

【台本の要件】
- Speaker 1: 明るく親しみやすい女性ホスト（導入と進行役）
- Speaker 2: 落ち着いた男性解説者（技術的な解説担当）
- 自然な会話形式で、聞き手が理解しやすいように説明
- 各ニュースについて簡潔に議論
- 冒頭に日付と挨拶、最後に締めの言葉を入れる

【出力形式】
Speaker 1: （セリフ）
Speaker 2: （セリフ）
という形式で出力してください。"""

        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        script = response.text
        print("✅ 台本生成完了")
        return script
    
    def generate_audio(self, script):
        """台本から音声を生成"""
        print("🎙️ 音声を生成中...")
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=f"以下の台本を自然な会話調で読み上げてください:\n\n{script}"),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            response_modalities=["audio"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker="Speaker 1",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="Zephyr"
                                )
                            ),
                        ),
                        types.SpeakerVoiceConfig(
                            speaker="Speaker 2",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="Puck"
                                )
                            ),
                        ),
                    ]
                ),
            ),
        )
        
        audio_data = b""
        mime_type = None
        
        for chunk in self.client.models.generate_content_stream(
            model="gemini-2.5-flash-preview-tts",
            contents=contents,
            config=generate_content_config,
        ):
            if (chunk.candidates and 
                chunk.candidates[0].content and 
                chunk.candidates[0].content.parts):
                
                part = chunk.candidates[0].content.parts[0]
                if part.inline_data and part.inline_data.data:
                    audio_data += part.inline_data.data
                    if mime_type is None:
                        mime_type = part.inline_data.mime_type
        
        # WAV形式に変換
        if mime_type and "audio/L" in mime_type:
            audio_data = self.convert_to_wav(audio_data, mime_type)
        
        # ファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"podcast_{timestamp}.wav"
        
        with open(filename, "wb") as f:
            f.write(audio_data)
        
        print(f"✅ 音声生成完了: {filename}")
        return filename
    
    def convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """音声データをWAV形式に変換"""
        parameters = self.parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size
        
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF", chunk_size, b"WAVE", b"fmt ",
            16, 1, num_channels, sample_rate,
            byte_rate, block_align, bits_per_sample,
            b"data", data_size
        )
        return header + audio_data
    
    def parse_audio_mime_type(self, mime_type: str) -> dict:
        """MIMEタイプから音声パラメータを抽出"""
        bits_per_sample = 16
        rate = 24000
        
        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate = int(param.split("=", 1)[1])
                except (ValueError, IndexError):
                    pass
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass
        
        return {"bits_per_sample": bits_per_sample, "rate": rate}
    
    def run(self):
        """メイン実行フロー"""
        print("=" * 50)
        print("🎙️ AIニュースポッドキャスト自動生成")
        print("=" * 50)
        
        # 1. ニュース検索
        news_items = self.search_ai_news()
        if not news_items:
            print("❌ ニュースが見つかりませんでした")
            return None
        
        print(f"✅ {len(news_items)}件のニュースを取得")
        
        # 2. 台本生成
        script = self.generate_podcast_script(news_items)
        
        # 台本を保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_filename = f"script_{timestamp}.txt"
        with open(script_filename, "w", encoding="utf-8") as f:
            f.write(script)
        print(f"✅ 台本保存: {script_filename}")
        
        # 3. 音声生成
        audio_filename = self.generate_audio(script)
        
        print("=" * 50)
        print("🎉 ポッドキャスト生成完了!")
        print(f"📄 台本: {script_filename}")
        print(f"🎵 音声: {audio_filename}")
        print("=" * 50)
        
        return audio_filename


if __name__ == "__main__":
    generator = PodcastGenerator()
    generator.run()