/**
 * 数据 API 契约测试
 *
 * 测试范围:
 * - /api/data/stocks/basic - 股票基本信息
 * - /api/data/stocks/daily - 日线数据
 * - /api/data/markets/overview - 市场概览
 * - /api/data/stocks/search - 股票搜索
 * - /api/data/kline - K线数据
 * - /api/data/financial - 财务数据
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

test.describe('数据 API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
    await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
  });

  test.describe('GET /api/data/stocks/basic', () => {
    test('获取股票基本信息 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/data/stocks/basic', {
        symbol: TEST_DATA.stocks.maotai,
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.stock);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'name', 'industry', 'market']);
      validateFieldType(data, 'symbol', 'string');
      validateFieldType(data, 'name', 'string');
      validateFieldType(data, 'industry', 'string');
    });

    test('缺少symbol参数 - 返回400错误', async () => {
      const response = await client.get('/api/data/stocks/basic');

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/data/stocks/daily', () => {
    test('获取日线数据 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/data/stocks/daily', {
        symbol: TEST_DATA.stocks.maotai,
        start_date: '2024-01-01',
        end_date: '2024-12-31',
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.stock);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'data']);
      validateFieldType(data, 'symbol', 'string');
      expect(Array.isArray(data.data)).toBe(true;

      if (data.data.length > 0) {
        validateRequiredFields(data.data[0], ['date', 'open', 'high', 'low', 'close', 'volume']);
      }
    });

    test('日线数据数值类型正确', async () => {
      const response = await client.get('/api/data/stocks/daily', {
        symbol: TEST_DATA.stocks.maotai,
        start_date: '2024-01-01',
        end_date: '2024-12-31',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      if (data.data && data.data.length > 0) {
        const record = data.data[0];
        expect(typeof record.open).toBe('number');
        expect(typeof record.high).toBe('number');
        expect(typeof record.low).toBe('number');
        expect(typeof record.close).toBe('number');
        expect(typeof record.volume).toBe('number');
      }
    });
  });

  test.describe('GET /api/data/markets/overview', () => {
    test('获取市场概览 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/data/markets/overview');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['markets', 'timestamp']);
      validateFieldType(data.timestamp, 'number');
      expect(Array.isArray(data.markets)).toBe(true;

      if (data.markets.length > 0) {
        validateRequiredFields(data.markets[0], ['name', 'index', 'change']);
      }
    });

    test('市场概览包含主要指数', async () => {
      const response = await client.get('/api/data/markets/overview');
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      if (data.markets && data.markets.length > 0) {
        const marketNames = data.markets.map(m => m.name);
        expect(marketNames.length).toBeGreaterThan(0);
      }
    });
  });

  test.describe('GET /api/data/stocks/search', () => {
    test('搜索股票 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/data/stocks/search', {
        keyword: '茅台',
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.stock);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true;

      if (data.length > 0) {
        validateRequiredFields(data[0], ['symbol', 'name', 'market']);
        validateFieldType(data[0], 'symbol', 'string');
        validateFieldType(data[0], 'name', 'string');
      }
    });

    test('搜索结果包含茅台', async () => {
      const response = await client.get('/api/data/stocks/search', {
        keyword: '茅台',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;
    });

    test('缺少keyword参数 - 返回400错误', async () => {
      const response = await client.get('/api/data/stocks/search');

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/data/kline', () => {
    test('获取K线数据 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/data/kline', {
        symbol: TEST_DATA.stocks.maotai,
        interval: '1d',
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'interval', 'klines']);
      validateFieldType(data, 'symbol', 'string');
      validateFieldType(data, 'interval', 'string');
      expect(Array.isArray(data.klines)).toBe(true;

      if (data.klines.length > 0) {
        validateRequiredFields(data.klines[0], ['timestamp', 'open', 'high', 'low', 'close', 'volume']);
      }
    });

    test('指定时间范围 - 返回指定范围的数据', async () => {
      const response = await client.get('/api/data/kline', {
        symbol: TEST_DATA.stocks.maotai,
        interval: '1d',
        start_date: '2024-01-01',
        end_date: '2024-12-31',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data.klines).toBeDefined();
    });

    test('缺少symbol参数 - 返回400错误', async () => {
      const response = await client.get('/api/data/kline', {
        interval: '1d',
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });

    test('缺少interval参数 - 返回400错误', async () => {
      const response = await client.get('/api/data/kline', {
        symbol: TEST_DATA.stocks.maotai,
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/data/financial', () => {
    test('获取财务数据 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/data/financial', {
        symbol: TEST_DATA.stocks.maotai,
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.stock);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'reports']);
      validateFieldType(data, 'symbol', 'string');
      expect(Array.isArray(data.reports)).toBe(true;

      if (data.reports.length > 0) {
        validateRequiredFields(data.reports[0], ['report_date', 'report_type', 'data']);
      }
    });

    test('财务数据包含报告类型', async () => {
      const response = await client.get('/api/data/financial', {
        symbol: TEST_DATA.stocks.maotai,
        report_type: 'quarterly',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data.reports).toBeDefined();
    });

    test('缺少symbol参数 - 返回400错误', async () => {
      const response = await client.get('/api/data/financial');

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });
});
