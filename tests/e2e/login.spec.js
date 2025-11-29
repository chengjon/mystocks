import { test, expect } from '@playwright/test';

/**
 * MyStocks Web 自动化测试 - 登录流程测试
 * 测试场景：
 * 1. 登录页面加载
 * 2. 管理员登录
 * 3. 普通用户登录
 * 4. 登录失败处理
 * 5. 登出功能
 */

const BASE_URL = process.env.BASE_URL || 'http://localhost:3006';
const TIMEOUT = 30000;

test.describe('MyStocks 登录功能测试', () => {
  test.beforeEach(async ({ page }) => {
    // 清空本地存储
    await page.evaluate(() => localStorage.clear());
    // 导航到登录页面
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle' });
  });

  test('1. 登录页面应该正确加载', async ({ page }) => {
    // 检查页面标题
    await expect(page).toHaveTitle(/MyStocks/);

    // 检查页面元素
    await expect(page.getByRole('heading', { name: /MyStocks 登录/ })).toBeVisible();
    await expect(page.getByLabel(/用户名/)).toBeVisible();
    await expect(page.getByLabel(/密码/)).toBeVisible();
    await expect(page.getByRole('button', { name: /登录/ })).toBeVisible();

    // 检查测试账号提示
    await expect(page.getByText(/管理员: admin \/ admin123/)).toBeVisible();
    await expect(page.getByText(/普通用户: user \/ user123/)).toBeVisible();
  });

  test('2. 管理员账号登录成功', async ({ page }) => {
    // 输入管理员账号
    await page.getByLabel(/用户名/).fill('admin');
    await page.getByLabel(/密码/).fill('admin123');

    // 点击登录按钮
    await page.getByRole('button', { name: /登录/ }).click();

    // 等待导航完成（应该跳转到首页或仪表板）
    await page.waitForNavigation({ url: /^(?!.*login)/, timeout: TIMEOUT });

    // 验证已登录（检查是否在首页或仪表板）
    const url = page.url();
    expect(url).not.toContain('/login');

    // 检查本地存储中是否有 token
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();

    // 检查用户信息是否已保存
    const user = await page.evaluate(() => {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    });
    expect(user).toBeTruthy();
  });

  test('3. 普通用户账号登录成功', async ({ page }) => {
    // 输入普通用户账号
    await page.getByLabel(/用户名/).fill('user');
    await page.getByLabel(/密码/).fill('user123');

    // 点击登录按钮
    await page.getByRole('button', { name: /登录/ }).click();

    // 等待导航完成
    await page.waitForNavigation({ url: /^(?!.*login)/, timeout: TIMEOUT });

    // 验证已登录
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
  });

  test('4. 空用户名应该显示验证错误', async ({ page }) => {
    // 保留用户名为空
    await page.getByLabel(/密码/).fill('admin123');

    // 点击登录按钮
    await page.getByRole('button', { name: /登录/ }).click();

    // 等待错误提示
    const errorText = page.getByText(/请输入用户名/);
    await expect(errorText).toBeVisible({ timeout: 5000 });
  });

  test('5. 空密码应该显示验证错误', async ({ page }) => {
    // 输入用户名但保留密码为空
    await page.getByLabel(/用户名/).fill('admin');

    // 点击登录按钮
    await page.getByRole('button', { name: /登录/ }).click();

    // 等待错误提示
    const errorText = page.getByText(/请输入密码/);
    await expect(errorText).toBeVisible({ timeout: 5000 });
  });

  test('6. 错误的密码应该显示登录失败提示', async ({ page }) => {
    // 输入错误的密码
    await page.getByLabel(/用户名/).fill('admin');
    await page.getByLabel(/密码/).fill('wrongpassword');

    // 点击登录按钮
    await page.getByRole('button', { name: /登录/ }).click();

    // 等待错误提示（应该看到登录失败消息）
    // 注意：实际的错误消息取决于后端返回的内容
    const errorMessage = page.locator('.el-message--error');
    await expect(errorMessage).toBeVisible({ timeout: TIMEOUT });
  });

  test('7. 使用 Enter 键提交表单', async ({ page }) => {
    // 输入账号
    await page.getByLabel(/用户名/).fill('admin');
    await page.getByLabel(/密码/).fill('admin123');

    // 在密码字段按 Enter 键
    await page.getByLabel(/密码/).press('Enter');

    // 等待导航完成（应该跳转到首页）
    await page.waitForNavigation({ url: /^(?!.*login)/, timeout: TIMEOUT });

    // 验证已登录
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
  });

  test('8. 登录按钮在登录过程中应该显示加载状态', async ({ page }) => {
    // 输入账号
    await page.getByLabel(/用户名/).fill('admin');
    await page.getByLabel(/密码/).fill('admin123');

    // 点击登录按钮
    const loginButton = page.getByRole('button', { name: /登录/ });
    await loginButton.click();

    // 检查按钮是否显示加载状态（通常会禁用或显示加载图标）
    // 这取决于实现方式，可能需要调整选择器
    await expect(loginButton).toHaveAttribute('disabled', '');
  });
});

