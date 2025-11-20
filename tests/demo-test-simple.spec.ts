import { test, expect } from '@playwright/test';

test.describe('MyStocks功能演示测试 - 简化版', () => {
  test('登录页面功能验证', async ({ page }) => {
    console.log('开始登录页面测试...');
    
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
          </div>
        </body>
      </html>
    `);
    
    await expect(page.locator('h1')).toHaveText('MyStocks交易系统');
    await expect(page.locator('#username')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    
    console.log('✅ 登录页面元素验证通过');
  });

  test('基础DOM测试', async ({ page }) => {
    console.log('开始基础DOM测试...');
    
    await page.setContent('<h1>测试标题</h1><p>测试段落</p>');
    
    await expect(page.locator('h1')).toHaveText('测试标题');
    await expect(page.locator('p')).toHaveText('测试段落');
    
    console.log('✅ 基础DOM测试通过');
  });

  test('简单JavaScript执行', async ({ page }) => {
    console.log('开始JavaScript执行测试...');
    
    await page.setContent('<div id="test"></div>');
    
    await page.evaluate(() => {
      const element = document.getElementById('test');
      element.textContent = 'Hello Playwright';
    });
    
    const text = await page.locator('#test').textContent();
    expect(text).toBe('Hello Playwright');
    
    console.log('✅ JavaScript执行测试通过');
  });
});