"""
tools — LangChain tools available to the chatbot agent.

Currently exposes a single retriever tool that searches the HVAC /
refrigeration knowledge base.  Additional tools (e.g. energy analytics
calculators, maintenance schedulers) can be appended to the `tools` list
as the agent grows.

The retriever is instantiated here at module load time so the tool is
ready before the LangGraph graph is compiled.  Settings are read from
the central config to keep this file free of hardcoded values.
"""
from __future__ import annotations

from langchain.tools import create_retriever_tool

from rag.retrievers import get_retriever
from config import Settings

# ------------------------------------------------------------------ #
#  Retriever                                                           #
# ------------------------------------------------------------------ #

retriever = get_retriever(
    embedding_model_id=Settings.RAG_TEXT_EMBEDDING_MODEL_ID,
    k=Settings.RAG_TOP_K,
    device=Settings.RAG_DEVICE,
)

# ------------------------------------------------------------------ #
#  Tools                                                               #
# ------------------------------------------------------------------ #

retriever_tool = create_retriever_tool(
    retriever,
    name="retrieve_hvac_context",
    description=(
        "Search the HVAC and refrigeration knowledge base for relevant information. "
        "Use this tool whenever the user asks about HVAC systems, CO2 refrigeration, "
        "energy analytics, maintenance procedures, troubleshooting, or company services."
    ),
)

tools = [retriever_tool]