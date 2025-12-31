/**
 * 缓存 API 契约测试
 *
 * 测试范围:
 * - /api/cache/status - 获取缓存状态
 * - /api/cache/{symbol}/{data_type} - 获取缓存数据
 * - /api/cache/eviction/stats - 获取缓存淘汰统计
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

test.describe('缓存 API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
    await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
  });

  test.describe('GET /api/cache/status', () => {
    test('获取缓存状态 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/cache/status');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['total_keys', 'memory_usage', 'cache_size']);
      validateFieldType(data.total_keys, 'number');
      validateFieldType(data.memory_usage, 'number');
      validateFieldType(data.cache_size, 'number');

      expect(data.total_keys).toBeGreaterThanOrEqual(0);
      expect(data.memory_usage).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('GET /api/cache/{symbol}/{data_type}', () => {
    test('获取股票K线缓存 - 返回正确的响应结构', async () => {
      const response = await client.get(
        `/api/cache/${TEST_DATA.stocks.maotai}/kline`,
        {
          interval: '1d',
        }
      );

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['symbol', 'data_type', 'data', 'cached']);
      validateFieldType(data.symbol, 'string');
      validateFieldType(data.data_type, 'string');
      validateFieldType(data.cached, 'boolean');
    });

    test('获取股票基本信息缓存 - 返回正确的响应结构', async () => {
      const response = await client.get(
        `/api/cache/${TEST_DATA.stocks.maotai}/basic`
      );

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['symbol', 'data_type', 'data', 'cached']);
      validateFieldType(data.symbol, 'string');
    });

    test('股票不存在 - 返回404错误', async () => {
      const response = await client.get(
        `/api/cache/999999/stock_basic`
      );

      expect(response.code).toBe(ERROR_CODES.NOT_FOUND);
    });
  });

  test.describe('GET /api/cache/{symbol}', () => {
    test('获取股票所有缓存 - 返回正确的响应结构', async () => {
      const response = await client.get(`/api/cache/${TEST_DATA.stocks.maotai}`);

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['symbol', 'cache_keys']);
      validateFieldType(data.symbol, 'string');
      expect(Array.isArray(data.cache_keys))).toBe(true);
    });
  });

  test.describe('GET /api/cache/{symbol}/{data_type}/fresh', () => {
    test('获取或刷新缓存数据 - 返回正确的响应结构', async () => {
      const response = await client.get(
        `/api/cache/${TEST_DATA.stocks.maotai}/kline/fresh`,
        {
          interval: '1d',
        }
      );

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['symbol', 'data_type', 'data']);
      validateFieldType(data.symbol, 'string');
      validateFieldType(data.data_type, 'string');
    });
  });

  test.describe('GET /api/cache', () => {
    test('获取所有缓存键 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/cache');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['total', 'keys']);
      validateFieldType(data.total, 'number');
      expect(Array.isArray(data.keys))).toBe(true);
    });

    test('分页获取缓存键 - 返回分页数据', async () => {
      const response = await client.get('/api/cache', {
        page: 1,
        page_size: 10,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['total', 'keys', 'page', 'page_size']);
      validateFieldType(data.total, 'number');
      validateFieldType(data.page, 'number');
      validateFieldType(data.page_size, 'number');

      expect(data.keys.length).toBeLessThanOrEqual(data.page_size);
    });
  });

  test.describe('POST /api/cache/evict/manual', () => {
    test('手动淘汰缓存 - 返回正确的响应结构', async () => {
      const response = await client.post('/api/cache/evict/manual', {
        symbol: TEST_DATA.stocks.maotai,
        data_type: 'kline',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['evicted_keys']);
      expect(Array.isArray(data.evicted_keys))).toBe(true);
    });

    test('淘汰所有缓存 - 返回淘汰数量', async () => {
      const response = await client.post('/api/cache/evict/manual', {
        evict_all: true,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['evicted_count']);
      validateFieldType(data.evicted_count, 'number');
      expect(data.evicted_count).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('GET /api/cache/eviction/stats', () => {
    test('获取缓存淘汰统计 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/cache/eviction/stats');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['total_evictions', 'policy', 'efficiency']);
      validateFieldType(data.total_evictions, 'number');
      validateFieldType(data.policy, 'string');

      const validPolicies = ['lru', 'lfu', 'ttl'];
      if (data.policy) {
        expect(validPolicies).toContain(data.policy);
      }
    });
  });

  test.describe('POST /api/cache/prewarming/trigger', () => {
    test('触发缓存预热 - 返回正确的响应结构', async () => {
      const response = await client.post('/api/cache/prewarming/trigger', {
        symbols: [
          TEST_DATA.stocks.maotai,
          TEST_DATA.stocks.pingan,
        ],
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['task_id', 'status']);
      validateFieldType(data.task_id, 'string');
      validateFieldType(data.status, 'string');

      const validStatuses = ['triggered', 'running', 'completed', 'failed'];
      expect(validStatuses).toContain(data.status);
    });

    test('缺少symbols参数 - 返回400错误', async () => {
      const response = await client.post('/api/cache/prewarming/trigger', {});

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/cache/prewarming/status', () => {
    test('获取缓存预热状态 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/cache/prewarming/status');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['status', 'progress', 'total_symbols']);
      validateFieldType(data.status, 'string');
      validateFieldType(data.progress, 'number');
      validateFieldType(data.total_symbols, 'number');

      expect(data.progress).toBeGreaterThanOrEqual(0);
      expect(data.progress).toBeLessThanOrEqual(100);
    });
  });

  test.describe('GET /api/cache/monitoring/metrics', () => {
    test('获取缓存监控指标 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/cache/monitoring/metrics');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['hits', 'misses', 'hit_rate', 'avg_latency']);
      validateFieldType(data.hits, 'number');
      validateFieldType(data.misses, 'number');
      validateFieldType(data.hit_rate, 'number');
      validateFieldType(data.avg_latency, 'number');

      expect(data.hit_rate).toBeGreaterThanOrEqual(0);
      expect(data.hit_rate).toBeLessThanOrEqual(1);
      expect(data.avg_latency).toBeGreaterThan(0);
    });
  });

  test.describe('GET /api/cache/monitoring/health', () => {
    test('缓存健康检查 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/cache/monitoring/health');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['status', 'memory_usage', 'disk_usage']);
      validateFieldType(data.status, 'string');

      const validStatuses = ['healthy', 'warning', 'critical'];
      expect(validStatuses).toContain(data.status);
    });
  });
});
