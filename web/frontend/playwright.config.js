const { defineConfig, devices } = require("@playwright/test");
const { loadPortEnv, resolveFrontendConfig } = require("./tests/e2e/helpers/port-env.js");

/**
 * @see https://playwright.dev/docs/test-configuration
 */

loadPortEnv(__dirname);

const resolvedFrontend = resolveFrontendConfig();
const e2eFrontendPortRaw = process.env.E2E_FRONTEND_PORT || process.env.PLAYWRIGHT_FRONTEND_PORT;
const e2eFrontendPort = e2eFrontendPortRaw ? Number.parseInt(e2eFrontendPortRaw, 10) : null;
const frontendPort = Number.isInteger(e2eFrontendPort) ? e2eFrontendPort : resolvedFrontend.port;
const baseURL = process.env.FRONTEND_BASE_URL || `http://127.0.0.1:${frontendPort}`;

// Ensure helper utilities that read FRONTEND_PORT/FRONTEND_BASE_URL use the same dedicated E2E server.
process.env.FRONTEND_PORT = String(frontendPort);
process.env.FRONTEND_BASE_URL = baseURL;

module.exports = defineConfig({
  // Canonical E2E scope: only chain/flow specs under tests/e2e.
  testDir: './tests/e2e',
  testMatch: '**/*.spec.ts',
  // Helper self-tests are maintained separately from browser E2E chain.
  testIgnore: ['**/helpers/**/*.spec.ts'],
  /* Keep local runs deterministic and avoid browser/context starvation. */
  fullyParallel: false,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Use a single worker by default for local stability; override with PW_WORKERS when needed. */
  workers: process.env.CI ? 1 : Number.parseInt(process.env.PW_WORKERS || "1", 10),
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["json", { outputFile: "test-results/results.json" }],
    ["github"],
  ],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL,
    /* Prevent SW cache/proxy from bypassing route interception in E2E mocks. */
    serviceWorkers: "block",

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: "on-first-retry",

    /* Take screenshot on failure */
    screenshot: "only-on-failure",

    /* Record video on failure */
    video: "retain-on-failure",
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: 'firefox',
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: 'webkit',
      use: { ...devices["Desktop Safari"] },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: `npm run dev:no-types -- --host 127.0.0.1 --port ${frontendPort} --strictPort`,
    port: frontendPort,
    // Never reuse an existing server: PM2 preview on 3020 can cause stale assets and false negatives.
    reuseExistingServer: false,
    timeout: 120 * 1000,
  },
});
