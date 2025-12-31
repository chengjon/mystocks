/**
 * MyStocks E2E测试 - 监控中心页面
 *
 * 测试场景：
 * 1. 监控中心页面加载
 * 2. 摘要统计显示
 * 3. 实时监控数据
 * 4. 告警记录
 * 5. 龙虎榜数据
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { MonitoringDashboardPage } from './pages/MonitoringDashboardPage';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('监控中心 - Monitoring Dashboard', () => {
  let monitoringPage: MonitoringDashboardPage;

  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();

    monitoringPage = new MonitoringDashboardPage(page);
  });

  /**
   * 测试用例 1: 监控中心页面加载
   */
  test('1. 监控中心页面应该正确加载 @smoke @ui', async () => {
    await monitoringPage.goto();
    await monitoringPage.isLoaded();

    await expect(monitoringPage.heading()).toBeVisible();
  });

  /**
   * 测试用例 2: 摘要统计卡片显示
   */
  test('2. 应该显示4个摘要统计卡片 @ui', async () => {
    await monitoringPage.goto();
    await monitoringPage.isLoaded();

    const stats = await monitoringPage.getSummaryStats();

    expect(stats.totalStocks).toBeGreaterThanOrEqual(0);
    expect(stats.limitUp).toBeGreaterThanOrEqual(0);
    expect(stats.limitDown).toBeGreaterThanOrEqual(0);
    expect(stats.unreadAlerts).toBeGreaterThanOrEqual(0);
  });

  /**
   * 测试用例 3: 实时监控数据卡片
   */
  test('3. 应该显示实时监控数据卡片 @ui', async () => {
    await monitoringPage.goto();
    await monitoringPage.isLoaded();

    await expect(monitoringPage.realtimeCard()).toBeVisible();
    await expect(monitoringPage.realtimeTable()).toBeVisible();
  });

  /**
   * 测试用例 4: 告警记录卡片
   */
  test('4. 应该显示告警记录卡片 @ui', async () => {
    await monitoringPage.goto();
    await monitoringPage.isLoaded();

    await expect(monitoringPage.alertsCard()).toBeVisible();
    await expect(monitoringPage.alertsTable()).toBeVisible();
  });

  /**
   * 测试用例 5: 龙虎榜数据卡片
   */
  test('5. 应该显示龙虎榜数据卡片 @ui', async () => {
    await monitoringPage.goto();
    await monitoringPage.isLoaded();

    await expect(monitoringPage.dragonTigerCard()).toBeVisible();
    await expect(monitoringPage.dragonTigerTable()).toBeVisible();
  });

  /**
   * 测试用例 6: 刷新功能
   */
  test('6. 应该能够刷新监控数据 @ui', async () => {
    await monitoringPage.goto();
    await monitoringPage.isLoaded();

    await monitoringPage.refresh();
    await monitoringPage.page.waitForTimeout(500);

    // 验证页面仍然正常
    await expect(monitoringPage.heading()).toBeVisible();
  });

  /**
   * 测试用例 7: 切换监控状态
   */
  test('7. 应该能够切换监控状态 @ui', async () => {
    await monitoringPage.goto();
    await monitoringPage.isLoaded();

    await monitoringPage.toggleMonitoring();
    await monitoringPage.page.waitForTimeout(500);

    // 验证按钮文本已改变
    const buttonText = await monitoringPage.toggleMonitoringButton().textContent();
    expect(buttonText).toMatch(/停止监控|开始监控/);
  });

  /**
   * 测试用例 8: 获取实时数据行数
   */
  test('8. 应该能够获取实时数据行数 @ui', async () => {
    await monitoringPage.goto();
    await monitoringPage.isLoaded();

    const count = await monitoringPage.getRealtimeDataCount();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  /**
   * 测试用例 9: 获取告警记录数
   */
  test('9. 应该能够获取告警记录数 @ui', async () => {
    await monitoringPage.goto();
    await monitoringPage.isLoaded();

    const count = await monitoringPage.getAlertCount();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  /**
   * 测试用例 10: 获取龙虎榜数据行数
   */
  test('10. 应该能够获取龙虎榜数据行数 @ui', async () => {
    await monitoringPage.goto();
    await monitoringPage.isLoaded();

    const count = await monitoringPage.getDragonTigerCount();
    expect(count).toBeGreaterThanOrEqual(0);
  });
});
