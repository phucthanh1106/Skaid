# Kết nối tới cùng Redis với terminal A.
import redis
from redis import Redis
from dotenv import load_dotenv
import os
from getpass import getpass

# Load ENV variables
load_dotenv()
PASSWORD = os.getenv("PASSWORD")

r = Redis(host="192.168.0.12", port=6379, password=PASSWORD, decode_responses=True)
r.ping()

# Use a fixed ID for this experiment.
job_id = "abc123"

# Store the answer before announcing it.
r.set(f"response:{job_id}", "Hello from the worker")

# Notify subscribers which job has an answer ready.
print(r.publish("practice", job_id))
