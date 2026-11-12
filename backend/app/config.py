import os
from pathlib import Path
from dotenv import load_dotenv

# Load backend/.env regardless of the directory used to start Python.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Read MySQL credentials separately from the Redis password.
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ["MYSQL_USER"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "skaid")

# Require a signing secret and enable secure cookies when using HTTPS.
JWT_SECRET = os.environ["JWT_SECRET"]
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

# Keep connection details and allowed browser origins in one place.
REDIS_HOST = os.getenv("REDIS_HOST", "192.168.0.12")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
PASSWORD = os.getenv("PASSWORD")
QUEUE_NAME = os.getenv("QUEUE_NAME", "toLLM")
