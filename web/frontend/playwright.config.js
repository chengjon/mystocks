const { defineConfig, devices } = require("@playwright/test");
const { loadPortEnv, resolveFrontendConfig } = require("./tests/e2e/helpers/port-env.js");

/**
 * @see https://playwright.dev/docs/test-configuration
 */

loadPortEnv(__dirname);

const { port: frontendPort, baseUrl: baseURL } = resolveFrontendConfig();

module.exports = defineConfig({
  // Canonical E2E scope: only chain/flow specs under tests/e2e.
  testDir: './tests/e2e',
  testMatch: '**/*.spec.ts',
  // Helper self-tests are maintained separately from browser E2E chain.
  testIgnore: ['**/helpers/**/*.spec.ts'],
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
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
    command: `npm run dev -- --port ${frontendPort}`,
    port: frontendPort,
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
