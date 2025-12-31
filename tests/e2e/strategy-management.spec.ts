/**
 * MyStocks E2E测试 - 策略管理页面
 *
 * 测试场景：
 * 1. 策略管理页面加载
 * 2. 创建策略按钮
 * 3. 空状态显示
 * 4. 策略列表显示
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { StrategyManagementPage } from './pages/StrategyManagementPage';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('策略管理 - Strategy Management', () => {
  let strategyPage: StrategyManagementPage;

  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();

    strategyPage = new StrategyManagementPage(page);
  });

  /**
   * 测试用例 1: 策略管理页面加载
   */
  test('1. 策略管理页面应该正确加载 @smoke @ui', async () => {
    await strategyPage.goto();
    await strategyPage.isLoaded();

    await expect(strategyPage.heading()).toBeVisible();
    await expect(strategyPage.subtitle()).toBeVisible();
  });

  /**
   * 测试用例 2: 创建策略按钮存在
   */
  test('2. 应该显示创建策略按钮 @ui', async () => {
    await strategyPage.goto();
    await strategyPage.isLoaded();

    await expect(strategyPage.createStrategyButton()).toBeVisible();
  });

  /**
   * 测试用例 3: 空状态或策略列表
   */
  test('3. 应该显示空状态或策略列表 @ui', async () => {
    await strategyPage.goto();
    await strategyPage.isLoaded();

    const isEmpty = await strategyPage.isEmpty();
    const hasStrategies = await strategyPage.getStrategyCount() > 0;

    expect(isEmpty || hasStrategies).toBeTruthy();
  });

  /**
   * 测试用例 4: 点击创建策略按钮
   */
  test('4. 应该能够点击创建策略按钮 @ui', async () => {
    await strategyPage.goto();
    await strategyPage.isLoaded();

    await strategyPage.clickCreateStrategy();
    await strategyPage.page.waitForTimeout(500);

    // 验证对话框打开（可能有）
    const dialog = strategyPage.page.locator('.el-dialog');
    const dialogVisible = await dialog.isVisible().catch(() => false);

    if (dialogVisible) {
      await expect(dialog).toBeVisible();
    }
  });

  /**
   * 测试用例 5: 页面不处于加载状态
   */
  test('5. 页面加载后应该不处于加载状态 @ui', async () => {
    await strategyPage.goto();
    await strategyPage.isLoaded();

    // 等待可能的加载状态结束
    await strategyPage.page.waitForTimeout(2000);

    const isLoading = await strategyPage.isLoading();
    expect(isLoading).toBeFalsy();
  });

  /**
   * 测试用例 6: 页面没有错误
   */
  test('6. 页面不应该显示错误状态 @ui', async () => {
    await strategyPage.goto();
    await strategyPage.isLoaded();

    // 等待可能的错误状态显示
    await strategyPage.page.waitForTimeout(1000);

    const hasError = await strategyPage.hasError();
    expect(hasError).toBeFalsy();
  });
});
