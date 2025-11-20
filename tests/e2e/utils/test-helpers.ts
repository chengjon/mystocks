/**
 * 测试工具函数
 * 提供E2E测试中常用的辅助函数和工具
 * 
 * 作者: Claude Code
 * 生成时间: 2025-11-14
 */

import { Page, BrowserContext, expect } from '@playwright/test';

/**
 * 用户登录工具函数
 */
export class UserAuth {
  /**
   * 执行用户登录
   */
  static async login(page: Page, credentials: { username: string; password: string }): Promise<void> {
    await page.goto('/login');
    
    // 等待页面加载
    await page.waitForLoadState('networkidle');
    
    // 填写登录表单
    await page.fill('[data-testid=username]', credentials.username);
    await page.fill('[data-testid=password]', credentials.password);
    
    // 提交登录
    await page.click('[data-testid=login-button]');
    
    // 验证登录成功
    await expect(page).toHaveURL('/dashboard');
    
    // 验证用户已登录
    await expect(page.locator('[data-testid=user-menu]')).toBeVisible();
  }
  
  /**
   * 执行用户登出
   */
  static async logout(page: Page): Promise<void> {
    // 点击用户菜单
    await page.click('[data-testid=user-menu]');
    
    // 点击登出
    await page.click('[data-testid=logout-button]');
    
    // 验证跳转到登录页
    await expect(page).toHaveURL('/login');
    
    // 验证登录状态已清除
    await expect(page.locator('[data-testid=login-form]')).toBeVisible();
  }
  
  /**
   * 检查用户登录状态
   */
  static async isLoggedIn(page: Page): Promise<boolean> {
    try {
      await expect(page.locator('[data-testid=user-menu]')).toBeVisible({ timeout: 2000 });
      return true;
    } catch {
      return false;
    }
  }
}

/**
 * 页面性能测试工具
 */
export class PerformanceTester {
  /**
   * 测量页面加载性能
   */
  static async measurePageLoad(page: Page, url: string): Promise<any> {
    // 开始性能测量
    const startTime = Date.now();
    
    // 导航到页面
    await page.goto(url);
    await page.waitForLoadState('networkidle');
    
    // 收集性能指标
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paint = performance.getEntriesByType('paint');
      
      const fcp = paint.find(entry => entry.name === 'first-contentful-paint');
      const lcp = paint.find(entry => entry.name === 'largest-contentful-paint');
      
      return {
        loadTime: navigation.loadEventEnd - navigation.navigationStart,
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.navigationStart,
        firstContentfulPaint: fcp ? fcp.startTime : null,
        largestContentfulPaint: lcp ? lcp.startTime : null,
        timeToFirstByte: navigation.responseStart - navigation.requestStart,
      };
    });
    
    const totalTime = Date.now() - startTime;
    
    return {
      ...performanceMetrics,
      totalTime,
      url,
      timestamp: new Date().toISOString()
    };
  }
  
  /**
   * 验证页面性能基准
   */
  static async validatePerformance(page: Page, url: string, budgets: any): Promise<{ passed: boolean; metrics: any; violations: string[] }> {
    const metrics = await this.measurePageLoad(page, url);
    const violations: string[] = [];
    
    // 检查性能预算
    if (metrics.firstContentfulPaint && metrics.firstContentfulPaint > budgets.FCP) {
      violations.push(`FCP: ${metrics.firstContentfulPaint.toFixed(0)}ms > ${budgets.FCP}ms`);
    }
    
    if (metrics.largestContentfulPaint && metrics.largestContentfulPaint > budgets.LCP) {
      violations.push(`LCP: ${metrics.largestContentfulPaint.toFixed(0)}ms > ${budgets.LCP}ms`);
    }
    
    if (metrics.timeToFirstByte > budgets.TTFB) {
      violations.push(`TTFB: ${metrics.timeToFirstByte.toFixed(0)}ms > ${budgets.TTFB}ms`);
    }
    
    const passed = violations.length === 0;
    
    return {
      passed,
      metrics,
      violations
    };
  }
}

/**
 * API测试工具
 */
export class APITester {
  /**
   * 测试API响应时间
   */
  static async testAPIResponseTime(
    page: Page, 
    endpoint: string, 
    maxResponseTime: number = 1000
  ): Promise<{ passed: boolean; responseTime: number; status: number }> {
    const startTime = Date.now();
    
    try {
      const response = await page.request.get(endpoint);
      const responseTime = Date.now() - startTime;
      const status = response.status();
      
      const passed = responseTime < maxResponseTime && status < 400;
      
      return {
        passed,
        responseTime,
        status
      };
    } catch (error) {
      return {
        passed: false,
        responseTime: Date.now() - startTime,
        status: 500
      };
    }
  }
  
  /**
   * 测试多个API端点
   */
  static async testMultipleAPIs(
    page: Page,
    endpoints: Array<{ name: string; url: string; maxTime: number }>
  ): Promise<{ results: any[]; summary: any }> {
    const results = [];
    
    for (const endpoint of endpoints) {
      const result = await this.testAPIResponseTime(page, endpoint.url, endpoint.maxTime);
      results.push({
        ...result,
        name: endpoint.name,
        url: endpoint.url
      });
    }
    
    const summary = {
      total: results.length,
      passed: results.filter(r => r.passed).length,
      failed: results.filter(r => !r.passed).length,
      avgResponseTime: results.reduce((sum, r) => sum + r.responseTime, 0) / results.length
    };
    
    return { results, summary };
  }
}

/**
 * UI组件测试工具
 */
export class UIHelper {
  /**
   * 等待元素可见
   */
  static async waitForElementVisible(
    page: Page, 
    selector: string, 
    timeout: number = 10000
  ): Promise<void> {
    await expect(page.locator(selector)).toBeVisible({ timeout });
  }
  
