# 🚀 Quick Reference Card - Chatbot Backend

## 5-Minute Setup

```bash
# 1. Navigate to backend
cd backend/api/Chatbot_Api/philoagents-api

# 2. Create virtual environment
python -m venv venv

# 3. Activate (choose your OS)
source venv/bin/activate        # macOS/Linux
# OR
venv\Scripts\activate           # Windows

# 4. Install dependencies
pip install -e ".[dev]"

# 5. Setup configuration
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=gsk_...

# 6. Run backend
python -m uvicorn src.chatbot.main:app --reload
```

## In Another Terminal - Run Frontend

```bash
cd frontend
streamlit run pages/Login/app.py
```

## API Endpoints

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/health` | GET | Health check | `curl http://localhost:8000/health` |
| `/api/chatbot/chatbots` | GET | List chatbots | `curl http://localhost:8000/api/chatbot/chatbots` |
| `/api/chatbot/chatbots/{id}` | GET | Get chatbot details | `curl http://localhost:8000/api/chatbot/chatbots/heat-pump-assistant` |
| `/api/chatbot/chat` | POST | Send message | `curl -X POST http://localhost:8000/api/chatbot/chat -H "Content-Type: application/json" -d '{"message":"...","chatbot_id":"...","user_id":1,"system_id":1}'` |

## Chat Endpoint Request/Response

### Request
```json
{
  "message": "What is my COP?",
  "chatbot_id": "heat-pump-assistant",
  "user_id": 1,
  "system_id": 1
}
```

### Response
```json
{
  "answer": "Your COP (Coefficient of Performance)...",
  "chatbot_id": "heat-pump-assistant",
  "status": "success"
}
```

## File Structure

```
src/chatbot/
├── domain/                  # Business models
├── application/             # Business logic
│   ├── chatbot_service.py
│   ├── conversation_orchestrator.py
│   └── (rag/, evaluation/, conversation/)
├── infrastructure/          # API & integrations
│   └── routes/
│       └── chat.py
├── config.py               # Settings
└── main.py                 # Entry point
```

## Key Commands

```bash
# Start backend (development)
python -m uvicorn src.chatbot.main:app --reload

# Start backend (production)
python -m uvicorn src.chatbot.main:app --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Format code
black src/

# Type checking
mypy src/

# View API docs
# Open: http://localhost:8000/docs
```

## Environment Variables (.env)

```bash
# Required
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Optional (Phase 2+)
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=chatbot
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check Python version (3.9+), virtual environment activated |
| "GROQ_API_KEY not set" | Add to .env and restart backend |
| Frontend can't reach backend | Backend running on 8000? Check CORS settings |
| Chatbot returns fallback | Normal if API slow, check API key validity |
| 404 Not Found | Check endpoint URL spelling |
| 500 Internal Error | Check backend logs for error details |

## Important URLs

- API Docs (Swagger): http://localhost:8000/docs
- API Docs (ReDoc): http://localhost:8000/redoc
- Health Check: http://localhost:8000/health
- Frontend: http://localhost:8501

## Directory Paths

```bash
# Backend root
backend/api/Chatbot_Api/philoagents-api/

# Source code
backend/api/Chatbot_Api/philoagents-api/src/chatbot/

# Configuration
backend/api/Chatbot_Api/philoagents-api/.env

# Documentation
backend/api/Chatbot_Api/philoagents-api/STARTUP_GUIDE.md
backend/api/Chatbot_Api/philoagents-api/README_CHATBOT.md

# Frontend
frontend/pages/consumer.py
```

## Testing Locally

```bash
# Test health
curl http://localhost:8000/health

# Test chatbots list
curl http://localhost:8000/api/chatbot/chatbots

# Test chat
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "chatbot_id": "heat-pump-assistant",
    "user_id": 1,
    "system_id": 1
  }'
```

## Documentation Files

| File | Purpose |
|------|---------|
| `STARTUP_GUIDE.md` | Step-by-step setup |
| `README_CHATBOT.md` | Feature overview |
| `TESTING_GUIDE.md` | Testing approaches |
| `IMPLEMENTATION_STATUS.md` | What was done |
| `COMPLETE_SUMMARY.md` | Executive summary |
| `.env.example` | Configuration template |

## Architecture

```
Streamlit Frontend
    ↓
FastAPI Routes
    ↓
ConversationOrchestrator
    ↓
Groq LLM
    ↓
Response
```

## Default Chatbot

**ID**: `heat-pump-assistant`

Use this ID when making API calls to the chat endpoint.

## API Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 404 | Chatbot not found |
| 500 | Server error |
| 422 | Validation error (missing fields) |

## Getting Help

1. Check `STARTUP_GUIDE.md` for setup issues
2. Check `TESTING_GUIDE.md` for testing
3. Visit `http://localhost:8000/docs` to test API
4. Check backend terminal logs
5. Check browser console (F12)

## Quick Wins

- ✅ Backend runs: `python -m uvicorn src.chatbot.main:app --reload`
- ✅ Frontend runs: `streamlit run pages/Login/app.py`
- ✅ API docs: http://localhost:8000/docs
- ✅ Chat works: Try message in frontend chat panel
- ✅ Logs show: Terminal window shows requests/responses

---

**Version**: 2.0.0  
**Status**: Ready to Run ✅  
**Last Updated**: May 8, 2026  

Print this card for quick reference! 📋
