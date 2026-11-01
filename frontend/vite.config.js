import { defineConfig, loadEnv } from "vite";

// Configure Vite on Pi 2, where npm run dev executes.
export default defineConfig(({ mode }) => {
    // Read the backend target from frontend/.env.
    const env = loadEnv(mode, process.cwd(), "");
    const chatTarget = env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

    // Set the frontend listener and forward API requests to FastAPI.
    return {
        server: {
            host: "127.0.0.1",
            port: 5173,
            strictPort: true,
            proxy: {
                "/api": {
                    target: chatTarget
                }
            }
        }
    };
});