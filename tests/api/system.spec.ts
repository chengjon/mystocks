/**
 * 系统 API 契约测试
 *
 * 测试范围:
 * - /api/system/health - 系统健康检查
 * - /api/system/datasources - 数据源列表
 * - /api/system/database/health - 数据库健康检查
 * - /api/system/logs - 系统日志
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

test.describe('系统 API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
    await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
  });

  test.describe('GET /api/system/health', () => {
    test('系统健康检查 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/system/health');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.system);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['status', 'timestamp']);
      validateFieldType(data, 'status', 'string');

      const validStatuses = ['healthy', 'degraded', 'unhealthy'];
      expect(validStatuses).toContain(data.status);
    });

    test('健康检查响应时间 < 500ms', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/system/health');
      const duration = Date.now() - startTime;

      validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(duration).toBeLessThan(500);
    });
  });

  test.describe('GET /api/system/architecture', () => {
    test('获取系统架构信息 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/system/architecture');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['version', 'components']);
      validateFieldType(data, 'version', 'string');
      expect(Array.isArray(data.components))).toBe(true);

      if (data.components.length > 0) {
        validateRequiredFields(data.components[0], ['name', 'status']);
      }
    });
  });

  test.describe('GET /api/system/datasources', () => {
    test('获取数据源列表 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/system/datasources');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.system);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        validateRequiredFields(data[0], ['name', 'type', 'status']);
        validateFieldType(data[0], 'name', 'string');
        validateFieldType(data[0], 'type', 'string');
        validateFieldType(data[0], 'status', 'string');
      }
    });
  });

  test.describe('POST /api/system/test-connection', () => {
    test('测试数据源连接 - 返回正确的响应结构', async () => {
      const response = await client.post('/api/system/test-connection', {
        datasource: 'tdx',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['datasource', 'status']);
      validateFieldType(data, 'datasource', 'string');
      validateFieldType(data, 'status', 'string');

      const validStatuses = ['connected', 'disconnected', 'error'];
      expect(validStatuses).toContain(data.status);
    });

    test('缺少datasource参数 - 返回400错误', async () => {
      const response = await client.post('/api/system/test-connection', {});

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/system/database/health', () => {
    test('数据库健康检查 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/system/database/health');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.system);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['postgresql', 'tdengine']);
      validateFieldType(data.postgresql, 'object');
      validateFieldType(data.tdengine, 'object');

      if (data.postgresql) {
        validateRequiredFields(data.postgresql, ['status', 'latency']);
      }

      if (data.tdengine) {
        validateRequiredFields(data.tdengine, ['status', 'latency']);
      }
    });
  });

  test.describe('GET /api/system/database/stats', () => {
    test('获取数据库统计信息 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/system/database/stats');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['postgresql', 'tdengine']);
      validateFieldType(data.postgresql, 'object');
      validateFieldType(data.tdengine, 'object');

      if (data.postgresql) {
        const numericFields = ['connections', 'queries', 'latency'];
        for (const field of numericFields) {
          if (data.postgresql[field] !== undefined) {
            expect(typeof data.postgresql[field]).toBe('number');
          }
        }
      }

      if (data.tdengine) {
        const numericFields = ['connections', 'queries', 'latency'];
        for (const field of numericFields) {
          if (data.tdengine[field] !== undefined) {
            expect(typeof data.tdengine[field]).toBe('number');
          }
        }
      }
    });
  });

  test.describe('GET /api/system/logs', () => {
    test('获取系统日志 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/system/logs', {
        limit: 50,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        validateRequiredFields(data[0], ['timestamp', 'level', 'message']);
        validateFieldType(data[0], 'timestamp', 'string');
        validateFieldType(data[0], 'level', 'string');
        validateFieldType(data[0], 'message', 'string');

        const validLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];
        expect(validLevels).toContain(data[0].level);
      }
    });

    test('按日志级别筛选 - 返回对应级别的日志', async () => {
      const response = await client.get('/api/system/logs', {
        level: 'ERROR',
        limit: 10,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true);

      if (data.length > 0) {
        expect(data[0].level).toBe('ERROR');
      }
    });
  });

  test.describe('GET /api/system/logs/summary', () => {
    test('获取日志摘要 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/system/logs/summary');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['total', 'by_level', 'recent_errors']);
      validateFieldType(data.total, 'number');
      validateFieldType(data.by_level, 'object');
      validateFieldType(data.recent_errors, 'number');
    });
  });

  test.describe('GET /api/metrics', () => {
    test('获取系统指标 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/metrics');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['system', 'performance', 'database']);
      validateFieldType(data.system, 'object');
      validateFieldType(data.performance, 'object');
      validateFieldType(data.database, 'object');
    });
  });

  test.describe('GET /api/pool-monitoring/health', () => {
    test('连接池健康检查 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/pool-monitoring/health');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['postgresql', 'tdengine']);
      validateFieldType(data.postgresql, 'object');
      validateFieldType(data.tdengine, 'object');
    });
  });

  test.describe('GET /api/pool-monitoring/postgresql/stats', () => {
    test('获取PostgreSQL连接池统计 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/pool-monitoring/postgresql/stats');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['total_connections', 'active_connections', 'idle_connections']);
      validateFieldType(data.total_connections, 'number');
      validateFieldType(data.active_connections, 'number');
      validateFieldType(data.idle_connections, 'number');

      expect(data.total_connections).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('GET /api/pool-monitoring/tdengine/stats', () => {
    test('获取TDengine连接池统计 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/pool-monitoring/tdengine/stats');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['total_connections', 'active_connections', 'idle_connections']);
      validateFieldType(data.total_connections, 'number');
      validateFieldType(data.active_connections, 'number');
      validateFieldType(data.idle_connections, 'number');

      expect(data.total_connections).toBeGreaterThanOrEqual(0);
    });
  });
});
