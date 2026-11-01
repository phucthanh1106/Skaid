import os
from dotenv import load_dotenv
from redis import Redis
from rq import Queue

# Load the Redis password from the backend environment.
load_dotenv()
PASSWORD = os.getenv("PASSWORD")

# Share the Redis connection and job queue.
redis_server = Redis(host="192.168.0.12", port=6379, password=PASSWORD)
toLLM = Queue("toLLM", connection=redis_server)