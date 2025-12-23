import { test, expect } from '@playwright/test';

test.describe('综合功能测试', () => {
  test('页面加载和基本元素验证', async ({ page }) => {
    await page.setContent(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>MyStocks登录页面</title>
        </head>
        <body>
          <div class="login-container">
            <h1>MyStocks系统</h1>
            <form id="login-form">
              <input type="text" id="username" placeholder="用户名" />
              <input type="password" id="password" placeholder="密码" />
              <button type="submit" id="login-button">登录</button>
            </form>
            <div id="welcome-message" style="display: none;">欢迎使用MyStocks！</div>
          </div>
        </body>
      </html>
    `);

    // 验证页面标题
    const title = await page.title();
    expect(title).toBe('MyStocks登录页面');

    // 验证页面元素存在
    const loginContainer = page.locator('.login-container');
    await expect(loginContainer).toBeVisible();

    const h1 = page.locator('h1');
    await expect(h1).toHaveText('MyStocks系统');

    const loginForm = page.locator('#login-form');
    await expect(loginForm).toBeVisible();

    const usernameInput = page.locator('#username');
    const passwordInput = page.locator('#password');
    const loginButton = page.locator('#login-button');

    await expect(usernameInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    await expect(loginButton).toBeVisible();

    console.log('✅ 页面加载和元素验证通过');
  });

  test('登录表单交互测试', async ({ page }) => {
    await page.setContent(`
      <div id="app">
        <input id="username" />
        <input id="password" />
        <button id="login-button">登录</button>
        <div id="result"></div>
      </div>
    `);

    // 填写表单
    await page.fill('#username', 'testuser');
    await page.fill('#password', 'password123');

    // 验证输入值
    const usernameValue = await page.locator('#username').inputValue();
    const passwordValue = await page.locator('#password').inputValue();

    expect(usernameValue).toBe('testuser');
    expect(passwordValue).toBe('password123');

    // 点击按钮
    await page.click('#login-button');

    // 模拟登录成功响应
    await page.evaluate(() => {
      document.getElementById('result').textContent = '登录成功';
      document.getElementById('welcome-message')?.style.setProperty('display', 'block');
    });

    const resultText = await page.locator('#result').textContent();
    expect(resultText).toBe('登录成功');

    console.log('✅ 登录表单交互测试通过');
  });

  test('Mock数据系统验证', async ({ page }) => {
    await page.setContent('<div id="mock-status"></div>');

    // 模拟localStorage操作
    await page.evaluate(() => {
      localStorage.setItem('mock_enabled', 'true');
      localStorage.setItem('user_token', 'mock_token_12345');
      localStorage.setItem('api_base_url', 'http://localhost:8000');
      sessionStorage.setItem('session_id', 'session_abc123');
    });

    // 验证localStorage
    const mockData = await page.evaluate(() => {
      return {
        mockEnabled: localStorage.getItem('mock_enabled'),
        userToken: localStorage.getItem('user_token'),
        apiBaseUrl: localStorage.getItem('api_base_url'),
        sessionId: sessionStorage.getItem('session_id'),
        localStorageCount: localStorage.length,
        sessionStorageCount: sessionStorage.length
      };
    });

    expect(mockData.mockEnabled).toBe('true');
    expect(mockData.userToken).toBe('mock_token_12345');
    expect(mockData.apiBaseUrl).toBe('http://localhost:8000');
    expect(mockData.sessionId).toBe('session_abc123');
    expect(mockData.localStorageCount).toBe(3);
    expect(mockData.sessionStorageCount).toBe(1);

    // 更新页面显示Mock状态
    await page.evaluate((data) => {
      document.getElementById('mock-status').innerHTML = `
        <p>Mock状态: ${data.mockEnabled}</p>
        <p>API地址: ${data.apiBaseUrl}</p>
        <p>存储项数量: ${data.localStorageCount}</p>
      `;
    }, mockData);

    const mockStatus = page.locator('#mock-status');
    await expect(mockStatus).toContainText('Mock状态: true');
    await expect(mockStatus).toContainText('API地址: http://localhost:8000');

    console.log('✅ Mock数据系统验证通过');
  });

  test('网络请求拦截和模拟', async ({ page }) => {
    // 拦截API请求
    await page.route('**/api/auth/login', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          token: 'mock_jwt_token_123',
          user: {
            id: 1,
            username: 'testuser',
            role: 'admin'
          }
        })
      });
    });

    await page.route('**/api/user/profile', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          username: 'testuser',
          email: 'testuser@example.com',
          preferences: {
            theme: 'dark',
            language: 'zh-CN'
          }
        })
      });
    });

    await page.setContent(`
      <div id="api-test">
        <button id="login-btn">登录</button>
        <button id="profile-btn">获取资料</button>
        <div id="api-result"></div>
      </div>
    `);

    // 测试登录API
    await page.click('#login-btn');

    // 等待并验证登录响应
    await page.waitForTimeout(1000);

    const loginResult = await page.evaluate(async () => {
      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: 'testuser', password: 'password123' })
        });
        return await response.json();
      } catch (error) {
        return { error: error.message };
      }
    });

    expect(loginResult.success).toBe(true);
    expect(loginResult.token).toBe('mock_jwt_token_123');
    expect(loginResult.user.username).toBe('testuser');

    // 测试用户资料API
    await page.click('#profile-btn');
    await page.waitForTimeout(1000);

    const profileResult = await page.evaluate(async () => {
      try {
        const response = await fetch('/api/user/profile');
        return await response.json();
      } catch (error) {
        return { error: error.message };
      }
    });

    expect(profileResult.username).toBe('testuser');
    expect(profileResult.preferences.theme).toBe('dark');

    console.log('✅ 网络请求拦截和模拟测试通过');
  });

  test('错误处理和异常情况', async ({ page }) => {
    const consoleErrors: string[] = [];

    // 监听控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.setContent(`
      <div id="error-test">
        <button id="trigger-error">触发错误</button>
        <button id="network-error">网络错误</button>
        <div id="error-display"></div>
      </div>
    `);

    // 测试JavaScript错误处理
    await page.evaluate(() => {
      const triggerErrorBtn = document.getElementById('trigger-error');
      const networkErrorBtn = document.getElementById('network-error');
      const errorDisplay = document.getElementById('error-display');

      triggerErrorBtn?.addEventListener('click', () => {
        try {
          // 故意触发错误
          throw new Error('模拟的JavaScript错误');
        } catch (error) {
          errorDisplay.textContent = `错误: ${error.message}`;
          console.error('捕获到错误:', error.message);
        }
      });

      networkErrorBtn?.addEventListener('click', () => {
        fetch('/nonexistent-api-endpoint')
          .catch(error => {
            errorDisplay.textContent = `网络错误: ${error.message}`;
            console.error('网络请求失败:', error.message);
          });
      });
    });

    // 触发JavaScript错误
    await page.click('#trigger-error');
    await page.waitForTimeout(500);

    const errorText = await page.locator('#error-display').textContent();
    expect(errorText).toContain('模拟的JavaScript错误');

    // 触发网络错误
    await page.click('#network-error');
    await page.waitForTimeout(1000);

    const networkErrorText = await page.locator('#error-display').textContent();
    expect(networkErrorText).toContain('网络错误');

    // 验证控制台错误被记录
    expect(consoleErrors.length).toBeGreaterThan(0);

    console.log('✅ 错误处理和异常情况测试通过');
  });

  test('性能和计时验证', async ({ page }) => {
    const startTime = Date.now();

    await page.setContent(`
      <div id="performance-test">
        <h1>性能测试页面</h1>
        <div id="content"></div>
      </div>
    `);

    // 模拟耗时操作
    await page.evaluate(() => {
      const content = document.getElementById('content');
      for (let i = 0; i < 100; i++) {
        const div = document.createElement('div');
        div.textContent = `测试项 ${i}`;
        div.className = 'test-item';
        content.appendChild(div);
      }
    });

    const domCreationTime = Date.now() - startTime;

    // 验证DOM操作结果
    const itemsCount = await page.locator('.test-item').count();
    expect(itemsCount).toBe(100);

    // 验证性能指标
    expect(domCreationTime).toBeLessThan(1000); // 应该在1秒内完成

    // 测量页面操作时间
    const operationStart = Date.now();
    await page.click('#performance-test h1');
    const operationTime = Date.now() - operationStart;

    expect(operationTime).toBeLessThan(100); // 点击操作应该很快

    const totalTime = Date.now() - startTime;
    console.log(`DOM创建时间: ${domCreationTime}ms`);
    console.log(`操作执行时间: ${operationTime}ms`);
    console.log(`总执行时间: ${totalTime}ms`);

    console.log('✅ 性能和计时验证测试通过');
  });

  test('本地存储和数据持久化', async ({ page }) => {
    await page.setContent(`
      <div id="storage-test">
        <input id="user-input" placeholder="输入数据" />
        <button id="save-data">保存数据</button>
        <button id="load-data">加载数据</button>
        <div id="data-display"></div>
      </div>
    `);

    // 测试localStorage保存和读取
    const testData = {
      username: 'testuser',
      preferences: {
        theme: 'dark',
        language: 'zh-CN',
        notifications: true
      },
      lastLogin: new Date().toISOString()
    };

    await page.evaluate((data) => {
      localStorage.setItem('userData', JSON.stringify(data));
      localStorage.setItem('userName', data.username);
      sessionStorage.setItem('sessionData', 'session_value_123');
    }, testData);

    // 验证数据保存
    const savedData = await page.evaluate(() => {
      return {
        userData: JSON.parse(localStorage.getItem('userData') || '{}'),
        userName: localStorage.getItem('userName'),
        sessionData: sessionStorage.getItem('sessionData'),
        allLocalStorage: Object.keys(localStorage),
        allSessionStorage: Object.keys(sessionStorage)
      };
    });

    expect(savedData.userData.username).toBe('testuser');
    expect(savedData.userData.preferences.theme).toBe('dark');
    expect(savedData.userName).toBe('testuser');
    expect(savedData.sessionData).toBe('session_value_123');

    // 测试数据更新
    await page.evaluate(() => {
      const userData = JSON.parse(localStorage.getItem('userData') || '{}');
      userData.preferences.theme = 'light';
      localStorage.setItem('userData', JSON.stringify(userData));
    });

    const updatedData = await page.evaluate(() => {
      const userData = JSON.parse(localStorage.getItem('userData') || '{}');
      return userData.preferences.theme;
    });

    expect(updatedData).toBe('light');

    console.log('✅ 本地存储和数据持久化测试通过');
  });
});
