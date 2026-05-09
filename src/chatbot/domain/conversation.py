"""Conversation models and state management"""

from langgraph.graph import MessagesState
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel


class Message(BaseModel):
    """A message in a conversation"""
    
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ConversationState(MessagesState):
    """Generic conversation state for LangGraph
    
    Extends LangGraph's MessagesState with chatbot-specific fields
    """
    
    chatbot_id: str
    system_prompt: str = ""
    context: str = ""  # Retrieved context from RAG
    summary: str = ""  # Conversation summary
    metadata: Dict[str, Any] = {}  # Flexible extension point
    
    started_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None


def state_to_dict(state: ConversationState) -> Dict[str, Any]:
    """Convert state to dictionary for serialization"""
    
    conversation = ""
    if state.get("summary"):
        conversation = state["summary"]
    elif state.get("messages"):
        conversation = str(state["messages"])
    
    return {
        "chatbot_id": state.get("chatbot_id", ""),
        "context": state.get("context", ""),
        "conversation": conversation,
        "metadata": state.get("metadata", {}),
    }
