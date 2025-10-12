# AI Podcast Generator - Windows セットアップスクリプト

Write-Host "🎙️ AI Podcast Generator - セットアップスクリプト" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Pythonバージョン確認
Write-Host "📋 Pythonバージョン確認中..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion が見つかりました" -ForegroundColor Green
} catch {
    Write-Host "✗ Python がインストールされていません" -ForegroundColor Red
    Write-Host "https://www.python.org/downloads/ からインストールしてください" -ForegroundColor Yellow
    exit 1
}

# 仮想環境の作成
Write-Host ""
Write-Host "🔧 仮想環境を作成中..." -ForegroundColor Yellow
if (Test-Path "venv") {
    $response = Read-Host "既存の仮想環境が見つかりました。削除して再作成しますか? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Remove-Item -Recurse -Force venv
        python -m venv venv
        Write-Host "✓ 仮想環境を再作成しました" -ForegroundColor Green
    } else {
        Write-Host "⚠ 既存の仮想環境を使用します" -ForegroundColor Yellow
    }
} else {
    python -m venv venv
    Write-Host "✓ 仮想環境を作成しました" -ForegroundColor Green
}

# 仮想環境の有効化
Write-Host ""
Write-Host "🔄 仮想環境を有効化中..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ 仮想環境を有効化しました" -ForegroundColor Green

# 依存関係のインストール
Write-Host ""
Write-Host "📦 依存関係をインストール中..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
Write-Host "✓ 依存関係のインストールが完了しました" -ForegroundColor Green

# .envファイルの作成
Write-Host ""
Write-Host "🔑 環境変数ファイルを設定中..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    @"
# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# GitHub設定 (GitHub Actionsで自動設定されます)
# GITHUB_TOKEN=your_github_token
# GITHUB_REPOSITORY=username/repo-name

# Spotify設定 (オプション)
# SPOTIFY_SHOW_ID=your_show_id
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✓ .env ファイルを作成しました" -ForegroundColor Green
    Write-Host "⚠ .env ファイルを編集してAPIキーを設定してください" -ForegroundColor Yellow
} else {
    Write-Host "⚠ .env ファイルは既に存在します" -ForegroundColor Yellow
}

# .githubディレクトリの作成
Write-Host ""
Write-Host "📁 必要なディレクトリを確認中..." -ForegroundColor Yellow
if (-not (Test-Path ".github\workflows")) {
    New-Item -ItemType Directory -Path ".github\workflows" -Force | Out-Null
}
if (-not (Test-Path "docs")) {
    New-Item -ItemType Directory -Path "docs" -Force | Out-Null
}
Write-Host "✓ ディレクトリ構造を確認しました" -ForegroundColor Green

# 完了メッセージ
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "✅ セットアップが完了しました！" -ForegroundColor Green
Write-Host ""
Write-Host "次のステップ:" -ForegroundColor Yellow
Write-Host "1. .env ファイルを編集して GEMINI_API_KEY を設定"
Write-Host "   > notepad .env"
Write-Host ""
Write-Host "2. ローカルでテスト実行"
Write-Host "   > .\venv\Scripts\Activate.ps1"
Write-Host "   > python test_local.py"
Write-Host ""
Write-Host "3. 実際のポッドキャスト生成"
Write-Host "   > python podcast_generator.py"
Write-Host ""
Write-Host "4. GitHubにプッシュ"
Write-Host "   > git add ."
Write-Host '   > git commit -m "Initial commit"'
Write-Host "   > git push origin main"
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan