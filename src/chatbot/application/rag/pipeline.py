"""
RAGPipeline — manages document ingestion and retriever construction.

Responsibilities
----------------
- Accept raw documents / texts and split them into chunks.
- Embed chunks and upsert into the vector store.
- Return a configured LangChain retriever ready for the workflow.

This class is a thin orchestration layer around LangChain primitives.
It knows nothing about the chatbot domain — it just moves text into a
vector store and hands back a retriever.

Usage
-----
pipeline = RAGPipeline.from_factory(agent_factory)

# Ingest documents at startup or via an admin endpoint:
await pipeline.ingest(documents)

# Build the retriever once and pass to build_graph():
retriever = pipeline.as_retriever()
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

if TYPE_CHECKING:
    from application.agent.factory import AgentFactory

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Ingestion + retriever construction over a configured vector store."""

    def __init__(
        self,
        vector_store: Any,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        top_k: int = 4,
        score_threshold: float = 0.5,
    ) -> None:
        self._vector_store = vector_store
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self._top_k = top_k
        self._score_threshold = score_threshold

    # ------------------------------------------------------------------ #
    #  Constructor from factory                                            #
    # ------------------------------------------------------------------ #

    @classmethod
    def from_factory(cls, factory: "AgentFactory") -> "RAGPipeline":
        """Convenience constructor — reads all settings from the AgentFactory."""
        cfg = factory.config.rag
        if not cfg.enabled:
            raise RuntimeError(
                "RAGPipeline.from_factory() called but rag.enabled is False."
            )
        return cls(
            vector_store=factory.vector_store,
            chunk_size=cfg.chunk_size,
            chunk_overlap=cfg.chunk_overlap,
            top_k=cfg.top_k,
            score_threshold=cfg.score_threshold,
        )

    # ------------------------------------------------------------------ #
    #  Ingestion                                                           #
    # ------------------------------------------------------------------ #

    def ingest(self, documents: list[Document | str]) -> int:
        """
        Split and embed documents into the vector store.

        Args
        ----
        documents:
            List of LangChain Documents or raw strings.

        Returns
        -------
        Number of chunks successfully upserted.
        """
        # Normalise strings → Documents.
        docs: list[Document] = [
            Document(page_content=d) if isinstance(d, str) else d
            for d in documents
        ]

        chunks = self._splitter.split_documents(docs)
        if not chunks:
            logger.warning("ingest: no chunks produced — check document content.")
            return 0

        logger.info("ingest: upserting %d chunks into vector store.", len(chunks))
        self._vector_store.add_documents(chunks)
        return len(chunks)

    def ingest_texts(self, texts: list[str], metadatas: list[dict] | None = None) -> int:
        """Convenience wrapper for plain text ingestion."""
        docs = [
            Document(page_content=text, metadata=meta or {})
            for text, meta in zip(texts, metadatas or [{}] * len(texts))
        ]
        return self.ingest(docs)

    # ------------------------------------------------------------------ #
    #  Retriever                                                           #
    # ------------------------------------------------------------------ #

    def as_retriever(self) -> Any:
        """
        Return a configured LangChain retriever.

        The retriever is what gets injected into WorkflowNodes.
        """
        return self._vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": self._top_k,
                "score_threshold": self._score_threshold,
            },
        )