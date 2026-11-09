const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export async function sendPrompt(prompt) {
    const submitted = await fetch(`/api/messages`, {
        method: "POST",
        headers: {
                'Content-Type': 'application/json', // Required for the server to "see" your data
        },
        body: JSON.stringify({
            prompt: prompt,
        })
    })

    if (!submitted.ok) {
        throw new Error(`Could not submit prompt: HTTP ${submitted.status}`);
    }

    // Read the job ID returned by the POST endpoint.
    const job = await submitted.json();
    const jobId = job.job_id;
    const deadline = Date.now() + 300000;

    // Check this specific job for up to five minutes.
    while (Date.now() < deadline) {
        const response = await fetch(`/api/messages/${encodeURIComponent(jobId)}`);

        if (!response.ok) {
            throw new Error(`Could not retrieve job: HTTP ${response.status}`);
        }

        const result = await response.json();

        // Return the answer string expected by App.jsx.
        if (result !== null) {
            return result;
        }

        // Wait one second before requesting the status again.
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Stop polling without canceling the worker's job.
throw new Error(`Timed out waiting for job ${jobId}.`);
}
