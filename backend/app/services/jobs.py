from rq.job import Job
from app.queue_connection import redis_server, toLLM
from app.services.rag import retrieve_pages, build_rag_prompt


# Retrieve evidence, build the prompt, and queue generation.
def submit_prompt(prompt, user_id):
    results = retrieve_pages(prompt)
    rag_prompt = build_rag_prompt(prompt, results)

    # Preserve ownership and allow a longer runtime for the Pi.
    return toLLM.enqueue("tasks.process_prompt", rag_prompt, meta={"user_id": user_id}, job_timeout=360)


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
