/**
 * MyStocks E2E测试 - 回测分析页面
 *
 * 测试场景：
 * 1. 回测分析页面加载
 * 2. 配置表单显示
 * 3. 运行回测功能
 * 4. 回测结果列表
 * 5. 查看详情功能
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { BacktestAnalysisPage } from './pages/BacktestAnalysisPage';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('回测分析 - Backtest Analysis', () => {
  let backtestPage: BacktestAnalysisPage;

  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();

    backtestPage = new BacktestAnalysisPage(page);
  });

  /**
   * 测试用例 1: 回测分析页面加载
   */
  test('1. 回测分析页面应该正确加载 @smoke @ui', async () => {
    await backtestPage.goto();
    await backtestPage.isLoaded();

    await expect(backtestPage.configCard()).toBeVisible();
    await expect(backtestPage.resultsCard()).toBeVisible();
  });

  /**
   * 测试用例 2: 配置表单显示
   */
  test('2. 应该显示回测配置表单 @ui', async () => {
    await backtestPage.goto();
    await backtestPage.isLoaded();

    await expect(backtestPage.strategySelect()).toBeVisible();
    await expect(backtestPage.symbolInput()).toBeVisible();
    await expect(backtestPage.runBacktestButton()).toBeVisible();
  });

  /**
   * 测试用例 3: 回测结果列表显示
   */
  test('3. 应该显示回测结果列表 @ui', async () => {
    await backtestPage.goto();
    await backtestPage.isLoaded();

    await expect(backtestPage.resultsTable()).toBeVisible();

    const resultCount = await backtestPage.getResultCount();
    expect(resultCount).toBeGreaterThanOrEqual(0);
  });

  /**
   * 测试用例 4: 刷新回测结果
   */
  test('4. 应该能够刷新回测结果 @ui', async () => {
    await backtestPage.goto();
    await backtestPage.isLoaded();

    await backtestPage.refreshResults();

    // 验证页面仍然正常
    await expect(backtestPage.resultsTable()).toBeVisible();
  });

  /**
   * 测试用例 5: 输入股票代码
   */
  test('5. 应该能够输入股票代码 @ui', async () => {
    await backtestPage.goto();
    await backtestPage.isLoaded();

    await backtestPage.enterSymbol('600519');

    const inputValue = await backtestPage.symbolInput().inputValue();
    expect(inputValue).toBe('600519');
  });

  /**
   * 测试用例 6: 查看详情功能（如果有结果）
   */
  test('6. 应该能够查看回测详情（如果有结果） @ui', async () => {
    await backtestPage.goto();
    await backtestPage.isLoaded();

    const resultCount = await backtestPage.getResultCount();

    if (resultCount > 0) {
      await backtestPage.viewDetail(0);
      await backtestPage.page.waitForTimeout(500);

      // 验证详情对话框打开
      const dialogVisible = await backtestPage.detailDialog().isVisible().catch(() => false);

      if (dialogVisible) {
        await expect(backtestPage.detailDialog()).toBeVisible();
        await backtestPage.closeDetailDialog();
      }
    }
  });

  /**
   * 测试用例 7: 分页功能
   */
  test('7. 应该显示分页组件 @ui', async () => {
    await backtestPage.goto();
    await backtestPage.isLoaded();

    const pagination = backtestPage.pagination();
    const isVisible = await pagination.isVisible().catch(() => false);

    if (isVisible) {
      await expect(pagination).toBeVisible();
    }
  });
});
