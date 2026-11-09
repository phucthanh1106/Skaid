import os
from pathlib import Path
from dotenv import load_dotenv

# Load backend/.env regardless of the directory used to start Python.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Keep connection details and allowed browser origins in one place.
REDIS_HOST = os.getenv("REDIS_HOST", "192.168.0.12")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
PASSWORD = os.getenv("PASSWORD")
QUEUE_NAME = os.getenv("QUEUE_NAME", "toLLM")
