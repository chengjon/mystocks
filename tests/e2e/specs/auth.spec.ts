/**
 * 用户认证流程端到端测试
 * 
 * 测试范围:
 * 1. 登录流程
 * 2. 登出流程
 * 3. 会话管理
 * 4. 权限验证
 * 
 * 作者: Claude Code
 * 生成时间: 2025-11-14
 */

import { test, expect } from '@playwright/test';
import { LoginPage } from '../utils/page-objects';
import { UserAuth, ScreenshotHelper } from '../utils/test-helpers';

test.describe('用户认证流程', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
  });

  test('登录页面正常加载', async ({ page }) => {
    await loginPage.navigate();
    
    // 验证页面基本元素
    await expect(loginPage.usernameInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.loginButton).toBeVisible();
    
    // 检查页面标题
    const title = await page.title();
    expect(title).toContain('登录');
    
    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'login-page-loaded');
  });

  test('成功登录流程', async ({ page }) => {
    await loginPage.navigate();
    
    // 使用测试用户登录
    await loginPage.login('testuser', 'password123');
    
    // 验证登录成功，页面跳转
    await expect(page).toHaveURL('/dashboard');
    
    // 验证用户菜单可见（表示登录成功）
    await expect(page.locator('[data-testid=user-menu]')).toBeVisible();
    
    // 验证欢迎消息显示
    await expect(page.locator('[data-testid=welcome-message]')).toBeVisible();
    
    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'login-success');
  });

  test('登录失败 - 无效凭据', async ({ page }) => {
    await loginPage.navigate();
    
    // 使用无效凭据登录
    await loginPage.login('invaliduser', 'wrongpassword');
    
    // 验证显示错误消息
    await expect(loginPage.errorMessage).toBeVisible();
    
    const errorText = await loginPage.getErrorMessage();
    expect(errorText).toContain('无效');
    
    // 验证仍然在登录页面
    await expect(page).toHaveURL('/login');
    
    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'login-failure');
  });

  test('登录失败 - 空字段', async ({ page }) => {
    await loginPage.navigate();
    
    // 直接点击登录按钮（空字段）
    await loginPage.clickLogin();
    
    // 验证表单验证错误
    const usernameError = await page.locator('[data-testid=username-error]').textContent();
    const passwordError = await page.locator('[data-testid=password-error]').textContent();
    
    expect(usernameError).toBeTruthy();
    expect(passwordError).toBeTruthy();
    
    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'login-validation-errors');
  });

  test('登出流程', async ({ page }) => {
    // 首先登录
    await loginPage.navigate();
    await loginPage.login('testuser', 'password123');
    
    // 等待跳转到仪表盘
    await expect(page).toHaveURL('/dashboard');
    
    // 点击用户菜单
    await page.click('[data-testid=user-menu]');
    
    // 点击登出按钮
    await page.click('[data-testid=logout-button]');
    
    // 验证跳转回登录页面
    await expect(page).toHaveURL('/login');
    
    // 验证登录状态已清除
    await expect(loginPage.loginFormVisible).toBeTruthy();
    
    // 尝试访问需要认证的页面，应该重定向到登录页
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/login');
    
    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'logout-success');
  });

  test('会话超时验证', async ({ page }) => {
    await loginPage.navigate();
    await loginPage.login('testuser', 'password123');
    
    // 验证登录成功
    await expect(page).toHaveURL('/dashboard');
    
    // 模拟会话超时（清空localStorage和sessionStorage）
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // 刷新页面
    await page.reload();
    
    // 应该重定向到登录页面
    await expect(page).toHaveURL('/login');
    
    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'session-timeout');
  });

  test('路由守卫 - 未登录用户访问受保护页面', async ({ page }) => {
    // 直接访问需要认证的页面
    const protectedPages = ['/dashboard', '/market', '/technical-analysis', '/wencai'];
    
    for (const protectedPage of protectedPages) {
      await page.goto(protectedPage);
      
      // 应该重定向到登录页面
      await expect(page).toHaveURL('/login');
    }
    
    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'route-guards-redirect');
  });

  test('记住密码功能', async ({ page }) => {
    await loginPage.navigate();
    
    // 勾选记住密码
    await page.check('[data-testid=remember-password]');
    
    // 填写表单
    await loginPage.inputUsername('testuser');
    await loginPage.inputPassword('password123');
    
    // 提交表单
    await loginPage.clickLogin();
    
    // 验证登录成功
    await expect(page).toHaveURL('/dashboard');
    
    // 登出
    await page.click('[data-testid=user-menu]');
    await page.click('[data-testid=logout-button]');
    
    // 验证登录页面显示记住的用户名
    const rememberedUsername = await loginPage.usernameInput.inputValue();
    expect(rememberedUsername).toBe('testuser');
    
    // 密码字段应该为空
    const rememberedPassword = await loginPage.passwordInput.inputValue();
    expect(rememberedPassword).toBe('');
    
    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'remember-password');
  });

  test('多设备登录验证', async ({ page, context }) => {
    // 第一个页面登录
    await loginPage.navigate();
    await loginPage.login('testuser', 'password123');
    
    // 创建新的上下文（模拟第二个设备）
    const newPage = await context.newPage();
    const newLoginPage = new LoginPage(newPage);
    
    // 访问仪表盘
    await newPage.goto('/dashboard');
    
    // 第一个页面登出
    await page.click('[data-testid=user-menu]');
    await page.click('[data-testid=logout-button]');
    
    // 第二个页面应该也被登出
    await expect(newPage).toHaveURL('/login');
    
    // 关闭新页面
    await newPage.close();
    
    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'multi-device-logout');
  });

  test('登录表单可访问性测试', async ({ page }) => {
    await loginPage.navigate();
    
    // 测试键盘导航
    await page.keyboard.press('Tab');
    await expect(loginPage.usernameInput).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(loginPage.passwordInput).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(loginPage.loginButton).toBeFocused();
    
    // 测试Enter键提交
    await page.fill('[data-testid=username]', 'testuser');
    await page.fill('[data-testid=password]', 'password123');
    await page.keyboard.press('Enter');
    
    // 验证提交成功
    await expect(page).toHaveURL('/dashboard');
    
    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'accessibility-keyboard-nav');
  });
});
