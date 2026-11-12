from fastapi import APIRouter, Depends, HTTPException
from rq.exceptions import NoSuchJobError
from app.services.auth import get_current_user_id
from app.services.jobs import get_answer, submit_prompt

# Group the message endpoints under their shared URL prefix.
message_router = APIRouter(prefix="/api/messages")


# Require login and associate the submitted job with that user.
@message_router.post("")
def send_prompt(payload: dict, user_id: str = Depends(get_current_user_id)):
    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise HTTPException(status_code=400, detail="A non-empty prompt is required.")

    job = submit_prompt(prompt.strip(), user_id)
    return {"job_id": job.id}


# Require login and return only jobs belonging to the current user.
@message_router.get("/{job_id}")
def get_response(job_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        return get_answer(job_id, user_id)
    except (NoSuchJobError, PermissionError):
        # Use the same response for missing jobs and another user's jobs.
        raise HTTPException(status_code=404, detail="Job not found or expired.")
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error))
