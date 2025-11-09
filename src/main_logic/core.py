# Improved version of chatbot.py
# Enhanced: Better filtering, error handling in memory ops.
# System prompt refined to showcase Mem0 by encouraging use of recalled facts.
# Removed duplicated/commented code.
# To showcase Mem0: In prompt, instruct to weave in relevant memories naturally.

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages
from config import llm
from src.utils.memory_manager import memory
from src.utils.memory_logger import log_memory
import logging

logger = logging.getLogger(__name__)

class State(TypedDict):
    """State for our chatbot - holds the conversation history and user ID"""
    messages: Annotated[list[BaseMessage], add_messages]
    mem0_user_id: str

def chatbot(state: State):
    messages = state["messages"]
    user_id = state["mem0_user_id"]
    user_query = messages[-1].content

    try:
        # Retrieve memories relevant to latest user message
        memories = memory.search(user_query, user_id=user_id)
        logger.debug(f"Full Memory for user {user_id}: {memories}")

        # --- Filter memories for token optimization ---
        MAX_RESULTS = 5  # Increased slightly for better recall
        SCORE_THRESHOLD = 0.18  # Adjusted for better balance

        filtered_memories = sorted(
            [m for m in memories.get("results", []) if m.get("score", 0) >= SCORE_THRESHOLD],
            key=lambda x: x["score"],
            reverse=True
        )[:MAX_RESULTS]

        logger.debug(f"Filtered Memories: {filtered_memories}")

        # Build context from filtered memories
        if not filtered_memories:
            context = "None"
        else:
            context = "\n".join(f"- {m['memory']} (from {m.get('created_at', 'unknown')})" for m in filtered_memories)
            logger.debug(f"Context: {context}")

        # Add system prompt - Refined to showcase Mem0's value: Recall and use personal facts.
        system_message = SystemMessage(
            content=f"""
You are a helpful, friendly assistant in a conversational AI system powered by Mem0 for long-term memory.

Instructions:
- Prioritize the user's current query.
- Use the "Relevant information" below ONLY if it directly enhances your response (e.g., recalling user preferences or past facts).
- Weave in relevant memories naturally to personalize the conversation, showcasing Mem0's ability to remember details over time.
- If context is unrelated, ignore it and respond based on general knowledge.
- Do not invent details; if unsure, ask for clarification.
- Keep responses concise, engaging, and helpful.

Relevant information:
{context}
"""
        )

        # Full conversation context
        full_message = [system_message] + messages

        # Get response from LLM
        response = llm.invoke(full_message)

        # --- Store memory with error handling ---
        try:
            # Store user message as a fact
            memory.add([{"role": "user", "content": user_query}], user_id=user_id)
            log_memory(user_id, [{"role": "user", "content": user_query}])   # LOG
            # Store the full conversation pair for context
            memory.add(
                [{"role": "user", "content": user_query}, {"role": "assistant", "content": response.content}],
                user_id=user_id
            )
            log_memory(user_id, [
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": response.content}
            ])
            logger.info(f"Memories stored for user {user_id}.")
        except Exception as e:
            logger.error(f"Error storing memory for user {user_id}: {str(e)}")

        return {"messages": [response]}

    except Exception as e:
        logger.error(f"Error in chatbot node: {str(e)}")
        error_response = SystemMessage(content="Sorry, I encountered an error. Please try again.")
        return {"messages": [error_response]}