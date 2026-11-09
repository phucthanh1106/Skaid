// Submit a prompt and report job status while polling for its answer.
export async function sendPrompt(prompt, onStatus) {
    const submitted = await fetch("/api/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prompt })
    });

    if (!submitted.ok) {
        throw new Error(`Could not submit prompt: HTTP ${submitted.status}`);
    }

    // Keep the existing one-minute polling budget for this job.
    const job = await submitted.json();
    const jobId = job.job_id;
    const deadline = Date.now() + 60000;

    while (Date.now() < deadline) {
        const response = await fetch(`/api/messages/${encodeURIComponent(jobId)}`);

        // Display the backend's failure explanation when one is available.
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `Could not retrieve job: HTTP ${response.status}`);
        }

        // Accept both the backend's "Finished" and RQ's lowercase statuses.
        const result = await response.json();
        const status = result.status.toLowerCase();
        onStatus(status);

        // Return text rather than the entire result object to the chat.
        if (status === "finished") {
            return result.answer;
        }

        // Also handle failures if the API returns them as status objects.
        if (["failed", "stopped", "canceled"].includes(status)) {
            throw new Error(result.error || `Job ${status}.`);
        }

        // Pause between status requests without blocking the browser.
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Stop waiting without canceling the worker's job.
    throw new Error(`Timed out waiting for job ${jobId}.`);
}
