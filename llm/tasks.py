from socket import gethostname
from rq import get_current_job
import json
from urllib.request import Request, urlopen
import os

MODEL = os.getenv("MODEL")

# Process a prompt; later this function will call the LLM.
def process_prompt(prompt):
    # Build the same request body that worked with curl.
    payload = {
        "model": "qwen2.5:1.5b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 200,
            "num_thread": 4
        }
    }

    # Convert the Python dictionary into JSON bytes for HTTP.
    request = Request("http://localhost:11434/api/generate", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")

    # Allow more time for processing the retrieved slide context.
    with urlopen(request, timeout=300) as response:
        data = json.loads(response.read().decode("utf-8"))

    # Extract and display the generated answer.
    answer = data["response"]

    # Get the RQ job currently executing.
    job = get_current_job()

    #--------------START BENCHMARK--------------
    # Convert Ollama's timing measurements into seconds.
    load_seconds = data["load_duration"] / 1_000_000_000
    prompt_seconds = data["prompt_eval_duration"] / 1_000_000_000
    generation_seconds = data["eval_duration"] / 1_000_000_000

    # Count the input and generated tokens.
    input_tokens = data["prompt_eval_count"]
    output_tokens = data["eval_count"]
    speed = output_tokens / generation_seconds

    # Show which stage consumed the time for this job.
    print(f"Job: {job.id}", flush=True)
    print(f"Load: {load_seconds:.2f}s", flush=True)
    print(f"Prompt: {input_tokens} tokens, {prompt_seconds:.2f}s", flush=True)
    print(f"Generation: {output_tokens} tokens, {generation_seconds:.2f}s", flush=True)
    print(f"Generation speed: {speed:.2f} tokens/s", flush=True)

    # Report reused prompt tokens when this Ollama version provides them.
    if "prompt_eval_cached_count" in data:
        print(f"Cached prompt tokens: {data['prompt_eval_cached_count']}", flush=True)
    #--------------END BENCHMARK--------------

    # Store the generated answer where the producer is polling.
    r = job.connection
    r.set(f"response:{job.id}", answer, ex=3600)

    return answer
