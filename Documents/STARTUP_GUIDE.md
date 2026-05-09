# 🚀 Chatbot Backend - Startup Guide

## Overview

This guide walks you through getting the refactored chatbot backend running and integrated with the frontend.

## Prerequisites

- Python 3.9+
- pip or conda
- Groq API key (free tier available at https://console.groq.com)
- Optional: MongoDB instance (for persistence features in Phase 2+)

## Step 1: Get Groq API Key

1. Visit https://console.groq.com
2. Sign up or log in
3. Create a new API key
4. Keep this key safe - you'll need it for configuration

## Step 2: Install Backend

### Option A: Windows

```powershell
cd backend\api\Chatbot_Api\philoagents-api
.\setup.ps1
```

### Option B: macOS/Linux

```bash
cd backend/api/Chatbot_Api/philoagents-api
chmod +x setup.sh
./setup.sh
```

### Option C: Manual Setup

```bash
cd backend/api/Chatbot_Api/philoagents-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env  # On Windows: copy .env.example .env
```

## Step 3: Configure Environment

Edit the `.env` file and add your settings:

```bash
# Required
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.7

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# MongoDB (optional for Phase 2+)
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=chatbot
```

## Step 4: Run the Backend

### Option A: Development Mode (with auto-reload)

```bash
# Activate virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the server
python -m uvicorn src.chatbot.main:app --reload --host 0.0.0.0 --port 8000
```

### Option B: Production Mode

```bash
python -m uvicorn src.chatbot.main:app --host 0.0.0.0 --port 8000 --workers 4
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Step 5: Test the API

### Option A: Interactive Swagger UI

Open your browser to: **http://localhost:8000/docs**

This gives you an interactive API explorer where you can test endpoints.

### Option B: curl Commands

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

List available chatbots:
```bash
curl http://localhost:8000/api/chatbot/chatbots
```

Send a chat message:
```bash
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my system status?",
    "chatbot_id": "heat-pump-assistant",
    "user_id": 1,
    "system_id": 1
  }'
```

Expected response:
```json
{
  "answer": "Your system is currently operating at 3.8 COP...",
  "chatbot_id": "heat-pump-assistant",
  "status": "success"
}
```

## Step 6: Run Frontend (Streamlit)

In a new terminal:

```bash
cd frontend

# Install dependencies if needed
pip install -r requirements.txt

# Run the app
streamlit run pages/Login/app.py
```

The frontend will open at **http://localhost:8501**

Login and navigate to the consumer page to test the chatbot integration.

## Step 7: Verify Integration

1. Backend should be running at `http://localhost:8000`
2. Frontend (Streamlit) should be running at `http://localhost:8501`
3. In the frontend, scroll down to the "Chat Assistant" section
4. Type a message and click Send
5. You should receive a response from the chatbot backend

### Debug Output

If something doesn't work:

1. **Check backend logs**: Watch terminal running the backend for error messages
2. **Check browser console**: In frontend, open developer tools (F12) and check Console tab
3. **Check API directly**: Use Swagger UI at http://localhost:8000/docs
4. **Verify API key**: Make sure GROQ_API_KEY is set correctly in .env

## Common Issues

### Issue: "Connection refused" from frontend
**Solution**: Make sure backend is running on port 8000

### Issue: "GROQ_API_KEY not set"
**Solution**: Add `GROQ_API_KEY=your_key` to `.env` file

### Issue: "Module not found" errors
**Solution**: Make sure you've run `pip install -e ".[dev]"` with the virtual environment activated

### Issue: Chatbot returns fallback responses
**Solution**: This is normal if Groq API is slow. Increase timeout or check Groq API status

### Issue: CORS errors in browser console
**Solution**: Make sure CORS_ORIGINS in .env includes your frontend URL

## Directory Structure

```
backend/api/Chatbot_Api/philoagents-api/
├── src/chatbot/
│   ├── domain/              # Business models
│   ├── application/         # Business logic
│   ├── infrastructure/      # API & external integrations
│   ├── config.py           # Configuration
│   └── main.py             # Entry point
├── tests/                  # Test files
├── .env.example            # Environment template
├── setup.sh / setup.ps1    # Setup scripts
├── pyproject.toml          # Dependencies
└── README_CHATBOT.md       # Documentation
```

## API Documentation

Once running, view interactive docs at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Next Steps

After successful setup:

1. **Customize chatbot**: Edit config to change prompts, models, or add new chatbots
2. **Add documents**: Phase 2 will add RAG support for retrieval
3. **Setup MongoDB**: Phase 2 will enable conversation persistence
4. **Add evaluation**: Phase 3 will add quality metrics

## Support & Troubleshooting

For detailed information:
- See `README_CHATBOT.md` for overview
- See `REFACTORING_IMPLEMENTATION_GUIDE.md` for architecture
- See `CODE_EXAMPLES_REFERENCE.md` for code patterns
- Check FastAPI docs at http://localhost:8000/docs

## Quick Reference Commands

```bash
# Activate virtual environment
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Run backend (development)
python -m uvicorn src.chatbot.main:app --reload

# Run tests
pytest tests/

# Format code
black src/

# Type checking
mypy src/

# View API docs
# Open http://localhost:8000/docs

# Run frontend
streamlit run pages/Login/app.py
```

---

**Version**: 2.0.0  
**Last Updated**: May 8, 2026  
**Status**: Ready to Run ✅
