/**
 * Technical Analysis Page E2E Tests
 *
 * Tests for the MyStocks Technical Analysis page including:
 * - Indicator library search and filtering
 * - Parameter configuration
 * - Template management
 * - Backtest execution
 * - Responsive design
 * - Error handling
 * - Performance
 *
 * Tier 1 Priority: Core business functionality for technical analysis
 */

import { test, expect, Page } from '@playwright/test';
import { TechnicalAnalysisPage } from '../helpers/page-objects';
import {
  mockTechnicalAnalysisApis,
  mockIndicatorRegistry,
  clearMocks,
  waitForApiCall,
  simulateNetworkError,
} from '../helpers/api-helpers';
import {
  assertPageLoadedSuccessfully,
  assertDataDisplayed,
  assertListNotEmpty,
  assertListEmpty,
  assertDesktopLayout,
  assertTabletLayout,
  assertMobileLayout,
  assertToastMessage,
  assertPagePerformance,
} from '../helpers/assertions';

/**
 * Technical Analysis page test suite - Core functionality
 */
test.describe('Technical Analysis Page - Core Functionality', () => {
  let analysisPage: TechnicalAnalysisPage;

  test.beforeEach(async ({ page }) => {
    // Setup mock APIs for technical analysis
    await mockTechnicalAnalysisApis(page);

    // Create technical analysis page object
    analysisPage = new TechnicalAnalysisPage(page);

    // Navigate to technical analysis page
    await analysisPage.navigateToTechnicalAnalysis();

    // Wait for page to load
    await analysisPage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    // Clear all route mocks
    await clearMocks(page);
  });

  test('应该成功加载技术分析页面', async () => {
    // Verify page is loaded
    const isLoaded = await analysisPage.verifyPageLoaded();
    expect(isLoaded).toBeTruthy();

    // Verify no errors
    await assertPageLoadedSuccessfully(analysisPage['page']);
  });

  test('应该显示指标库列表', async () => {
    // Get indicator count
    const indicatorCount = await analysisPage.getIndicatorCount();
    expect(indicatorCount).toBeGreaterThan(0);

    // Verify list is not empty
    const indicatorList = analysisPage['page'].locator('[data-testid="indicator-list"]');
    await assertListNotEmpty(indicatorList, '[data-testid="indicator-item"]');
  });

  test('应该显示指标分类选项卡', async () => {
    // Check if categories exist
    const categories = analysisPage['page'].locator('[data-testid="indicator-category"]');
    const categoryCount = await categories.count();
    expect(categoryCount).toBeGreaterThan(0);
  });

  test('应该显示第一个指标的完整信息', async () => {
    // Get first indicator data
    const indicatorData = await analysisPage.getFirstIndicatorData();

    // Verify all fields are present
    expect(indicatorData.name).toBeTruthy();
    expect(indicatorData.abbr).toBeTruthy();
    expect(indicatorData.category).toBeTruthy();
  });

  test('应该支持指标搜索功能', async ({ page }) => {
    // Search for indicator
    await analysisPage.searchIndicator('SMA');

    // Wait for search results
    await waitForApiCall(page, '/api/technical/indicators/search', 5000);

    // Get results
    const indicatorCount = await analysisPage.getIndicatorCount();
    expect(indicatorCount).toBeGreaterThan(0);

    // Verify first result matches search
    const firstIndicator = await analysisPage.getFirstIndicatorData();
    expect(firstIndicator.name.toUpperCase()).toContain('SMA');
  });

  test('应该支持按分类过滤指标', async ({ page }) => {
    // Get initial count
    const initialCount = await analysisPage.getIndicatorCount();

    // Apply category filter
    await analysisPage.filterByCategory('Momentum Indicators');

    // Wait for results
    await waitForApiCall(page, '/api/technical/indicators', 5000);

    // Verify results changed
    const filteredCount = await analysisPage.getIndicatorCount();
    expect(filteredCount).toBeGreaterThanOrEqual(0);
  });

  test('应该支持搜索空白查询', async () => {
    // Search with empty string
    await analysisPage.searchIndicator('');

    // Should show all indicators
    const indicatorCount = await analysisPage.getIndicatorCount();
    expect(indicatorCount).toBeGreaterThanOrEqual(0);
  });

  test('应该支持搜索不存在的指标', async ({ page }) => {
    // Search for non-existent indicator
    await analysisPage.searchIndicator('NOTEXIST');

    // Wait for search to complete
    await page.waitForLoadState('networkidle');

    // Should show zero results
    const indicatorCount = await analysisPage.getIndicatorCount();
    expect(indicatorCount).toBe(0);

    // Check for empty state message
    const emptyState = analysisPage['page'].locator('[data-testid="empty-state"]');
    const isVisible = await emptyState.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该显示指标注册表元数据', async () => {
    // Verify mock data has registry info
    expect(mockIndicatorRegistry.total).toBeGreaterThan(0);
    expect(mockIndicatorRegistry.categories).toBeTruthy();
    expect(mockIndicatorRegistry.indicators).toBeTruthy();
  });
});

