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
    
    console.log('✅ Mock数据系统验证通过');
  });
});