/**
 * Playwright API测试配置
 * 用于API契约一致性测试
 *
 * 创建时间: 2025-12-30
 * 作者: Test CLI
 */

import { defineConfig } from '@playwright/test';

/**
 * 测试环境配置
 */
const baseURL = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8000';
const timeout = parseInt(process.env.PLAYWRIGHT_TIMEOUT || '30000');

export default defineConfig({
  testDir: './',

  // 测试执行配置
  timeout,
  expect: {
    timeout: 10000,
  },

  // 全局测试配置
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: process.env.CI ? 1 : 4,

  // 报告配置
  reporter: [
    ['html', { outputFolder: 'playwright-report/api' }],
    ['json', { outputFile: 'api-test-results/results.json' }],
    ['junit', { outputFile: 'api-test-results/junit.xml' }],
    ['list'],
  ],

  // 全局设置
  use: {
    baseURL,
    actionTimeout: 10000,
    trace: 'on-first-retry',
  },

  // 输出目录配置
  outputDir: 'api-test-results/',

  // 报告慢测试
  reportSlowTests: {
    max: 5,
    threshold: 30000,
  },
});

/**
 * 测试分类配置
 */
export const testCategories = {
  // P0: 核心API，100%覆盖
  P0: {
    priority: 'critical',
    coverageTarget: 100,
    apis: [
      '/api/auth/login',
      '/api/auth/logout',
      '/api/market/realtime',
      '/api/strategy/create',
      '/api/strategy/execute',
    ],
  },

  // P1: 重要API，80%覆盖
  P1: {
    priority: 'high',
    coverageTarget: 80,
    apis: [
      '/api/stock/info',
      '/api/stock/kline',
      '/api/market/snapshot',
      '/api/wencai/query',
    ],
  },

  // P2: 一般API，按需覆盖
  P2: {
    priority: 'medium',
    coverageTarget: 40,
    apis: [
      '/api/technical/indicator',
      '/api/backtest/run',
      '/api/order/create',
    ],
  },
};

/**
 * 测试数据配置
 */
export const testData = {
  baseURL,
  endpoints: {
    auth: {
      login: '/api/auth/login',
      logout: '/api/auth/logout',
      register: '/api/auth/register',
    },
    market: {
      realtime: '/api/market/realtime',
      snapshot: '/api/market/snapshot',
      kline: '/api/market/kline',
    },
    stock: {
      info: '/api/stock/info',
      detail: '/api/stock/detail',
      financial: '/api/stock/financial',
    },
    strategy: {
      list: '/api/strategy/list',
      create: '/api/strategy/create',
      update: '/api/strategy/update',
      delete: '/api/strategy/delete',
      execute: '/api/strategy/execute',
    },
    wencai: {
      query: '/api/wencai/query',
      history: '/api/wencai/history',
    },
    technical: {
      indicator: '/api/technical/indicator',
      analysis: '/api/technical/analysis',
    },
    backtest: {
      run: '/api/backtest/run',
      result: '/api/backtest/result',
      list: '/api/backtest/list',
    },
    order: {
      create: '/api/order/create',
      cancel: '/api/order/cancel',
      list: '/api/order/list',
      detail: '/api/order/detail',
    },
  },

  // 测试用户凭证
  credentials: {
    admin: {
      username: 'admin',
      password: 'admin123',
    },
    user: {
      username: 'user',
      password: 'user123',
    },
  },

  // 测试股票代码
  stockSymbols: {
    maotai: '600519',
    wuliangye: '000858',
    pingan: '000001',
    zhongshang: '601012',
    ningde: '300750',
  },
};

/**
 * 性能基准
 */
export const performanceBenchmarks = {
  responseTime: {
    fast: 500,      // < 500ms
    normal: 1000,   // < 1s
    slow: 3000,     // < 3s
  },

  // 各类API的性能基准
  apiBenchmarks: {
    auth: 1000,         // 认证API < 1s
    market: 800,        // 行情API < 800ms
    stock: 1200,        // 股票API < 1.2s
    strategy: 1500,     // 策略API < 1.5s
    wencai: 2000,       // 问财API < 2s
    technical: 1500,    // 技术分析API < 1.5s
    backtest: 5000,    // 回测API < 5s
    order: 1000,        // 订单API < 1s
  },
};
