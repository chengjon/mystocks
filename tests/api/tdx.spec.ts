/**
 * TDX API 契约测试
 *
 * 测试范围:
 * - /api/tdx/quote/{symbol} - TDX实时行情
 * - /api/tdx/kline - TDX K线数据
 * - /api/tdx/index/quote/{symbol} - 指数行情
 * - /api/tdx/index/kline - 指数K线
 * - /api/tdx/health - TDX服务健康检查
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

test.describe('TDX API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
    await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
  });

  test.describe('GET /api/tdx/quote/{symbol}', () => {
    test('获取TDX实时行情 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get(
        `/api/tdx/quote/${TEST_DATA.stocks.maotai}`
      );

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'name', 'price', 'change', 'volume']);
      validateFieldType(data, 'symbol', 'string');
      validateFieldType(data, 'price', 'number');
      validateFieldType(data, 'volume', 'number');
    });

    test('股票不存在 - 返回404错误', async () => {
      const response = await client.get('/api/tdx/quote/999999');

      expect(response.code).toBe(ERROR_CODES.NOT_FOUND);
    });
  });

  test.describe('GET /api/tdx/kline', () => {
    test('获取TDX K线数据 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/tdx/kline', {
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
      const response = await client.get('/api/tdx/kline', {
        symbol: TEST_DATA.stocks.maotai,
        interval: '1d',
        start_date: '2024-01-01',
        end_date: '2024-12-31',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data.klines).toBeDefined();
    });

    test('缺少symbol参数 - 返回400错误', async () => {
      const response = await client.get('/api/tdx/kline', {
        interval: '1d',
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });

    test('缺少interval参数 - 返回400错误', async () => {
      const response = await client.get('/api/tdx/kline', {
        symbol: TEST_DATA.stocks.maotai,
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/tdx/index/quote/{symbol}', () => {
    test('获取指数实时行情 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/tdx/index/quote/000001.SH');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'name', 'value', 'change', 'changePercent']);
      validateFieldType(data, 'symbol', 'string');
      validateFieldType(data, 'value', 'number');
      validateFieldType(data, 'change', 'number');
    });

    test('指数不存在 - 返回404错误', async () => {
      const response = await client.get('/api/tdx/index/quote/999999.SH');

      expect(response.code).toBe(ERROR_CODES.NOT_FOUND);
    });
  });

  test.describe('GET /api/tdx/index/kline', () => {
    test('获取指数K线数据 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/tdx/index/kline', {
        symbol: '000001.SH',
        interval: '1d',
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'interval', 'klines']);
      validateFieldType(data, 'symbol', 'string');
      expect(Array.isArray(data.klines)).toBe(true;

      if (data.klines.length > 0) {
        validateRequiredFields(data.klines[0], ['timestamp', 'open', 'high', 'low', 'close', 'volume']);
      }
    });

    test('指数K线数据类型正确', async () => {
      const response = await client.get('/api/tdx/index/kline', {
        symbol: '000001.SH',
        interval: '1d',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      if (data.klines && data.klines.length > 0) {
        const kline = data.klines[0];
        expect(typeof kline.open).toBe('number');
        expect(typeof kline.high).toBe('number');
        expect(typeof kline.low).toBe('number');
        expect(typeof kline.close).toBe('number');
        expect(typeof kline.volume).toBe('number');
      }
    });
  });

  test.describe('GET /api/tdx/health', () => {
    test('TDX服务健康检查 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/tdx/health');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.system);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['status', 'connections', 'last_update']);
      validateFieldType(data, 'status', 'string');
      validateFieldType(data, 'connections', 'number');

      const validStatuses = ['connected', 'disconnected', 'error'];
      expect(validStatuses).toContain(data.status);
    });

    test('健康检查响应时间 < 500ms', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/tdx/health');
      const duration = Date.now() - startTime;

      validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(duration).toBeLessThan(500);
    });
  });
});
