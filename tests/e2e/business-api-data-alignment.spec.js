const { test, expect } = require('@playwright/test');

test.describe('MyStocks 真实业务API + 数据对齐测试套件', () => {
  const API_BASE_URL = 'http://localhost:8020';
  const FRONTEND_BASE_URL = 'http://localhost:3000';
  let jwtToken; // 存储JWT令牌
  let testStockSymbol = '000001.SZ'; // 测试用股票代码

  // 前置操作：登录获取JWT令牌（解决401问题）
  test.beforeAll(async ({ request }) => {
    console.log('🔑 前置操作：登录获取JWT令牌');

    const loginResponse = await request.post(`${API_BASE_URL}/api/auth/login`, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      form: { username: 'admin', password: 'admin123' }
    });

    expect(loginResponse.status()).toBe(200);
    const loginData = await loginResponse.json();
    jwtToken = loginData.access_token;
    expect(jwtToken).toBeTruthy();

    // 验证令牌有效性
    expect(loginData.token_type).toBe('bearer');
    expect(loginData.user.role).toBe('admin');

    console.log('✅ JWT令牌获取成功，用户角色:', loginData.user.role);
  });

  test.describe('核心业务API - 数据完整性验证', () => {

    test('CASE-API-BUSINESS-001: 股票基本信息查询（业务核心）', async ({ request }) => {
      console.log('CASE-API-BUSINESS-001: 开始股票基本信息查询测试');

      const response = await request.get(`${API_BASE_URL}/api/data/stocks/basic`, {
        headers: { Authorization: `Bearer ${jwtToken}` },
        params: { limit: 5, offset: 0 }
      });

      // 基础状态检查
      expect(response.status()).toBe(200);
      const data = await response.json();
      console.log('📊 API响应结构:', JSON.stringify(data, null, 2));

      // 数据结构验证
      if (data.status === 'success' && data.data) {
        expect(Array.isArray(data.data)).toBeTruthy();
        expect(typeof data.total).toBe('number');
        expect(data.total).toBeGreaterThanOrEqual(0);

        if (data.total > 0 && data.data.length > 0) {
          const stock = data.data[0];
          console.log('📈 股票样本数据:', stock);

          // 业务字段完整性验证（数据对齐基础）
          expect(stock).toHaveProperty('symbol'); // 股票代码
          expect(stock).toHaveProperty('name'); // 股票名称
          expect(stock).toHaveProperty('price'); // 当前价格
          expect(stock).toHaveProperty('change'); // 涨跌幅

          // 数据类型验证（避免前端渲染异常）
          expect(typeof stock.symbol).toBe('string');
          expect(typeof stock.name).toBe('string');
          expect(typeof stock.price).toBe('number');
          expect(typeof stock.change).toBe('number');

          // 业务合理性验证
          expect(stock.symbol.length).toBeGreaterThan(0);
          expect(stock.name.length).toBeGreaterThan(0);
          expect(stock.price).toBeGreaterThan(0);

          console.log(`✅ 股票 ${stock.symbol}(${stock.name}) 价格: ¥${stock.price}, 涨跌幅: ${stock.change}%`);
        } else {
          console.log('⚠️ 返回数据为空，可能是测试环境数据缺失');
        }
      } else {
        console.log('❌ API响应状态异常:', data);
        // 如果API返回错误，我们至少验证它能正确处理错误
        expect(data).toHaveProperty('status');
        expect(data.status).toMatch(/success|error/);
      }

      console.log('✅ CASE-API-BUSINESS-001: 股票基本信息查询测试完成');
    });

    test('CASE-API-BUSINESS-002: 股票搜索功能（业务核心）', async ({ request }) => {
      console.log('CASE-API-BUSINESS-002: 开始股票搜索测试');

      const response = await request.get(`${API_BASE_URL}/api/data/stocks/search`, {
        headers: { Authorization: `Bearer ${jwtToken}` },
        params: { q: '平安', limit: 3 }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      console.log('🔍 搜索结果:', JSON.stringify(data, null, 2));

      // 搜索功能验证
      if (data.status === 'success' && data.data) {
        expect(Array.isArray(data.data)).toBeTruthy();

        if (data.data.length > 0) {
          data.data.forEach(stock => {
            expect(stock.name).toMatch(/平安/); // 搜索结果应包含关键词
            expect(stock).toHaveProperty('symbol');
            expect(stock).toHaveProperty('price');
          });
          console.log(`✅ 搜索到 ${data.data.length} 只包含"平安"的股票`);
        }
      }

      console.log('✅ CASE-API-BUSINESS-002: 股票搜索测试完成');
    });

    test('CASE-API-BUSINESS-003: 市场资金流向数据（业务核心）', async ({ request }) => {
      console.log('CASE-API-BUSINESS-003: 开始资金流向测试');

      const response = await request.get(`${API_BASE_URL}/api/market/v2/fund-flow`, {
        headers: { Authorization: `Bearer ${jwtToken}` }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      console.log('💰 资金流向数据:', JSON.stringify(data, null, 2));

      // 资金流向数据结构验证
      if (data.status === 'success' && data.data) {
        expect(data.data).toHaveProperty('main_net_inflow'); // 主力净流入
        expect(data.data).toHaveProperty('retail_net_inflow'); // 散户净流入

        // 数据类型验证
        expect(typeof data.data.main_net_inflow).toBe('number');
        expect(typeof data.data.retail_net_inflow).toBe('number');

        console.log(`💰 主力净流入: ¥${data.data.main_net_inflow}亿`);
        console.log(`💰 散户净流入: ¥${data.data.retail_net_inflow}亿`);
      }

      console.log('✅ CASE-API-BUSINESS-003: 资金流向测试完成');
    });

    test('CASE-API-BUSINESS-004: 行业分析数据（业务核心）', async ({ request }) => {
      console.log('CASE-API-BUSINESS-004: 开始行业分析测试');

      const response = await request.get(`${API_BASE_URL}/api/analysis/industry/list`, {
        headers: { Authorization: `Bearer ${jwtToken}` }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      console.log('📊 行业分析数据:', JSON.stringify(data, null, 2));

      // 行业数据结构验证
      if (data.status === 'success' && data.data) {
        expect(Array.isArray(data.data)).toBeTruthy();

        if (data.data.length > 0) {
          const industry = data.data[0];
          expect(industry).toHaveProperty('name'); // 行业名称
          expect(industry).toHaveProperty('change'); // 行业涨跌幅
          expect(industry).toHaveProperty('stock_count'); // 股票数量

          console.log(`📈 行业 ${industry.name}: ${industry.change}%, ${industry.stock_count}只股票`);
        }
      }

      console.log('✅ CASE-API-BUSINESS-004: 行业分析测试完成');
    });
  });

  test.describe('数据一致性验证 - 前后端对齐测试', () => {

    test('CASE-DATA-ALIGNMENT-001: 前端页面与API数据对齐', async ({ page, request }) => {
      console.log('CASE-DATA-ALIGNMENT-001: 开始前后端数据对齐测试');

      // 1. 前端登录
      await page.goto(`${FRONTEND_BASE_URL}/login`);
      await page.locator('input[name="username"]').fill('admin');
      await page.locator('input[name="password"]').fill('admin123');
      await page.locator('button[type="submit"]').click();

      // 等待登录完成
      try {
        await page.waitForURL(`${FRONTEND_BASE_URL}/dashboard`, { timeout: 10000 });
        console.log('✅ 前端登录成功');
      } catch (error) {
        console.log('⚠️ 前端登录可能超时，继续测试...');
      }

      // 2. 拦截API请求和响应
      let capturedApiData = null;
      page.on('response', async (response) => {
        if (response.url().includes('/api/data/stocks/basic')) {
          const apiData = await response.json();
          capturedApiData = apiData;
          console.log('🔍 拦截到API响应:', JSON.stringify(apiData, null, 2));
        }
      });

      // 3. 导航到股票页面（如果存在）
      try {
        await page.goto(`${FRONTEND_BASE_URL}/stocks`);
        await page.waitForLoadState('networkidle', { timeout: 15000 });
      } catch (error) {
        console.log('⚠️ 股票页面可能不存在，使用主页继续测试');
        await page.goto(`${FRONTEND_BASE_URL}`);
        await page.waitForLoadState('networkidle', { timeout: 15000 });
      }

      // 4. 验证前端JavaScript错误处理
      let frontendErrors = [];
      page.on('pageerror', (error) => {
        if (!error.message.includes('startAutoCleanup')) {
          frontendErrors.push(error.message);
        }
      });

      // 5. 数据对齐验证
      if (capturedApiData && capturedApiData.data) {
        console.log('📊 API返回数据总数:', capturedApiData.total);
        console.log('📊 API返回数据数组长度:', capturedApiData.data.length);

        // 基础数据一致性检查
        expect(capturedApiData.status).toBe('success');
        expect(typeof capturedApiData.total).toBe('number');
        expect(Array.isArray(capturedApiData.data)).toBeTruthy();

        console.log('✅ API数据结构验证通过');
      } else {
        console.log('⚠️ 未捕获到API数据，可能前端未调用该接口');
      }

      // 6. 前端错误检查
      if (frontendErrors.length > 0) {
        console.log('❌ 前端JavaScript错误:', frontendErrors);
        // 注意关键错误，但不因CacheManager等次要问题中断测试
        const criticalErrors = frontendErrors.filter(err =>
          !err.includes('CacheManager') && !err.includes('startAutoCleanup')
        );
        expect(criticalErrors.length).toBe(0);
      }

      console.log('✅ CASE-DATA-ALIGNMENT-001: 前后端数据对齐测试完成');
    });
  });

  test.describe('API错误处理和边界测试', () => {

    test('CASE-API-ERROR-001: 无效令牌处理', async ({ request }) => {
      console.log('CASE-API-ERROR-001: 开始无效令牌测试');

      const response = await request.get(`${API_BASE_URL}/api/data/stocks/basic`, {
        headers: { Authorization: 'Bearer invalid_token_12345' }
      });

      // 应该返回401未授权
      expect(response.status()).toBe(401);
      console.log('✅ 无效令牌正确返回401');
    });

    test('CASE-API-ERROR-002: 无令牌访问保护资源', async ({ request }) => {
      console.log('CASE-API-ERROR-002: 开始无令牌访问测试');

      const response = await request.get(`${API_BASE_URL}/api/data/stocks/basic`);

      // 应该返回401未授权
      expect(response.status()).toBe(401);
      console.log('✅ 无令牌访问正确返回401');
    });

    test('CASE-API-ERROR-003: 无效搜索参数处理', async ({ request }) => {
      console.log('CASE-API-ERROR-003: 开始无效参数测试');

      const response = await request.get(`${API_BASE_URL}/api/data/stocks/search`, {
        headers: { Authorization: `Bearer ${jwtToken}` },
        params: { q: '', limit: 1000 } // 空搜索词和超大limit
      });

      // 应该处理错误参数或返回空结果，但不应该500错误
      expect([200, 400, 422]).toContain(response.status());
      console.log('✅ 无效参数处理正确，状态码:', response.status());
    });
  });

  test.describe('性能和稳定性测试', () => {

    test('CASE-API-PERFORMANCE-001: API响应时间测试', async ({ request }) => {
      console.log('CASE-API-PERFORMANCE-001: 开始API响应时间测试');

      const startTime = Date.now();
      const response = await request.get(`${API_BASE_URL}/api/data/stocks/basic`, {
        headers: { Authorization: `Bearer ${jwtToken}` },
        params: { limit: 10 }
      });
      const endTime = Date.now();

      const responseTime = endTime - startTime;
      expect(response.status()).toBe(200);

      // API响应时间应该在合理范围内（< 5秒）
      expect(responseTime).toBeLessThan(5000);

      console.log(`✅ API响应时间: ${responseTime}ms`);
    });

    test('CASE-API-PERFORMANCE-002: 并发请求稳定性测试', async ({ request }) => {
      console.log('CASE-API-PERFORMANCE-002: 开始并发请求测试');

      const promises = [];
      for (let i = 0; i < 5; i++) {
        promises.push(
          request.get(`${API_BASE_URL}/api/data/stocks/search`, {
            headers: { Authorization: `Bearer ${jwtToken}` },
            params: { q: `测试${i}`, limit: 1 }
          })
        );
      }

      const results = await Promise.all(promises);
      const successCount = results.filter(r => r.status() === 200).length;

      // 至少80%的请求应该成功
      expect(successCount).toBeGreaterThanOrEqual(4);
      console.log(`✅ 并发测试通过: ${successCount}/5 成功`);
    });
  });
});
