# Chatbot Backend Setup Script
# For Windows PowerShell

Write-Host "🚀 Setting up Chatbot Backend..." -ForegroundColor Green

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (-Not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    & venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
    & venv\Scripts\Activate.ps1
}

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -e ".[dev]"

# Create .env file if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host "🔧 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Please configure .env with your API keys!" -ForegroundColor Red
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "logs" -Force | Out-Null
New-Item -ItemType Directory -Path "data" -Force | Out-Null

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Configure your .env file with API keys"
Write-Host "2. Run: python -m uvicorn src.chatbot.main:app --reload"
Write-Host "3. Open http://localhost:8000/docs in your browser"
Write-Host ""
