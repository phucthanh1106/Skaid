import os
import requests
from app import config

# app.config loads the existing backend .env file.
OLLAMA_URL = os.environ["OLLAMA_URL"].rstrip("/")
QDRANT_URL = os.environ["QDRANT_URL"].rstrip("/")
QDRANT_API_KEY = os.environ["QDRANT_API_KEY"]
COLLECTION = "qwen3_embedding_06b_pages"
EMBEDDING_MODEL = "qwen3-embedding:0.6b"


# Embed a question and retrieve the three closest slides.
def retrieve_pages(question):
    embedding_request = {
        "model": EMBEDDING_MODEL,
        "input": question,
        "truncate": False,
        "keep_alive": "10m"
    }

    # Use the same embedding model used during ingestion.
    response = requests.post(f"{OLLAMA_URL}/api/embed", json=embedding_request, timeout=300)
    response.raise_for_status()
    vector = response.json()["embeddings"][0]

    # Search Qdrant and include the stored text and source metadata.
    search_request = {
        "query": vector,
        "limit": 3,
        "with_payload": True
    }
    headers = {"api-key": QDRANT_API_KEY}
    url = f"{QDRANT_URL}/collections/{COLLECTION}/points/query"

    response = requests.post(url, headers=headers, json=search_request, timeout=60)
    response.raise_for_status()

    return response.json()["result"]["points"]
