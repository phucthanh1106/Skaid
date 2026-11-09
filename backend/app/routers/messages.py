from fastapi import APIRouter, HTTPException
from rq.exceptions import NoSuchJobError
from app.services.jobs import get_answer, submit_prompt

# Group the existing message endpoints under their shared URL prefix.
message_router = APIRouter(prefix="/api/messages")

# Validate the prompt and immediately return the submitted job ID.
@message_router.post("")
def send_prompt(payload: dict):
    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise HTTPException(status_code=400, detail="A non-empty prompt is required.")

    job = submit_prompt(prompt.strip())
    return {"job_id": job.id}

# Translate job lookup outcomes into the existing HTTP responses.
@message_router.get("/{job_id}")
def get_response(job_id: str):
    try:
        return get_answer(job_id)
    except NoSuchJobError:
        raise HTTPException(status_code=404, detail="Job not found or expired.")
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error))
