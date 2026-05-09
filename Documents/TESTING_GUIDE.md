# 🧪 Testing Guide - Chatbot Backend

## Overview

This guide covers manual testing, unit testing, and integration testing for the chatbot backend.

## Table of Contents

1. [Manual Testing](#manual-testing)
2. [Automated Unit Tests](#automated-unit-tests)
3. [Integration Testing](#integration-testing)
4. [Frontend Testing](#frontend-testing)
5. [Performance Testing](#performance-testing)

---

## Manual Testing

### Test 1: Backend Health Check

**Goal**: Verify the backend is running

**Steps**:
1. Start backend: `python -m uvicorn src.chatbot.main:app --reload`
2. Open browser: http://localhost:8000/health
3. Expected response: `{"status": "healthy"}`

**Pass/Fail**: ✅ Pass if you see the JSON response

---

### Test 2: List Available Chatbots

**Goal**: Verify default chatbot configuration

**Method**: Swagger UI or curl

**curl**:
```bash
curl -X GET http://localhost:8000/api/chatbot/chatbots
```

**Expected Response**:
```json
{
  "chatbots": [
    {
      "id": "heat-pump-assistant",
      "name": "Heat Pump Assistant",
      "description": "Helpful assistant for heat pump system queries",
      "system_prompt": "You are a helpful assistant for heat pump systems...",
      "enabled": true
    }
  ]
}
```

**Pass/Fail**: ✅ Pass if default chatbot is listed

---

### Test 3: Single Chatbot Details

**Goal**: Verify chatbot configuration retrieval

**curl**:
```bash
curl -X GET http://localhost:8000/api/chatbot/chatbots/heat-pump-assistant
```

**Expected Response**:
```json
{
  "id": "heat-pump-assistant",
  "name": "Heat Pump Assistant",
  "description": "Helpful assistant for heat pump system queries",
  "system_prompt": "...",
  "enabled": true
}
```

**Pass/Fail**: ✅ Pass if chatbot details are returned

---

### Test 4: Chat Endpoint with Valid Request

**Goal**: Verify chatbot can process messages

**curl**:
```bash
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is COP?",
    "chatbot_id": "heat-pump-assistant",
    "user_id": 1,
    "system_id": 1
  }'
```

**Expected Response**:
```json
{
  "answer": "The COP (Coefficient of Performance) indicates how efficiently...",
  "chatbot_id": "heat-pump-assistant",
  "status": "success"
}
```

**Pass/Fail**: 
- ✅ Pass if status is "success" and answer is provided
- ⚠️ Pass (with fallback) if answer is a fallback response (API might be slow)

---

### Test 5: Chat Endpoint with Invalid Chatbot ID

**Goal**: Verify error handling

**curl**:
```bash
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "chatbot_id": "nonexistent-chatbot",
    "user_id": 1,
    "system_id": 1
  }'
```

**Expected Response**:
```json
{
  "status": "error",
  "message": "Chatbot 'nonexistent-chatbot' not found"
}
```

**Pass/Fail**: ✅ Pass if proper error message is returned

---

### Test 6: Chat Endpoint with Missing Required Field

**Goal**: Verify request validation

**curl**:
```bash
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello"
  }'
```

**Expected Response**:
```json
{
  "detail": [
    {
      "loc": ["body", "chatbot_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Pass/Fail**: ✅ Pass if validation error is returned

---

## Automated Unit Tests

### Setup

Create `tests/test_chatbot_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from src.chatbot.infrastructure.api import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

def test_health_check(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_chatbots(client):
    """Test list chatbots endpoint"""
    response = client.get("/api/chatbot/chatbots")
    assert response.status_code == 200
    data = response.json()
    assert "chatbots" in data
    assert len(data["chatbots"]) > 0

def test_get_chatbot(client):
    """Test get specific chatbot"""
    response = client.get("/api/chatbot/chatbots/heat-pump-assistant")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "heat-pump-assistant"

def test_chat_valid_message(client):
    """Test chat with valid message"""
    response = client.post(
        "/api/chatbot/chat",
        json={
            "message": "What is COP?",
            "chatbot_id": "heat-pump-assistant",
            "user_id": 1,
            "system_id": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "answer" in data

def test_chat_invalid_chatbot(client):
    """Test chat with invalid chatbot ID"""
    response = client.post(
        "/api/chatbot/chat",
        json={
            "message": "Hello",
            "chatbot_id": "nonexistent",
            "user_id": 1,
            "system_id": 1
        }
    )
    assert response.status_code == 400

def test_chat_missing_fields(client):
    """Test chat with missing required fields"""
    response = client.post(
        "/api/chatbot/chat",
        json={"message": "Hello"}
    )
    assert response.status_code == 422  # Validation error
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_chatbot_api.py::test_health_check -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

---

## Integration Testing

### Test 1: Frontend to Backend Flow

**Goal**: Verify Streamlit frontend can call backend

**Steps**:

1. Start backend:
   ```bash
   python -m uvicorn src.chatbot.main:app --reload
   ```

2. Start frontend:
   ```bash
   cd frontend
   streamlit run pages/Login/app.py
   ```

3. Login to Streamlit app

4. Navigate to Consumer page

5. Scroll to "Chat Assistant" section

6. Type message: "What is my current COP?"

7. Click Send button

**Expected Result**:
- ✅ Message appears in chat history
- ✅ Bot response appears below message
- ✅ Response is meaningful (not just fallback)

**Troubleshooting**:
- Check backend logs for errors
- Check browser console (F12) for network errors
- Verify GROQ_API_KEY is set in .env

---

### Test 2: Fallback Response (No API)

**Goal**: Verify fallback works when API is unavailable

**Steps**:

1. Stop backend (Ctrl+C)

2. Refresh frontend

3. Type message in chat

4. Click Send

**Expected Result**:
- ✅ Response appears (fallback response)
- ✅ No error in browser console
- ✅ Chat continues working

---

### Test 3: Multiple Messages

**Goal**: Verify conversation continuity

**Steps**:

1. Send message 1: "Hello"
2. Send message 2: "What is a heat pump?"
3. Send message 3: "How much can I save?"

**Expected Result**:
- ✅ All messages appear in order
- ✅ Each gets a response
- ✅ No errors in console

---

## Frontend Testing

### Test 1: Chat UI Elements

**Goal**: Verify chat interface is visible and functional

**Checklist**:
- ✅ Chat Assistant header visible
- ✅ Message input field present
- ✅ Send button visible
- ✅ Previous chat messages display correctly
- ✅ Messages styled differently (user vs bot)

### Test 2: Message Formatting

**Goal**: Verify messages display correctly

**Tests**:
- ✅ Long messages wrap properly
- ✅ Special characters display correctly
- ✅ Emoji display correctly
- ✅ Links (if any) are clickable

### Test 3: Error Handling

**Goal**: Verify frontend handles errors gracefully

**Scenarios**:
- ✅ Network timeout: Should show fallback response
- ✅ Invalid response: Should show error message
- ✅ Backend crash: Should show fallback response

---

## Performance Testing

### Test 1: Response Time

**Goal**: Measure API response time

**Method**:
```bash
# Single request timing
time curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "chatbot_id": "heat-pump-assistant",
    "user_id": 1,
    "system_id": 1
  }'
```

**Expected**: < 5 seconds (including LLM API latency)

### Test 2: Concurrent Requests

**Goal**: Verify backend handles multiple requests

**Method**:
```bash
# Send 10 requests concurrently
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/chatbot/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Test $i\", \"chatbot_id\": \"heat-pump-assistant\", \"user_id\": 1, \"system_id\": 1}" &
done
wait
```

**Expected**: 
- ✅ All requests complete
- ✅ No errors
- ✅ Response times remain consistent

---

## Test Checklist

### Pre-Deployment

- [ ] All manual tests pass (Test 1-6)
- [ ] Unit tests pass: `pytest tests/`
- [ ] No console errors in frontend
- [ ] Frontend-Backend integration works (Frontend Test)
- [ ] Fallback responses work (Integration Test 2)
- [ ] Response times acceptable (Performance Test 1)
- [ ] Concurrent requests work (Performance Test 2)

### Post-Deployment

- [ ] Backend running on correct port
- [ ] Frontend can reach backend
- [ ] Chat functionality works end-to-end
- [ ] Logs show no errors
- [ ] API docs available at /docs

---

## Debugging Tips

### Backend Issues

**Check logs**:
```bash
# If running with logging
tail -f chatbot.log

# Or watch terminal output
# Look for errors in Uvicorn output
```

**Common issues**:
- `GROQ_API_KEY not set`: Add to .env
- `Connection refused`: Backend not running
- `404 Not Found`: Wrong endpoint URL

### Frontend Issues

**Check console** (Press F12):
- Network errors: Backend URL wrong or not accessible
- JavaScript errors: Streamlit library issues
- CORS errors: CORS not configured properly

**Enable debug logging**:
In consumer.py, you'll see `[DEBUG]` messages showing API calls.

### API Testing

**Use Swagger UI**:
1. Open http://localhost:8000/docs
2. Try endpoints from there
3. See exact request/response format
4. Test with different parameters

---

## Test Environment Variables

For testing, create `.env.test`:
```bash
GROQ_API_KEY=test_key
GROQ_MODEL=llama-3.3-70b-versatile
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=true
```

Then load it for tests:
```python
# In test file
import os
from dotenv import load_dotenv
load_dotenv(".env.test")
```

---

## Continuous Integration

### Example GitHub Actions Workflow

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: "3.9"
      - run: pip install -e ".[dev]"
      - run: pytest tests/
```

---

## Support

If tests fail:
1. Check GROQ_API_KEY is valid
2. Verify backend is running
3. Check .env configuration
4. Review error messages in logs
5. Try manual tests first

---

**Happy Testing!** 🎉