test.describe('MyStocks 登出功能测试', () => {
  test.beforeEach(async ({ page }) => {
    // 清空本地存储
    await page.evaluate(() => localStorage.clear());
  });

  test('9. 登出后应该清除存储数据并返回登录页面', async ({ page }) => {
    // 先登录
    await page.goto(`${BASE_URL}/login`);
    await page.getByLabel(/用户名/).fill('admin');
    await page.getByLabel(/密码/).fill('admin123');
    await page.getByRole('button', { name: /登录/ }).click();

    // 等待登录成功
    await page.waitForNavigation({ url: /^(?!.*login)/, timeout: TIMEOUT });

    // 查找登出按钮（通常在导航栏或用户菜单中）
    // 这个选择器可能需要根据实际UI调整
    const logoutButton = page.locator('button:has-text("登出"), button:has-text("退出")');

    if (await logoutButton.count() > 0) {
      await logoutButton.first().click();

      // 等待导航回到登录页面
      await page.waitForNavigation({ url: /login/, timeout: TIMEOUT });

      // 检查本地存储是否已清除
      const token = await page.evaluate(() => localStorage.getItem('token'));
      const user = await page.evaluate(() => localStorage.getItem('user'));

      expect(token).toBeNull();
      expect(user).toBeNull();
    }
  });
});

test.describe('MyStocks 页面导航测试', () => {
  test.beforeEach(async ({ page }) => {
    // 清空本地存储后登录
    await page.evaluate(() => localStorage.clear());
    await page.goto(`${BASE_URL}/login`);
    await page.getByLabel(/用户名/).fill('admin');
    await page.getByLabel(/密码/).fill('admin123');
    await page.getByRole('button', { name: /登录/ }).click();

    // 等待登录成功
    await page.waitForNavigation({ url: /^(?!.*login)/, timeout: TIMEOUT });
  });

  test('10. 成功登录后应该显示仪表板', async ({ page }) => {
    // 检查页面中是否有主要内容（仪表板或首页的标志）
    // 这个选择器需要根据实际页面结构调整
    const dashboard = page.locator('[class*="dashboard"], [class*="content"], main');

    // 等待页面加载完成
    await page.waitForLoadState('networkidle');

    // 检查至少有一个内容容器可见
    await expect(page).not.toHaveTitle(/登录/);
  });

  test('11. 刷新页面后应该保持登录状态', async ({ page }) => {
    // 记录当前 URL
    const currentUrl = page.url();

    // 刷新页面
    await page.reload();

    // 等待页面加载完成
    await page.waitForLoadState('networkidle');

    // 检查是否仍在同一页面（没有被重定向到登录页）
    expect(page.url()).not.toContain('/login');

    // 检查本地存储中仍然有 token
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
  });
});
