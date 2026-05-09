"""
build_graph — constructs and compiles the LangGraph StateGraph.

The graph is compiled once at startup and reused for all requests.
Thread-level state isolation is handled by LangGraph via the checkpointer
and the `thread_id` key in RunnableConfig.

Graph shape
-----------

  START
    │
    ▼
  [conversation_node]
    │
    ├─ should_retrieve == "retrieve" ──► [retrieval_node] ──► [conversation_node]
    │
    └─ should_retrieve == "respond"
         │
         ▼
       [connector]  (should_summarize)
         │
         ├─ "summarize" ──► [summarize_node] ──► END
         │
         └─ "end" ──────────────────────────► END
"""
from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, START, StateGraph

from .nodes import WorkflowNodes
from .state import ConversationState

logger = logging.getLogger(__name__)


def build_graph(llm: Any, retriever: Any | None, checkpointer: Any) -> Any:
    """
    Build and compile the conversation LangGraph.

    Args
    ----
    llm:
        Initialised LangChain chat model from AgentFactory.
    retriever:
        Optional LangChain retriever.  Pass None to disable RAG routing.
    checkpointer:
        LangGraph checkpointer (MemorySaver or AsyncMongoDBSaver).
        Provides per-thread conversation persistence.

    Returns
    -------
    A compiled LangGraph runnable.
    """
    nodes = WorkflowNodes(llm=llm, retriever=retriever)

    graph = StateGraph(ConversationState)

    # ── Register nodes ───────────────────────────────────────────────── #
    graph.add_node("conversation", nodes.conversation_node)
    graph.add_node("retrieval", nodes.retrieval_node)
    graph.add_node("summarize", nodes.summarize_node)

    # ── Entry point ───────────────────────────────────────────────────── #
    graph.add_edge(START, "conversation")

    # ── After conversation: decide whether to retrieve ────────────────── #
    graph.add_conditional_edges(
        "conversation",
        nodes.should_retrieve,
        {
            "retrieve": "retrieval",
            "respond": "__connector__",  # virtual label → handled below
        },
    )

    # After retrieval, loop back to conversation so the LLM sees the context.
    graph.add_edge("retrieval", "conversation")

    # ── After responding (no retrieval needed): decide whether to summarize #
    # LangGraph does not support virtual labels, so we use a pass-through
    # approach: add a conditional from conversation to summarize / END.
    # When should_retrieve returns "respond", we want to run should_summarize.
    # The cleanest way is to add a second conditional from conversation,
    # but LangGraph only supports one conditional edge per source node.
    #
    # Solution: use a lightweight "connector" node that just passes state through.
    graph.add_node("connector", lambda state: state)

    # Rebuild the conditional structure with connector as the intermediary.
    # (Replacing the earlier add_conditional_edges call.)
    graph.add_conditional_edges(
        "conversation",
        nodes.should_retrieve,
        {
            "retrieve": "retrieval",
            "respond": "connector",
        },
    )

    graph.add_conditional_edges(
        "connector",
        nodes.should_summarize,
        {
            "summarize": "summarize",
            "end": END,
        },
    )

    graph.add_edge("summarize", END)

    logger.info("LangGraph compiled (rag=%s).", retriever is not None)
    return graph.compile(checkpointer=checkpointer)