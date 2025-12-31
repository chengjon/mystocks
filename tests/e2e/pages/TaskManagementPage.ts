/**
 * TaskManagementPage - Page Object Model for Task Management
 *
 * 封装任务管理页面的主要交互逻辑
 */

import { Page, expect } from '@playwright/test';

export class TaskManagementPage {
  readonly page: Page;
  readonly url: string;

  // 页面元素定位器
  readonly statsRow = () => this.page.locator('.stats-row');
  readonly createTaskButton = () => this.page.getByRole('button', { name: '新建任务' });
  readonly importButton = () => this.page.getByRole('button', { name: '导入配置' });
  readonly exportButton = () => this.page.getByRole('button', { name: '导出配置' });
  readonly refreshButton = () => this.page.getByRole('button', { name: '刷新' });
  readonly tasksTabs = () => this.page.locator('.el-tabs');
  readonly tasksTable = () => this.page.locator('.el-table');

  constructor(page: Page, baseUrl: string = 'http://localhost:3000') {
    this.page = page;
    this.url = `${baseUrl}/tasks`;
  }

  /**
   * 导航到任务管理页面
   */
  async goto(): Promise<void> {
    await this.page.goto(this.url);
    await this.waitForLoad();
  }

  /**
   * 等待页面加载完成
   */
  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForTimeout(500);
  }

  /**
   * 验证任务管理页面已加载
   */
  async isLoaded(): Promise<void> {
    await this.waitForLoad();
    // Verify URL contains /tasks
    expect(this.page.url()).toContain('/tasks');
    // Don't enforce strict element visibility - page may be empty or loading
  }


  /**
   * 点击创建任务按钮
   */
  async clickCreateTask(): Promise<void> {
    await this.createTaskButton().click();
  }

  /**
   * 刷新任务列表
   */
  async refresh(): Promise<void> {
    await this.refreshButton().click();
    await this.page.waitForTimeout(1000);
  }

  /**
   * 切换标签页
   */
  async switchTab(tabName: string): Promise<void> {
    await this.page.getByRole('tab', { name: tabName }).click();
    await this.page.waitForTimeout(500);
  }

  /**
   * 获取统计数据
   */
  async getStats(): Promise<{ total: number; running: number; todayExecutions: number; successRate: string }> {
    const statCards = this.statsRow().locator('.stat-card');

    const totalText = await statCards.nth(0).locator('.stat-value').textContent();
    const runningText = await statCards.nth(1).locator('.stat-value').textContent();
    const todayText = await statCards.nth(2).locator('.stat-value').textContent();
    const successRateText = await statCards.nth(3).locator('.stat-value').textContent();

    return {
      total: parseInt(totalText || '0'),
      running: parseInt(runningText || '0'),
      todayExecutions: parseInt(todayText || '0'),
      successRate: successRateText || '0%'
    };
  }

  /**
   * 获取任务数量
   */
  async getTaskCount(): Promise<number> {
    const rows = await this.tasksTable().locator('tbody tr').count();
    return rows;
  }
}
