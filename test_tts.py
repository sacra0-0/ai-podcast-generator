import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# 短いテスト
contents = [
    types.Content(
        role="user",
        parts=[types.Part.from_text(text="Speaker 1: こんにちは\nSpeaker 2: こんにちは")],
    ),
]

config = types.GenerateContentConfig(
    temperature=1,
    response_modalities=["audio"],
    speech_config=types.SpeechConfig(
        multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
            speaker_voice_configs=[
                types.SpeakerVoiceConfig(
                    speaker="Speaker 1",
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
                    ),
                ),
                types.SpeakerVoiceConfig(
                    speaker="Speaker 2",
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                    ),
                ),
            ]
        ),
    ),
)

print("🎙️ TTS テスト中...")
for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash-preview-tts",
    contents=contents,
    config=config,
):
    if chunk.candidates and chunk.candidates[0].content:
        part = chunk.candidates[0].content.parts[0]
        if part.inline_data and part.inline_data.data:
            with open("test_audio.wav", "wb") as f:
                f.write(part.inline_data.data)
            print("✅ 音声生成成功: test_audio.wav")
            break