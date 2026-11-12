from rq.job import Job
from app.queue_connection import redis_server, toLLM


# Save the authenticated owner alongside the job before it is queued.
def submit_prompt(prompt, user_id):
    return toLLM.enqueue("tasks.process_prompt", prompt, meta={"user_id": user_id})


# Check ownership before reading either the answer or the job status.
def get_answer(job_id, user_id):
    job = Job.fetch(job_id, connection=redis_server)

    if job.meta.get("user_id") != user_id:
        raise PermissionError("This job belongs to another user.")

    # Return a cached answer only after verifying ownership.
    answer = redis_server.get(f"response:{job_id}")
    if answer is not None:
        return {"status": "Finished", "answer": answer.decode("utf-8")}

    # Preserve the existing handling of pending and failed jobs.
    job_status = job.get_status(refresh=True)
    if job_status in ("failed", "stopped", "canceled"):
        raise RuntimeError("Job ended without an answer. Check the worker logs.")

    return {"status": job_status, "answer": None}
