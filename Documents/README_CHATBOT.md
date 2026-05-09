# Chatbot Backend - Refactored from PhiloAgents

A generic, modular chatbot backend built on the PhiloAgents architecture, adapted for production chatbot systems with RAG (Retrieval-Augmented Generation) and evaluation capabilities.

## 🎯 Overview

This is a **Phase 1 implementation** of a refactored chatbot backend that:

- ✅ Removes philosopher-specific logic
- ✅ Provides generic chatbot configuration
- ✅ Integrates with LangChain/LangGraph
- ✅ Supports RAG pipelines (framework in place)
- ✅ Includes evaluation hooks (framework in place)
- ✅ Offers clean REST API
- ✅ Maintains modular architecture

## 📁 Project Structure

```
src/chatbot/
├── domain/                  # Business entities
│   ├── chatbot.py          # Chatbot configuration model
│   ├── conversation.py     # Conversation state and messages
│   ├── exceptions.py       # Domain-specific exceptions
│   └── __init__.py
├── application/            # Business logic
│   ├── chatbot_service.py # Service for managing chatbots
│   ├── conversation_orchestrator.py  # Main orchestration logic
│   ├── rag/               # RAG pipeline (Phase 2)
│   ├── evaluation/        # Evaluation framework (Phase 3)
│   ├── conversation/      # Conversation workflow (Phase 2)
│   └── __init__.py
├── infrastructure/        # External integrations
│   ├── api.py            # FastAPI application
│   ├── routes/           # API route handlers
│   │   ├── chat.py       # Chat endpoints
│   │   └── __init__.py
│   └── __init__.py
├── config.py             # Settings management
├── main.py              # Application entry point
└── __init__.py
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend/api/Chatbot_Api/philoagents-api
pip install -e ".[dev]"
```

### 2. Configure Environment

Create a `.env` file:

```bash
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key (optional)
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=chatbot
```

### 3. Run the Backend

```bash
python -m uvicorn src.chatbot.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 4. Access API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 💬 API Endpoints

### Chat Endpoint

**POST** `/api/chatbot/chat`

Request:
```json
{
  "message": "What is the COP of my heat pump?",
  "chatbot_id": "heat-pump-assistant",
  "user_id": 1,
  "system_id": 1
}
```

Response:
```json
{
  "answer": "The COP (Coefficient of Performance)...",
  "chatbot_id": "heat-pump-assistant",
  "status": "success"
}
```

### List Chatbots

**GET** `/api/chatbot/chatbots`

Returns all available chatbots.

### Get Chatbot Details

**GET** `/api/chatbot/chatbots/{chatbot_id}`

Returns configuration for a specific chatbot.

### Health Check

**GET** `/health`

Returns server health status.

## 🔧 Configuration

Edit `src/chatbot/config.py` to modify:

- LLM model and parameters
- MongoDB connection
- RAG settings
- Chatbot defaults

## 📋 Features Implemented (Phase 1)

✅ Generic chatbot model  
✅ Chatbot service with in-memory storage  
✅ Conversation orchestrator  
✅ FastAPI application setup  
✅ Chat endpoints  
✅ Fallback responses  
✅ Error handling  
✅ Health checks  
✅ CORS support  
✅ Configuration management  

## 🔮 Features in Development (Phase 2-5)

- RAG pipeline integration (documents, embeddings, retrieval)
- LangGraph workflow with nodes (conversation, retrieval, summarization)
- Evaluation framework (metrics, quality assessment)
- Conversation history persistence
- Multi-turn dialogue management
- Streaming responses
- WebSocket support
- Advanced chatbot management

## 📊 Current Limitations

- Chatbots stored in memory (not persistent)
- No document retrieval yet
- No evaluation metrics yet
- Basic response generation (LLM only)
- No streaming responses yet
- No conversation history yet

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_chatbot_service.py -v
```

## 📝 Integration with Frontend

The Streamlit frontend (`frontend/pages/consumer.py`) is already configured to call this API:

```python
RAG_API_ENDPOINT = "http://localhost:8000/api/chatbot/chat"

response = requests.post(
    RAG_API_ENDPOINT,
    json={
        "message": user_message,
        "chatbot_id": "heat-pump-assistant",
        "user_id": 1,
        "system_id": 1,
    }
)
```

## 🐛 Troubleshooting

### API not responding
- Check if backend is running: `python -m uvicorn src.chatbot.main:app --reload`
- Verify GROQ_API_KEY is set in `.env`
- Check logs for errors

### Chatbot not found
- Use default ID: `heat-pump-assistant`
- List available chatbots: `GET /api/chatbot/chatbots`

### Connection errors
- Ensure MongoDB is running (if using persistence)
- Check MONGO_URI in `.env`

## 📚 Documentation

See the root project documentation:
- `ARCHITECTURE_ANALYSIS.md` - Architecture overview
- `REFACTORING_IMPLEMENTATION_GUIDE.md` - Detailed refactoring plan
- `CODE_EXAMPLES_REFERENCE.md` - Code patterns and examples

## 🔄 Refactoring Roadmap

This is **Phase 1 (Abstraction Layer)** of a planned 5-phase refactoring:

- **Phase 1** ✅ (Current): Generic agent/chatbot model, basic services
- **Phase 2** (Next): Conversation state, workflow nodes, tool registry
- **Phase 3**: Evaluation abstraction, knowledge base interface
- **Phase 4**: API redesign, agent management endpoints
- **Phase 5**: Testing, cleanup, documentation

## 🤝 Contributing

When extending this backend:

1. Keep domain logic separate from infrastructure
2. Add tests for new features
3. Update API documentation
4. Follow the established patterns
5. Use type hints

## 📞 Support

For issues or questions:
1. Check API docs at `/docs`
2. Review error messages and logs
3. Refer to implementation guides
4. Check example configurations

## 📄 License

MIT License - See LICENSE file for details

---

**Version**: 2.0.0  
**Status**: Phase 1 Complete, Phase 2 In Planning  
**Last Updated**: May 8, 2026
