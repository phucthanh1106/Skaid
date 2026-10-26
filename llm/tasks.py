from socket import gethostname
from rq import get_current_job

# Process a prompt; later this function will call the LLM.
def process_prompt(prompt):
    answer = f"Received: {prompt}"
    print(f"{gethostname()} processed: {prompt}", flush=True)
    return answer

def process_array(array):
    job = get_current_job()
    answer = sum(array)

    # # Reuse redis connection
    # r = job.connection
    # r.set(f"response:{job.id}", answer)

    # # Notify subscribers after the answer is stored in redis 
    # r.publish("llm_responses", job.id)
    return answer