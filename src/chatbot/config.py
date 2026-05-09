"""Configuration management for chatbot"""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )
    
    # --- GROQ Configuration ---
    GROQ_API_KEY: str = ""
    GROQ_LLM_MODEL: str = "llama-3.3-70b-versatile"
    
    # --- OpenAI Configuration (Optional) ---
    OPENAI_API_KEY: str | None = None
    
    # --- MongoDB Configuration ---
    MONGO_URI: str = Field(
        default="mongodb://localhost:27017/",
        description="Connection URI for MongoDB.",
    )
    MONGO_DB_NAME: str = "chatbot"
    MONGO_CONVERSATIONS_COLLECTION: str = "conversations"
    MONGO_EVALUATIONS_COLLECTION: str = "evaluations"
    
    # --- Chatbot Configuration ---
    CHATBOT_DEFAULT_ID: str = "heat-pump-assistant"
    TOTAL_MESSAGES_SUMMARY_TRIGGER: int = 30
    TOTAL_MESSAGES_AFTER_SUMMARY: int = 5
    
    # --- RAG Configuration ---
    RAG_TEXT_EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    RAG_TEXT_EMBEDDING_MODEL_DIM: int = 384
    RAG_TOP_K: int = 3
    RAG_DEVICE: str = "cpu"
    RAG_CHUNK_SIZE: int = 256
    
    # --- API Configuration ---
    API_TITLE: str = "Chatbot API"
    API_VERSION: str = "2.0.0"
    API_PREFIX: str = "/api/chatbot"
    
    # --- Server Configuration ---
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000


settings = Settings()
