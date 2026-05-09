"""
WorkflowNodes — stateless node functions for the LangGraph workflow.

Each method receives the current ConversationState and returns a partial state
update (a dict with only the keys that changed).  LangGraph merges this into
the shared state via the reducers defined in ConversationState.

Node responsibilities
---------------------
conversation_node   — call the LLM; optionally inject RAG context into the prompt.
retrieval_node      — run the retriever tool; populate state["context"].
summarize_node      — compress old messages into a summary when the history is long.
connector_node      — routing logic: decide whether to summarize or end.

Design notes
------------
- Nodes are methods on a class so the LLM and retriever are injected via __init__
  rather than imported as globals.  This makes unit testing trivial — just pass
  mock objects.
- Nodes are intentionally thin.  Business logic (prompt construction, chunking)
  lives in private helpers, not inside the node body.
"""
from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import BaseMessage

from .state import ConversationState

logger = logging.getLogger(__name__)


class WorkflowNodes:
    """
    Container for all node functions used by the LangGraph graph.

    Args
    ----
    llm:
        A LangChain-compatible chat model (ChatGroq, ChatOpenAI, etc.).
    retriever:
        Optional LangChain retriever.  When None, retrieval_node is a no-op.
    """

    def __init__(self, llm: Any, retriever: Any | None = None) -> None:
        self._llm = llm
        self._retriever = retriever

    # ------------------------------------------------------------------ #
    #  Node: conversation                                                  #
    # ------------------------------------------------------------------ #

    def conversation_node(self, state: ConversationState) -> dict:
        """
        Core LLM call.

        Builds the message list:
          [SystemMessage] + optional summary message + recent messages

        The system prompt comes from agent_config — no hard-coded strings here.
        If context (RAG output) is present it is appended to the system prompt.
        """
        config = state["agent_config"]
        system_prompt = self._build_system_prompt(
            base_prompt=config.system_prompt,
            context=state.get("context", ""),
        )

        messages_to_send: list[BaseMessage] = [SystemMessage(content=system_prompt)]

        # Re-inject running summary as a synthetic assistant message so the LLM
        # is aware of what was discussed before the context window was trimmed.
        summary = state.get("summary", "")
        if summary:
            messages_to_send.append(
                AIMessage(
                    content=f"[Summary of earlier conversation]\n{summary}"
                )
            )

        # Only pass the last N messages to stay within the context window.
        max_msgs = config.memory.max_context_messages
        recent = state["messages"][-max_msgs:]
        messages_to_send.extend(recent)

        logger.debug(
            "conversation_node: sending %d messages to LLM (summary=%s, context_len=%d)",
            len(messages_to_send),
            bool(summary),
            len(state.get("context", "")),
        )

        response = self._llm.invoke(messages_to_send)
        return {"messages": [response]}

    # ------------------------------------------------------------------ #
    #  Node: retrieval                                                     #
    # ------------------------------------------------------------------ #

    def retrieval_node(self, state: ConversationState) -> dict:
        """
        Run the retriever and populate state["context"].

        Uses the last human message as the retrieval query.
        If the retriever is not configured, returns an empty context.
        """
        if self._retriever is None:
            logger.debug("retrieval_node: no retriever configured — skipping.")
            return {"context": ""}

        # Find the most recent human message to use as the query.
        query = self._last_human_message(state["messages"])
        if not query:
            logger.debug("retrieval_node: no human message found — skipping.")
            return {"context": ""}

        config = state["agent_config"]
        logger.debug("retrieval_node: querying retriever with %r", query[:80])

        try:
            docs = self._retriever.invoke(query)
            context = self._format_docs(docs)
            logger.info(
                "retrieval_node: retrieved %d docs, context_len=%d",
                len(docs),
                len(context),
            )
            return {"context": context}
        except Exception as exc:
            logger.warning("retrieval_node: retrieval failed — %s", exc)
            return {"context": ""}

    # ------------------------------------------------------------------ #
    #  Node: summarize                                                     #
    # ------------------------------------------------------------------ #

    def summarize_node(self, state: ConversationState) -> dict:
        """
        Compress conversation history into a rolling summary.

        Called when the message count exceeds memory.summarize_after_n_messages.
        Keeps the last 2 messages verbatim; the rest are summarised.

        Returns an updated summary and a trimmed messages list.
        """
        config = state["agent_config"]
        messages = state["messages"]
        existing_summary = state.get("summary", "")

        # Build prompt to ask LLM to summarise.
        if existing_summary:
            summary_prompt = (
                f"This is the summary of the conversation so far:\n{existing_summary}\n\n"
                f"Extend the summary by incorporating the following new messages. "
                f"Be concise — capture the key topics and decisions only."
            )
        else:
            summary_prompt = (
                "Summarise the following conversation. "
                "Be concise — capture the key topics and decisions only."
            )

        messages_to_summarise = [SystemMessage(content=summary_prompt)] + messages[:-2]

        logger.info(
            "summarize_node: summarising %d messages.", len(messages_to_summarise)
        )

        response = self._llm.invoke(messages_to_summarise)
        new_summary = response.content

        # Trim state to only the 2 most recent messages.
        trimmed_messages = messages[-2:]

        return {
            "summary": new_summary,
            "messages": trimmed_messages,
        }

    # ------------------------------------------------------------------ #
    #  Node: connector (routing helper — not a true node, used as edge)   #
    # ------------------------------------------------------------------ #

    def should_summarize(self, state: ConversationState) -> str:
        """
        Conditional edge function: returns 'summarize' or 'end'.

        LangGraph uses the return value to decide which node to route to next.
        """
        config = state["agent_config"]
        threshold = config.memory.summarize_after_n_messages
        msg_count = len(state["messages"])

        if msg_count > threshold:
            logger.debug(
                "should_summarize: %d messages > threshold %d → summarize",
                msg_count,
                threshold,
            )
            return "summarize"

        return "end"

    def should_retrieve(self, state: ConversationState) -> str:
        """
        Conditional edge: returns 'retrieve' or 'respond'.

        Routes to retrieval_node only when the agent has 'retriever' in its tools.
        """
        config = state["agent_config"]
        if "retriever" in config.tools and self._retriever is not None:
            return "retrieve"
        return "respond"

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _build_system_prompt(base_prompt: str, context: str) -> str:
        if not context:
            return base_prompt
        return (
            f"{base_prompt}\n\n"
            f"Use the following retrieved information to help answer the user's question. "
            f"If the information is not relevant, rely on your general knowledge.\n\n"
            f"---\n{context}\n---"
        )

    @staticmethod
    def _last_human_message(messages: list[BaseMessage]) -> str | None:
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                return str(msg.content)
        return None

    @staticmethod
    def _format_docs(docs: list) -> str:
        if not docs:
            return ""
        parts = []
        for i, doc in enumerate(docs, start=1):
            content = getattr(doc, "page_content", str(doc))
            parts.append(f"[{i}] {content.strip()}")
        return "\n\n".join(parts)