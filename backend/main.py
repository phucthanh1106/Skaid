from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from queue_connection import redis_server, toLLM
from rq.job import Job
from rq.exceptions import NoSuchJobError

app = FastAPI()

# Configure CORS safety gates
origins = [
    "http://localhost:5173", 
    "http://localhost:4000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/messages")
def send_response(payload: dict):
    # Reject invalid prompts before creating a job.
    prompt = payload.get("prompt")
    print(prompt)
    if not isinstance(prompt, str) or not prompt.strip():
        raise HTTPException(status_code=400, detail="A non-empty prompt is required.")

    # Submit the validated prompt.
    job = toLLM.enqueue("tasks.process_prompt", prompt.strip())

    return {"job_id": job.id}

@app.get("/api/messages/{job_id}")
def get_response(job_id: str):
    answer = redis_server.get(f"response:{job_id}")

    # Return completed answers without another job lookup.
    if answer is not None:
        return answer.decode("utf-8")

    # Distinguish an unknown or expired job from pending work.
    try:
        job = Job.fetch(job_id, connection=redis_server)
    except NoSuchJobError:
        raise HTTPException(status_code=404, detail="Job not found or expired.")

    # Make the frontend stop waiting when execution has ended unsuccessfully.
    if job.get_status(refresh=True) in ("failed", "stopped", "canceled"):
        raise HTTPException(status_code=500, detail="Job ended without an answer. Check the worker logs.")

    # A valid job without an answer is still pending.
    return None






