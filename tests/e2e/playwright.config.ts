/**
 * Playwright E2E测试配置
 * 为Vue 3 + FastAPI架构优化的端到端测试配置
 *
 * 作者: Claude Code
 * 生成时间: 2025-11-14
 */

import { defineConfig, devices } from '@playwright/test';

/**
 * 测试环境配置
 * Per CLAUDE.md port allocation: Frontend 3020-3029, Backend 8020-8029
 */
const baseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3020';
const apiURL = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8000';
const timeout = parseInt(process.env.PLAYWRIGHT_TIMEOUT || '60000');

export default defineConfig({
  testDir: './',

  // 测试执行配置
  timeout,
  expect: {
    timeout: 10000,
    /**
     * 期望值自定义匹配器
     */
    toHaveScreenshot: {
      threshold: 0.1,
      maxDiffPixelRatio: 0.01,
    },
  },

  // 全局测试配置
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],

  // 全局设置
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  // 测试项目配置 - 简化版本（仅Chromium）
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // 开发服务器配置（已禁用，使用独立的服务器启动脚本）
  // webServer: {
  //   command: 'npm run dev',
  //   url: 'http://localhost:3000',  // Per port allocation spec
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120000,
  // },

  // 输出目录配置
  outputDir: 'test-results/',

  // 全局测试钩子
  globalSetup: './global-setup.ts',
  globalTeardown: './global-teardown.ts',

  // 报告配置
  reportSlowTests: {
    max: 5,
    threshold: 60000,
  },

  // 警告配置
  preserveScreenshotDir: true,
});

/**
 * 环境特定配置
 */
export const environments = {
  development: {
    baseURL: 'http://localhost:3020',  // Per CLAUDE.md port allocation: Frontend 3020-3029
    apiURL: 'http://localhost:8000',    // Backend 8000-8029
    headless: false,
    slowMo: 0,
  },

  staging: {
    baseURL: 'https://staging.mystocks.company.com',
    apiURL: 'https://staging-api.mystocks.company.com',
    headless: true,
    slowMo: 0,
  },

  production: {
    baseURL: 'https://mystocks.company.com',
    apiURL: 'https://api.mystocks.company.com',
    headless: true,
    slowMo: 0,
  },
};

/**
 * 测试数据配置
 */
export const testData = {
  users: {
    admin: {
      username: 'admin',
      password: 'admin123',
      role: 'admin',
    },
    trader: {
      username: 'trader',
      password: 'trader123',
      role: 'trader',
    },
    viewer: {
      username: 'viewer',
      password: 'viewer123',
      role: 'viewer',
    },
  },

  stocks: {
    // 常用测试股票
    maotai: '600519',
    wuliangye: '000858',
    pingan: '000001',
    zhongshang: '601012',
    ningde: '300750',
  },

  queries: {
    // 常用问财查询
    strong_stocks: '强势股票',
    limit_up: '涨停板股票',
    high_volume: '放量股票',
    ma_cross: 'MA金叉',
  },
};

/**
 * 性能基准配置
 */
export const performance = {
  budgets: {
    FCP: 2000,  // 首次内容绘制 < 2秒
    LCP: 2500,  // 最大内容绘制 < 2.5秒
    CLS: 0.1,   // 累积布局偏移 < 0.1
    TTFB: 600,  // 首字节时间 < 600ms
    TTI: 3500,  // 可交互时间 < 3.5秒
  },

  apiResponse: {
    dashboard: 1000,  // 仪表盘API < 1秒
    market: 800,      // 市场数据API < 800ms
    technical: 1500,  // 技术分析API < 1.5秒
    wencai: 2000,     // 问财查询API < 2秒
  },
};
