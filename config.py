# Improved version of config.py
# Added: Separate config for in-memory, load env properly.

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)  # Updated to gpt-4o-mini for cost-efficiency

# Mem0 Configuration - SQLite for local/in-memory
MEM0_CONFIG_INMEMORY = {
    "history_db_path": "history_chatbot.db"
}

DEFAULT_USER_ID = "Guna"