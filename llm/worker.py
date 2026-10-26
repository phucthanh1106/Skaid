import os
from dotenv import load_dotenv
from redis import Redis
from rq import Worker

load_dotenv()
PASSWORD = os.getenv("PASSWORD")

# Connect to the same Redis server used by the producer.
redis_server = Redis(host="192.168.0.12", port=6379, password=PASSWORD)

# Listen continuously for jobs in toLLM.
worker = Worker(["toLLM"], connection=redis_server)
worker.work()



