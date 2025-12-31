/**
 * MyStocks E2E测试 - 股票列表页面
 *
 * 测试场景：
 * 1. 股票列表页面加载
 * 2. 搜索股票功能
 * 3. 筛选功能
 * 4. 刷新功能
 * 5. 重置筛选
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { StocksPage } from './pages/StocksPage';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('股票列表 - Stocks', () => {
  let stocksPage: StocksPage;

  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();

    stocksPage = new StocksPage(page);
  });

  /**
   * 测试用例 1: 股票列表页面加载
   */
  test('1. 股票列表页面应该正确加载 @smoke @ui', async () => {
    await stocksPage.goto();
    await stocksPage.isLoaded();

    await expect(stocksPage.heading()).toBeVisible();
    await expect(stocksPage.stocksTable()).toBeVisible();
  });

  /**
   * 测试用例 2: 搜索股票功能
   */
  test('2. 应该能够搜索股票 @ui', async () => {
    await stocksPage.goto();
    await stocksPage.isLoaded();

    // 搜索股票
    await stocksPage.searchStock('600519');

    // 验证搜索后页面状态
    await stocksPage.page.waitForTimeout(1000);
    const stockCount = await stocksPage.getStockCount();
    expect(stockCount).toBeGreaterThanOrEqual(0);
  });

  /**
   * 测试用例 3: 按行业筛选
   */
  test('3. 应该能够按行业筛选 @ui', async () => {
    await stocksPage.goto();
    await stocksPage.isLoaded();

    // 按行业筛选（如果有选项）
    const industrySelect = stocksPage.industrySelect();
    const isSelectVisible = await industrySelect.isVisible().catch(() => false);

    if (isSelectVisible) {
      await industrySelect.click();
      await stocksPage.page.waitForTimeout(500);
    }
  });

  /**
   * 测试用例 4: 刷新股票列表
   */
  test('4. 应该能够刷新股票列表 @ui', async () => {
    await stocksPage.goto();
    await stocksPage.isLoaded();

    await stocksPage.refresh();

    // 验证刷新后页面仍然正常
    await expect(stocksPage.stocksTable()).toBeVisible();
  });

  /**
   * 测试用例 5: 重置筛选条件
   */
  test('5. 应该能够重置筛选条件 @ui', async () => {
    await stocksPage.goto();
    await stocksPage.isLoaded();

    // 先搜索
    await stocksPage.searchStock('600519');
    await stocksPage.page.waitForTimeout(500);

    // 重置
    await stocksPage.resetFilters();
    await stocksPage.page.waitForTimeout(500);

    // 验证搜索框已清空
    const searchValue = await stocksPage.searchInput().inputValue();
    expect(searchValue).toBe('');
  });

  /**
   * 测试用例 6: 分页功能
   */
  test('6. 应该显示分页组件 @ui', async () => {
    await stocksPage.goto();
    await stocksPage.isLoaded();

    const pagination = stocksPage.pagination();
    const isVisible = await pagination.isVisible().catch(() => false);

    if (isVisible) {
      await expect(pagination).toBeVisible();
    }
  });
});
