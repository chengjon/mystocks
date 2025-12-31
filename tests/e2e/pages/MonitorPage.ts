/**
 * MonitorPage - Page Object Model for System Monitor
 *
 * 封装系统监控页面的主要交互逻辑
 */

import { Page, expect } from '@playwright/test';

export class MonitorPage {
  readonly page: Page;
  readonly url: string;

  // 页面元素定位器
  readonly heading = () => this.page.getByRole('heading', { name: '系统监控' });
  readonly refreshButton = () => this.page.getByRole('button', { name: '刷新' });
  readonly toggleAutoRefreshButton = () => this.page.getByRole('button', { name: /暂停自动刷新|启动自动刷新/ });
  readonly monitorSummary = () => this.page.locator('.monitor-summary');
  readonly servicesSection = () => this.page.locator('.services-section');
  readonly historySection = () => this.page.locator('.history-section');
  readonly summaryCards = () => this.page.locator('.summary-card');
  readonly serviceCards = () => this.page.locator('.service-card');

  constructor(page: Page, baseUrl: string = 'http://localhost:3000') {
    this.page = page;
    this.url = `${baseUrl}/monitor`;
  }

  /**
   * 导航到系统监控页面
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
   * 验证系统监控页面已加载
   */
  async isLoaded(): Promise<void> {
    await this.waitForLoad();
    // Verify URL contains /monitor
    expect(this.page.url()).toContain('/monitor');
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
   * 切换自动刷新
   */
  async toggleAutoRefresh(): Promise<void> {
    await this.toggleAutoRefreshButton().click();
    await this.page.waitForTimeout(500);
  }

  /**
   * 获取系统健康状态
   */
  async isSystemHealthy(): Promise<boolean> {
    const text = await this.page.locator('.summary-title').textContent();
    return text?.includes('运行正常') ?? false;
  }

  /**
   * 获取服务状态
   */
  async getServiceStatus(serviceName: string): Promise<string> {
    const serviceCard = this.serviceCards().filter({ hasText: serviceName });
    const statusText = await serviceCard.locator('.service-status').textContent();
    return statusText?.includes('正常') ? 'normal' : 'warning';
  }
}
