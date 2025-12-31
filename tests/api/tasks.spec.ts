/**
 * Tasks API 契约测试
 *
 * 测试范围:
 * - /api/tasks/register - 注册任务
 * - /api/tasks/{task_id} - 获取任务详情
 * - /api/tasks/ - 获取任务列表
 * - /api/tasks/{task_id}/start - 启动任务
 * - /api/tasks/{task_id}/stop - 停止任务
 * - /api/tasks/executions/ - 获取执行记录
 * - /api/tasks/executions/{execution_id} - 获取执行详情
 * - /api/tasks/statistics/ - 任务统计
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

test.describe('Tasks API 契约测试', () => {
  let client: APITestClient;
  let testTaskId: number;

  test.beforeAll(async () => {
    client = new APITestClient();
    await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
  });

  test.describe('POST /api/tasks/register', () => {
    test('注册任务 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.post('/api/tasks/register', {
        name: '测试任务',
        type: 'data_sync',
        config: {
          symbol: TEST_DATA.stocks.maotai,
          interval: '1d',
        },
        schedule: '0 9 * * 1-5',
      });

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.system);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['task_id', 'name', 'type', 'status']);
      validateFieldType(data, 'task_id', 'number');
      validateFieldType(data, 'name', 'string');
      validateFieldType(data, 'type', 'string');
      validateFieldType(data, 'status', 'string');

      testTaskId = data.task_id;

      const validStatuses = ['pending', 'active', 'paused', 'error'];
      expect(validStatuses).toContain(data.status);
    });

    test('缺少name参数 - 返回400错误', async () => {
      const response = await client.post('/api/tasks/register', {
        type: 'data_sync',
        config: {},
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });

    test('缺少type参数 - 返回400错误', async () => {
      const response = await client.post('/api/tasks/register', {
        name: '测试任务',
        config: {},
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/tasks/{task_id}', () => {
    test('获取任务详情 - 返回正确的响应结构', async () => {
      if (!testTaskId) {
        test.skip();
        return;
      }

      const startTime = Date.now();

      const response = await client.get(`/api/tasks/${testTaskId}`);

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.system);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['task_id', 'name', 'type', 'status', 'config']);
      validateFieldType(data, 'task_id', 'number');
      validateFieldType(data, 'name', 'string');
      validateFieldType(data, 'status', 'string');
    });

    test('任务不存在 - 返回404错误', async () => {
      const response = await client.get('/api/tasks/999999');

      expect(response.code).toBe(ERROR_CODES.NOT_FOUND);
    });
  });

  test.describe('GET /api/tasks/', () => {
    test('获取任务列表 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/tasks/');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.system);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true;

      if (data.length > 0) {
        validateRequiredFields(data[0], ['task_id', 'name', 'type', 'status']);
        validateFieldType(data[0], 'task_id', 'number');
        validateFieldType(data[0], 'name', 'string');
      }
    });

    test('按类型筛选任务 - 返回对应类型的任务', async () => {
      const response = await client.get('/api/tasks/', {
        type: 'data_sync',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;

      if (data.length > 0) {
        for (const task of data) {
          expect(task.type).toBe('data_sync');
        }
      }
    });

    test('按状态筛选任务 - 返回对应状态的任务', async () => {
      const response = await client.get('/api/tasks/', {
        status: 'active',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;
    });

    test('分页获取任务 - 返回分页数据', async () => {
      const response = await client.get('/api/tasks/', {
        page: 1,
        page_size: 10,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(data.length).toBeLessThanOrEqual(10);
    });
  });

  test.describe('POST /api/tasks/{task_id}/start', () => {
    test('启动任务 - 返回正确的响应结构', async () => {
      if (!testTaskId) {
        test.skip();
        return;
      }

      const startTime = Date.now();

      const response = await client.post(`/api/tasks/${testTaskId}/start`);

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.system);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['task_id', 'status', 'message']);
      validateFieldType(data, 'task_id', 'number');
      validateFieldType(data, 'status', 'string');

      const validStatuses = ['active', 'running'];
      expect(validStatuses).toContain(data.status);
    });

    test('启动不存在的任务 - 返回404错误', async () => {
      const response = await client.post('/api/tasks/999999/start');

      expect(response.code).toBe(ERROR_CODES.NOT_FOUND);
    });
  });

  test.describe('POST /api/tasks/{task_id}/stop', () => {
    test('停止任务 - 返回正确的响应结构', async () => {
      if (!testTaskId) {
        test.skip();
        return;
      }

      const startTime = Date.now();

      const response = await client.post(`/api/tasks/${testTaskId}/stop`);

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.system);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['task_id', 'status', 'message']);
      validateFieldType(data, 'task_id', 'number');
      validateFieldType(data, 'status', 'string');
    });

    test('停止不存在的任务 - 返回404错误', async () => {
      const response = await client.post('/api/tasks/999999/stop');

      expect(response.code).toBe(ERROR_CODES.NOT_FOUND);
    });
  });

  test.describe('GET /api/tasks/executions/', () => {
    test('获取执行记录列表 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/tasks/executions/');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.system);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      expect(Array.isArray(data)).toBe(true;

      if (data.length > 0) {
        validateRequiredFields(data[0], ['execution_id', 'task_id', 'status', 'start_time']);
        validateFieldType(data[0], 'execution_id', 'number');
        validateFieldType(data[0], 'task_id', 'number');
      }
    });

    test('按任务ID筛选 - 返回对应任务的执行记录', async () => {
      if (!testTaskId) {
        test.skip();
        return;
      }

      const response = await client.get('/api/tasks/executions/', {
        task_id: testTaskId,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;
    });

    test('按状态筛选 - 返回对应状态的执行记录', async () => {
      const response = await client.get('/api/tasks/executions/', {
        status: 'completed',
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      expect(Array.isArray(data)).toBe(true;
    });
  });

  test.describe('GET /api/tasks/executions/{execution_id}', () => {
    test('获取执行详情 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/tasks/executions/1');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['execution_id', 'task_id', 'status', 'start_time', 'end_time']);
      validateFieldType(data, 'execution_id', 'number');
      validateFieldType(data, 'task_id', 'number');
    });

    test('执行记录不存在 - 返回404错误', async () => {
      const response = await client.get('/api/tasks/executions/999999');

      expect(response.code).toBe(ERROR_CODES.NOT_FOUND);
    });
  });

  test.describe('GET /api/tasks/statistics/', () => {
    test('获取任务统计 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/tasks/statistics/');

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.system);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['total_tasks', 'active_tasks', 'total_executions', 'success_rate']);
      validateFieldType(data.total_tasks, 'number');
      validateFieldType(data.active_tasks, 'number');
      validateFieldType(data.total_executions, 'number');
      validateFieldType(data.success_rate, 'number');

      expect(data.total_tasks).toBeGreaterThanOrEqual(0);
      expect(data.success_rate).toBeGreaterThanOrEqual(0);
      expect(data.success_rate).toBeLessThanOrEqual(1);
    });
  });

  test.describe('POST /api/tasks/import', () => {
    test('导入任务 - 返回正确的响应结构', async () => {
      const response = await client.post('/api/tasks/import', {
        tasks: [
          {
            name: '导入任务1',
            type: 'data_sync',
            config: {},
            schedule: '0 9 * * 1-5',
          },
        ],
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['imported_count', 'tasks']);
      validateFieldType(data.imported_count, 'number');
      expect(Array.isArray(data.tasks)).toBe(true;
    });
  });

  test.describe('POST /api/tasks/export', () => {
    test('导出任务 - 返回正确的响应结构', async () => {
      const response = await client.post('/api/tasks/export', {
        task_ids: [],
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['exported_count', 'tasks']);
      validateFieldType(data.exported_count, 'number');
      expect(Array.isArray(data.tasks)).toBe(true;
    });
  });

  test.describe('POST /api/tasks/executions/cleanup', () => {
    test('清理执行记录 - 返回清理数量', async () => {
      const response = await client.post('/api/tasks/executions/cleanup', {
        days: 30,
      });

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['cleaned_count']);
      validateFieldType(data.cleaned_count, 'number');
      expect(data.cleaned_count).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('GET /api/tasks/health', () => {
    test('任务系统健康检查 - 返回正确的响应结构', async () => {
      const response = await client.get('/api/tasks/health');

      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);
      validateRequiredFields(data, ['status', 'active_tasks', 'scheduler_status']);
      validateFieldType(data, 'status', 'string');
      validateFieldType(data.active_tasks, 'number');
      validateFieldType(data.scheduler_status, 'string');
    });
  });
});
