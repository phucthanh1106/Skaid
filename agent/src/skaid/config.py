import os
from pathlib import Path
from dotenv import load_dotenv

# Locate the backend directory without using a computer-specific path
BACKEND_DIR = Path(__file__).resolve().parents[2]

# Load all secrets from backend/.env
load_dotenv(BACKEND_DIR / ".env")

# Build the document path from the project location
DOCUMENT_PATH = BACKEND_DIR / "data" / "documents.json"

# Read external-service configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "skaid")