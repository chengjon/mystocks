/**
 * Market V2 API 契约测试
 *
 * 测试范围:
 * - /api/market/v2/fund-flow - 资金流向V2
 * - /api/market/v2/etf/list - ETF列表V2
 * - /api/market/v2/lhb - 龙虎榜V2
 * - /api/market/v2/sector/fund-flow - 板块资金流向V2
 * - /api/market/v2/dividend - 分红信息V2
 * - /api/market/v2/blocktrade - 大宗交易V2
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

test.describe('Market V2 API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
    await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
  });

  test.describe('GET /api/market/v2/fund-flow', () => {
    test('获取资金流向 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/v2/fund-flow');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['timestamp', 'fund_flows']);
      validateFieldType(data.timestamp, 'number');
      expect(Array.isArray(data.fund_flows)).toBe(true;

      if (data.fund_flows.length > 0) {
        validateRequiredFields(data.fund_flows[0], ['symbol', 'main_inflow', 'net_inflow']);
      }
    });
  });

  test.describe('POST /api/market/v2/fund-flow/refresh', () => {
    test('刷新资金流向数据 - 返回刷新状态', async () => {
      const response = await client.post('/api/market/v2/fund-flow/refresh');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['status', 'timestamp']);
      validateFieldType(data, 'status', 'string');

      const validStatuses = ['success', 'error', 'processing'];
      expect(validStatuses).toContain(data.status);
    });
  });

  test.describe('GET /api/market/v2/etf/list', () => {
    test('获取ETF列表 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/v2/etf/list');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true;

      if (data.length > 0) {
        validateRequiredFields(data[0], ['symbol', 'name', 'price', 'volume']);
        validateFieldType(data[0], 'symbol', 'string');
        validateFieldType(data[0], 'price', 'number');
      }
    });

    test('按市场筛选ETF - 返回对应市场的ETF', async () => {
      const response = await client.get('/api/market/v2/etf/list', {
        market: 'SH',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;
    });
  });

  test.describe('POST /api/market/v2/etf/refresh', () => {
    test('刷新ETF数据 - 返回刷新状态', async () => {
      const response = await client.post('/api/market/v2/etf/refresh');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['status', 'updated_count']);
      validateFieldType(data, 'status', 'string');
      validateFieldType(data, 'updated_count', 'number');
    });
  });

  test.describe('GET /api/market/v2/lhb', () => {
    test('获取龙虎榜 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/v2/lhb');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true;

      if (data.length > 0) {
        validateRequiredFields(data[0], ['symbol', 'name', 'date', 'reason']);
        validateFieldType(data[0], 'symbol', 'string');
        validateFieldType(data[0], 'name', 'string');
      }
    });

    test('按日期筛选 - 返回指定日期的龙虎榜', async () => {
      const response = await client.get('/api/market/v2/lhb', {
        date: '2024-12-30',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;
    });

    test('按市场筛选 - 返回对应市场的龙虎榜', async () => {
      const response = await client.get('/api/market/v2/lhb', {
        market: 'SH',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;
    });
  });

  test.describe('POST /api/market/v2/lhb/refresh', () => {
    test('刷新龙虎榜数据 - 返回刷新状态', async () => {
      const response = await client.post('/api/market/v2/lhb/refresh');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['status', 'updated_count']);
      validateFieldType(data, 'status', 'string');
    });
  });

  test.describe('GET /api/market/v2/sector/fund-flow', () => {
    test('获取板块资金流向 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/v2/sector/fund-flow');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['timestamp', 'sectors']);
      validateFieldType(data.timestamp, 'number');
      expect(Array.isArray(data.sectors)).toBe(true;

      if (data.sectors.length > 0) {
        validateRequiredFields(data.sectors[0], ['name', 'net_inflow', 'change_percent']);
      }
    });

    test('板块数据数值类型正确', async () => {
      const response = await client.get('/api/market/v2/sector/fund-flow');
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      if (data.sectors && data.sectors.length > 0) {
        const sector = data.sectors[0];
        expect(typeof sector.net_inflow).toBe('number');
        expect(typeof sector.change_percent).toBe('number');
      }
    });
  });

  test.describe('POST /api/market/v2/sector/fund-flow/refresh', () => {
    test('刷新板块资金流向 - 返回刷新状态', async () => {
      const response = await client.post('/api/market/v2/sector/fund-flow/refresh');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['status', 'timestamp']);
      validateFieldType(data, 'status', 'string');
    });
  });

  test.describe('GET /api/market/v2/dividend', () => {
    test('获取分红信息 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/v2/dividend');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true;

      if (data.length > 0) {
        validateRequiredFields(data[0], ['symbol', 'name', 'dividend_date', 'amount']);
        validateFieldType(data[0], 'symbol', 'string');
      }
    });

    test('按日期筛选 - 返回指定日期的分红信息', async () => {
      const response = await client.get('/api/market/v2/dividend', {
        start_date: '2024-01-01',
        end_date: '2024-12-31',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;
    });
  });

  test.describe('POST /api/market/v2/dividend/refresh', () => {
    test('刷新分红信息 - 返回刷新状态', async () => {
      const response = await client.post('/api/market/v2/dividend/refresh');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['status', 'updated_count']);
      validateFieldType(data, 'status', 'string');
    });
  });

  test.describe('GET /api/market/v2/blocktrade', () => {
    test('获取大宗交易 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/market/v2/blocktrade');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.market);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true;

      if (data.length > 0) {
        validateRequiredFields(data[0], ['symbol', 'name', 'price', 'volume', 'amount']);
        validateFieldType(data[0], 'symbol', 'string');
        validateFieldType(data[0], 'price', 'number');
      }
    });

    test('按日期筛选 - 返回指定日期的大宗交易', async () => {
      const response = await client.get('/api/market/v2/blocktrade', {
        date: '2024-12-30',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;
    });
  });

  test.describe('POST /api/market/v2/blocktrade/refresh', () => {
    test('刷新大宗交易数据 - 返回刷新状态', async () => {
      const response = await client.post('/api/market/v2/blocktrade/refresh');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['status', 'updated_count']);
      validateFieldType(data, 'status', 'string');
    });
  });

  test.describe('POST /api/market/v2/refresh-all', () => {
    test('刷新所有市场数据V2 - 返回刷新状态', async () => {
      const response = await client.post('/api/market/v2/refresh-all');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['status', 'refreshed_modules']);
      validateFieldType(data, 'status', 'string');
      expect(Array.isArray(data.refreshed_modules)).toBe(true;
    });
  });
});
