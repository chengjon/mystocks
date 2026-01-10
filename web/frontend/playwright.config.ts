import { defineConfig, devices } from '@playwright/test';

/**
 * MyStocks Frontend - Playwright Configuration
 * Phase 3: Bloomberg Terminal Style Verification
 *
 * Comprehensive Playwright configuration for testing:
 * - Design Token system validation
 * - Bloomberg Terminal style compliance
 * - Component style isolation
 * - Visual regression testing
 * - ECharts rendering verification
 */

export default defineConfig({
  // Test directory
  testDir: './tests',

  // Test timeout
  timeout: 30 * 1000, // 30 seconds per test
  expect: {
    // Screenshot comparison threshold (0.1% tolerance)
    threshold: 0.001,
    // Assertion timeout
    timeout: 5000,
  },

  // Fully parallelized test execution
  fullyParallel: true,

  // Fail on first error
  // stopOnFirstFailure: true, // Commented to see all failures

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Workers: number of CPU cores
  workers: process.env.CI ? 2 : undefined,

  // Reporter configuration
  reporter: [
    ['html', {
      outputFolder: 'playwright-report',
      open: 'never',
    }],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'junit-results.xml' }],
    ['list'],
  ],

  // Shared settings for all tests
  use: {
    // Base URL for tests (PM2 served production build)
    baseURL: process.env.BASE_URL || 'http://localhost:8080',

    // Collect trace on first retry
    trace: 'on-first-retry',

    // Screenshot configuration
    screenshot: 'only-on-failure',

    // Video recording
    video: 'retain-on-failure',

    // Browser viewport
    viewport: { width: 1920, height: 1080 },

    // Ignore HTTPS errors (if using self-signed certs)
    ignoreHTTPSErrors: true,

    // Wait for network idle
    waitUntil: 'networkidle',

    // Action timeout
    actionTimeout: 10000,

    // Navigation timeout
    navigationTimeout: 30000,
  },

  // Projects for different browsers/devices
  projects: [
    {
      name: 'chromium-desktop',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox-desktop',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit-desktop',
      use: { ...devices['Desktop Safari'] },
    },

    // Visual regression tests (Chrome only, consistent environment)
    {
      name: 'visual-regression',
      use: {
        ...devices['Desktop Chrome'],
        // Ensure consistent font rendering
        fontFamily: 'Inter, system-ui, sans-serif',
      },
      testMatch: /.*\.visual\.test\.ts/,
    },

    // Bloomberg Style Compliance Tests
    {
      name: 'bloomberg-style',
      use: { ...devices['Desktop Chrome'] },
      testMatch: /.*\.bloomberg\.test\.ts/,
    },

    // Design Token Tests
    {
      name: 'design-token',
      use: { ...devices['Desktop Chrome'] },
      testMatch: /.*\.token\.test\.ts/,
    },

    // Component Tests
    {
      name: 'component-tests',
      use: { ...devices['Desktop Chrome'] },
      testMatch: /.*\.component\.test\.ts/,
    },
  ],

  // Development server (if needed for local testing)
  // webServer: {
  //   command: 'npm run dev',
  //   port: 3000,
  //   reuseExistingServer: !process.env.CI,
  // },
});
