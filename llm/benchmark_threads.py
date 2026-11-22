import requests
from statistics import median

# Use the same model and prompt for every request.
URL = "http://127.0.0.1:11434/api/generate"
PROMPT = "Explain how an HTTP request works in six short sentences."


# Send one request with the selected thread count.
def generate(threads, max_tokens):
    payload = {
        "model": "qwen2.5:1.5b",
        "prompt": PROMPT,
        "stream": False,
        "keep_alive": "10m",
        "options": {
            "num_thread": threads,
            "num_predict": max_tokens,
            "temperature": 0,
            "seed": 42
        }
    }

    response = requests.post(URL, json=payload, timeout=600)
    response.raise_for_status()
    return response.json()


# Compare warm generation speed for two and four threads.
for threads in [2, 4]:
    # Load and prepare this configuration before measuring.
    print(f"\nWarming up {threads} threads...", flush=True)
    generate(threads, 1)

    speeds = []

    # Repeat to avoid judging the setting from one unusual result.
    for run in range(1, 4):
        print(f"Running test {run}/3...", flush=True)
        data = generate(threads, 64)

        # Ollama reports durations in nanoseconds; convert to seconds.
        load_seconds = data["load_duration"] / 1_000_000_000
        generation_seconds = data["eval_duration"] / 1_000_000_000

        # Tokens per second measures useful generation throughput.
        tokens = data["eval_count"]
        speed = tokens / generation_seconds
        speeds.append(speed)

        print(f"Load: {load_seconds:.2f}s")
        print(f"Generated: {tokens} tokens in {generation_seconds:.2f}s")
        print(f"Speed: {speed:.2f} tokens/s")

    # The median is the middle value of the three measured speeds.
    print(f"RESULT: {threads} threads = {median(speeds):.2f} tokens/s")