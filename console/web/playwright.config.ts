import { defineConfig, devices } from "@playwright/test";

// This environment pre-installs Chromium at a revision that doesn't match
// whatever @playwright/test happens to be pinned to (see PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD
// in the environment notes) -- point at it explicitly instead of letting
// Playwright try to download its own copy.
export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  fullyParallel: false,
  workers: 1,
  reporter: [["list"]],
  use: {
    baseURL: "http://127.0.0.1:5183",
    launchOptions: {
      executablePath: "/opt/pw-browsers/chromium",
    },
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
  webServer: [
    {
      command: "npm run dev -- --port 5183 --strictPort",
      url: "http://127.0.0.1:5183",
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: "python3 -m uvicorn console.api.main:app --port 8000",
      url: "http://127.0.0.1:8000/api/health",
      reuseExistingServer: false,
      timeout: 30_000,
      cwd: "../../",
    },
  ],
});
