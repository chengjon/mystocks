/**
 * 策略 API 契约测试
 *
 * 测试范围:
 * - /api/strategy/definitions - 获取策略定义
 * - /api/strategy/run/single - 执行单个策略
 * - /api/strategy/run/batch - 批量执行策略
 * - /api/strategy/results - 获取策略结果
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

test.describe('策略 API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
    await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
  });

  test.describe('GET /api/strategy/definitions', () => {
    test('获取策略定义列表 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/strategy/definitions');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.strategy);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        validateRequiredFields(data[0], ['id', 'name', 'description']);
        validateFieldType(data[0], 'id', 'number');
        validateFieldType(data[0], 'name', 'string');
      }
    });

    test('策略定义包含必要字段', async () => {
      const response = await client.get('/api/strategy/definitions');
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      if (data.length > 0) {
        const strategy = data[0];
        expect(strategy.name).toBeDefined();
        expect(strategy.description).toBeDefined();
        expect(strategy.parameters).toBeDefined();
      }
    });
  });

  test.describe('POST /api/strategy/run/single', () => {
    test('执行单个策略 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.post('/api/strategy/run/single', {
        strategy_id: 1,
        symbol: TEST_DATA.stocks.maotai,
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.strategy);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['strategy_id', 'symbol', 'result']);
      validateFieldType(data, 'strategy_id', 'number');
      validateFieldType(data, 'symbol', 'string');
    });

    test('缺少strategy_id参数 - 返回400错误', async () => {
      const response = await client.post('/api/strategy/run/single', {
        symbol: TEST_DATA.stocks.maotai,
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });

    test('缺少symbol参数 - 返回400错误', async () => {
      const response = await client.post('/api/strategy/run/single', {
        strategy_id: 1,
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('POST /api/strategy/run/batch', () => {
    test('批量执行策略 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.post('/api/strategy/run/batch', {
        strategy_id: 1,
        symbols: [
          TEST_DATA.stocks.maotai,
          TEST_DATA.stocks.pingan,
        ],
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.strategy);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['strategy_id', 'results']);
      validateFieldType(data, 'strategy_id', 'number');
      expect(Array.isArray(data.results)).toBe(true);

      if (data.results.length > 0) {
        validateRequiredFields(data.results[0], ['symbol', 'result']);
      }
    });

    test('批量执行缺少symbols参数 - 返回400错误', async () => {
      const response = await client.post('/api/strategy/run/batch', {
        strategy_id: 1,
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });

    test('批量执行symbols为空数组 - 返回400错误', async () => {
      const response = await client.post('/api/strategy/run/batch', {
        strategy_id: 1,
        symbols: [],
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/strategy/matched-stocks', () => {
    test('获取匹配股票列表 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/strategy/matched-stocks', {
        strategy_id: 1,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['strategy_id', 'stocks']);
      expect(Array.isArray(data.stocks))).toBe(true);

      if (data.stocks.length > 0) {
        validateRequiredFields(data.stocks[0], ['symbol', 'name']);
      }
    });
  });

  test.describe('GET /api/strategy/results', () => {
    test('获取策略执行结果 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/strategy/results', {
        strategy_id: 1,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['strategy_id', 'results']);
      expect(Array.isArray(data.results))).toBe(true);
    });
  });

  test.describe('GET /api/strategy/stats/summary', () => {
    test('获取策略统计摘要 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/strategy/stats/summary');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['total_strategies', 'active_strategies', 'total_executions']);
      validateFieldType(data, 'total_strategies', 'number');
      validateFieldType(data, 'active_strategies', 'number');
      validateFieldType(data, 'total_executions', 'number');

      expect(data.total_strategies).toBeGreaterThanOrEqual(0);
      expect(data.active_strategies).toBeGreaterThanOrEqual(0);
    });
  });
});