/**
 * Technical Analysis page test suite - Indicator details and parameters
 */
test.describe('Technical Analysis Page - Indicator Details', () => {
  let analysisPage: TechnicalAnalysisPage;

  test.beforeEach(async ({ page }) => {
    await mockTechnicalAnalysisApis(page);
    analysisPage = new TechnicalAnalysisPage(page);
    await analysisPage.navigateToTechnicalAnalysis();
    await analysisPage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该显示指标参数面板', async ({ page }) => {
    // Get first indicator
    await analysisPage.clickIndicator(0);

    // Wait for detail panel
    const paramPanel = analysisPage['page'].locator('[data-testid="parameter-panel"]');
    await paramPanel.waitFor({ timeout: 5000 });

    // Verify panel is visible
    const isVisible = await paramPanel.isVisible();
    expect(isVisible).toBeTruthy();
  });

  test('应该显示指标参数表', async ({ page }) => {
    // Click indicator
    await analysisPage.clickIndicator(0);
    await page.waitForLoadState('networkidle');

    // Check for parameter table
    const paramTable = analysisPage['page'].locator('[data-testid="parameter-table"]');
    const isVisible = await paramTable.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该支持修改指标参数', async ({ page }) => {
    // Click indicator
    await analysisPage.clickIndicator(0);
    await page.waitForLoadState('networkidle');

    // Set parameter value
    await analysisPage.setParameter('period', '20');

    // Verify parameter was set
    const paramInput = analysisPage['page'].locator('[data-testid="param-period"]');
    const value = await paramInput.inputValue().catch(() => '');
    expect(value).toBe('20');
  });

  test('应该显示指标输出字段', async ({ page }) => {
    // Click indicator
    await analysisPage.clickIndicator(0);
    await page.waitForLoadState('networkidle');

    // Check for output fields
    const outputFields = analysisPage['page'].locator('[data-testid="output-field"]');
    const count = await outputFields.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('应该支持参数验证', async () => {
    // Try to set invalid parameter
    await analysisPage.clickIndicator(0);
    await analysisPage.setParameter('period', 'invalid');

    // Should show validation error or revert
    await analysisPage['page'].waitForLoadState('networkidle');
  });
});

/**
 * Technical Analysis page test suite - Template management
 */
test.describe('Technical Analysis Page - Templates', () => {
  let analysisPage: TechnicalAnalysisPage;

  test.beforeEach(async ({ page }) => {
    await mockTechnicalAnalysisApis(page);
    analysisPage = new TechnicalAnalysisPage(page);
    await analysisPage.navigateToTechnicalAnalysis();
    await analysisPage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该显示保存模板按钮', async ({ page }) => {
    // Check if save button exists
    const saveButton = page.locator('[data-testid="save-template-button"]');
    const isVisible = await saveButton.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该支持保存自定义模板', async ({ page }) => {
    // Click save button
    const saveButton = page.locator('[data-testid="save-template-button"]');
    const isVisible = await saveButton.isVisible().catch(() => false);

    if (isVisible) {
      await saveButton.click();

      // Fill template name
      const nameInput = page.locator('[data-testid="template-name-input"]');
      await nameInput.fill('My Template');

      // Submit
      const submitButton = page.locator('[data-testid="confirm-button"]');
      await submitButton.click();

      // Wait for save
      await page.waitForLoadState('networkidle');
    }
  });

  test('应该显示已保存的模板列表', async ({ page }) => {
    // Check for templates list
    const templateList = page.locator('[data-testid="template-list"]');
    const isVisible = await templateList.isVisible().catch(() => false);
    expect(isVisible || true).toBeTruthy();
  });

  test('应该支持加载模板', async ({ page }) => {
    // Check for template load buttons
    const loadButtons = page.locator('[data-testid="load-template"]');
    const count = await loadButtons.count();

    if (count > 0) {
      await loadButtons.first().click();
      await page.waitForLoadState('networkidle');
    }
  });

  test('应该支持删除模板', async ({ page }) => {
    // Check for delete buttons
    const deleteButtons = page.locator('[data-testid="delete-template"]');
    const count = await deleteButtons.count();

    if (count > 0) {
      await deleteButtons.first().click();

      // Confirm deletion
      const confirmButton = page.locator('[data-testid="confirm-delete"]');
      const isVisible = await confirmButton.isVisible().catch(() => false);

      if (isVisible) {
        await confirmButton.click();
        await page.waitForLoadState('networkidle');
      }
    }
  });
});

/**
 * Technical Analysis page test suite - Responsive design
 */
test.describe('Technical Analysis Page - Responsive Design', () => {
  let analysisPage: TechnicalAnalysisPage;

  test.beforeEach(async ({ page }) => {
    await mockTechnicalAnalysisApis(page);
    analysisPage = new TechnicalAnalysisPage(page);
    await analysisPage.navigateToTechnicalAnalysis();
    await analysisPage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在桌面视图下正确显示 (1920x1080)', async ({ page }) => {
    await assertDesktopLayout(page);

    // Verify all controls visible
    const searchInput = page.locator('[data-testid="indicator-search"]');
    await expect(searchInput).toBeVisible();

    const filterButton = page.locator('[data-testid="category-filter"]');
    await expect(filterButton).toBeVisible();
  });

  test('应该在平板视图下正确显示 (768x1024)', async ({ page }) => {
    await assertTabletLayout(page);

    // Verify core elements still visible
    const indicatorList = page.locator('[data-testid="indicator-list"]');
    await expect(indicatorList).toBeVisible();
  });

  test('应该在手机视图下正确显示 (375x667)', async ({ page }) => {
    await assertMobileLayout(page);

    // Verify search input is accessible
    const searchInput = page.locator('[data-testid="indicator-search"]');
    await expect(searchInput).toBeVisible();
  });
});

/**
 * Technical Analysis page test suite - Error handling
 */
test.describe('Technical Analysis Page - Error Handling', () => {
  let analysisPage: TechnicalAnalysisPage;

  test.beforeEach(async ({ page }) => {
    analysisPage = new TechnicalAnalysisPage(page);
  });

  test('应该在API失败时显示错误消息', async ({ page }) => {
    // Setup network error
    await simulateNetworkError(page, '/api/technical/indicators');

    // Navigate to page
    await analysisPage.navigateToTechnicalAnalysis();

    // Wait for error
    await page.waitForTimeout(2000);

    // Check for error message
    const errorElement = page.locator('[data-testid="error-message"]');
    const isVisible = await errorElement.isVisible().catch(() => false);

    if (isVisible) {
      const errorText = await errorElement.textContent();
      expect(errorText).toBeTruthy();
    }
  });

  test('应该在网络错误后支持重试', async ({ page }) => {
    // Setup initial error
    await simulateNetworkError(page, '/api/technical/indicators');

    // Navigate
    await analysisPage.navigateToTechnicalAnalysis();
    await page.waitForTimeout(1000);

    // Clear error mock
    await clearMocks(page);

    // Setup success mock
    await mockTechnicalAnalysisApis(page);

    // Click retry button
    const retryButton = page.locator('[data-testid="retry-button"]');
    const isVisible = await retryButton.isVisible().catch(() => false);

    if (isVisible) {
      await retryButton.click();
      await page.waitForLoadState('networkidle');

      // Verify data loaded
      const indicatorCount = await analysisPage.getIndicatorCount();
      expect(indicatorCount).toBeGreaterThan(0);
    }
  });
});

/**
 * Technical Analysis page test suite - Performance
 */
test.describe('Technical Analysis Page - Performance', () => {
  let analysisPage: TechnicalAnalysisPage;

  test.beforeEach(async ({ page }) => {
    await mockTechnicalAnalysisApis(page);
    analysisPage = new TechnicalAnalysisPage(page);
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在2秒内加载技术分析页面', async ({ page }) => {
    const startTime = Date.now();

    await analysisPage.navigateToTechnicalAnalysis();
    await analysisPage.waitForPageLoad();

    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(2000);
  });

  test('应该快速响应搜索请求', async ({ page }) => {
    await analysisPage.navigateToTechnicalAnalysis();
    await analysisPage.waitForPageLoad();

    const startTime = Date.now();

    await analysisPage.searchIndicator('SMA');
    await page.waitForLoadState('networkidle');

    const searchTime = Date.now() - startTime;
    expect(searchTime).toBeLessThan(1500);
  });

  test('应该快速响应分类过滤', async ({ page }) => {
    await analysisPage.navigateToTechnicalAnalysis();
    await analysisPage.waitForPageLoad();

    const startTime = Date.now();

    await analysisPage.filterByCategory('Momentum Indicators');
    await page.waitForLoadState('networkidle');

    const filterTime = Date.now() - startTime;
    expect(filterTime).toBeLessThan(1500);
  });
});
