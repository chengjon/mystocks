import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright 自动化测试配置
 * 用于 MyStocks Web 前端测试
 */
export default defineConfig({
  testDir: './tests/e2e',
  /* 测试并发数 */
  fullyParallel: true,

  /* 测试超时 */
  timeout: 60 * 1000,

  /* 断言超时 */
  expect: {
    timeout: 10 * 1000,
  },

  /* 禁用 Playwright 报告 */
  forbidOnly: !!process.env.CI,

  /* 在 CI 上失败失败会失败 */
  retries: process.env.CI ? 2 : 0,

  /* CI 上的并发数 */
  workers: process.env.CI ? 1 : undefined,

  /* 报告设置 */
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],

  /* 全局设置 */
  use: {
    /* 基础 URL */
    baseURL: process.env.BASE_URL || 'http://localhost:3000',

    /* 收集跟踪 */
    trace: 'on-first-retry',

    /* 启用视频 */
    video: 'retain-on-failure',

    /* 启用截图 */
    screenshot: 'only-on-failure',

    /* 设置用户代理 */
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  },

  /* 项目配置 */
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

    /* 移动设备测试 */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },

    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  /* Web 服务器配置 */
  webServer: [
    {
      command: 'npm run dev',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
    {
      command: 'cd ../backend && python run_server.py',
      url: 'http://localhost:8000',
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
  ],
});
