import React, { useEffect, useRef, useState } from "react";
import { sendPrompt } from "./api.js";

// Display the conversation and send one prompt at a time.
export default function App() {
    const [messages, setMessages] = useState([]);
    const [prompt, setPrompt] = useState("");
    const [waiting, setWaiting] = useState(false);
    const [error, setError] = useState("");
    const conversation = useRef(null);

    // Keep the newest message visible as the conversation grows.
    useEffect(() => {
        conversation.current.scrollTop = conversation.current.scrollHeight;
    }, [messages, waiting, error]);

    // Add the user's message, then wait for the API helper's answer.
    async function handleSubmit(event) {
        event.preventDefault();
        const text = prompt.trim();
        if (!text || waiting) return;

        setMessages(current => [...current, { role: "user", content: text }]);
        setPrompt("");
        setError("");
        setWaiting(true);

        try {
            const answer = await sendPrompt(text);
            setMessages(current => [...current, { role: "assistant", content: answer }]);
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
                        <p className="speaker">{message.role === "user" ? "YOU" : "SKAID"}</p>
                        <p className="content">{message.content}</p>
                    </article>
                ))}
                {waiting && <p className="waiting" role="status">Waiting for an answer…</p>}
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
