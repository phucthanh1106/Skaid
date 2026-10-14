from socket import gethostname

# Process a prompt; later this function will call the LLM.
def process_prompt(prompt):
    answer = f"Received: {prompt}"
    print(f"{gethostname()} processed: {prompt}", flush=True)
    return answer