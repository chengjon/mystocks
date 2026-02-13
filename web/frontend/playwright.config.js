import { defineConfig, devices } from '@playwright/test';

/**
 * @see https://playwright.dev/docs/test-configuration
 */

// 从环境变量获取端口配置
const getFrontendPort = () => {
  // 优先使用命令行参数或环境变量
  if (process.env.FRONTEND_PORT) {
    return parseInt(process.env.FRONTEND_PORT);
  }
  // 然后使用.env文件中的配置
  if (process.env.FRONTEND_PORT_RANGE_START) {
    return parseInt(process.env.FRONTEND_PORT_RANGE_START);
  }
  // 默认值
  return 3101;
};

const frontendPort = getFrontendPort();
const baseURL = `http://localhost:${frontendPort}`;

export default defineConfig({
  testDir: './tests',
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
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['github'],
  ],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL,

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',

    /* Take screenshot on failure */
    screenshot: 'only-on-failure',

    /* Record video on failure */
    video: 'retain-on-failure',
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: `FRONTEND_PORT=${frontendPort} FRONTEND_PORT_RANGE_START=${frontendPort} FRONTEND_PORT_RANGE_END=${frontendPort} npm run dev:no-types`,
    port: frontendPort,
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
