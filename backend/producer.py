import os
from dotenv import load_dotenv
from redis import Redis
from rq import Queue
from tasks import process_prompt
from rq.job import Job
import time

# Load ENV variables
load_dotenv()
PASSWORD = os.getenv("PASSWORD")

# Establish the queue and the connection
connection = Redis(host="192.168.0.12", port=6379, password=PASSWORD)
toLLM = Queue("toLLM", connection=connection)

# Dummy job
prompt=input("Prompt: ")
job = toLLM.enqueue(process_prompt, prompt) # Pass the function and its argument to RQ without executing it here.

while not job.is_finished and not job.is_failed:
    time.sleep(1) # A cooldown to prevent polling
    job.refresh()

print("Result:", job.result)




