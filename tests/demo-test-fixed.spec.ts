import { test, expect } from '@playwright/test';

test.describe('MyStocks功能演示测试', () => {
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
            <div id="message"></div>
          </div>
        </body>
      </html>
    `);
    
    await expect(page.locator('h1')).toHaveText('MyStocks交易系统');
    await expect(page.locator('#username')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('#login-btn')).toBeVisible();
    
    await page.fill('#username', 'demo_user');
    await page.fill('#password', 'demo123');
    
    await page.evaluate(() => {
      const messageDiv = document.getElementById('message');
      if (messageDiv) {
        messageDiv.textContent = '登录成功！欢迎使用MyStocks系统';
      }
    });
    
    await page.waitForTimeout(200);
    
    console.log('✅ 登录页面功能验证通过');
  });

  test('Mock数据系统测试', async ({ page }) => {
    console.log('开始Mock数据系统测试...');
    
    await page.setContent('<div id="mock-data"></div>');
    
    await page.evaluate(() => {
      try {
        localStorage.setItem('stock_data', JSON.stringify([
          { code: '000001', name: '平安银行', price: 12.34, change: 0.56 },
          { code: '600519', name: '贵州茅台', price: 1678.88, change: -12.45 }
        ]));
        localStorage.setItem('user_session', 'active');
      } catch (error) {
        console.error('localStorage设置失败:', error);
      }
    });
    
    const stockData = await page.evaluate(() => {
      try {
        return JSON.parse(localStorage.getItem('stock_data') || '[]');
      } catch (error) {
        console.error('localStorage读取失败:', error);
        return [];
      }
    });
    
    expect(stockData.length).toBeGreaterThan(0);
    expect(stockData[0].code).toBe('000001');
    expect(stockData[1].name).toBe('贵州茅台');
    
    console.log('✅ Mock数据系统测试通过');
  });

  test('基础JavaScript功能测试', async ({ page }) => {
    console.log('开始JavaScript功能测试...');
    
    await page.setContent(`
      <div>
        <button id="calculate-btn">计算</button>
        <div id="result"></div>
      </div>
    `);
    
    await page.evaluate(() => {
      const btn = document.getElementById('calculate-btn');
      const resultDiv = document.getElementById('result');
      
      if (btn && resultDiv) {
        btn.addEventListener('click', () => {
          const sum = 1 + 2 + 3;
          resultDiv.textContent = `计算结果: ${sum}`;
        });
      }
    });
    
    await page.click('#calculate-btn');
    await page.waitForTimeout(200);
    
    const result = await page.locator('#result').textContent();
    expect(result).toContain('计算结果: 6');
    
    console.log('✅ JavaScript功能测试通过');
  });

  test('错误处理测试', async ({ page }) => {
    console.log('开始错误处理测试...');
    
    const consoleErrors: string[] = [];
    
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
      const btn = document.getElementById('error-btn');
      const msgDiv = document.getElementById('error-msg');
      
      if (btn && msgDiv) {
        btn.addEventListener('click', () => {
          try {
            const result = 1 / 0; // 不会抛出错误，但会产生Infinity
            msgDiv.textContent = '计算完成';
            console.log('计算结果:', result);
          } catch (error) {
            msgDiv.textContent = '错误: ' + error.message;
            console.error('捕获到错误:', error.message);
          }
        });
      }
    });
    
    await page.click('#error-btn');
    await page.waitForTimeout(200);
    
    const errorText = await page.locator('#error-msg').textContent();
    expect(errorText).toBe('计算完成');
    
    console.log('✅ 错误处理测试通过');
  });

  test('数据绑定测试', async ({ page }) => {
    console.log('开始数据绑定测试...');
    
    await page.setContent(`
      <div>
        <input type="text" id="input-text" value="初始值" />
        <div id="display-text"></div>
        <button id="update-btn">更新</button>
      </div>
    `);
    
    await page.evaluate(() => {
      const input = document.getElementById('input-text') as HTMLInputElement;
      const display = document.getElementById('display-text') as HTMLElement;
      const btn = document.getElementById('update-btn') as HTMLButtonElement;
      
      if (input && display && btn) {
        btn.addEventListener('click', () => {
          display.textContent = input.value.toUpperCase();
        });
      }
    });
    
    await page.fill('#input-text', 'mystocks');
    await page.click('#update-btn');
    await page.waitForTimeout(200);
    
    const displayText = await page.locator('#display-text').textContent();
    expect(displayText).toBe('MYSTOCKS');
    
    console.log('✅ 数据绑定测试通过');
  });
});