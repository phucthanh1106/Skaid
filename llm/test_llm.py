import json
from urllib.request import Request, urlopen

# Build the same request body that worked with curl.
payload = {
    "model": "qwen2.5:0.5b",
    "prompt": "Explain what a job queue does in two short sentences.",
    "stream": False
}

# Convert the Python dictionary into JSON bytes for HTTP.
request = Request("http://localhost:11434/api/generate", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")

# Send the request and wait up to 120 seconds for network operations.
with urlopen(request, timeout=120) as response:
    data = json.loads(response.read().decode("utf-8"))

# Extract and display the generated answer.
answer = data["response"]
print(answer)

