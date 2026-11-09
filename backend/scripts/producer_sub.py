from app.queue_connection import redis_server, toLLM

# Initialize subscriber to listen to responses from worker and confirm registration
sub = redis_server.pubsub()
sub.subscribe("llm_responses")

for message in sub.listen():
    if message["type"] == "subscribe":
        print("Subscriber registered successfully")
        break

# Dummy job
array=[2, 4, 6]
job = toLLM.enqueue("tasks.process_array", array) # Pass the function and its argument to RQ without executing it here.
print("Submitted job:", job.id)

# Listen for the response notification belonging to this job.
for message in sub.listen():
    if message["type"] == "message":
        # Use the published job ID to retrieve its stored answer.
        job_id = message["data"].decode("utf-8")

        # Ignore notifications for other jobs.
        if job_id != job.id:
            continue

        answer = redis_server.get(f"response:{job.id}")
        if answer is None:
            print("Answer missing for job:", job_id)
        else:
            print(job_id, answer.decode("utf-8"))
        break

sub.close()



