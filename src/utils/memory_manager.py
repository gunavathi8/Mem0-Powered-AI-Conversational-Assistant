# Improved version of memory_manager.py
# Enhanced with better error handling, logging, and graceful shutdown.

import os
import logging
from mem0 import Memory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "mem0_conversations")
HISTORY_DB = os.environ.get("MEM0_HISTORY_DB", "history_chatbot.db")  # Fallback, but not used here
EMBEDDING_DIMS = int(os.environ.get("MEM0_EMBEDDING_DIMS", "1536"))

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("QDRANT_URL and QDRANT_API_KEY must be set as environment variables")

MEM0_CONFIG = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "url": QDRANT_URL,
            "api_key": QDRANT_API_KEY,
            "collection_name": QDRANT_COLLECTION,
            "embedding_model_dims": EMBEDDING_DIMS,
            "on_disk": True  # Persistent mode
        }
    },
}

try:
    # Initialize mem0 Memory (connected to Qdrant Cloud)
    memory = Memory.from_config(MEM0_CONFIG)
    logger.info("Mem0 initialized successfully with Qdrant.")
except Exception as e:
    logger.error(f"Failed to initialize Mem0: {str(e)}")
    raise

def close_memory():
    """Gracefully close underlying Qdrant client if available."""
    try:
        if hasattr(memory, "vector_store") and hasattr(memory.vector_store, "client"):
            memory.vector_store.client.close()
            logger.info("Qdrant client closed successfully.")
    except Exception as e:
        logger.warning(f"Error closing Qdrant client: {str(e)}")
        # Best effort; don't raise