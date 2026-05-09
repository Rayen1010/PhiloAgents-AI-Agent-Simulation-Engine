"""
application/conversation_service/generate_response.py

Single public entry point for running the HVAC assistant agent.

Bridges the outside world (API layer, evaluation pipeline) and the
LangGraph workflow (graph.py / nodes.py).

No infrastructure is owned here — all construction is delegated:
    LLM + checkpointer  →  application/agent/factory.py  (AgentFactory)
    Retriever           →  application/rag/retrievers.py  (MongoDB Atlas hybrid search)
    Graph               →  application/workflow/graph.py  (build_graph)
    System prompt       →  domain/prompt.py               (HEAT_PUMP_ASSISTANT_PROMPT)

Call flow
---------
  get_response()
    ├── _render_system_prompt()          → fills HEAT_PUMP_ASSISTANT_PROMPT template
    ├── _build_agent_config()            → builds AgentConfig from HVACAssistant fields
    ├── AgentFactory.from_config()       → initialises LLM + checkpointer
    ├── _build_retriever()               → MongoDB Atlas hybrid retriever
    ├── build_graph()                    → compiles LangGraph StateGraph
    └── graph.ainvoke()                  → runs the workflow, returns final state
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from application.agent.config import (
    AgentConfig,
    EvaluationConfig,
    LLMConfig,
    MemoryConfig,
    RAGConfig,
)
from application.agent.factory import AgentFactory
from application.rag.retrievers import get_retriever
from application.workflow.graph import build_graph
from application.workflow.state import ConversationState
from config import settings
from domain.prompts import HEAT_PUMP_ASSISTANT_PROMPT

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# System prompt rendering
# ---------------------------------------------------------------------------

def _render_system_prompt(
    assistant_name: str,
    assistant_context: str = "",
    company_name: str = "Tabreed Thermal Control",
    company_description: str = "",
    company_services: str = "",
    client_name: str = "",
    client_company: str = "",
    client_location: str = "",
    installed_systems: str = "",
    dashboard_data: str = "",
    summary: str = "",
) -> str:
    """Render the versioned ``HEAT_PUMP_ASSISTANT_PROMPT`` template.

    Replaces all ``{{variable}}`` placeholders in the Opik-versioned prompt
    with runtime values.  Any variable not supplied defaults to a safe
    "not available" string so the LLM never sees a raw ``{{placeholder}}``.

    The ``HEAT_PUMP_ASSISTANT_PROMPT`` object (``domain/prompt.py``) fetches
    the latest prompt version from Opik if available, falling back to the
    local string — so prompt changes are tracked without code deploys.

    Args:
        assistant_name:      Display name injected for personalisation.
        assistant_context:   Pre-fetched context block (dashboard snapshot,
                             client JSON). Overrides individual fields when
                             provided as a single pre-formatted string.
        company_name:        Tabreed company name.
        company_description: Company description for context.
        company_services:    Services offered by Tabreed.
        client_name:         Name of the client/facility manager.
        client_company:      Client's company name.
        client_location:     Physical site location.
        installed_systems:   Description of installed HVAC/heat pump equipment.
        dashboard_data:      Current dashboard metrics (COP, temperatures, etc.).
        summary:             Running conversation summary for memory continuity.

    Returns:
        str: The fully rendered system prompt ready to pass to the LLM.
    """
    # If a single pre-formatted context block is provided, use it as
    # dashboard_data so callers don't need to decompose it.
    if assistant_context and not dashboard_data:
        dashboard_data = assistant_context

    raw_prompt: str = HEAT_PUMP_ASSISTANT_PROMPT.prompt

    replacements = {
        "{{company_name}}": company_name or "Tabreed Thermal Control",
        "{{company_description}}": company_description or "Not available.",
        "{{company_services}}": company_services or "Not available.",
        "{{client_name}}": client_name or "Not available.",
        "{{client_company}}": client_company or "Not available.",
        "{{client_location}}": client_location or "Not available.",
        "{{installed_systems}}": installed_systems or "Not available.",
        "{{dashboard_data}}": dashboard_data or "No dashboard data available.",
        "{{summary}}": summary or "No previous conversation summary.",
    }

    rendered = raw_prompt
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)

    return rendered


# ---------------------------------------------------------------------------
# RAG retriever
# ---------------------------------------------------------------------------

def _build_retriever(agent_config: AgentConfig) -> Any | None:
    """Build the MongoDB Atlas hybrid search retriever if RAG is enabled.

    Delegates entirely to ``application.rag.retrievers.get_retriever``,
    which sets up the HuggingFace embedding model and MongoDB Atlas hybrid
    search index — matching the rest of the RAG stack exactly.

    Returns ``None`` when RAG is disabled, ``"retriever"`` is not in tools,
    or initialisation fails (agent falls back gracefully to no RAG).

    Args:
        agent_config: Fully populated ``AgentConfig``.

    Returns:
        ``MongoDBAtlasHybridSearchRetriever`` instance, or ``None``.
    """
    if not agent_config.rag.enabled or "retriever" not in agent_config.tools:
        logger.debug("RAG disabled or 'retriever' not in tools — skipping.")
        return None

    try:
        retriever = get_retriever(
            embedding_model_id=settings.RAG_TEXT_EMBEDDING_MODEL_ID,
            k=settings.RAG_TOP_K,
            device=settings.RAG_DEVICE,
        )
        logger.info(
            "Hybrid retriever initialised | model=%s | top_k=%d",
            settings.RAG_TEXT_EMBEDDING_MODEL_ID,
            settings.RAG_TOP_K,
        )
        return retriever
    except Exception as exc:
        logger.warning("Retriever init failed — running without RAG. Error: %s", exc)
        return None


# ---------------------------------------------------------------------------
# AgentConfig builder
# ---------------------------------------------------------------------------

def _build_agent_config(
    assistant_id: str,
    assistant_name: str,
    assistant_expertise: str,
    assistant_tone: str,
    rendered_system_prompt: str,
) -> AgentConfig:
    """Build an ``AgentConfig`` from ``HVACAssistant`` identity fields.

    Receives the already-rendered system prompt so this function stays
    focused on config assembly without any prompt logic.

    Args:
        assistant_id:          ``HVACAssistant.id``
        assistant_name:        ``HVACAssistant.name``
        assistant_expertise:   ``HVACAssistant.expertise``
        assistant_tone:        ``HVACAssistant.tone``
        rendered_system_prompt: Output of ``_render_system_prompt()``.

    Returns:
        ``AgentConfig`` ready to inject into ``ConversationState``.
    """
    return AgentConfig(
        id=assistant_id,
        name=assistant_name,
        description=f"HVAC assistant specialising in {assistant_expertise}.",
        system_prompt=rendered_system_prompt,
        tools=["retriever"],
        llm=LLMConfig(
            provider="groq",
            model=settings.GROQ_LLM_MODEL,
            temperature=0.3,    # Low temp → factual, deterministic HVAC answers
            max_tokens=1024,
            streaming=False,    # Disabled for evaluation; API layer may override
        ),
        rag=RAGConfig(
            enabled=True,
            embedding_provider="huggingface",
            embedding_model=settings.RAG_TEXT_EMBEDDING_MODEL_ID,
            vector_store="mongodb",
            collection_name=settings.MONGO_CONVERSATIONS_COLLECTION,
            top_k=settings.RAG_TOP_K,
        ),
        memory=MemoryConfig(
            backend="memory",   # In-memory for evaluation; override to "mongodb" in prod
            summarize_after_n_messages=settings.TOTAL_MESSAGES_SUMMARY_TRIGGER,
            max_context_messages=settings.TOTAL_MESSAGES_AFTER_SUMMARY,
        ),
        evaluation=EvaluationConfig(enabled=False),
    )


# ---------------------------------------------------------------------------
# Message helpers
# ---------------------------------------------------------------------------

def _to_langchain_messages(messages: list[dict]) -> list[BaseMessage]:
    """Convert role/content dicts to LangChain message objects.

    Idempotent — passes through ``BaseMessage`` instances unchanged.

    Args:
        messages: ``{"role": ..., "content": ...}`` dicts or ``BaseMessage`` objects.

    Returns:
        List of ``HumanMessage`` / ``AIMessage`` objects.
    """
    result: list[BaseMessage] = []
    for msg in messages:
        if isinstance(msg, BaseMessage):
            result.append(msg)
            continue
        role = msg.get("role", "user")
        content = msg.get("content", "")
        result.append(
            HumanMessage(content=content)
            if role == "user"
            else AIMessage(content=content)
        )
    return result


def _extract_last_response(state: ConversationState) -> str:
    """Extract the last AI message content from the final workflow state.

    Args:
        state: Final ``ConversationState`` after graph invocation.

    Returns:
        Assistant response text, or empty string if none found.
    """
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, AIMessage):
            return str(msg.content)
    return ""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def get_response(
    messages: list[dict],
    assistant_id: str,
    assistant_name: str,
    assistant_expertise: str,
    assistant_tone: str,
    assistant_context: str = "",
    new_thread: bool = False,
    thread_id: str | None = None,
    # Optional rich context fields for full prompt rendering
    company_name: str = "Tabreed Thermal Control",
    company_description: str = "",
    company_services: str = "",
    client_name: str = "",
    client_company: str = "",
    client_location: str = "",
    installed_systems: str = "",
    dashboard_data: str = "",
    summary: str = "",
) -> tuple[str, ConversationState]:
    """Run the HVAC assistant LangGraph on a single conversation turn.

    Single public function consumed by:
    - ``application/evaluation/evaluate.py``  — evaluation pipeline
    - FastAPI / Streamlit API layer            — real-time conversations

    The system prompt is rendered from the Opik-versioned
    ``HEAT_PUMP_ASSISTANT_PROMPT`` (``domain/prompt.py``) with all
    template variables filled in.  Callers can pass individual context
    fields (``dashboard_data``, ``client_name``, etc.) for full rendering,
    or pass a single ``assistant_context`` string which is used as
    ``dashboard_data`` when the individual fields are not provided.

    Args:
        messages (list[dict]):
            Conversation history as ``{"role": ..., "content": ...}`` dicts.
        assistant_id (str):        ``HVACAssistant.id``
        assistant_name (str):      ``HVACAssistant.name``
        assistant_expertise (str): ``HVACAssistant.expertise``
        assistant_tone (str):      ``HVACAssistant.tone``
        assistant_context (str):   Pre-fetched context blob. Used as
                                   ``dashboard_data`` if that arg is empty.
        new_thread (bool):         Generate a fresh thread ID for isolation
                                   (always True in evaluation pipeline).
        thread_id (str | None):    Explicit thread ID (ignored if new_thread).
        company_name (str):        Tabreed company name for prompt rendering.
        company_description (str): Company description for prompt rendering.
        company_services (str):    Company services for prompt rendering.
        client_name (str):         Client name for prompt rendering.
        client_company (str):      Client company for prompt rendering.
        client_location (str):     Client location for prompt rendering.
        installed_systems (str):   Installed equipment for prompt rendering.
        dashboard_data (str):      Live dashboard metrics for prompt rendering.
        summary (str):             Conversation summary for memory continuity.

    Returns:
        tuple[str, ConversationState]:
            - Assistant response text (last AI message content).
            - Final ``ConversationState`` for context extraction and evaluation.
    """
    # --- Render the versioned system prompt ---
    rendered_prompt = _render_system_prompt(
        assistant_name=assistant_name,
        assistant_context=assistant_context,
        company_name=company_name,
        company_description=company_description,
        company_services=company_services,
        client_name=client_name,
        client_company=client_company,
        client_location=client_location,
        installed_systems=installed_systems,
        dashboard_data=dashboard_data,
        summary=summary,
    )

    # --- Build AgentConfig ---
    agent_config = _build_agent_config(
        assistant_id=assistant_id,
        assistant_name=assistant_name,
        assistant_expertise=assistant_expertise,
        assistant_tone=assistant_tone,
        rendered_system_prompt=rendered_prompt,
    )

    # --- Initialise infrastructure via AgentFactory ---
    factory = AgentFactory.from_config(agent_config)
    llm = factory.llm
    checkpointer = factory.checkpointer

    # --- Build retriever from the actual RAG stack ---
    retriever = _build_retriever(agent_config)

    # --- Compile LangGraph workflow ---
    graph = build_graph(llm=llm, retriever=retriever, checkpointer=checkpointer)

    # --- Resolve thread ID ---
    effective_thread_id = (
        str(uuid.uuid4()) if new_thread else (thread_id or assistant_id)
    )

    # --- Build initial ConversationState ---
    lc_messages = _to_langchain_messages(messages)
    initial_state: ConversationState = {
        "messages": lc_messages,
        "agent_config": agent_config,
        "context": "",
        "summary": summary,   # Seed the graph with any existing summary
        "metadata": {
            "assistant_id": assistant_id,
            "thread_id": effective_thread_id,
        },
    }

    langgraph_config = {"configurable": {"thread_id": effective_thread_id}}

    logger.info(
        "get_response | assistant='%s' | thread='%s' | messages=%d | rag=%s | new_thread=%s",
        assistant_id,
        effective_thread_id,
        len(lc_messages),
        "on" if retriever else "off",
        new_thread,
    )

    # --- Invoke graph ---
    final_state: ConversationState = await graph.ainvoke(
        initial_state, config=langgraph_config
    )

    # --- Extract response ---
    response = _extract_last_response(final_state)

    if not response:
        logger.warning(
            "get_response: no AI message in final state for thread '%s'.",
            effective_thread_id,
        )

    logger.info(
        "get_response done | response_len=%d | context_len=%d",
        len(response),
        len(final_state.get("context", "")),
    )

    return response, final_state