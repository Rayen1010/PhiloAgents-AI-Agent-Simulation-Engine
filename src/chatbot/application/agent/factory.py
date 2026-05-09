"""
AgentFactory — owns the lifecycle of the single chatbot agent.

Responsibilities
----------------
- Holds the AgentConfig singleton (loaded once at startup).
- Constructs the LLM client, embeddings, and vector store based on config.
- Exposes these as typed properties so the orchestrator and nodes never
  import infrastructure directly — they always go through the factory.

Why a factory and not a DI container?
--------------------------------------
This project is a single-agent system; a full DI framework would be
overkill.  The factory pattern gives us lazy initialization, easy mocking
in tests (just swap the factory), and a single place to swap providers.
"""
from __future__ import annotations

import logging
from functools import cached_property
from typing import Any

from .config import AgentConfig
from .loader import AgentLoader

logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Initializes and owns all agent-level resources.

    Usage (at app startup)
    ----------------------
    factory = AgentFactory.from_config_path("config/agent.yaml")

    # Inside orchestrator / nodes:
    llm     = factory.llm
    embeddings = factory.embeddings
    vector_store = factory.vector_store
    config  = factory.config
    """

    def __init__(self, config: AgentConfig) -> None:
        self._config = config

    # ------------------------------------------------------------------ #
    #  Constructors                                                        #
    # ------------------------------------------------------------------ #

    @classmethod
    def from_config_path(
        cls,
        config_path: str | None = None,
        overrides: dict[str, Any] | None = None,
    ) -> "AgentFactory":
        config = AgentLoader.load(config_path=config_path, overrides=overrides)
        return cls(config)

    @classmethod
    def from_config(cls, config: AgentConfig) -> "AgentFactory":
        return cls(config)

    # ------------------------------------------------------------------ #
    #  Config access                                                       #
    # ------------------------------------------------------------------ #

    @property
    def config(self) -> AgentConfig:
        return self._config

    # ------------------------------------------------------------------ #
    #  LLM                                                                 #
    # ------------------------------------------------------------------ #

    @cached_property
    def llm(self) -> Any:
        """
        Returns a LangChain-compatible chat model for the configured provider.

        cached_property means the client is created once and reused.
        """
        cfg = self._config.llm
        logger.info("Initializing LLM: %s / %s", cfg.provider, cfg.model)

        if cfg.provider == "groq":
            from langchain_groq import ChatGroq

            return ChatGroq(
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                streaming=cfg.streaming,
            )

        if cfg.provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                streaming=cfg.streaming,
            )

        if cfg.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )

        if cfg.provider == "ollama":
            from langchain_ollama import ChatOllama

            return ChatOllama(
                model=cfg.model,
                temperature=cfg.temperature,
            )

        raise ValueError(
            f"Unknown LLM provider: '{cfg.provider}'. "
            "Supported: groq, openai, anthropic, ollama"
        )

    # ------------------------------------------------------------------ #
    #  Embeddings                                                          #
    # ------------------------------------------------------------------ #

    @cached_property
    def embeddings(self) -> Any:
        """Returns a LangChain Embeddings instance for the configured provider."""
        if not self._config.rag.enabled:
            return None

        cfg = self._config.rag
        logger.info(
            "Initializing embeddings: %s / %s",
            cfg.embedding_provider,
            cfg.embedding_model,
        )

        if cfg.embedding_provider == "huggingface":
            from langchain_huggingface import HuggingFaceEmbeddings

            return HuggingFaceEmbeddings(model_name=cfg.embedding_model)

        if cfg.embedding_provider == "openai":
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(model=cfg.embedding_model)

        raise ValueError(
            f"Unknown embedding provider: '{cfg.embedding_provider}'. "
            "Supported: huggingface, openai"
        )

    # ------------------------------------------------------------------ #
    #  Vector store                                                        #
    # ------------------------------------------------------------------ #

    @cached_property
    def vector_store(self) -> Any:
        """Returns a LangChain VectorStore instance for the configured backend."""
        if not self._config.rag.enabled:
            return None

        cfg = self._config.rag
        embeddings = self.embeddings
        logger.info("Initializing vector store: %s", cfg.vector_store)

        if cfg.vector_store == "qdrant":
            import os
            from langchain_qdrant import QdrantVectorStore
            from qdrant_client import QdrantClient

            client = QdrantClient(
                url=os.getenv("QDRANT_URL", "http://localhost:6333"),
                api_key=os.getenv("QDRANT_API_KEY"),
            )
            return QdrantVectorStore(
                client=client,
                collection_name=cfg.collection_name,
                embedding=embeddings,
            )

        if cfg.vector_store == "mongodb":
            import os
            from langchain_mongodb import MongoDBAtlasVectorSearch
            from pymongo import MongoClient

            client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
            db = client[os.getenv("MONGODB_DB", "chatbot")]
            collection = db[cfg.collection_name]
            return MongoDBAtlasVectorSearch(
                collection=collection,
                embedding=embeddings,
                index_name="vector_index",
            )

        if cfg.vector_store == "faiss":
            # FAISS is in-memory; requires a pre-built index or returns empty store
            try:
                from langchain_community.vectorstores import FAISS

                return FAISS.from_texts(["init"], embeddings)
            except Exception:
                logger.warning("FAISS init failed — returning None vector store.")
                return None

        if cfg.vector_store == "chroma":
            import os
            from langchain_chroma import Chroma

            return Chroma(
                collection_name=cfg.collection_name,
                embedding_function=embeddings,
                persist_directory=os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"),
            )

        raise ValueError(
            f"Unknown vector store: '{cfg.vector_store}'. "
            "Supported: qdrant, mongodb, faiss, chroma"
        )

    # ------------------------------------------------------------------ #
    #  Checkpointer (LangGraph memory backend)                            #
    # ------------------------------------------------------------------ #

    @cached_property
    def checkpointer(self) -> Any:
        """
        Returns a LangGraph checkpointer for conversation state persistence.
        Used by the LangGraph workflow to save/restore thread state.
        """
        backend = self._config.memory.backend
        logger.info("Initializing checkpointer: %s", backend)

        if backend == "mongodb":
            import os
            from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver

            # Caller must await .setup() before using — see orchestrator.
            return AsyncMongoDBSaver.from_conn_string(
                os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
                db_name=os.getenv("MONGODB_DB", "chatbot"),
            )

        if backend == "memory":
            from langgraph.checkpoint.memory import MemorySaver

            return MemorySaver()

        raise ValueError(
            f"Unknown memory backend: '{backend}'. Supported: mongodb, memory"
        )

    # ------------------------------------------------------------------ #
    #  Diagnostics                                                         #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return (
            f"AgentFactory("
            f"id={self._config.id!r}, "
            f"llm={self._config.llm.provider}/{self._config.llm.model}, "
            f"rag={'on' if self._config.rag.enabled else 'off'}, "
            f"memory={self._config.memory.backend}"
            f")"
        )