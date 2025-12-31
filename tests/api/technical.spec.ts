/**
 * 技术指标 API 契约测试
 *
 * 测试范围:
 * - /api/technical/{symbol}/indicators - 获取技术指标
 * - /api/technical/{symbol}/trend - 获取趋势分析
 * - /api/technical/{symbol}/signals - 获取交易信号
 * - /api/technical/batch/indicators - 批量获取指标
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

test.describe('技术指标 API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
    await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
  });

  const testSymbol = TEST_DATA.stocks.maotai;

  test.describe('GET /api/technical/{symbol}/indicators', () => {
    test('获取技术指标 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get(`/api/technical/${testSymbol}/indicators`);

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.technical);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'indicators']);
      validateFieldType(data, 'symbol', 'string');

      if (data.indicators) {
        const indicatorKeys = Object.keys(data.indicators);
        expect(indicatorKeys.length).toBeGreaterThan(0);
      }
    });

    test('指标数据类型正确 - 返回数值类型', async () => {
      const response = await client.get(`/api/technical/${testSymbol}/indicators`);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      if (data.indicators) {
        for (const [key, value] of Object.entries(data.indicators)) {
          if (value !== null && value !== undefined) {
            expect(typeof value).toBe('number');
          }
        }
      }
    });
  });

  test.describe('GET /api/technical/{symbol}/trend', () => {
    test('获取趋势分析 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get(`/api/technical/${testSymbol}/trend`);

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.technical);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'trend', 'strength']);
      validateFieldType(data, 'symbol', 'string');
      validateFieldType(data, 'trend', 'string');

      const validTrends = ['bullish', 'bearish', 'neutral'];
      expect(validTrends).toContain(data.trend);
    });

    test('趋势强度在0-100之间', async () => {
      const response = await client.get(`/api/technical/${testSymbol}/trend`);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      if (data.strength !== undefined && data.strength !== null) {
        expect(data.strength).toBeGreaterThanOrEqual(0);
        expect(data.strength).toBeLessThanOrEqual(100);
      }
    });
  });

  test.describe('GET /api/technical/{symbol}/signals', () => {
    test('获取交易信号 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get(`/api/technical/${testSymbol}/signals`);

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.technical);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'signals']);
      validateFieldType(data, 'symbol', 'string');
      expect(Array.isArray(data.signals)).toBe(true);

      if (data.signals.length > 0) {
        validateRequiredFields(data.signals[0], ['type', 'direction', 'confidence']);
      }
    });

    test('信号方向类型正确', async () => {
      const response = await client.get(`/api/technical/${testSymbol}/signals`);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      if (data.signals && data.signals.length > 0) {
        const validDirections = ['buy', 'sell', 'hold'];
        for (const signal of data.signals) {
          if (signal.direction) {
            expect(validDirections).toContain(signal.direction);
          }
        }
      }
    });
  });

  test.describe('GET /api/technical/{symbol}/volume', () => {
    test('获取成交量分析 - 返回正确的响应结构', async () => {
      const response = await client.get(`/api/technical/${testSymbol}/volume`);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'volume_analysis']);
      validateFieldType(data, 'symbol', 'string');
    });
  });

  test.describe('GET /api/technical/{symbol}/momentum', () => {
    test('获取动量分析 - 返回正确的响应结构', async () => {
      const response = await client.get(`/api/technical/${testSymbol}/momentum`);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'momentum']);
      validateFieldType(data, 'symbol', 'string');
    });
  });

  test.describe('GET /api/technical/{symbol}/volatility', () => {
    test('获取波动率分析 - 返回正确的响应结构', async () => {
      const response = await client.get(`/api/technical/${testSymbol}/volatility`);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'volatility']);
      validateFieldType(data, 'symbol', 'string');

      if (data.volatility !== undefined && data.volatility !== null) {
        expect(data.volatility).toBeGreaterThan(0);
      }
    });
  });

  test.describe('GET /api/technical/batch/indicators', () => {
    test('批量获取技术指标 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/technical/batch/indicators', {
        symbols: `${TEST_DATA.stocks.maotai},${TEST_DATA.stocks.pingan}`,
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.technical);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        validateRequiredFields(data[0], ['symbol', 'indicators']);
      }
    });

    test('批量请求缺少symbols参数 - 返回400错误', async () => {
      const response = await client.get('/api/technical/batch/indicators');

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/technical/{symbol}/history', () => {
    test('获取历史指标 - 返回正确的响应结构', async () => {
      const response = await client.get(`/api/technical/${testSymbol}/history`);

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['symbol', 'history']);
      validateFieldType(data, 'symbol', 'string');
      expect(Array.isArray(data.history)).toBe(true);
    });
  });

  test.describe('GET /api/technical/patterns/{symbol}', () => {
    test('获取K线形态 - 返回正确的响应结构', async () => {
      const response = await client.get(`/api/technical/patterns/${testSymbol}`);

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['symbol', 'patterns']);
      validateFieldType(data, 'symbol', 'string');
      expect(Array.isArray(data.patterns)).toBe(true);
    });
  });
});