  /**
   * 等待元素可交互
   */
  static async waitForElementClickable(
    page: Page, 
    selector: string, 
    timeout: number = 10000
  ): Promise<void> {
    await expect(page.locator(selector)).toBeEnabled({ timeout });
  }
  
  /**
   * 等待页面网络空闲
   */
  static async waitForNetworkIdle(
    page: Page, 
    timeout: number = 5000
  ): Promise<void> {
    await page.waitForLoadState('networkidle', { timeout });
  }
  
  /**
   * 等待特定文本出现
   */
  static async waitForText(
    page: Page, 
    text: string, 
    timeout: number = 10000
  ): Promise<void> {
    await expect(page.getByText(text)).toBeVisible({ timeout });
  }
  
  /**
   * 滚动到元素
   */
  static async scrollToElement(page: Page, selector: string): Promise<void> {
    const element = page.locator(selector);
    await element.scrollIntoViewIfNeeded();
  }
  
  /**
   * 清除输入框
   */
  static async clearInput(page: Page, selector: string): Promise<void> {
    await page.click(selector, { clickCount: 3 });
    await page.keyboard.press('Backspace');
  }
}

/**
 * Mock数据工具
 */
export class MockDataHelper {
  /**
   * 验证Mock数据响应
   */
  static async validateMockResponse(
    page: Page,
    apiCall: () => Promise<any>,
    expectedFields: string[]
  ): Promise<{ passed: boolean; data: any; missingFields: string[] }> {
    try {
      const data = await apiCall();
      const missingFields = expectedFields.filter(field => !this.hasNestedProperty(data, field));
      
      const passed = missingFields.length === 0 && data !== null && data !== undefined;
      
      return {
        passed,
        data,
        missingFields
      };
    } catch (error) {
      return {
        passed: false,
        data: null,
        missingFields: expectedFields
      };
    }
  }
  
  /**
   * 检查嵌套属性
   */
  private static hasNestedProperty(obj: any, path: string): boolean {
    return path.split('.').reduce((current, prop) => {
      return current && current[prop] !== undefined ? current[prop] : null;
    }, obj) !== null;
  }
  
  /**
   * 生成测试股票代码
   */
  static generateTestStockCodes(count: number = 5): string[] {
    const codes = [];
    const baseCode = 600000;
    
    for (let i = 0; i < count; i++) {
      codes.push((baseCode + i).toString());
    }
    
    return codes;
  }
}

/**
 * 截图工具
 */
export class ScreenshotHelper {
  /**
   * 截取页面截图并保存
   */
  static async takeScreenshot(
    page: Page, 
    name: string, 
    fullPage: boolean = false
  ): Promise<void> {
    await page.screenshot({
      path: `test-results/screenshots/${name}.png`,
      fullPage,
      animations: 'disabled'
    });
  }
  
  /**
   * 截取特定元素截图
   */
  static async takeElementScreenshot(
    page: Page, 
    selector: string, 
    name: string
  ): Promise<void> {
    await page.locator(selector).screenshot({
      path: `test-results/screenshots/${name}.png`
    });
  }
}

/**
 * 控制台日志监控
 */
export class ConsoleMonitor {
  /**
   * 监控页面控制台错误
   */
  static async monitorConsoleErrors(page: Page): Promise<string[]> {
    const errors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    return errors;
  }
  
  /**
   * 监控网络请求失败
   */
  static async monitorNetworkFailures(page: Page): Promise<any[]> {
    const failures: any[] = [];
    
    page.on('response', response => {
      if (!response.ok()) {
        failures.push({
          url: response.url(),
          status: response.status(),
          statusText: response.statusText()
        });
      }
    });
    
    return failures;
  }
}

/**
 * 测试数据生成器
 */
export class TestDataGenerator {
  /**
   * 生成随机股票代码
   */
  static generateRandomStockCode(): string {
    const exchanges = ['sh', 'sz'];
    const exchange = exchanges[Math.floor(Math.random() * exchanges.length)];
    const code = Math.floor(Math.random() * 9000 + 1000).toString();
    return `${exchange}.${code}`;
  }
  
  /**
   * 生成随机查询文本
   */
  static generateRandomQuery(): string {
    const queries = [
      '涨停板股票',
      '放量股票', 
      '强势股票',
      'MA金叉',
      'RSI超买',
      '技术面突破'
    ];
    
    return queries[Math.floor(Math.random() * queries.length)];
  }
  
  /**
   * 生成随机日期范围
   */
  static generateRandomDateRange(): { start: string; end: string } {
    const end = new Date();
    const start = new Date(end.getTime() - 30 * 24 * 60 * 60 * 1000); // 30天前
    
    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0]
    };
  }
}

/**
 * 测试报告工具
 */
export class ReportHelper {
  /**
   * 记录测试结果
   */
  static async recordTestResult(
    page: Page,
    testName: string,
    result: 'passed' | 'failed',
    details?: any
  ): Promise<void> {
    const report = {
      testName,
      result,
      timestamp: new Date().toISOString(),
      url: page.url(),
      details
    };
    
    // 这里可以实现将结果保存到文件或发送通知
    console.log(`📋 Test Result: ${testName} - ${result.toUpperCase()}`);
  }
  
  /**
   * 生成测试总结
   */
  static generateTestSummary(results: any[]): any {
    const summary = {
      total: results.length,
      passed: results.filter(r => r.result === 'passed').length,
      failed: results.filter(r => r.result === 'failed').length,
      successRate: 0,
      timestamp: new Date().toISOString()
    };
    
    summary.successRate = summary.total > 0 ? 
      (summary.passed / summary.total * 100).toFixed(2) : '0.00';
    
    return summary;
  }
}
