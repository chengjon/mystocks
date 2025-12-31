/**
 * MyStocks E2E测试 - 技术分析页面
 *
 * 测试场景：
 * 1. 技术分析页面加载
 * 2. 搜索技术指标
 * 3. 指标概览显示
 * 4. 批量计算功能
 * 5. 重置搜索
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { TechnicalAnalysisPage } from './pages/TechnicalAnalysisPage';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('技术分析 - Technical Analysis', () => {
  let techPage: TechnicalAnalysisPage;

  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();

    techPage = new TechnicalAnalysisPage(page);
  });

  /**
   * 测试用例 1: 技术分析页面加载
   */
  test('1. 技术分析页面应该正确加载 @smoke @ui', async () => {
    await techPage.goto();
    await techPage.isLoaded();

    await expect(techPage.heading()).toBeVisible();
    await expect(techPage.searchCard()).toBeVisible();
  });

  /**
   * 测试用例 2: 指标概览显示
   */
  test('2. 应该显示指标概览卡片 @ui', async () => {
    await techPage.goto();
    await techPage.isLoaded();

    await expect(techPage.indicatorsOverview()).toBeVisible();

    // 验证3个概览卡片
    const cards = techPage.page.locator('.indicator-card');
    await expect(cards).toHaveCount(3);
  });

  /**
   * 测试用例 3: 搜索股票指标
   */
  test('3. 应该能够搜索股票指标 @ui', async () => {
    await techPage.goto();
    await techPage.isLoaded();

    // 搜索股票
    await techPage.searchIndicator('600519');
    await techPage.page.waitForTimeout(2000);

    // 验证搜索后页面状态
    const chartVisible = await techPage.chartCard().isVisible().catch(() => false);
    const indicatorsVisible = await techPage.indicatorsCard().isVisible().catch(() => false);

    expect(chartVisible || indicatorsVisible).toBeTruthy();
  });

  /**
   * 测试用例 4: 重置搜索
   */
  test('4. 应该能够重置搜索 @ui', async () => {
    await techPage.goto();
    await techPage.isLoaded();

    // 先搜索
    await techPage.searchIndicator('600519');
    await techPage.page.waitForTimeout(500);

    // 重置
    await techPage.resetSearch();
    await techPage.page.waitForTimeout(500);

    // 验证搜索框已清空
    const searchValue = await techPage.symbolInput().inputValue();
    expect(searchValue).toBe('');
  });

  /**
   * 测试用例 5: 批量计算功能
   */
  test('5. 应该能够进行批量计算 @ui', async () => {
    await techPage.goto();
    await techPage.isLoaded();

    await expect(techPage.batchCard()).toBeVisible();
    await expect(techPage.batchInput()).toBeVisible();
    await expect(techPage.batchButton()).toBeVisible();
  });

  /**
   * 测试用例 6: 批量计算输入
   */
  test('6. 应该能够输入批量计算股票代码 @ui', async () => {
    await techPage.goto();
    await techPage.isLoaded();

    await techPage.batchInput().fill('600519,000001');

    const inputValue = await techPage.batchInput().inputValue();
    expect(inputValue).toContain('600519');
  });
});
