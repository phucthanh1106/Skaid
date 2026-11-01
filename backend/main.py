from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from queue_connection import redis_server, toLLM

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
    prompt = payload.get("prompt")
    print(prompt)

    job = toLLM.enqueue("tasks.process_prompt", prompt.strip())

    return {"job_id": job.id}

@app.get("/api/messages/{job_id}")
def get_response(job_id: str):
    answer = redis_server.get(f"response:{job_id}")

    return answer






