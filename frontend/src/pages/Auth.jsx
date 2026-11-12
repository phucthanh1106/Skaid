// Import the effect used to dismiss notifications.
import React, { useEffect, useState } from "react";

// Load the existing chatbot interface.
import App from "../App.jsx";

// Display the login or signup mockup.
export default function Auth() {
    const [isSignup, setIsSignup] = useState(false);

    // Track a successful login for the current page visit.
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    // Wait for the cookie check before showing login or chat.
    const [checkingSession, setCheckingSession] = useState(true);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [message, setMessage] = useState("");

    // Choose the notification color and dismiss it automatically.
    const [messageType, setMessageType] = useState("error");

    useEffect(() => {
        if (!message) return;

        const timer = setTimeout(() => setMessage(""), 6000);
        return () => clearTimeout(timer);
    }, [message]);

    // Restore the session when the page is opened or refreshed.
    useEffect(() => {
        async function checkSession() {
            try {
                const response = await fetch("/api/users/me", {
                    credentials: "include"
                });

                // A 401 means login is needed; other failures need an explanation.
                if (!response.ok && response.status !== 401) {
                    throw new Error("Session check failed.");
                }

                setIsLoggedIn(response.ok);
            } catch (error) {
                setMessageType("error");
                setMessage("Couldn't check your session. Please try logging in.");
            } finally {
                setCheckingSession(false);
            }
        }

        checkSession();
    }, []);

    // Check each signup password requirement as the user types.
    const passwordRules = [
        { label: "At least 8 characters", valid: password.length >= 8 },
        { label: "At least 1 uppercase letter", valid: /[A-Z]/.test(password) },
        { label: "At least 1 number", valid: /[0-9]/.test(password) },
        { label: "At least 1 symbol", valid: /[^A-Za-z0-9\s]/.test(password) }
    ];

    // Validate the form before sending credentials to the backend.
    async function handleSubmit(event) {
        // Clear the previous notification and default to error styling.
        event.preventDefault();
        setMessage("");
        setMessageType("error");

        // Allow signup only with a Skidmore College email.
        if (isSignup && !email.trim().toLowerCase().endsWith("@skidmore.edu")) {
            setMessage("Please use your @skidmore.edu email to sign up.");
            return;
        }

        if (isSignup && !passwordRules.every(rule => rule.valid)) {
            setMessage("Please meet all four password requirements.");
            return;
        }

        if (isSignup && password !== confirmPassword) {
            setMessage("Passwords do not match.");
            return;
        }

        // Send credentials to signup or login and accept the backend cookie.
        try {
            const response = await fetch(isSignup ? "/api/users/signup" : "/api/users/login", {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: email.trim(), password: password })
            });

            // Read the response and handle backend validation errors.
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                const detail = Array.isArray(data.detail)
                    ? data.detail.map(error => error.msg).join(" ")
                    : data.detail;

                // Explain server failures without showing technical HTTP messages.
                throw new Error(
                    response.status >= 500
                        ? "The server couldn't complete your request. Please try again."
                        : detail || "Please check your email and password and try again."
                );
            }

            // Clear passwords and switch successful signups to the login form.
            setPassword("");
            setConfirmPassword("");
            setShowPassword(false);

            // Return signups to login; open the chatbot after successful login.
            if (isSignup) {
                setIsSignup(false);
            } else {
                setIsLoggedIn(true);
            }

            // Confirm success with an instruction appropriate to the form.
            setMessageType("success");
            setMessage(isSignup ? "Account created! Please log in." : "You’re logged in successfully.");
        } catch (error) {
            // Explain connection failures or show the backend's validation message.
            setMessageType("error");
            setMessage(
                error instanceof TypeError
                    ? "Can't reach the server. Check your connection and try again."
                    : error.message
            );
        }
    }

    // Clear form values when switching between login and signup.
    function switchForm() {
        setIsSignup(!isSignup);
        setEmail("");
        setPassword("");
        setConfirmPassword("");
        setShowPassword(false);
        setMessage("");
    }

    // Avoid briefly displaying the login form while checking the cookie.
    if (checkingSession) {
        return <main className="auth-page"><p role="status">Checking your session…</p></main>;
    }

    // Replace the authentication form with the chatbot after login.
    if (isLoggedIn) {
        return <App />;
    }

    // Check the email format and exact Skidmore domain for the signup indicator.
    const isSkidmoreEmail = /^[^@\s]+@skidmore\.edu$/i.test(email.trim());

    return (
        <main className="auth-page">
            {/* Keep the existing Skaid branding above the form. */}
            <section className="auth-card">
                <h2>{isSignup ? "Create your account" : "Welcome back"}</h2>

                {/* Use browser validation for required fields and email format. */}
                <form onSubmit={handleSubmit}>
                    <label htmlFor="email">Email</label>
                    <input id="email" type="email" autoComplete="email" placeholder="you@example.com" value={email} onChange={event => setEmail(event.target.value)} required />

                    {/* Show the email requirement only during signup. */}
                    {isSignup && (
                        <ul className="password-rules">
                            <li className={isSkidmoreEmail ? "rule-met" : ""}>
                                {isSkidmoreEmail ? "✓" : "•"} Must be a Skidmore email
                            </li>
                        </ul>
                    )}

                    <label htmlFor="password">Password</label>
                    <input id="password" type={showPassword ? "text" : "password"} autoComplete={isSignup ? "new-password" : "current-password"} value={password} onChange={event => setPassword(event.target.value)} required />

                    {/* Show which signup requirements have been met. */}
                    {isSignup && (
                        <ul className="password-rules">
                            {passwordRules.map(rule => (
                                <li key={rule.label} className={rule.valid ? "rule-met" : ""}>
                                    {rule.valid ? "✓" : "•"} {rule.label}
                                </li>
                            ))}
                        </ul>
                    )}

                    {/* Confirm the password when creating an account. */}
                    {isSignup && (
                        <>
                            <label htmlFor="confirm-password">Confirm password</label>
                            <input id="confirm-password" type={showPassword ? "text" : "password"} autoComplete="new-password" value={confirmPassword} onChange={event => setConfirmPassword(event.target.value)} required />
                            {confirmPassword && password !== confirmPassword && (
                                <p className="error">Passwords do not match.</p>
                            )}
                        </>
                    )}

                    {/* Toggle visibility for both password fields. */}
                    <label className="show-password">
                        <input type="checkbox" checked={showPassword} onChange={event => setShowPassword(event.target.checked)} />
                        Show password
                    </label>

                    {/* Display the notification inside the form above its submit button. */}
                    {message && (
                        <div className={`auth-toast ${messageType}`} role={messageType === "error" ? "alert" : "status"}>
                            <span>{message}</span>
                            <button type="button" aria-label="Dismiss notification" onClick={() => setMessage("")}>×</button>
                        </div>
                    )}

                    <button className="auth-submit" type="submit">
                        {isSignup ? "Sign up" : "Log in"}
                    </button>
                </form>

                {/* Switch forms without adding a routing library. */}
                <p className="auth-switch">
                    {isSignup ? "Already have an account? " : "Don't have an account? "}
                    <button type="button" onClick={switchForm}>
                        {isSignup ? "Log in" : "Sign up"}
                    </button>
                </p>
            </section>
        </main>
    );
}