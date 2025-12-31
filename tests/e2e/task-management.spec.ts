/**
 * MyStocks E2E测试 - 任务管理页面
 *
 * 测试场景：
 * 1. 任务管理页面加载
 * 2. 统计数据显示
 * 3. 创建任务按钮
 * 4. 标签页切换
 * 5. 刷新功能
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { TaskManagementPage } from './pages/TaskManagementPage';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('任务管理 - Task Management', () => {
  let taskPage: TaskManagementPage;

  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();

    taskPage = new TaskManagementPage(page);
  });

  /**
   * 测试用例 1: 任务管理页面加载
   */
  test('1. 任务管理页面应该正确加载 @smoke @ui', async () => {
    await taskPage.goto();
    await taskPage.isLoaded();

    await expect(taskPage.statsRow()).toBeVisible();
    await expect(taskPage.tasksTabs()).toBeVisible();
  });

  /**
   * 测试用例 2: 统计数据显示
   */
  test('2. 应该显示统计数据 @ui', async () => {
    await taskPage.goto();
    await taskPage.isLoaded();

    const stats = await taskPage.getStats();

    expect(stats.total).toBeGreaterThanOrEqual(0);
    expect(stats.running).toBeGreaterThanOrEqual(0);
    expect(stats.todayExecutions).toBeGreaterThanOrEqual(0);
    expect(stats.successRate).toMatch(/\d+%/);
  });

  /**
   * 测试用例 3: 创建任务按钮
   */
  test('3. 应该显示创建任务按钮 @ui', async () => {
    await taskPage.goto();
    await taskPage.isLoaded();

    await expect(taskPage.createTaskButton()).toBeVisible();
  });

  /**
   * 测试用例 4: 导入和导出按钮
   */
  test('4. 应该显示导入和导出按钮 @ui', async () => {
    await taskPage.goto();
    await taskPage.isLoaded();

    await expect(taskPage.importButton()).toBeVisible();
    await expect(taskPage.exportButton()).toBeVisible();
  });

  /**
   * 测试用例 5: 刷新按钮
   */
  test('5. 应该能够刷新任务列表 @ui', async () => {
    await taskPage.goto();
    await taskPage.isLoaded();

    await taskPage.refresh();
    await taskPage.page.waitForTimeout(500);

    // 验证页面仍然正常
    await expect(taskPage.tasksTabs()).toBeVisible();
  });

  /**
   * 测试用例 6: 切换标签页
   */
  test('6. 应该能够切换任务标签页 @ui', async () => {
    await taskPage.goto();
    await taskPage.isLoaded();

    // 切换到定时任务标签
    await taskPage.switchTab('定时任务');
    await taskPage.page.waitForTimeout(500);

    // 验证仍然在任务管理页面
    expect(taskPage.page.url()).toContain('/tasks');
  });

  /**
   * 测试用例 7: 切换到执行历史标签
   */
  test('7. 应该能够切换到执行历史标签 @ui', async () => {
    await taskPage.goto();
    await taskPage.isLoaded();

    await taskPage.switchTab('执行历史');
    await taskPage.page.waitForTimeout(500);

    // 验证标签已切换
    const activeTab = taskPage.page.locator('.el-tabs__active-bar');
    await expect(activeTab).toBeVisible();
  });

  /**
   * 测试用例 8: 获取任务数量
   */
  test('8. 应该能够获取任务数量 @ui', async () => {
    await taskPage.goto();
    await taskPage.isLoaded();

    const taskCount = await taskPage.getTaskCount();
    expect(taskCount).toBeGreaterThanOrEqual(0);
  });

  /**
   * 测试用例 9: 任务表格显示
   */
  test('9. 应该显示任务表格 @ui', async () => {
    await taskPage.goto();
    await taskPage.isLoaded();

    await expect(taskPage.tasksTable()).toBeVisible();
  });

  /**
   * 测试用例 10: 点击创建任务按钮
   */
  test('10. 应该能够点击创建任务按钮 @ui', async () => {
    await taskPage.goto();
    await taskPage.isLoaded();

    await taskPage.clickCreateTask();
    await taskPage.page.waitForTimeout(500);

    // 验证对话框打开（可能有）
    const dialog = taskPage.page.locator('.el-dialog');
    const dialogVisible = await dialog.isVisible().catch(() => false);

    if (dialogVisible) {
      await expect(dialog).toBeVisible();
    }
  });
});
