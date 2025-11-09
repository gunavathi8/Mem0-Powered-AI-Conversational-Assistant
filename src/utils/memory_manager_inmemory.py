# Improved version of memory_manager_inmemory.py
# We consolidate to use Qdrant primarily, but keep this as optional for local dev.
# For production, recommend Qdrant or similar persistent store.

from mem0 import Memory
from config import MEM0_CONFIG_INMEMORY as MEM0_CONFIG  # Renamed in config.py for clarity

# Initialize Mem0 with SQLite for in-memory/local testing
memory = Memory.from_config(MEM0_CONFIG)