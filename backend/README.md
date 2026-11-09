# Skaid backend

Run commands from `Skaid/backend` with the `skaid` Conda environment active.

## Setup

```bash
# Install the application dependencies.
python -m pip install -r requirements.txt
```

Keep local credentials in `.env`; `.env.example` documents the settings.
The configuration always reads `backend/.env`. Existing credentials do not need moving.

## Start the API

```bash
# Start FastAPI with the app package as the entry point.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

If the FastAPI CLI is installed, `fastapi dev app/main.py` also starts the application.
Vite continues forwarding `/api` to this server; no frontend changes are required.

## Layout

- `app/main.py`: application and middleware setup.
- `app/config.py`: environment configuration.
- `app/queue_connection.py`: Redis client and RQ queue.
- `app/schemas.py`: submitted-job response shape.
- `app/routers/messages.py`: HTTP endpoints and HTTP errors.
- `app/services/jobs.py`: job submission and result lookup.
- `scripts/`: manual terminal experiments.
- `tests/`: endpoint tests with mocked Redis/RQ operations.

## API contract

- `POST /api/messages`: accepts `{"prompt": "..."}` and returns `{"job_id": "..."}`.
- `GET /api/messages/{job_id}`: returns a JSON string when ready or JSON `null` while pending.
- Invalid prompts return 400, missing/expired jobs return 404, and unsuccessful jobs return 500.

## Manual experiments

```bash
# Run the polling producer from the backend directory.
python -m scripts.producer

# Run the older Pub/Sub experiment separately.
python -m scripts.producer_sub
```

The Pub/Sub experiment still requires its matching worker task to publish notifications.

## Tests

```bash
# Install test dependencies if they are not already available.
python -m pip install -r requirements-dev.txt

# Verify endpoint behavior without submitting jobs or calling Ollama.
python -m unittest discover -s tests -v
```
