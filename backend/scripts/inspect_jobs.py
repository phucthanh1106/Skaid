from rq.job import Job
from rq.exceptions import NoSuchJobError
from app.queue_connection import redis_server

# Retrieve an existing job without submitting another one.
job_id = input("Job ID: ").strip()
try:
    job = Job.fetch(job_id, connection=redis_server)
except NoSuchJobError:
    raise SystemExit("Job not found or its record has expired.")

# Display the execution information RQ recorded.
print("Job ID:", job.id)
print("Worker:", job.worker_name)
print("Status:", job.get_status())
print("Enqueued:", job.enqueued_at)
print("Started:", job.started_at)
print("Finished:", job.ended_at)

# Calculate durations only when all timestamps are available.
if job.enqueued_at and job.started_at and job.ended_at:
    queue_seconds = (job.started_at - job.enqueued_at).total_seconds()
    processing_seconds = (job.ended_at - job.started_at).total_seconds()
    total_seconds = (job.ended_at - job.enqueued_at).total_seconds()

    print(f"Queue waiting: {queue_seconds:.2f}s")
    print(f"Processing: {processing_seconds:.2f}s")
    print(f"Total: {total_seconds:.2f}s")
else:
    print("Complete timing information is not available yet.")