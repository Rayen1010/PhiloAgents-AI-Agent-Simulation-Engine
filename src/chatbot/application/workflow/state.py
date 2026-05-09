"""
ConversationState — the typed state dict that flows through the LangGraph workflow.

Design principles
-----------------
- All fields are agent-agnostic.
- No philosopher-specific fields (perspective, style) — those belonged to the domain.
- agent_config is passed in once and threaded through; nodes read from it but
  never mutate it.
- `context` holds retrieved documents (RAG output) as plain text so any node
  can use it without knowing which retriever produced it.
- `metadata` is a flexible escape hatch for future fields without breaking the state schema.
"""
from __future__ import annotations

from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from application.agent.config import AgentConfig


class ConversationState(TypedDict):
    """
    Shared state for all nodes in the LangGraph workflow.

    Fields
    ------
    messages:
        Full conversation history, managed by LangGraph's add_messages reducer.
        New messages are appended; the list is never replaced wholesale.
    agent_config:
        The loaded AgentConfig.  Injected once by the orchestrator at graph
        invocation; read-only for all nodes.
    context:
        Retrieved document snippets concatenated as a single string.
        Empty string when RAG is disabled or no results were found.
    summary:
        Running summary of older messages, produced by summarize_node.
        Replaces older messages in the context window once the threshold is hit.
    metadata:
        Arbitrary key-value pairs — session id, user id, request id, etc.
        Kept here so nodes can log / trace without coupling to HTTP concerns.
    """

    messages: Annotated[list[BaseMessage], add_messages]
    agent_config: AgentConfig
    context: str
    summary: str
    metadata: dict[str, Any]