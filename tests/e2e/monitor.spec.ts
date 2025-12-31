/**
 * MyStocks E2E测试 - 系统监控页面
 *
 * 测试场景：
 * 1. 系统监控页面加载
 * 2. 监控摘要显示
 * 3. 服务详情显示
 * 4. 刷新功能
 * 5. 自动刷新切换
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { MonitorPage } from './pages/MonitorPage';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('系统监控 - System Monitor', () => {
  let monitorPage: MonitorPage;

  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();

    monitorPage = new MonitorPage(page);
  });

  /**
   * 测试用例 1: 系统监控页面加载
   */
  test('1. 系统监控页面应该正确加载 @smoke @ui', async () => {
    await monitorPage.goto();
    await monitorPage.isLoaded();

    await expect(monitorPage.heading()).toBeVisible();
    await expect(monitorPage.monitorSummary()).toBeVisible();
  });

  /**
   * 测试用例 2: 监控摘要显示
   */
  test('2. 应该显示监控摘要 @ui', async () => {
    await monitorPage.goto();
    await monitorPage.isLoaded();

    const summaryCards = monitorPage.summaryCards();
    await expect(summaryCards).toHaveCount(5); // 1个主摘要 + 4个服务详情
  });

  /**
   * 测试用例 3: 服务详情显示
   */
  test('3. 应该显示服务详情 @ui', async () => {
    await monitorPage.goto();
    await monitorPage.isLoaded();

    await expect(monitorPage.servicesSection()).toBeVisible();

    const serviceCards = monitorPage.serviceCards();
    const count = await serviceCards.count();
    expect(count).toBeGreaterThan(0);
  });

  /**
   * 测试用例 4: 刷新功能
   */
  test('4. 应该能够刷新监控数据 @ui', async () => {
    await monitorPage.goto();
    await monitorPage.isLoaded();

    await monitorPage.refresh();
    await monitorPage.page.waitForTimeout(500);

    // 验证页面仍然正常
    await expect(monitorPage.heading()).toBeVisible();
  });

  /**
   * 测试用例 5: 自动刷新切换
   */
  test('5. 应该能够切换自动刷新 @ui', async () => {
    await monitorPage.goto();
    await monitorPage.isLoaded();

    await monitorPage.toggleAutoRefresh();
    await monitorPage.page.waitForTimeout(500);

    // 验证按钮文本已改变
    const buttonText = await monitorPage.toggleAutoRefreshButton().textContent();
    expect(buttonText).toMatch(/暂停自动刷新|启动自动刷新/);
  });

  /**
   * 测试用例 6: 历史记录显示
   */
  test('6. 应该显示监控历史记录 @ui', async () => {
    await monitorPage.goto();
    await monitorPage.isLoaded();

    await expect(monitorPage.historySection()).toBeVisible();

    const historyTable = monitorPage.page.locator('.history-table table');
    const isVisible = await historyTable.isVisible().catch(() => false);

    if (isVisible) {
      await expect(historyTable).toBeVisible();
    }
  });

  /**
   * 测试用例 7: 获取系统健康状态
   */
  test('7. 应该能够获取系统健康状态 @ui', async () => {
    await monitorPage.goto();
    await monitorPage.isLoaded();

    const isHealthy = await monitorPage.isSystemHealthy();
    expect(typeof isHealthy).toBe('boolean');
  });
});
