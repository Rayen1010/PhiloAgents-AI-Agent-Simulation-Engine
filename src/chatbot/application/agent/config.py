"""
AgentConfig — the single source of truth for how the chatbot agent behaves.

Loaded once at startup; all workflow nodes receive a reference to this object
instead of hard-coded values.  Keeping configuration here (rather than scattered
across nodes) makes it trivial to change model, prompt, or tool list without
touching orchestration logic.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class LLMConfig(BaseModel):
    """LLM provider settings."""

    provider: str = Field(
        default="groq",
        description="LLM provider identifier: 'groq' | 'openai' | 'anthropic' | 'ollama'",
    )
    model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Model name as accepted by the provider SDK.",
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, gt=0)
    streaming: bool = Field(
        default=True,
        description="Whether to use streaming responses in the API layer.",
    )


class RAGConfig(BaseModel):
    """Retrieval-Augmented Generation settings."""

    enabled: bool = True
    embedding_provider: str = Field(
        default="huggingface",
        description="'huggingface' | 'openai'",
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
    )
    vector_store: str = Field(
        default="qdrant",
        description="'qdrant' | 'mongodb' | 'faiss' | 'chroma'",
    )
    collection_name: str = "chatbot_kb"
    top_k: int = Field(default=4, ge=1, le=20)
    score_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    chunk_size: int = Field(default=512, gt=0)
    chunk_overlap: int = Field(default=64, ge=0)


class MemoryConfig(BaseModel):
    """Conversation memory / checkpointing settings."""

    backend: str = Field(
        default="mongodb",
        description="Where to persist LangGraph checkpoints: 'mongodb' | 'memory'",
    )
    summarize_after_n_messages: int = Field(
        default=30,
        ge=2,
        description="Trigger conversation summarization when this many messages accumulate.",
    )
    max_context_messages: int = Field(
        default=10,
        ge=1,
        description="How many recent messages to pass to the LLM on each turn.",
    )


class EvaluationConfig(BaseModel):
    """Evaluation / tracing settings."""

    enabled: bool = False
    backend: str = Field(
        default="opik",
        description="'opik' | 'none'",
    )
    project_name: str = "chatbot-eval"
    dataset_name: str = "chatbot-dataset"


class AgentConfig(BaseModel):
    """
    Top-level configuration for the single chatbot agent.

    This replaces the philosopher-specific Philosopher model.
    Everything the workflow needs to know about the agent lives here.
    """

    id: str = Field(default="chatbot", description="Unique agent identifier.")
    name: str = Field(default="Chatbot", description="Human-readable agent name.")
    description: str = Field(default="A helpful conversational assistant.")
    system_prompt: str = Field(
        default=(
            "You are a helpful, knowledgeable assistant. "
            "Answer questions clearly and concisely. "
            "If you are unsure about something, say so honestly."
        )
    )
    tools: list[str] = Field(
        default_factory=lambda: ["retriever"],
        description="Tool names that this agent is allowed to use.",
    )
    llm: LLMConfig = Field(default_factory=LLMConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary extra config for future extensibility.",
    )

    @model_validator(mode="after")
    def validate_tools_vs_rag(self) -> "AgentConfig":
        """Warn if retriever tool is listed but RAG is disabled."""
        if "retriever" in self.tools and not self.rag.enabled:
            raise ValueError(
                "Tool 'retriever' is listed but rag.enabled is False. "
                "Either enable RAG or remove 'retriever' from tools."
            )
        return self