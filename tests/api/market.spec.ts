/**
 * 市场数据 API 契约测试
 *
 * 测试范围:
 * - /api/market/quotes - 获取实时行情
 * - /api/market/kline - 获取K线数据
 * - /api/market/stocks - 获取股票列表
 * - /api/market/fund-flow - 获取资金流向
 * - /api/market/etf/list - 获取ETF列表
 */

import { test, expect } from '@playwright/test';
import {
  APITestClient,
  validateAPIResponse,
  validateRequiredFields,
  validateFieldType,
  TEST_DATA,
  ERROR_CODES,
  PERFORMANCE_BENCHMARKS,
  validateResponseTime,
} from '../fixtures/api-client';

test.describe('市场数据 API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
    await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
  });

  test.describe('GET /api/market/quotes', () => {
    test('获取单只股票行情 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/quotes', {
        symbol: TEST_DATA.stocks.maotai,
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'name', 'price', 'change', 'changePercent']);
      validateFieldType(data, 'symbol', 'string');
      validateFieldType(data, 'price', 'number');
    });

    test('获取多只股票行情 - 返回数组', async () => {
      const response = await client.get('/api/market/quotes', {
        symbols: `${TEST_DATA.stocks.maotai},${TEST_DATA.stocks.pingan}`,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        validateRequiredFields(data[0], ['symbol', 'name', 'price']);
      }
    });

    test('缺少symbol参数 - 返回400错误', async () => {
      const response = await client.get('/api/market/quotes');

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/market/kline', () => {
    test('获取日K线数据 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/kline', {
        symbol: TEST_DATA.stocks.maotai,
        interval: '1d',
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'interval', 'klines']);
      validateFieldType(data, 'symbol', 'string');
      validateFieldType(data, 'interval', 'string');
      expect(Array.isArray(data.klines)).toBe(true);

      if (data.klines.length > 0) {
        validateRequiredFields(data.klines[0], ['timestamp', 'open', 'high', 'low', 'close', 'volume']);
        validateFieldType(data.klines[0], 'timestamp', 'number');
        validateFieldType(data.klines[0], 'open', 'number');
      }
    });

    test('指定时间范围 - 返回指定范围的数据', async () => {
      const response = await client.get('/api/market/kline', {
        symbol: TEST_DATA.stocks.maotai,
        interval: '1d',
        start_date: '2024-01-01',
        end_date: '2024-12-31',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data.klines).toBeDefined();
    });

    test('使用复权类型 - 返回复权数据', async () => {
      const response = await client.get('/api/market/kline', {
        symbol: TEST_DATA.stocks.maotai,
        interval: '1d',
        adjust: 'qfq',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data.klines).toBeDefined();
    });

    test('缺少symbol参数 - 返回400错误', async () => {
      const response = await client.get('/api/market/kline', {
        interval: '1d',
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });

    test('缺少interval参数 - 返回400错误', async () => {
      const response = await client.get('/api/market/kline', {
        symbol: TEST_DATA.stocks.maotai,
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/market/stocks', () => {
    test('获取股票列表 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/stocks', {
        market: 'SH',
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        validateRequiredFields(data[0], ['symbol', 'name', 'market']);
      }
    });

    test('分页查询 - 返回分页数据', async () => {
      const response = await client.get('/api/market/stocks', {
        market: 'SH',
        page: 1,
        page_size: 10,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data.length).toBeLessThanOrEqual(10);
    });
  });

  test.describe('GET /api/market/fund-flow', () => {
    test('获取资金流向 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/fund-flow');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        validateRequiredFields(data[0], ['symbol', 'main_inflow', 'net_inflow']);
      }
    });
  });

  test.describe('GET /api/market/etf/list', () => {
    test('获取ETF列表 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/etf/list');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        validateRequiredFields(data[0], ['symbol', 'name', 'price', 'volume']);
      }
    });
  });
});
