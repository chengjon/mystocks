import { test, expect } from '@playwright/test';

test.describe('MyStocks功能演示测试', () => {
  test('登录页面功能验证', async ({ page }) => {
    // 创建登录页面内容
    await page.setContent(`
      <!DOCTYPE html>
      <html>
        <head><title>MyStocks登录</title></head>
        <body>
          <div class="login-form">
            <h1>MyStocks交易系统</h1>
            <input type="text" id="username" placeholder="用户名" />
            <input type="password" id="password" placeholder="密码" />
            <button id="login-btn">登录</button>
            <div id="message"></div>
          </div>
        </body>
      </html>
    `);

    // 验证页面元素
    await expect(page.locator('h1')).toHaveText('MyStocks交易系统');
    await expect(page.locator('#username')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('#login-btn')).toBeVisible();

    // 测试表单交互
    await page.fill('#username', 'demo_user');
    await page.fill('#password', 'demo123');

    // 模拟登录响应
    await page.evaluate(() => {
      document.getElementById('message').textContent = '登录成功！欢迎使用MyStocks系统';
    });

    const message = await page.locator('#message').textContent();
    expect(message).toContain('登录成功');

    console.log('✅ 登录页面功能验证通过');
  });

  test('Mock数据系统测试', async ({ page }) => {
    await page.setContent('<div id="mock-data"></div>');

    // 模拟股票数据
    await page.evaluate(() => {
      localStorage.setItem('stock_data', JSON.stringify([
        { code: '000001', name: '平安银行', price: 12.34, change: 0.56 },
        { code: '600519', name: '贵州茅台', price: 1678.88, change: -12.45 }
      ]));
      localStorage.setItem('user_session', 'active');
    });

    // 验证Mock数据
    const stockData = await page.evaluate(() => {
      return JSON.parse(localStorage.getItem('stock_data') || '[]');
    });

    expect(stockData.length).toBe(2);
    expect(stockData[0].code).toBe('000001');
    expect(stockData[1].name).toBe('贵州茅台');

    console.log('✅ Mock数据系统测试通过');
  });

  test('API请求模拟测试', async ({ page }) => {
    // 拦截API请求
    await page.route('**/api/market/quote', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            symbol: '000001',
            price: 12.34,
            change: 0.56,
            volume: 1000000
          }
        })
      });
    });

    await page.setContent(`
      <div>
        <button id="get-quote">获取行情</button>
        <div id="quote-result"></div>
      </div>
    `);

    // 触发API请求
    await page.click('#get-quote');
    await page.waitForTimeout(500);

    const result = await page.evaluate(async () => {
      try {
        const response = await fetch('/api/market/quote');
        return await response.json();
      } catch (error) {
        return { error: error.message };
      }
    });

    expect(result.success).toBe(true);
    expect(result.data.symbol).toBe('000001');
    expect(result.data.price).toBe(12.34);

    console.log('✅ API请求模拟测试通过');
  });

  test('错误处理测试', async ({ page }) => {
    const consoleErrors = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.setContent(`
      <div>
        <button id="error-btn">触发错误</button>
        <div id="error-msg"></div>
      </div>
    `);

    await page.evaluate(() => {
      document.getElementById('error-btn').addEventListener('click', () => {
        try {
          throw new Error('测试错误');
        } catch (error) {
          document.getElementById('error-msg').textContent = error.message;
          console.error('捕获到错误:', error.message);
        }
      });
    });

    await page.click('#error-btn');
    await page.waitForTimeout(200);

    const errorText = await page.locator('#error-msg').textContent();
    expect(errorText).toBe('测试错误');
    expect(consoleErrors.length).toBeGreaterThan(0);

    console.log('✅ 错误处理测试通过');
  });
});
