import { test, expect } from '@playwright/test';

test.describe('环境验证测试', () => {
  test('页面基本加载测试', async ({ page }) => {
    // 创建一个简单的测试页面
    await page.setContent(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>测试页面</title>
        </head>
        <body>
          <h1>MyStocks 测试环境验证</h1>
          <div id="test-element">测试元素</div>
          <button id="test-button">测试按钮</button>
        </body>
      </html>
    `);

    // 验证页面标题
    const title = await page.title();
    expect(title).toBe('测试页面');

    // 验证页面元素
    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();
    await expect(h1).toHaveText('MyStocks 测试环境验证');

    const testElement = page.locator('#test-element');
    await expect(testElement).toBeVisible();
    await expect(testElement).toHaveText('测试元素');

    const testButton = page.locator('#test-button');
    await expect(testButton).toBeVisible();
    await expect(testButton).toHaveText('测试按钮');

    // 截图保存
    await page.screenshot({
      path: 'test-results/screenshots/environment-validation.png',
      fullPage: true
    });

    console.log('✅ 页面基本加载测试通过');
  });

  test('Playwright基本功能验证', async ({ page }) => {
    // 设置页面内容
    await page.setContent('<div id="result"></div>');

    // 测试JavaScript执行
    const result = await page.evaluate(() => {
      return {
        userAgent: navigator.userAgent,
        url: window.location.href,
        timestamp: new Date().toISOString(),
        localStorage: localStorage.length,
        sessionStorage: sessionStorage.length
      };
    });

    console.log('浏览器信息:', result);

    // 验证基本API
    expect(result.userAgent).toBeTruthy();
    expect(result.url).toBeTruthy();
    expect(result.timestamp).toBeTruthy();

    // 验证DOM操作
    await page.evaluate(() => {
      document.getElementById('result').textContent = 'DOM操作成功';
    });

    const resultText = await page.locator('#result').textContent();
    expect(resultText).toBe('DOM操作成功');

    console.log('✅ Playwright基本功能验证通过');
  });

  test('Mock数据系统验证', async ({ page }) => {
    // 设置页面内容
    await page.setContent('<div id="mock-test"></div>');

    // 设置Mock数据环境变量
    await page.evaluate(() => {
      localStorage.setItem('mock_data_enabled', 'true');
      localStorage.setItem('test_mode', 'enabled');
      localStorage.setItem('user_token', 'test_token_123');
    });

    // 验证localStorage设置成功
    const mockEnabled = await page.evaluate(() => {
      return {
        enabled: localStorage.getItem('mock_data_enabled'),
        mode: localStorage.getItem('test_mode'),
        token: localStorage.getItem('user_token'),
        count: localStorage.length
      };
    });

    expect(mockEnabled.enabled).toBe('true');
    expect(mockEnabled.mode).toBe('enabled');
    expect(mockEnabled.token).toBe('test_token_123');
    expect(mockEnabled.count).toBe(3);

    // 更新页面显示结果
    await page.evaluate((data) => {
      document.getElementById('mock-test').innerHTML = `
        <p>Mock数据已启用: ${data.enabled}</p>
        <p>测试模式: ${data.mode}</p>
        <p>用户令牌: ${data.token}</p>
        <p>存储项数量: ${data.count}</p>
      `;
    }, mockEnabled);

    // 验证页面更新
    const mockTestDiv = page.locator('#mock-test');
    await expect(mockTestDiv).toContainText('Mock数据已启用: true');
    await expect(mockTestDiv).toContainText('测试模式: enabled');

    console.log('✅ Mock数据系统验证通过');
  });

  test('网络请求模拟验证', async ({ page }) => {
    // 启用请求拦截
    await page.route('**/api/**', route => {
      // 模拟API响应
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: '模拟API响应',
          data: {
            stockCode: '000001',
            price: 12.34,
            volume: 1000000
          }
        })
      });
    });

    // 设置页面内容
    await page.setContent(`
      <div id="api-result">
        <button id="fetch-data">获取数据</button>
        <div id="response"></div>
      </div>
    `);

    // 点击按钮触发请求
    await page.click('#fetch-data');

    // 等待响应并验证
    await page.waitForSelector('#response:not(:empty)');

    const responseText = await page.locator('#response').textContent();
    expect(responseText).toContain('模拟API响应');
    expect(responseText).toContain('000001');

    console.log('✅ 网络请求模拟验证通过');
  });

  test('错误处理验证', async ({ page }) => {
    // 设置页面内容
    await page.setContent(`
      <div id="error-test">
        <button id="trigger-error">触发错误</button>
        <div id="error-message"></div>
      </div>
    `);

    // 监听控制台错误
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // 触发一个JavaScript错误
    await page.evaluate(() => {
      const button = document.getElementById('trigger-error');
      button?.addEventListener('click', () => {
        try {
          // 故意触发错误
          throw new Error('这是一个测试错误');
        } catch (error) {
          document.getElementById('error-message').textContent = error.message;
          console.error('测试错误:', error.message);
        }
      });
    });

    // 点击按钮
    await page.click('#trigger-error');

    // 验证错误处理
    await page.waitForSelector('#error-message:not(:empty)');
    const errorMessage = await page.locator('#error-message').textContent();
    expect(errorMessage).toContain('这是一个测试错误');

    // 验证控制台错误被捕获
    expect(consoleErrors.length).toBeGreaterThan(0);

    console.log('✅ 错误处理验证通过');
  });
});
