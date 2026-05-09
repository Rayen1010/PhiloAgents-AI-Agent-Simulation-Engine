"""Chat API endpoints"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from chatbot.application.chatbot_service import ChatbotService
from chatbot.application.conversation_orchestrator import ConversationOrchestrator
from chatbot.domain.exceptions import ChatbotNotFound

# Initialize services
chatbot_service = ChatbotService()
orchestrator = ConversationOrchestrator(chatbot_service)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str
    chatbot_id: Optional[str] = "heat-pump-assistant"
    system_id: Optional[int] = None
    user_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Chat response schema"""
    answer: str
    chatbot_id: str
    status: str = "success"


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the chatbot
    
    Args:
        request: Chat request with message and optional chatbot_id
        
    Returns:
        ChatResponse with generated answer
    """
    try:
        # Validate message
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate response
        response = await orchestrator.generate_response(
            messages=request.message,
            chatbot_id=request.chatbot_id,
            system_id=request.system_id,
            user_id=request.user_id,
        )
        
        logger.info(
            f"Chat response generated for user {request.user_id} "
            f"on system {request.system_id}"
        )
        
        return ChatResponse(
            answer=response,
            chatbot_id=request.chatbot_id,
        )
    
    except ChatbotNotFound as e:
        logger.error(f"Chatbot not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chatbots")
async def list_chatbots():
    """List all available chatbots
    
    Returns:
        List of chatbot configurations
    """
    try:
        chatbots = await chatbot_service.list_chatbots()
        return {
            "chatbots": [c.model_dump() for c in chatbots],
            "count": len(chatbots),
        }
    
    except Exception as e:
        logger.error(f"Error listing chatbots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chatbots/{chatbot_id}")
async def get_chatbot(chatbot_id: str):
    """Get chatbot configuration by ID
    
    Args:
        chatbot_id: ID of the chatbot to retrieve
        
    Returns:
        Chatbot configuration
    """
    try:
        chatbot = await chatbot_service.get_chatbot(chatbot_id)
        return chatbot.model_dump()
    
    except ChatbotNotFound as e:
        logger.error(f"Chatbot not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error getting chatbot: {e}")
        raise HTTPException(status_code=500, detail=str(e))
