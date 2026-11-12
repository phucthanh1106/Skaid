import React from "react";
import { createRoot } from "react-dom/client";
import Auth from "./pages/Auth.jsx";
import "./App.css";

// Mount the chat interface in the page.
createRoot(document.getElementById("root")).render(<Auth />);