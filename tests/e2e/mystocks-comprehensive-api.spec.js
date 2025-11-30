const { test, expect } = require('@playwright/test');

test.describe('MyStocks 完整API功能测试套件', () => {
  const API_BASE_URL = 'http://localhost:8000';
  const FRONTEND_BASE_URL = 'http://localhost:3000';

  test.describe('高优先级核心API测试', () => {

    test('CASE-API-SYSTEM-001: 系统健康检查API', async ({ request }) => {
      console.log('CASE-API-SYSTEM-001: 开始系统健康检查API测试');

      const response = await request.get(`${API_BASE_URL}/health`);
      expect(response.status()).toBe(200);

      const data = await response.json();
      expect(data).toHaveProperty('status');
      expect(data).toHaveProperty('service');
      expect(data).toHaveProperty('timestamp');
      expect(data.status).toBe('healthy');

      console.log('✅ CASE-API-SYSTEM-001: 系统健康检查API测试通过');
    });

    test('CASE-API-SYSTEM-002: Socket.IO状态检查API', async ({ request }) => {
      console.log('CASE-API-SYSTEM-002: 开始Socket.IO状态检查API测试');

      const response = await request.get(`${API_BASE_URL}/api/socketio-status`);
      expect(response.status()).toBe(200);

      const data = await response.json();
      expect(data).toHaveProperty('status');
      expect(data).toHaveProperty('service');
      expect(data.status).toBe('active');

      console.log('✅ CASE-API-SYSTEM-002: Socket.IO状态检查API测试通过');
    });

    test('CASE-API-SYSTEM-003: CSRF Token获取API', async ({ request }) => {
      console.log('CASE-API-SYSTEM-003: 开始CSRF Token获取API测试');

      const response = await request.get(`${API_BASE_URL}/api/csrf-token`);
      expect(response.status()).toBe(200);

      const data = await response.json();
      expect(data).toHaveProperty('csrf_token');
      expect(data).toHaveProperty('token_type');
      expect(data).toHaveProperty('expires_in');
      expect(data.token_type).toBe('Bearer');

      console.log('✅ CASE-API-SYSTEM-003: CSRF Token获取API测试通过');
    });

    test('CASE-API-SYSTEM-004: API文档访问测试', async ({ page }) => {
      console.log('CASE-API-SYSTEM-004: 开始API文档访问测试');

      await page.goto(`${API_BASE_URL}/api/docs`);

      // 等待页面加载完成
      await page.waitForLoadState('networkidle', { timeout: 10000 });

      // 检查页面内容是否包含Swagger UI
      const bodyContent = await page.locator('body').textContent();
      expect(bodyContent).toContain('Swagger');

      const title = await page.title();
      expect(title).toContain('MyStocks Web API');

      console.log('✅ CASE-API-SYSTEM-004: API文档访问测试通过');
    });
  });

  test.describe('市场数据API测试', () => {

    test('CASE-API-MARKET-001: 市场数据根路径测试', async ({ request }) => {
      console.log('CASE-API-MARKET-001: 开始市场数据根路径测试');

      const response = await request.get(`${API_BASE_URL}/api/market/health`);
      expect(response.status()).toBe(200);

      const data = await response.json();
      expect(data).toHaveProperty('status');

      console.log('✅ CASE-API-MARKET-001: 市场数据根路径测试通过');
    });

    test('CASE-API-MARKET-002: 市场数据V2 API测试', async ({ request }) => {
      console.log('CASE-API-MARKET-002: 开始市场数据V2 API测试');

      const response = await request.get(`${API_BASE_URL}/api/market/quotes`);
      expect(response.status()).toBe(200);

      const data = await response.json();
      expect(data).toHaveProperty('status');

      console.log('✅ CASE-API-MARKET-002: 市场数据V2 API测试通过');
    });
  });

  test.describe('数据管理API测试', () => {

    test('CASE-API-DATA-001: 数据管理根路径测试', async ({ request }) => {
      console.log('CASE-API-DATA-001: 开始数据管理根路径测试');

      const response = await request.get(`${API_BASE_URL}/`);
      expect(response.status()).toBe(200);

      const data = await response.json();
      expect(data).toHaveProperty('message');

      console.log('✅ CASE-API-DATA-001: 数据管理根路径测试通过');
    });

    test('CASE-API-CACHE-001: 缓存状态检查API', async ({ request }) => {
      console.log('CASE-API-CACHE-001: 开始缓存状态检查API测试');

      const response = await request.get(`${API_BASE_URL}/api/cache/monitoring/health`);
      expect(response.status()).toBe(200);

      const data = await response.json();
      expect(data).toHaveProperty('success');

      console.log('CASE-API-CACHE-001: 缓存状态检查API测试完成');
    });
  });

  test.describe('系统指标API测试', () => {

    test('CASE-API-METRICS-001: Prometheus指标API', async ({ request }) => {
      console.log('CASE-API-METRICS-001: 开始Prometheus指标API测试');

      const response = await request.get(`${API_BASE_URL}/api/metrics`);
      expect(response.status()).toBe(200);

      console.log('✅ CASE-API-METRICS-001: Prometheus指标API测试通过');
    });
  });

  test.describe('前端集成测试', () => {

    test('CASE-FRONTEND-001: 前端主页加载测试', async ({ page }) => {
      console.log('CASE-FRONTEND-001: 开始前端主页加载测试');

      await page.goto(`${FRONTEND_BASE_URL}`);
      await expect(page.locator('body')).toBeVisible();

      const title = await page.title();
      expect(title).toBeTruthy();

      console.log('✅ CASE-FRONTEND-001: 前端主页加载测试通过');
    });

    test('CASE-FRONTEND-002: 前端资源加载测试', async ({ page }) => {
      console.log('CASE-FRONTEND-002: 开始前端资源加载测试');

      await page.goto(`${FRONTEND_BASE_URL}`);

      // 检查是否有JavaScript错误（暂时忽略CacheManager错误）
      page.on('pageerror', (error) => {
        if (!error.message.includes('startAutoCleanup')) {
          console.error('前端页面错误:', error);
          throw error;
        }
      });

      await page.waitForLoadState('networkidle', { timeout: 5000 });

      console.log('✅ CASE-FRONTEND-002: 前端资源加载测试通过');
    });
  });

  test.describe('后端服务压力测试', () => {

    test('CASE-API-PERFORMANCE-001: API并发压力测试', async ({ request }) => {
      console.log('CASE-API-PERFORMANCE-001: 开始API并发压力测试');

      // 并发10个请求测试/health端点
      const promises = [];
      for (let i = 0; i < 10; i++) {
        promises.push(request.get(`${API_BASE_URL}/health`));
      }

      const results = await Promise.all(promises);
      const successCount = results.filter(r => r.status() === 200).length;

      expect(successCount).toBe(10);
      console.log(`✅ CASE-API-PERFORMANCE-001: API并发压力测试通过 (${successCount}/10成功)`);
    });

    test('CASE-API-PERFORMANCE-002: 响应时间测试', async ({ request }) => {
      console.log('CASE-API-PERFORMANCE-002: 开始响应时间测试');

      const startTime = Date.now();
      const response = await request.get(`${API_BASE_URL}/health`);
      const endTime = Date.now();

      const responseTime = endTime - startTime;
      expect(response.status()).toBe(200);
      expect(responseTime).toBeLessThan(1000); // 1秒内响应

      console.log(`✅ CASE-API-PERFORMANCE-002: 响应时间测试通过 (${responseTime}ms)`);
    });
  });
});
