/**
 * 问财 API 契约测试
 *
 * 测试范围:
 * - /api/market/wencai/query - 执行问财查询
 * - /api/market/wencai/queries - 获取查询列表
 * - /api/market/wencai/results/{query_name} - 获取查询结果
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

test.describe('问财 API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
    await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
  });

  test.describe('POST /api/market/wencai/query', () => {
    test('执行问财查询 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.post('/api/market/wencai/query', {
        query: '强势股票',
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.wencai);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['query', 'results']);
      validateFieldType(data, 'query', 'string');
      expect(Array.isArray(data.results)).toBe(true);

      if (data.results.length > 0) {
        validateRequiredFields(data.results[0], ['symbol', 'name']);
      }
    });

    test('查询涨停板股票 - 返回正确的结果', async () => {
      const response = await client.post('/api/market/wencai/query', {
        query: '涨停板股票',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data.results).toBeDefined();
    });

    test('缺少query参数 - 返回400错误', async () => {
      const response = await client.post('/api/market/wencai/query', {});

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });

    test('query为空字符串 - 返回400错误', async () => {
      const response = await client.post('/api/market/wencai/query', {
        query: '',
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/market/wencai/queries', () => {
    test('获取查询列表 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/wencai/queries');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.wencai);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        validateRequiredFields(data[0], ['name', 'query']);
      }
    });
  });

  test.describe('GET /api/market/wencai/queries/{query_name}', () => {
    test('获取特定查询 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/market/wencai/queries/强势股票');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['name', 'query']);
      validateFieldType(data, 'name', 'string');
    });

    test('查询不存在的查询 - 返回404错误', async () => {
      const response = await client.get('/api/market/wencai/queries/不存在的查询');

      expect(response.code).toBe(ERROR_CODES.NOT_FOUND);
    });
  });

  test.describe('GET /api/market/wencai/results/{query_name}', () => {
    test('获取查询结果 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/market/wencai/results/强势股票');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['query_name', 'results']);
      validateFieldType(data, 'query_name', 'string');
      expect(Array.isArray(data.results)).toBe(true);
    });

    test('结果包含股票信息', async () => {
      const response = await client.get('/api/market/wencai/results/强势股票');
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      if (data.results.length > 0) {
        validateRequiredFields(data.results[0], ['symbol', 'name']);
      }
    });
  });

  test.describe('GET /api/market/wencai/history/{query_name}', () => {
    test('获取查询历史 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/market/wencai/history/强势股票');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['query_name', 'history']);
      validateFieldType(data, 'query_name', 'string');
      expect(Array.isArray(data.history)).toBe(true);
    });
  });

  test.describe('POST /api/market/wencai/custom-query', () => {
    test('执行自定义查询 - 返回正确的响应结构', async () => {
      const response = await client.post('/api/market/wencai/custom-query', {
        query: 'MA5 > MA10',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['query', 'results']);
      validateFieldType(data, 'query', 'string');
      expect(Array.isArray(data.results)).toBe(true);
    });

    test('复杂查询条件 - 返回正确结果', async () => {
      const response = await client.post('/api/market/wencai/custom-query', {
        query: 'MA5 > MA10 AND 成交量 > 1000000',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data.results).toBeDefined();
    });
  });

  test.describe('POST /api/market/wencai/refresh/{query_name}', () => {
    test('刷新查询结果 - 返回刷新状态', async () => {
      const response = await client.post('/api/market/wencai/refresh/强势股票');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['query_name', 'status']);
      validateFieldType(data, 'query_name', 'string');
      validateFieldType(data, 'status', 'string');

      const validStatuses = ['success', 'error', 'processing'];
      expect(validStatuses).toContain(data.status);
    });
  });

  test.describe('GET /api/market/wencai/health', () => {
    test('检查问财服务健康状态 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/wencai/health');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.wencai);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['status', 'last_update']);
      validateFieldType(data, 'status', 'string');

      const validStatuses = ['healthy', 'unhealthy', 'error'];
      expect(validStatuses).toContain(data.status);
    });
  });
});
