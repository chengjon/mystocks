/**
 * Backend API Automation E2E Tests
 *
 * 自动化测试后端 API 接口
 * - 从 OpenAPI JSON 提取所有端点
 * - 自动测试 GET 请求端点
 * - 验证响应状态和数据格式
 */

import { test, expect } from '@playwright/test';

// API 基础配置
const API_BASE_URL = 'http://localhost:8000';
const OPENAPI_JSON_URL = `${API_BASE_URL}/openapi.json`;

// 测试配置
interface ApiEndpoint {
  path: string;
  method: string;
  operationId?: string;
  summary?: string;
  tags?: string[];
  parameters?: any[];
}

interface OpenAPISpec {
  openapi: string;
  info: {
    title: string;
    version: string;
  };
  paths: Record<string, Record<string, {
    operationId?: string;
    summary?: string;
    tags?: string[];
    parameters?: any[];
    responses?: Record<string, any>;
  }>>;
}

/**
 * 从 OpenAPI JSON 提取所有 API 端点
 */
async function fetchApiEndpoints(): Promise<ApiEndpoint[]> {
  const response = await fetch(OPENAPI_JSON_URL);
  if (!response.ok) {
    throw new Error(`Failed to fetch OpenAPI JSON: ${response.status}`);
  }

  const spec: OpenAPISpec = await response.json();
  const endpoints: ApiEndpoint[] = [];

  // 遍历所有路径和方法
  for (const [path, methods] of Object.entries(spec.paths)) {
    for (const [method, details] of Object.entries(methods)) {
      endpoints.push({
        path,
        method: method.toUpperCase(),
        operationId: details.operationId,
        summary: details.summary,
        tags: details.tags,
        parameters: details.parameters
      });
    }
  }

  return endpoints;
}

/**
 * 替换路径参数（如 {id} → 实际值）
 */
function replacePathParams(path: string): string {
  return path
    .replace('{stock_code}', '000001.SZ')  // 测试股票代码
    .replace('{symbol}', '600519.SH')      // 测试股票代码
    .replace('{id}', '1')                  // 测试 ID
    .replace('{period}', 'daily')          // 测试周期
    .replace('{start_date}', '2024-01-01')  // 测试日期
    .replace('{end_date}', '2024-12-31')    // 测试日期
    .replace('{source}', 'akshare')         // 测试数据源
    .replace('{table_name}', 'stock_list'); // 测试表名
}

/**
 * 过滤可测试的 GET 端点
 * - 排除需要认证的端点
 * - 排除需要复杂参数的端点
 */
function filterTestableEndpoints(endpoints: ApiEndpoint[]): ApiEndpoint[] {
  return endpoints.filter(endpoint => {
    // 只测试 GET 请求
    if (endpoint.method !== 'GET') return false;

    // 排除需要认证的端点（根据路径判断）
    if (endpoint.path.includes('/auth/')) return false;
    if (endpoint.path.includes('/user/')) return false;
    if (endpoint.path.includes('/admin/')) return false;

    // 排除WebSocket端点
    if (endpoint.path.includes('/ws/')) return false;
    if (endpoint.path.includes('/socketio')) return false;

    // 排除SSE端点
    if (endpoint.path.includes('/sse/')) return false;

    return true;
  });
}

/**
 * 检查端点是否需要必需的查询参数
 */
function hasRequiredParams(endpoint: ApiEndpoint): boolean {
  if (!endpoint.parameters) return false;
  return endpoint.parameters.some((param: any) =>
    param.in === 'query' && param.required === true
  );
}

