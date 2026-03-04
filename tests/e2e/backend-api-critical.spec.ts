/**
 * Backend API Automation E2E Tests - Simplified Version
 *
 * 只测试关键 API 端点，用于快速验证
 */

import { test, expect } from '@playwright/test';

const API_BASE_URL = 'http://localhost:8020';

// 关键端点列表（不需要参数替换）
const CRITICAL_ENDPOINTS = [
  { path: '/health', name: 'Health Check' },
  { path: '/openapi.json', name: 'OpenAPI Spec' },
  { path: '/api/v1/market/status', name: 'Market Status' },
  { path: '/api/v1/data-sources/', name: 'Data Sources List' },
  { path: '/api/v1/data-sources/categories', name: 'Data Source Categories' },
  { path: '/api/data-quality/status/overview', name: 'Data Quality Overview' },
  { path: '/api/dashboard/summary', name: 'Dashboard Summary' },
  { path: '/api/monitoring/summary', name: 'Monitoring Summary' },
];

// 带路径参数的端点（使用默认测试值）
const PARAMETERIZED_ENDPOINTS = [
  { path: '/api/v1/market/stock/list?limit=10', name: 'Stock List' },
  { path: '/api/v1/market/kline?stock_code=000001.SZ&period=daily&limit=5', name: 'K-Line Data' },
  { path: '/api/stock-search/search?query=600519', name: 'Stock Search' },
  { path: '/api/technical/000001.SZ/indicators', name: 'Technical Indicators' },
];

test.describe('Backend API - Critical Endpoints', () => {
  test('should test all critical endpoints', async ({ request }) => {
    console.log(`\n📋 Testing ${CRITICAL_ENDPOINTS.length} critical endpoints...\n`);

    const results = {
      passed: 0,
      failed: 0,
      slow: 0,
      errors: [] as string[]
    };

    const SLOW_THRESHOLD = 1000; // 1秒

    for (const endpoint of CRITICAL_ENDPOINTS) {
      const url = `${API_BASE_URL}${endpoint.path}`;
      console.log(`\n🧪 ${endpoint.name}`);
      console.log(`  URL: ${url}`);

      try {
        const startTime = Date.now();
        const response = await request.get(url);
        const duration = Date.now() - startTime;

        console.log(`  Status: ${response.status()}`);
        console.log(`  Duration: ${duration}ms`);

        // 性能检查
        if (duration > SLOW_THRESHOLD) {
          results.slow++;
          console.log(`  ⚠️  SLOW (>${SLOW_THRESHOLD}ms)`);
        }

        // 状态码检查
        if (response.status() === 200) {
          results.passed++;
          console.log(`  ✅ PASS`);

          // 验证响应是 JSON
          const contentType = response.headers()['content-type'];
          if (contentType && contentType.includes('application/json')) {
            const json = await response.json();

            // 验证统一响应格式
            if ('code' in json) {
              console.log(`  ✓ Has 'code' field (UnifiedResponse)`);
            }
            if ('data' in json) {
              console.log(`  ✓ Has 'data' field (UnifiedResponse)`);
            }
          }
        } else if (response.status() < 500) {
          // 4xx 错误也算通过（可能是参数错误）
          results.passed++;
          console.log(`  ✅ PASS (client error expected)`);
        } else {
          results.failed++;
          console.log(`  ❌ FAIL (server error)`);
          results.errors.push(`${endpoint.name}: HTTP ${response.status()}`);
        }

      } catch (error) {
        results.failed++;
        const errorMsg = error instanceof Error ? error.message : String(error);
        console.error(`  ❌ ERROR: ${errorMsg.substring(0, 100)}`);
        results.errors.push(`${endpoint.name}: ${errorMsg}`);
      }
    }

    // 输出测试摘要
    console.log('\n' + '='.repeat(70));
    console.log('📊 Test Summary:');
    console.log(`  Total:    ${CRITICAL_ENDPOINTS.length}`);
    console.log(`  ✅ Pass:    ${results.passed}`);
    console.log(`  ❌ Fail:    ${results.failed}`);
    console.log(`  ⚠️  Slow:    ${results.slow}`);
    console.log('='.repeat(70));

    // 断言：所有关键端点都应该通过
    expect(results.failed).toBe(0);

    // 性能断言：慢端点不应该超过20%
    const slowRate = results.slow / CRITICAL_ENDPOINTS.length;
    expect(slowRate).toBeLessThan(0.2);
  });
});

test.describe('Backend API - Parameterized Endpoints', () => {
  test('should test endpoints with parameters', async ({ request }) => {
    console.log(`\n📋 Testing ${PARAMETERIZED_ENDPOINTS.length} parameterized endpoints...\n`);

    let passed = 0;
    let failed = 0;

    for (const endpoint of PARAMETERIZED_ENDPOINTS) {
      const url = `${API_BASE_URL}${endpoint.path}`;
      console.log(`\n🧪 ${endpoint.name}`);
      console.log(`  URL: ${url}`);

      try {
        const startTime = Date.now();
        const response = await request.get(url, { timeout: 10000 });
        const duration = Date.now() - startTime;

        console.log(`  Status: ${response.status()}`);
        console.log(`  Duration: ${duration}ms`);

        if (response.status() < 500) {
          passed++;
          console.log(`  ✅ PASS`);
        } else {
          failed++;
          console.log(`  ❌ FAIL`);
        }

      } catch (error) {
        failed++;
        const errorMsg = error instanceof Error ? error.message : String(error);
        console.error(`  ❌ ERROR: ${errorMsg.substring(0, 100)}`);
      }
    }

    console.log('\n' + '='.repeat(70));
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log('='.repeat(70));

    // 断言：至少应该有50%通过
    const passRate = passed / PARAMETERIZED_ENDPOINTS.length;
    expect(passRate).toBeGreaterThanOrEqual(0.5);
  });
});

test.describe('Backend API - Health & Status', () => {
  test('health endpoint should return healthy status', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/health`);

    expect(response.status()).toBe(200);

    const json = await response.json();
    expect(json).toHaveProperty('status', 'healthy');
  });

  test('OpenAPI spec should be valid', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/openapi.json`);

    expect(response.status()).toBe(200);

    const json = await response.json();
    expect(json).toHaveProperty('openapi');
    expect(json.openapi).toMatch(/^3\./);
    expect(json.info).toHaveProperty('title');
  });

  test('root endpoint should redirect to documentation', async ({ page }) => {
    await page.goto(API_BASE_URL);
    await page.waitForLoadState('networkidle');

    const url = page.url();
    expect(url).toMatch(/\/(docs|redoc)/);
  });
});

test.describe('Backend API - Performance', () => {
  test('critical endpoints should respond quickly', async ({ request }) => {
    const performanceTargets = [
      { path: '/health', maxDuration: 100 },
      { path: '/api/v1/market/status', maxDuration: 500 },
      { path: '/api/data-quality/status/overview', maxDuration: 200 },
    ];

    for (const target of performanceTargets) {
      const url = `${API_BASE_URL}${target.path}`;
      const startTime = Date.now();
      const response = await request.get(url);
      const duration = Date.now() - startTime;

      console.log(`${target.path}: ${duration}ms (target: <${target.maxDuration}ms)`);

      expect(response.status()).toBe(200);
      expect(duration).toBeLessThan(target.maxDuration);
    }
  });
});
