import os
from dotenv import load_dotenv
from redis import Redis
from rq import Queue
from tasks import process_prompt

load_dotenv()
PASSWORD = os.getenv("PASSWORD")

connection = Redis(host="192.168.0.12", port=6379, password=PASSWORD)
queue = Queue("toLLM", connection=connection)

# prompt=input("Prompt: ")
# job = queue.enqueue(process_prompt, prompt) # Pass the function and its argument to RQ without executing it here.
# print(job)
# print(f"Queued job: {job.id}")