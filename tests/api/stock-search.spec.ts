/**
 * 股票搜索 API 契约测试
 *
 * 测试范围:
 * - /api/stock-search/search - 股票搜索
 * - /api/stock-search/quote/{symbol} - 获取股票行情
 * - /api/stock-search/profile/{symbol} - 获取股票资料
 * - /api/stock-search/news/{symbol} - 获取股票新闻
 * - /api/stock-search/news/market/{category} - 获取市场新闻
 * - /api/stock-search/recommendation/{symbol} - 获取推荐
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

test.describe('股票搜索 API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
    await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
  });

  test.describe('POST /api/stock-search/search', () => {
    test('搜索股票 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.post('/api/stock-search/search', {
        query: '茅台',
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.stock);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        validateRequiredFields(data[0], ['symbol', 'name', 'market']);
        validateFieldType(data[0], 'symbol', 'string');
        validateFieldType(data[0], 'name', 'string');
      }
    });

    test('按股票代码搜索 - 返回精确匹配结果', async () => {
      const response = await client.post('/api/stock-search/search', {
        query: TEST_DATA.stocks.maotai,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        expect(data[0].symbol).toContain(TEST_DATA.stocks.maotai);
      }
    });

    test('缺少query参数 - 返回400错误', async () => {
      const response = await client.post('/api/stock-search/search', {});

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });

    test('query为空字符串 - 返回400错误', async () => {
      const response = await client.post('/api/stock-search/search', {
        query: '',
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/stock-search/quote/{symbol}', () => {
    test('获取股票行情 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get(
        `/api/stock-search/quote/${TEST_DATA.stocks.maotai}`
      );

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.stock);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['symbol', 'name', 'price', 'change', 'changePercent']);
      validateFieldType(data, 'symbol', 'string');
      validateFieldType(data, 'price', 'number');
      validateFieldType(data, 'change', 'number');
      validateFieldType(data, 'changePercent', 'number');
    });

    test('股票不存在 - 返回404错误', async () => {
      const response = await client.get('/api/stock-search/quote/999999');

      expect(response.code).toBe(ERROR_CODES.NOT_FOUND);
    });
  });

  test.describe('GET /api/stock-search/profile/{symbol}', () => {
    test('获取股票资料 - 返回正确的响应结构', async () => {
      const response = await client.get(
        `/api/stock-search/profile/${TEST_DATA.stocks.maotai}`
      );

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['symbol', 'name', 'industry', 'market']);
      validateFieldType(data, 'symbol', 'string');
      validateFieldType(data, 'name', 'string');
      validateFieldType(data, 'industry', 'string');
    });

    test('股票资料包含详细信息', async () => {
      const response = await client.get(
        `/api/stock-search/profile/${TEST_DATA.stocks.maotai}`
      );

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data.symbol).toBeDefined();
      expect(data.name).toBeDefined();
    });
  });

  test.describe('GET /api/stock-search/news/{symbol}', () => {
    test('获取股票新闻 - 返回正确的响应结构', async () => {
      const response = await client.get(
        `/api/stock-search/news/${TEST_DATA.stocks.maotai}`,
        {
          limit: 10,
        }
      );

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;

      if (data.length > 0) {
        validateRequiredFields(data[0], ['title', 'url', 'publish_time']);
        validateFieldType(data[0], 'title', 'string');
        validateFieldType(data[0], 'url', 'string');
      }
    });

    test('分页获取新闻 - 返回分页数据', async () => {
      const response = await client.get(
        `/api/stock-search/news/${TEST_DATA.stocks.maotai}`,
        {
          page: 1,
          page_size: 5,
        }
      );

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data.length).toBeLessThanOrEqual(5);
    });
  });

  test.describe('GET /api/stock-search/news/market/{category}', () => {
    test('获取市场新闻 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/stock-search/news/market/SH', {
        limit: 10,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;

      if (data.length > 0) {
        validateRequiredFields(data[0], ['title', 'url', 'publish_time']);
      }
    });

    test('获取不同市场的新闻 - 返回正确结果', async () => {
      const response = await client.get('/api/stock-search/news/market/SZ', {
        limit: 10,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;
    });
  });

  test.describe('GET /api/stock-search/recommendation/{symbol}', () => {
    test('获取股票推荐 - 返回正确的响应结构', async () => {
      const response = await client.get(
        `/api/stock-search/recommendation/${TEST_DATA.stocks.maotai}`
      );

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['symbol', 'recommendations']);
      expect(Array.isArray(data.recommendations)).toBe(true;

      if (data.recommendations.length > 0) {
        validateRequiredFields(data.recommendations[0], ['type', 'reason', 'confidence']);
        validateFieldType(data.recommendations[0], 'type', 'string');
      }
    });

    test('推荐置信度在0-100之间', async () => {
      const response = await client.get(
        `/api/stock-search/recommendation/${TEST_DATA.stocks.maotai}`
      );

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      if (data.recommendations && data.recommendations.length > 0) {
        for (const rec of data.recommendations) {
          if (rec.confidence !== undefined && rec.confidence !== null) {
            expect(rec.confidence).toBeGreaterThanOrEqual(0);
            expect(rec.confidence).toBeLessThanOrEqual(100);
          }
        }
      }
    });
  });

  test.describe('POST /api/stock-search/cache/clear', () => {
    test('清除搜索缓存 - 返回清除状态', async () => {
      const response = await client.post('/api/stock-search/cache/clear', {
        symbol: TEST_DATA.stocks.maotai,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['cleared_count']);
      validateFieldType(data.cleared_count, 'number');
      expect(data.cleared_count).toBeGreaterThanOrEqual(0);
    });

    test('清除所有缓存 - 返回清除状态', async () => {
      const response = await client.post('/api/stock-search/cache/clear', {
        clear_all: true,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['cleared_count']);
      validateFieldType(data.cleared_count, 'number');
    });
  });
});
