/**
 * 回测 API 契约测试
 *
 * 测试范围:
 * - /api/v1/strategy/backtest/run - 运行回测
 * - /api/v1/strategy/backtest/results - 获取回测结果
 * - /api/v1/strategy/backtest/results/{backtest_id} - 获取特定回测结果
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

test.describe('回测 API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
    await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
  });

  test.describe('POST /api/v1/strategy/backtest/run', () => {
    test('运行回测 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.post('/api/v1/strategy/backtest/run', {
        strategy_id: 1,
        symbol: TEST_DATA.stocks.maotai,
        start_date: '2024-01-01',
        end_date: '2024-12-31',
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.strategy);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['backtest_id', 'status']);
      validateFieldType(data, 'backtest_id', 'number');
      validateFieldType(data, 'status', 'string');

      const validStatuses = ['running', 'completed', 'failed'];
      expect(validStatuses).toContain(data.status);
    });

    test('缺少strategy_id参数 - 返回400错误', async () => {
      const response = await client.post('/api/v1/strategy/backtest/run', {
        symbol: TEST_DATA.stocks.maotai,
        start_date: '2024-01-01',
        end_date: '2024-12-31',
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });

    test('缺少symbol参数 - 返回400错误', async () => {
      const response = await client.post('/api/v1/strategy/backtest/run', {
        strategy_id: 1,
        start_date: '2024-01-01',
        end_date: '2024-12-31',
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });

    test('日期格式错误 - 返回400错误', async () => {
      const response = await client.post('/api/v1/strategy/backtest/run', {
        strategy_id: 1,
        symbol: TEST_DATA.stocks.maotai,
        start_date: '2024/01/01',
        end_date: '2024-12-31',
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/v1/strategy/backtest/results', () => {
    test('获取回测结果列表 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/v1/strategy/backtest/results');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.strategy);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        validateRequiredFields(data[0], ['backtest_id', 'strategy_id', 'symbol']);
        validateFieldType(data[0], 'backtest_id', 'number');
        validateFieldType(data[0], 'strategy_id', 'number');
        validateFieldType(data[0], 'symbol', 'string');
      }
    });

    test('按策略ID筛选 - 返回对应的回测结果', async () => {
      const response = await client.get('/api/v1/strategy/backtest/results', {
        strategy_id: 1,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true);
    });

    test('按股票筛选 - 返回对应的回测结果', async () => {
      const response = await client.get('/api/v1/strategy/backtest/results', {
        symbol: TEST_DATA.stocks.maotai,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true);
    });
  });

  test.describe('GET /api/v1/strategy/backtest/results/{backtest_id}', () => {
    test('获取特定回测结果 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/v1/strategy/backtest/results/1');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['backtest_id', 'strategy_id', 'symbol', 'performance']);
      validateFieldType(data, 'backtest_id', 'number');
      validateFieldType(data, 'symbol', 'string');
      validateFieldType(data, 'performance', 'object');

      if (data.performance) {
        validateRequiredFields(data.performance, ['total_return', 'max_drawdown', 'sharpe_ratio']);
      }
    });

    test('性能指标数值类型正确', async () => {
      const response = await client.get('/api/v1/strategy/backtest/results/1');
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      if (data.performance) {
        const numericFields = ['total_return', 'max_drawdown', 'sharpe_ratio', 'win_rate'];
        for (const field of numericFields) {
          if (data.performance[field] !== undefined) {
            expect(typeof data.performance[field]).toBe('number');
          }
        }
      }
    });

    test('回测结果不存在 - 返回404错误', async () => {
      const response = await client.get('/api/v1/strategy/backtest/results/999999');

      expect(response.code).toBe(ERROR_CODES.NOT_FOUND);
    });
  });

  test.describe('GET /api/v1/strategy/backtest/results/{backtest_id}/chart-data', () => {
    test('获取回测图表数据 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/v1/strategy/backtest/results/1/chart-data');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['backtest_id', 'chart_data']);
      expect(Array.isArray(data.chart_data))).toBe(true);
    });

    test('图表数据包含日期和收益', async () => {
      const response = await client.get('/api/v1/strategy/backtest/results/1/chart-data');
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      if (data.chart_data && data.chart_data.length > 0) {
        validateRequiredFields(data.chart_data[0], ['date', 'equity', 'return']);
      }
    });
  });

  test.describe('GET /api/v1/sse/backtest', () => {
    test('SSE回测进度推送 - 返回流式数据', async ({ request }) => {
      const response = await request.get('/api/v1/sse/backtest', {
        params: {
          backtest_id: 1,
        },
        headers: {
          'Accept': 'text/event-stream',
        },
      });

      expect(response.status()).toBe(200);
      expect(response.headers()['content-type']).toContain('text/event-stream');
    });
  });
});
