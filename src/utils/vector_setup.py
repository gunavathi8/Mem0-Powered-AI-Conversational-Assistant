# Improved version of vector_setup.py
# Made env-var based for production; run once to setup collection.

from qdrant_client import QdrantClient, models
import os
import logging
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "mem0_conversations")
EMBEDDING_DIMS = int(os.environ.get("MEM0_EMBEDDING_DIMS", "1536"))

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("QDRANT_URL and QDRANT_API_KEY must be set.")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

try:
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=models.VectorParams(size=EMBEDDING_DIMS, distance=models.Distance.COSINE),
    )
    logger.info(f"Collection {QDRANT_COLLECTION} created successfully.")
except Exception as e:
    logger.error(f"Error creating collection: {str(e)}")
