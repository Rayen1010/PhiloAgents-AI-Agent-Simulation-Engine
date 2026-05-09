from typing_extensions import Literal

from langgraph.graph import END

from workflow.state import ConversationState
from config import Settings


def should_summarize_conversation(
    state: ConversationState,
) -> Literal["summarize_conversation_node", "__end__"]:
    messages = state["messages"]

    if len(messages) > Settings.TOTAL_MESSAGES_SUMMARY_TRIGGER:
        return "summarize_conversation_node"

    return END
