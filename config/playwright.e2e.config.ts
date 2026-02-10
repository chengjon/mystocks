import { defineConfig, devices } from '@playwright/test';

/**
 * MyStocks Web应用端到端可用性测试配置
 *
 * 测试目标：
 * - 前端: http://localhost:3020 (Vue3 + Element Plus)
 * - 后端: http://localhost:8000 (FastAPI + Swagger UI)
 */
export default defineConfig({
  testDir: './tests/e2e',

  /* 测试并发数 */
  fullyParallel: true,

  /* 测试超时 - 增加到3分钟以应对网络延迟 */
  timeout: 180 * 1000,

  /* 断言超时 */
  expect: {
    timeout: 15 * 1000,
  },

  /* 禁用 only 测试 */
  forbidOnly: !!process.env.CI,

  /* 重试次数 */
  retries: process.env.CI ? 3 : 1,

  /* CI 上的并发数 */
  workers: process.env.CI ? 1 : 2,

  /* 报告设置 */
  reporter: [
    ['html', {
      outputFolder: 'playwright-report',
      open: process.env.CI ? 'never' : 'on-failure'
    }],
    ['json', { outputFile: 'test-results/mystocks-e2e-results.json' }],
    ['junit', { outputFile: 'test-results/mystocks-e2e-junit.xml' }],
    ['list'],
  ],

  /* 全局设置 */
  use: {
    /* 基础 URL - 指向实际的前端服务器 (per CLAUDE.md port allocation) */
    baseURL: process.env.BASE_URL || 'http://localhost:3020',

    /* 收集跟踪 */
    trace: 'retain-on-failure',

    /* 启用视频录制 */
    video: 'retain-on-failure',

    /* 启用截图 */
    screenshot: 'only-on-failure',

    /* 设置用户代理 */
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MyStocks-E2E-Test/1.0',

    /* 忽略HTTPS错误 */
    ignoreHTTPSErrors: true,

    /* 设置视窗大小 */
    viewport: { width: 1920, height: 1080 },

    /* 设置默认超时 */
    actionTimeout: 30 * 1000,
    navigationTimeout: 60 * 1000,
  },

  /* 项目配置 - 测试不同浏览器和设备 */
  projects: [
    {
      name: 'chromium-desktop',
      use: {
        ...devices['Desktop Chrome'],
        contextOptions: {
          recordVideo: {
            dir: 'test-results/videos/',
            size: { width: 1920, height: 1080 }
          }
        }
      },
    },

    {
      name: 'firefox-desktop',
      use: {
        ...devices['Desktop Firefox'],
        contextOptions: {
          recordVideo: {
            dir: 'test-results/videos/',
            size: { width: 1920, height: 1080 }
          }
        }
      },
    },

    {
      name: 'webkit-desktop',
      use: {
        ...devices['Desktop Safari'],
        contextOptions: {
          recordVideo: {
            dir: 'test-results/videos/',
            size: { width: 1920, height: 1080 }
          }
        }
      },
    },

    /* 移动设备测试 */
    {
      name: 'mobile-chrome',
      use: {
        ...devices['Pixel 5'],
        contextOptions: {
          recordVideo: {
            dir: 'test-results/videos/mobile/',
            size: { width: 393, height: 851 }
          }
        }
      },
    },

    {
      name: 'mobile-safari',
      use: {
        ...devices['iPhone 12'],
        contextOptions: {
          recordVideo: {
            dir: 'test-results/videos/mobile/',
            size: { width: 390, height: 844 }
          }
        }
      },
    },
  ],

  /* 全局设置 - 性能监控和环境变量 */
  // globalSetup: './tests/e2e/global-setup.ts',
  // globalTeardown: './tests/e2e/global-teardown.ts',

  /* 环境变量 */
  outputDir: 'test-results/',

  /* 网络设置 */
  webServer: [
    {
      command: 'echo "Frontend server already running on port 3020"',
      url: 'http://localhost:3020',
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

  /* 测试元数据 */
  metadata: {
    'Test Suite': 'MyStocks E2E Usability Tests',
    'Application': 'MyStocks Web Application',
    'Frontend': 'Vue3 + Vite + Element Plus',
    'Backend': 'FastAPI + PostgreSQL + TDengine',
    'Test Environment': 'Development',
    'Test Date': new Date().toISOString(),
  },
});
