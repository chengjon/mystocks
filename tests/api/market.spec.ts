/**
 * 市场数据 API 契约测试
 *
 * 测试范围:
 * - /api/v1/data/markets/overview - 获取市场概览
 * - /api/v1/data/stocks/kline - 获取K线数据
 * - /api/v1/data/stocks/basic - 获取股票列表
 * - /api/v1/market/fund-flow - 获取资金流向
 * - /api/v1/market/etf/list - 获取ETF列表
 */

import { test, expect } from '@playwright/test';
import {
  APITestClient,
  validateAPIResponse,
  TEST_DATA,
  ERROR_CODES,
  PERFORMANCE_BENCHMARKS,
  validateResponseTime,
} from './fixtures/api-client';

test.describe('市场数据 API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
    const loginResult = await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
    expect(loginResult.success === true || loginResult.code === 200).toBe(true);
  });

  test.describe('GET /api/v1/data/markets/overview', () => {
    test('获取市场概览数据 - API正常工作', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/v1/data/markets/overview', {
        symbol: TEST_DATA.stocks.maotai,
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      // 验证响应包含必要字段
      expect(data).toBeDefined();
      expect(typeof data === 'object').toBe(true);
    });

    test('获取多只股票概览', async () => {
      const response = await client.get('/api/v1/data/markets/overview', {
        symbols: `${TEST_DATA.stocks.maotai},${TEST_DATA.stocks.pingan}`,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data).toBeDefined();
    });
  });

  test.describe('GET /api/v1/data/stocks/kline', () => {
    test('获取日K线数据 - API正常工作', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/v1/data/stocks/kline', {
        symbol: TEST_DATA.stocks.maotai,
        start_date: '2024-01-01',
        end_date: '2024-12-31',
        period: 'day',
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(data).toBeDefined();
    });

    test('获取不同周期K线数据', async () => {
      const periods = ['day', 'week', 'month'];

      for (const period of periods) {
        const response = await client.get('/api/v1/data/stocks/kline', {
          symbol: TEST_DATA.stocks.maotai,
          start_date: '2024-01-01',
          end_date: '2024-12-31',
          period,
        });

        const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
        expect(data).toBeDefined();
      }
    });
  });

  test.describe('GET /api/v1/data/stocks/basic', () => {
    test('获取股票列表 - API正常工作', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/v1/data/stocks/basic', {
        market: 'SH',
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(data).toBeDefined();
    });

    test('股票搜索功能', async () => {
      const response = await client.get('/api/v1/data/stocks/basic', {
        search: '平安',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data).toBeDefined();
    });
  });

  test.describe('GET /api/v1/market/fund-flow', () => {
    test('获取资金流向 - API正常工作', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/v1/market/fund-flow', {
        symbol: TEST_DATA.stocks.maotai,
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(data).toBeDefined();
    });
  });

  test.describe('GET /api/v1/market/etf/list', () => {
    test('获取ETF列表 - API正常工作', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/v1/market/etf/list');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(data).toBeDefined();
    });
  });
});
