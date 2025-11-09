# app.py
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from src.main_logic.workflow import graph
from config import DEFAULT_USER_ID
from src.utils.memory_manager import memory
import atexit

import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# --- Graceful shutdown ---
atexit.register(memory.close_memory if hasattr(memory, "close_memory") else lambda: None)

# --- Page config ---
st.set_page_config(page_title="AI Memory Chatbot", page_icon="robot", layout="wide")

# --- Sidebar ---
st.sidebar.title("Settings")
mem0_user_id = st.sidebar.text_input("User ID", value=DEFAULT_USER_ID, key="user_id")
show_memory = st.sidebar.checkbox("Show retrieved memories", value=True)

# --- Title ---
st.title("Conversational AI with Persistent Memory (LangGraph + Mem0 + Qdrant)")

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory_log" not in st.session_state:
    st.session_state.memory_log = []
if "greeted" not in st.session_state:
    st.session_state.greeted = False

# --- Auto-greet on first load (if memory exists) ---
if not st.session_state.greeted:
    # Search for any memory containing "name is"
    results = memory.search("name is", user_id=mem0_user_id)
    name = None
    for r in results.get("results", []):
        mem = r["memory"].lower()
        if "name is" in mem:
            # Extract name after "name is"
            try:
                name = mem.split("name is")[-1].strip().split()[0].capitalize()
                break
            except:
                continue

    if name:
        greeting = f"Hi {name}! Welcome back! How can I help you today?"
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        st.session_state.greeted = True
    else:
        st.session_state.greeted = True  # Skip next time

# --- Display chat history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- Chat input ---
if user_input := st.chat_input("Type your message..."):
    # User message
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Run LangGraph
    state = {
        "messages": [HumanMessage(content=user_input)],
        "mem0_user_id": mem0_user_id
    }
    with st.spinner("Thinking..."):
        result = graph.invoke(state)
    ai_response = result["messages"][-1].content

    # AI response
    with st.chat_message("assistant"):
        st.write(ai_response)
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # Log memory retrieval
    retrieved = memory.search(user_input, user_id=mem0_user_id)
    st.session_state.memory_log.append({
        "query": user_input,
        "results": retrieved.get("results", [])
    })

# --- Sidebar: Memory Viewer ---
if show_memory and st.session_state.memory_log:
    st.sidebar.subheader("Retrieved Memories")
    last = st.session_state.memory_log[-1]
    st.sidebar.write(f"**Query:** {last['query']}")
    if not last["results"]:
        st.sidebar.info("No relevant memory.")
    else:
        for m in last["results"][:5]:
            st.sidebar.success(f"- {m['memory']} (score={m['score']:.2f})")

st.sidebar.markdown("---")
st.sidebar.caption("Mem0 stores your info across sessions. Try closing and reopening!")

# # Improved 
# version of app.py (Streamlit app)
# # Added: Persistent chat history per user via Mem0 (optional), error handling, better UI.
# # To showcase Mem0: Display how memories influence responses.
# # For production: Use secrets for env vars, deploy with Streamlit sharing or similar.

# import streamlit as st
# from langchain_core.messages import HumanMessage
# from workflow import graph
# from config import DEFAULT_USER_ID
# from memory_manager import memory, close_memory
# import atexit
# import logging

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Register shutdown hook
# atexit.register(close_memory)

# # Streamlit page config
# st.set_page_config(
#     page_title="AI Memory Chatbot Demo",
#     page_icon="🤖",
#     layout="wide"
# )

# # --- Sidebar ---
# st.sidebar.title("🔧 Chatbot Settings")
# mem0_user_id = st.sidebar.text_input("User ID", value=DEFAULT_USER_ID, help="Unique ID for memory persistence.")
# show_memory = st.sidebar.checkbox("Show retrieved memories", value=True)

# # --- Title ---
# st.title("🤖 Conversational AI with Memory (LangGraph + Mem0 + Qdrant)")

# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []
#     # Optional: Load previous chat history from Mem0 if desired
#     # For demo, we start fresh per session; in prod, query Mem0 for past conversations.

# if "memory_log" not in st.session_state:
#     st.session_state.memory_log = []

# # --- Display conversation history ---
# for msg in st.session_state.messages:
#     if msg["role"] == "user":
#         st.chat_message("user").write(msg["content"])
#     else:
#         st.chat_message("assistant").write(msg["content"])

# # --- Chat input ---
# if user_input := st.chat_input("Type your message..."):
#     try:
#         # Display user message
#         st.chat_message("user").write(user_input)
#         st.session_state.messages.append({"role": "user", "content": user_input})

#         # Run conversation with LangGraph
#         state = {
#             "messages": [HumanMessage(content=user_input)],
#             "mem0_user_id": mem0_user_id
#         }
#         result = graph.invoke(state)
#         ai_response = result["messages"][-1].content

#         # Display AI response
#         st.chat_message("assistant").write(ai_response)
#         st.session_state.messages.append({"role": "assistant", "content": ai_response})

#         # For memory log: Reuse from chatbot or search again (optimized: could pass from graph)
#         retrieved = memory.search(user_input, user_id=mem0_user_id)
#         st.session_state.memory_log.append({
#             "query": user_input,
#             "results": retrieved.get("results", [])
#         })
#         logger.info(f"Processed query for user {mem0_user_id}: {user_input}")

#     except Exception as e:
#         st.error(f"Error processing your message: {str(e)}")
#         logger.error(f"Error in chat processing: {str(e)}")

# # --- Sidebar memory viewer ---
# if show_memory:
#     st.sidebar.subheader("📚 Retrieved Memories")
#     if st.session_state.memory_log:
#         last_mem = st.session_state.memory_log[-1]
#         st.sidebar.write(f"**Query:** {last_mem['query']}")
#         if not last_mem["results"]:
#             st.sidebar.info("No relevant memory found.")
#         else:
#             for m in last_mem["results"][:5]:
#                 st.sidebar.success(f"- {m['memory']} (score={m['score']:.2f})")
#     st.sidebar.markdown("---")
#     st.sidebar.info("Mem0 showcases persistent memory: Try mentioning facts about yourself and ask later!")