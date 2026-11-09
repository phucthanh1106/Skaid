import time
from app.queue_connection import redis_server, toLLM


# Submit the dummy job without importing the worker's task locally.
prompt = input("Type your prompt: ")
job = toLLM.enqueue("tasks.process_prompt", prompt)

# Check for the stored answer for up to 60 seconds.
wait_seconds = 60
deadline = time.monotonic() + wait_seconds

while time.monotonic() < deadline:
    answer = redis_server.get(f"response:{job.id}")

    # Display the answer once the worker has stored it.
    if answer is not None:
        print(job.id, answer.decode("utf-8"))
        break

    # Check for a job that ended without producing an answer.
    status = job.get_status(refresh=True)
    if status in ("failed", "stopped", "canceled"):
        print("Job ended without an answer:", job.id, status)

        # Fetch the worker's saved traceback when execution failed.
        if status == "failed":
            job.refresh()
            print(job.exc_info)
        break

    # Wait one second before checking again.
    time.sleep(1)
else:
    # A timeout stops waiting; it does not cancel the job.
    print(f"No answer within {wait_seconds} seconds. Job ID:", job.id)