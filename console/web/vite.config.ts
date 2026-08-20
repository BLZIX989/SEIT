import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// UOC Research Console web shell. Dev server proxies /api to the
// FastAPI backend (console/api, run separately with uvicorn) so the
// frontend never needs a hard-coded absolute API origin.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
    // e2e/ holds Playwright specs (a different test runner, real browser
    // against the real backend) -- vitest must never try to collect them.
    exclude: ["**/node_modules/**", "e2e/**"],
  },
});
