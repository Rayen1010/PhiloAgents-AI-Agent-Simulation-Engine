"""Chatbot configuration model"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List
from datetime import datetime


class Chatbot(BaseModel):
    """Generic chatbot configuration"""
    
    id: str = Field(..., description="Unique chatbot identifier")
    name: str = Field(..., description="Human-readable chatbot name")
    description: str = Field(..., description="Chatbot description")
    system_prompt: str = Field(..., description="System prompt for the chatbot")
    
    # Configuration
    tools: List[str] = Field(
        default_factory=list,
        description="List of tool names available to chatbot"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Chatbot-specific configuration"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    # State
    enabled: bool = Field(default=True, description="Whether chatbot is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "heat-pump-assistant",
                "name": "Heat Pump Assistant",
                "description": "Assistant for heat pump system inquiries",
                "system_prompt": "You are a helpful assistant for heat pump systems...",
                "tools": ["retriever"],
                "config": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
            }
        }
