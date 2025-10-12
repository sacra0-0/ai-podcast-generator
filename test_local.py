"""
ローカル環境でのテスト実行用スクリプト
実際のAPI呼び出しを行わずに動作確認ができます
"""

import os
from datetime import datetime


def test_environment():
    """環境設定のテスト"""
    print("=" * 50)
    print("🧪 環境設定テスト")
    print("=" * 50)
    
    checks = {
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
        "Python Version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
    }
    
    all_ok = True
    for key, value in checks.items():
        if value and value != "your_gemini_api_key_here":
            print(f"✅ {key}: 設定済み")
        else:
            print(f"❌ {key}: 未設定")
            all_ok = False
    
    return all_ok


def test_imports():
    """必要なライブラリのインポートテスト"""
    print("\n" + "=" * 50)
    print("📦 ライブラリインポートテスト")
    print("=" * 50)
    
    libraries = [
        ("google.genai", "Google Generative AI"),
        ("requests", "Requests"),
        ("bs4", "BeautifulSoup4"),
    ]
    
    all_ok = True
    for module_name, display_name in libraries:
        try:
            __import__(module_name)
            print(f"✅ {display_name}: OK")
        except ImportError as e:
            print(f"❌ {display_name}: インポートエラー - {e}")
            all_ok = False
    
    return all_ok


def test_news_search():
    """ニュース検索機能のテスト（モック）"""
    print("\n" + "=" * 50)
    print("🔍 ニュース検索テスト")
    print("=" * 50)
    
    # モックニュースデータ
    mock_news = [
        {
            "title": "OpenAI releases GPT-5 with breakthrough capabilities",
            "description": "OpenAI announced GPT-5 today...",
            "link": "https://example.com/news1"
        },
        {
            "title": "Google announces Gemini 3.0 Pro",
            "description": "Google's latest AI model...",
            "link": "https://example.com/news2"
        }
    ]
    
    print(f"✅ {len(mock_news)}件のモックニュースを生成")
    for i, news in enumerate(mock_news, 1):
        print(f"   {i}. {news['title'][:50]}...")
    
    return True


def test_script_generation():
    """台本生成のテスト（モック）"""
    print("\n" + "=" * 50)
    print("📝 台本生成テスト")
    print("=" * 50)
    
    mock_script = """Speaker 1: こんにちは！今日のAIニュースポッドキャストへようこそ。
Speaker 2: こんにちは。今日も面白いニュースがたくさんありますよ。
Speaker 1: それでは早速、最初のニュースから見ていきましょう！"""
    
    print("✅ モック台本を生成:")
    print(mock_script[:100] + "...")
    
    return True


def test_file_operations():
    """ファイル操作のテスト"""
    print("\n" + "=" * 50)
    print("📄 ファイル操作テスト")
    print("=" * 50)
    
    test_file = "test_output.txt"
    
    try:
        # 書き込みテスト
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(f"Test at {datetime.now()}")
        print(f"✅ ファイル書き込み: {test_file}")
        
        # 読み込みテスト
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"✅ ファイル読み込み: {len(content)} bytes")
        
        # クリーンアップ
        os.remove(test_file)
        print(f"✅ ファイル削除: {test_file}")
        
        return True
    except Exception as e:
        print(f"❌ ファイル操作エラー: {e}")
        return False


def main():
    """メインテスト実行"""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║  🎙️  AI Podcast Generator - ローカルテスト  ║")
    print("╚" + "=" * 48 + "╝")
    print("\n")
    
    results = []
    
    # 各テストを実行
    results.append(("環境設定", test_environment()))
    results.append(("ライブラリ", test_imports()))
    results.append(("ニュース検索", test_news_search()))
    results.append(("台本生成", test_script_generation()))
    results.append(("ファイル操作", test_file_operations()))
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("📊 テスト結果サマリー")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 50)
    print(f"結果: {passed}/{total} テスト合格")
    print("=" * 50)
    
    if passed == total:
        print("\n🎉 すべてのテストに合格しました！")
        print("\n次のステップ:")
        print("1. .env ファイルに有効なGEMINI_API_KEYを設定")
        print("2. python podcast_generator.py で実行")
        return 0
    else:
        print("\n⚠️  いくつかのテストが失敗しました")
        print("エラーを確認して修正してください")
        return 1


if __name__ == "__main__":
    exit(main())