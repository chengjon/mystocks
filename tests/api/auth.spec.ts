/**
 * 认证API契约测试
 *
 * 测试范围:
 * - /api/v1/auth/login - 用户登录
 * - /api/v1/auth/logout - 用户登出
 * - /api/v1/auth/me - 获取当前用户信息
 * - /api/v1/auth/refresh - 刷新Token
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

test.describe('认证 API 契约测试', () => {
  let client: APITestClient;

  test.beforeAll(async () => {
    client = new APITestClient();
  });

  test.describe('POST /api/v1/auth/login', () => {
    test('成功登录 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.login(
        TEST_DATA.auth.admin.username,
        TEST_DATA.auth.admin.password
      );

      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.auth);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['token', 'user']);
      validateRequiredFields(data.user, ['id', 'username', 'role']);
      validateFieldType(data, 'token', 'string');
      validateFieldType(data.user, 'id', 'number');
      validateFieldType(data.user, 'username', 'string');
    });

    test('用户名不存在 - 返回401错误', async () => {
      const response = await client.post('/api/v1/auth/login', {
        username: 'nonexistent',
        password: 'wrongpassword',
      });

      expect(response.code).toBe(ERROR_CODES.UNAUTHORIZED);
      expect(response.message).toBeDefined();
    });

    test('密码错误 - 返回401错误', async () => {
      const response = await client.post('/api/v1/auth/login', {
        username: TEST_DATA.auth.admin.username,
        password: 'wrongpassword',
      });

      expect(response.code).toBe(ERROR_CODES.UNAUTHORIZED);
      expect(response.message).toBeDefined();
    });

    test('缺少用户名 - 返回400错误', async () => {
      const response = await client.post('/api/v1/auth/login', {
        password: TEST_DATA.auth.admin.password,
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });

    test('缺少密码 - 返回400错误', async () => {
      const response = await client.post('/api/v1/auth/login', {
        username: TEST_DATA.auth.admin.username,
      });

      expect(response.code).toBe(ERROR_CODES.BAD_REQUEST);
    });
  });

  test.describe('GET /api/v1/auth/me', () => {
    test.beforeEach(async () => {
      await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
    });

    test('获取当前用户信息 - 返回正确的响应结构', async () => {
      const startTime = Date.now();

      const response = await client.get('/api/v1/auth/me');
      const duration = validateResponseTime(startTime, PERFORMANCE_BENCHMARKS.auth);
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['id', 'username', 'role']);
      validateFieldType(data, 'id', 'number');
      validateFieldType(data, 'username', 'string');
    });

    test('未认证 - 返回401错误', async () => {
      client.setToken('');
      const response = await client.get('/api/v1/auth/me');

      expect(response.code).toBe(ERROR_CODES.UNAUTHORIZED);
    });
  });

  test.describe('POST /api/v1/auth/logout', () => {
    test('成功登出 - 返回200状态', async () => {
      await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);

      const response = await client.post('/api/v1/auth/logout');

      expect(response.code).toBe(ERROR_CODES.SUCCESS);
    });
  });

  test.describe('POST /api/v1/auth/refresh', () => {
    test.beforeEach(async () => {
      await client.login(TEST_DATA.auth.admin.username, TEST_DATA.auth.admin.password);
    });

    test('刷新Token - 返回新的token', async () => {
      const response = await client.post('/api/v1/auth/refresh');
      const data = validateAPIResponse(response, ERROR_CODES.SUCCESS);

      validateRequiredFields(data, ['token']);
      validateFieldType(data, 'token', 'string');
    });

    test('未认证 - 返回401错误', async () => {
      client.setToken('');
      const response = await client.post('/api/v1/auth/refresh');

      expect(response.code).toBe(ERROR_CODES.UNAUTHORIZED);
    });
  });
});