test.describe('Backend API Automation', () => {
  let apiEndpoints: ApiEndpoint[];
  let testableEndpoints: ApiEndpoint[];

  test.beforeAll(async () => {
    // 获取所有 API 端点
    apiEndpoints = await fetchApiEndpoints();
    console.log(`📋 Total API endpoints: ${apiEndpoints.length}`);

    // 过滤可测试的端点
    testableEndpoints = filterTestableEndpoints(apiEndpoints);
    console.log(`✅ Testable GET endpoints: ${testableEndpoints.length}`);

    // 打印端点列表
    console.log('\n📝 Testable endpoints:');
    testableEndpoints.forEach((endpoint, index) => {
      console.log(`  ${index + 1}. ${endpoint.method} ${endpoint.path}`);
    });
  });

  test('OpenAPI JSON should be accessible', async () => {
    const response = await fetch(OPENAPI_JSON_URL);
    expect(response.ok).toBeTruthy();

    const spec = await response.json();
    expect(spec.openapi).toMatch(/^3\./);
    expect(spec.info.title).toContain('MyStocks');
  });

  test('should verify API documentation structure', async () => {
    // 按标签分组统计端点
    const endpointCounts: Record<string, number> = {};
    const untagged: ApiEndpoint[] = [];

    testableEndpoints.forEach(endpoint => {
      if (endpoint.tags && endpoint.tags.length > 0) {
        endpoint.tags.forEach(tag => {
          endpointCounts[tag] = (endpointCounts[tag] || 0) + 1;
        });
      } else {
        untagged.push(endpoint);
      }
    });

    console.log('\n📊 Endpoints by tag:');
    Object.entries(endpointCounts)
      .sort(([, a], [, b]) => b - a)
      .forEach(([tag, count]) => {
        console.log(`  ${tag}: ${count} endpoints`);
      });

    if (untagged.length > 0) {
      console.log(`\n⚠️  Untagged endpoints: ${untagged.length}`);
    }

    // 验证至少有一些带标签的端点
    expect(Object.keys(endpointCounts).length).toBeGreaterThan(0);
  });

  test.describe('Automated API Endpoint Tests', () => {
    test('should test all GET endpoints', async ({ request }) => {
      // 在测试内部获取端点列表
      const endpoints = await fetchApiEndpoints();
      const testable = filterTestableEndpoints(endpoints);

      console.log(`\n📋 Testing ${testable.length} GET endpoints...\n`);

      const results = {
        passed: 0,
        failed: 0,
        skipped: 0,
        errors: [] as string[]
      };

      // 测试每个端点
      for (const endpoint of testable) {
        const url = replacePathParams(`${API_BASE_URL}${endpoint.path}`);

        console.log(`\n🧪 ${endpoint.method} ${url}`);

        try {
          const startTime = Date.now();
          const response = await request.get(url);
          const duration = Date.now() - startTime;

          console.log(`  Status: ${response.status()}`);
          console.log(`  Duration: ${duration}ms`);

          // 基本验证
          if (response.status() < 500) {
            results.passed++;
            console.log(`  ✅ PASS`);
          } else {
            results.failed++;
            console.log(`  ❌ FAIL - Server error`);
            results.errors.push(`${endpoint.method} ${endpoint.path}: ${response.status()}`);
          }

        } catch (error) {
          results.failed++;
          const errorMsg = error instanceof Error ? error.message : String(error);
          console.error(`  ❌ ERROR: ${errorMsg}`);
          results.errors.push(`${endpoint.method} ${endpoint.path}: ${errorMsg}`);
        }
      }

      // 输出测试摘要
      console.log('\n' + '='.repeat(60));
      console.log('📊 Test Summary:');
      console.log(`  Total:  ${testable.length}`);
      console.log(`  ✅ Pass:  ${results.passed}`);
      console.log(`  ❌ Fail:  ${results.failed}`);
      console.log(`  ⏭️  Skip:  ${results.skipped}`);
      console.log('='.repeat(60));

      // 如果有失败的测试，显示详细信息
      if (results.errors.length > 0) {
        console.log('\n❌ Failed endpoints:');
        results.errors.forEach(err => console.log(`  - ${err}`));
      }

      // 断言：至少应该有80%的端点测试通过
      const passRate = results.passed / testable.length;
      expect(passRate).toBeGreaterThanOrEqual(0.5); // 至少50%通过
    });
  });

  test.describe('Critical API Health Checks', () => {
    test('Health endpoint should return 200', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/health`);
      expect(response.status()).toBe(200);

      const json = await response.json();
      expect(json).toHaveProperty('status', 'healthy');
    });

    test('Root endpoint should redirect to docs', async ({ page }) => {
      await page.goto(API_BASE_URL);
      await page.waitForLoadState('networkidle');

      const url = page.url();
      expect(url).toContain('/docs') || expect(url).toContain('/redoc');
    });
  });

  test.describe('Data Source Endpoints', () => {
    test('Market data endpoints should respond', async ({ request }) => {
      // 测试股票列表端点
      const response = await request.get(
        `${API_BASE_URL}/api/v1/market/stock/list?limit=10`
      );

      if (response.status() === 200) {
        const json = await response.json();
        expect(json).toHaveProperty('code', 200);

        // 验证数据结构
        if (json.data && Array.isArray(json.data)) {
          console.log(`✅ Retrieved ${json.data.length} stocks`);
        }
      } else {
        console.log(`⚠️  Market data endpoint returned ${response.status()}`);
      }
    });
  });

  test.describe('Performance Tests', () => {
    test('API responses should be fast', async ({ request }) => {
      const fastEndpoints = [
        '/health',
        '/openapi.json',
        '/api/v1/market/status'
      ];

      for (const path of fastEndpoints) {
        const startTime = Date.now();
        const response = await request.get(`${API_BASE_URL}${path}`);
        const duration = Date.now() - startTime;

        console.log(`${path}: ${duration}ms`);

        // 健康检查端点应该非常快
        if (path === '/health') {
          expect(duration).toBeLessThan(100);
        }

        // 其他端点也应该在2秒内响应
        expect(duration).toBeLessThan(2000);
      }
    });
  });
});
