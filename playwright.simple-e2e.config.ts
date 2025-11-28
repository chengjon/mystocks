import { defineConfig, devices } from '@playwright/test';

/**
 * 简化的MyStocks E2E测试配置
 */
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  timeout: 60 * 1000,
  expect: { timeout: 10 * 1000 },
  retries: 1,
  workers: 1,

  reporter: [
    ['list'],
    ['html', { outputFolder: 'test-results/playwright-report', open: 'never' }],
    ['json', { outputFile: 'test-results/e2e-results.json' }]
  ],

  use: {
    baseURL: 'http://localhost:3001',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
    viewport: { width: 1920, height: 1080 },
    ignoreHTTPSErrors: true,
    actionTimeout: 30 * 1000,
    navigationTimeout: 60 * 1000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: [
    {
      command: 'echo "Frontend server already running on port 3001"',
      url: 'http://localhost:3001',
      reuseExistingServer: true,
      timeout: 10 * 1000,
    },
    {
      command: 'echo "Backend server already running on port 8000"',
      url: 'http://localhost:8000',
      reuseExistingServer: true,
      timeout: 10 * 1000,
    },
  ],
});
