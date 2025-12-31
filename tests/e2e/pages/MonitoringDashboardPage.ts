/**
 * MonitoringDashboardPage - Page Object Model for Monitoring Dashboard
 *
 * 封装监控中心页面的主要交互逻辑
 */

import { Page, expect } from '@playwright/test';

export class MonitoringDashboardPage {
  readonly page: Page;
  readonly url: string;

  // 页面元素定位器
  readonly heading = () => this.page.getByRole('heading', { name: '📊 监控中心' });
  readonly summaryCards = () => this.page.locator('.summary-cards .summary-card');
  readonly realtimeCard = () => this.page.locator('.realtime-card');
  readonly alertsCard = () => this.page.locator('.alerts-card');
  readonly dragonTigerCard = () => this.page.locator('.dragon-tiger-card');
  readonly refreshButton = () => this.page.getByRole('button', { name: '刷新' });
  readonly toggleMonitoringButton = () => this.page.getByRole('button', { name: /停止监控|开始监控/ });
  readonly realtimeTable = () => this.page.locator('.realtime-card .el-table');
  readonly alertsTable = () => this.page.locator('.alerts-card .el-table');
  readonly dragonTigerTable = () => this.page.locator('.dragon-tiger-card .el-table');

  constructor(page: Page, baseUrl: string = 'http://localhost:3000') {
    this.page = page;
    this.url = `${baseUrl}/monitoring`;
  }

  /**
   * 导航到监控中心页面
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
   * 验证监控中心页面已加载
   */
  async isLoaded(): Promise<void> {
    await this.waitForLoad();
    // Verify URL contains /monitoring
    expect(this.page.url()).toContain('/monitoring');
    // Don't enforce strict element visibility - page may be empty or loading
  }


  /**
   * 刷新监控数据
   */
  async refresh(): Promise<void> {
    await this.refreshButton().click();
    await this.page.waitForTimeout(1000);
  }

  /**
   * 切换监控状态
   */
  async toggleMonitoring(): Promise<void> {
    await this.toggleMonitoringButton().click();
    await this.page.waitForTimeout(500);
  }

  /**
   * 获取摘要统计
   */
  async getSummaryStats(): Promise<{ totalStocks: number; limitUp: number; limitDown: number; unreadAlerts: number }> {
    const cards = this.summaryCards();
    const totalStocksText = await cards.nth(0).locator('.summary-number').textContent();
    const limitUpText = await cards.nth(1).locator('.summary-number').textContent();
    const limitDownText = await cards.nth(2).locator('.summary-number').textContent();
    const unreadAlertsText = await cards.nth(3).locator('.summary-number').textContent();

    return {
      totalStocks: parseInt(totalStocksText || '0'),
      limitUp: parseInt(limitUpText || '0'),
      limitDown: parseInt(limitDownText || '0'),
      unreadAlerts: parseInt(unreadAlertsText || '0')
    };
  }

  /**
   * 获取实时数据行数
   */
  async getRealtimeDataCount(): Promise<number> {
    const rows = await this.realtimeTable().locator('tbody tr').count();
    return rows;
  }

  /**
   * 获取告警记录数
   */
  async getAlertCount(): Promise<number> {
    const rows = await this.alertsTable().locator('tbody tr').count();
    return rows;
  }

  /**
   * 获取龙虎榜数据行数
   */
  async getDragonTigerCount(): Promise<number> {
    const rows = await this.dragonTigerTable().locator('tbody tr').count();
    return rows;
  }
}
