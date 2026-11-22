from redis import Redis
from rq import Queue
from app.config import PASSWORD, QUEUE_NAME, REDIS_HOST, REDIS_PORT

# Construct the Redis client and RQ queue without decoding RQ's binary data.
redis_server = Redis(host=REDIS_HOST, port=REDIS_PORT, password=PASSWORD)
toLLM = Queue(QUEUE_NAME, connection=redis_server)
