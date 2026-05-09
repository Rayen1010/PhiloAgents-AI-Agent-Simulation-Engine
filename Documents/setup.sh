#!/bin/bash
# Setup script for chatbot backend

echo "🚀 Setting up Chatbot Backend..."

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
else
    echo "✓ Virtual environment already exists"
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -e ".[dev]"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please configure .env with your API keys!"
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Configure your .env file with API keys"
echo "2. Run: python -m uvicorn src.chatbot.main:app --reload"
echo "3. Open http://localhost:8000/docs in your browser"
echo ""
