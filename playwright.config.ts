import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // 测试项目分离
  projects: [
    // E2E 测试项目
    {
      name: 'e2e',
      testDir: './tests/e2e',
      testIgnore: '**/specs/**',
      use: {
        baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
        locale: 'zh-CN',
        timezoneId: 'Asia/Shanghai',
        ...devices['Desktop Chrome'],
      },
      timeout: 60000,
      retries: process.env.CI ? 2 : 0,
      fullyParallel: true,
      workers: process.env.CI ? 1 : undefined,
      webServer: {
        command: 'cd web/frontend && npm run dev',
        url: 'http://localhost:3000',
        reuseExistingServer: !process.env.CI,
        timeout: 120000,
      },
    },
    // API 测试项目
    {
      name: 'api',
      testDir: './tests/api',
      use: {
        baseURL: process.env.API_BASE_URL || 'http://localhost:8000',
        trace: 'on-first-retry',
      },
      timeout: 30000,
      retries: process.env.CI ? 2 : 1,
      fullyParallel: true,
      workers: 4,
    },
    // 多浏览器E2E测试
    {
      name: 'e2e-firefox',
      testDir: './tests/e2e',
      testIgnore: '**/specs/**',
      use: {
        ...devices['Desktop Firefox'],
        baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
        locale: 'zh-CN',
        timezoneId: 'Asia/Shanghai',
      },
      timeout: 60000,
      retries: process.env.CI ? 2 : 0,
      fullyParallel: true,
    },
    {
      name: 'e2e-webkit',
      testDir: './tests/e2e',
      testIgnore: '**/specs/**',
      use: {
        ...devices['Desktop Safari'],
        baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
        locale: 'zh-CN',
        timezoneId: 'Asia/Shanghai',
      },
      timeout: 60000,
      retries: process.env.CI ? 2 : 0,
      fullyParallel: true,
    },
  ],

  // 全局报告配置
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['list'],
  ],

  // 全局配置
  forbidOnly: !!process.env.CI,

  // 性能报告
  reportSlowTests: {
    max: 5,
    threshold: 30000,
  },

  // 期望超时
  expect: {
    timeout: 10000,
  },

  // 输出目录
  outputDir: 'test-results/',
});
