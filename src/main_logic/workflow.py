# Improved version of workflow.py
# Added: Error handling in run_conversation.

from langgraph.graph import StateGraph, START, END
from src.main_logic.core import State, chatbot
import logging

logger = logging.getLogger(__name__)

# Build LangGraph workflow
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

def run_conversation(user_input: str, mem0_user_id: str):
    """Runs a single conversation turn with error handling."""
    from langchain_core.messages import HumanMessage
    try:
        state = {"messages": [HumanMessage(content=user_input)], "mem0_user_id": mem0_user_id}
        result = graph.invoke(state)
        ai_response = result["messages"][-1].content
        logger.info(f"Assistant response: {ai_response}")
        return ai_response
    except Exception as e:
        logger.error(f"Error in run_conversation: {str(e)}")
        raise