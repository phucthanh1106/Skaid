import React, { useEffect, useRef, useState } from "react";
import { sendPrompt } from "./api.js";

// Format elapsed seconds as minutes and seconds.
function formatDuration(seconds) {
    return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

// Display the conversation and send one prompt at a time.
export default function App() {
    const [messages, setMessages] = useState([]);
    const [prompt, setPrompt] = useState("");
    const [waiting, setWaiting] = useState(false);
    const [error, setError] = useState("");
    const [jobStatus, setJobStatus] = useState("submitting");
    const [elapsedSeconds, setElapsedSeconds] = useState(0);
    const conversation = useRef(null);
    const requestStartedAt = useRef(0);

    // Describe the worker state without claiming generation has already started.
    const statusLabels = {
        submitting: "Sending prompt…",
        queued: "Waiting for a worker…",
        started: "Skaid is working…",
        deferred: "Waiting for a dependency…",
        scheduled: "Waiting for scheduled execution…",
        finished: "Answer ready."
    };

    // Update elapsed waiting time once per second and clean up after completion.
    useEffect(() => {
        if (!waiting) return;
        const timer = setInterval(() => {
            setElapsedSeconds(Math.floor((performance.now() - requestStartedAt.current) / 1000));
        }, 1000);
        return () => clearInterval(timer);
    }, [waiting]);

    // Keep the newest message visible as the conversation grows.
    useEffect(() => {
        conversation.current.scrollTop = conversation.current.scrollHeight;
    }, [messages, waiting, error]);

    // Add the user's message, then wait for the API helper's answer.
    async function handleSubmit(event) {
        event.preventDefault();
        const text = prompt.trim();
        if (!text || waiting) return;

        // Timestamp submission and start the total waiting-time clock.
        requestStartedAt.current = performance.now();
        setJobStatus("submitting");
        setElapsedSeconds(0);
        setMessages(current => [...current, { role: "user", content: text, timestamp: new Date().toISOString() }]);
        setPrompt("");
        setError("");
        setWaiting(true);

        try {
            const answer = await sendPrompt(text, setJobStatus);

            // Timestamp receipt and retain the full response time, including queue waiting.
            const elapsedSeconds = Math.floor((performance.now() - requestStartedAt.current) / 1000);
            setMessages(current => [...current, { role: "assistant", content: answer, timestamp: new Date().toISOString(), elapsedSeconds: elapsedSeconds }]);
        } catch (error) {
            setError(error.message || "Could not get an answer. Please try again.");
            setPrompt(text);
        } finally {
            setWaiting(false);
        }
    }

    // Send with Enter; use Shift+Enter to insert a new line.
    function handleKeyDown(event) {
        if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
            event.preventDefault();
            event.currentTarget.form.requestSubmit();
        }
    }

    return (
        <main className="chat">
            <header className="header">
                <div><p className="eyebrow">YOUR PERSONAL TEACHING ASSISTANT</p><h1>Skaid Chat<span>.</span></h1></div>
                <img className="wordmark" src="/skidmore-logo.svg" alt="Skidmore College" />
            </header>

            {/* Render model output as plain text, including line breaks. */}
            <section className="conversation" ref={conversation} role="log" aria-label="Conversation" aria-live="polite">
                {messages.length === 0 && (
                    <div className="empty"><img className="mark" src="/skidmore-seal.png" alt="Skidmore College seal" /><h2>Start a conversation.</h2><p>Ask a question or explore an idea.<br /></p></div>
                )}
                {messages.map((message, index) => (
                    <article className={`message ${message.role}`} key={index}>
                        {/* Show each message's timestamp in the browser's local timezone. */}
                        <div className="message-heading">
                            <p className="speaker">{message.role === "user" ? "YOU" : "SKAID"}</p>
                            <time className="timestamp" dateTime={message.timestamp} title={new Date(message.timestamp).toLocaleString()}>{new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</time>
                        </div>
                        <p className="content">{message.content}</p>
                        {message.role === "assistant" && <p className="response-time">Response time {formatDuration(message.elapsedSeconds)}</p>}
                    </article>
                ))}
                {/* Keep the visual timer quiet for screen readers as it changes each second. */}
                {waiting && <p className="waiting" role="status">{statusLabels[jobStatus] || "Waiting for an answer…"} <span aria-hidden="true">· {formatDuration(elapsedSeconds)} elapsed</span></p>}
            </section>

            {/* Keep API failures visible and allow the prompt to be retried. */}
            {error && <p className="error" role="alert">{error}</p>}

            {/* Submit prompts using the button or Enter. */}
            <form className="composer" onSubmit={handleSubmit}>
                <label className="sr-only" htmlFor="prompt">Your message</label>
                <textarea id="prompt" rows="2" placeholder="Message Skaid…" value={prompt} onChange={event => setPrompt(event.target.value)} onKeyDown={handleKeyDown} disabled={waiting} />
                <button type="submit" disabled={waiting || !prompt.trim()}>{waiting ? "Waiting…" : "Send ↗"}</button>
            </form>
            <p className="footnote">Enter to send · Shift+Enter for a new line · Model answers can be incorrect</p>
        </main>
    );
}
