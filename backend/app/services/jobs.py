from rq.job import Job
from app.queue_connection import redis_server, toLLM

# Submit work for the existing worker on the toLLM queue.
def submit_prompt(prompt):
    return toLLM.enqueue("tasks.process_prompt", prompt)


# Return an answer, None while pending, or an exception for missing/failed jobs.
def get_answer(job_id):
    answer = redis_server.get(f"response:{job_id}")
    if answer is not None:
        return {"status": "Finished", "answer": answer.decode("utf-8")}

    # Fetch the job only when its answer is not available.
    job = Job.fetch(job_id, connection=redis_server)
    job_status = job.get_status(refresh=True)

    if job_status in ("failed", "stopped", "canceled"):
        raise RuntimeError("Job ended without an answer. Check the worker logs.")

    return {"status": job_status, "answer": None}